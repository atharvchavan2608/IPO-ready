"""Local server: static pages from site/ plus Python APIs.

  python -m ipo_ready.server [--port 8765]

Routes
  /                      Page 1 (company dashboard, home)
  /compare.html          Page 2 (listed peers + unlisted screener)
  /portfolio.html        Page 3 (portfolio risk lab)
  /data/current/...      pipeline JSON (versioned copies under /data/builds/<id>/)
  GET /api/screen?query=...                                run an unlisted screen
  GET /api/portfolio/allocate?amount=500000&tolerance=balanced&company=igx
  GET /api/agent/disclosure?company=igx&field=inventories   run the disclosure-gap agent now
  GET /api/health
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import webbrowser
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlencode

from flask import Flask, abort, jsonify, redirect, request, send_from_directory
from werkzeug.serving import make_server

from . import agent, allocation, lookup, screener
from .config import BUILDS, CURRENT, SITE, load_universe

app = Flask(__name__, static_folder=None)
PUBLISHED_CURRENT = CURRENT


def _snapshot_file(name: str) -> Path:
    path = CURRENT / name
    if path.is_file() or CURRENT != PUBLISHED_CURRENT:
        return path
    manifest = CURRENT / "manifest.json"
    if manifest.is_file():
        try:
            version = json.loads(manifest.read_text(encoding="utf-8")).get("build_id", "")
        except (OSError, ValueError):
            version = ""
        if re.fullmatch(r"\d{8}T\d{6}Z", version):
            archived = BUILDS / version / name
            return archived if archived.is_file() else path
    for build in sorted(BUILDS.glob("????????T??????Z"), reverse=True):
        if (build / "manifest.json").is_file() and (build / name).is_file():
            return build / name
    return path


def _revision(path: Path) -> tuple:
    stat = path.stat()
    return stat.st_ino, stat.st_mtime_ns, stat.st_size


@app.after_request
def no_cache(resp):
    if request.path.startswith("/data/") or request.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    return resp


@app.get("/")
def home():
    return send_from_directory(SITE, "index.html")


@app.get("/portfolio.html")
def portfolio_page():
    if request.args.get("legacy") == "1" or not _snapshot_file("catalog.json").is_file():
        return send_from_directory(SITE, "portfolio.html")
    values = {key: request.args[key] for key in ("amount", "tolerance", "include_unlisted") if key in request.args}
    if request.args.get("company"):
        values["workspace_company"] = request.args["company"]
    return redirect(f"/compare.html?{urlencode(values)}#allocation")


@app.get("/<path:path>")
def static_files(path: str):
    if ".." in path:
        abort(404)
    if path.startswith("data/current/"):
        relative = path.removeprefix("data/current/")
        if re.fullmatch(r"(?:company/[a-z0-9-]+|[a-z]+)\.json", relative):
            snapshot = _snapshot_file(relative)
            if relative == "catalog.json" and snapshot.is_file():
                catalog = _catalog(snapshot)
                response = jsonify(catalog)
                if snapshot != CURRENT / relative:
                    response.headers["X-IPO-Ready-Data"] = "retained-build"
                return response
            if relative.startswith("company/") and not snapshot.is_file():
                acquired = lookup.read_acquired(Path(relative).stem)
                if acquired:
                    return jsonify(acquired["company"])
            if snapshot != CURRENT / relative:
                response = send_from_directory(snapshot.parent, snapshot.name)
                response.headers["X-IPO-Ready-Data"] = "retained-build"
                return response
    return send_from_directory(SITE, path)


@app.get("/api/health")
def health():
    path = _snapshot_file("manifest.json")
    man = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
    return jsonify({"ok": True, "build_id": man and man["build_id"], "mode": man and man["mode"],
                    "retained_build": path != CURRENT / "manifest.json"})


@lru_cache(maxsize=1)
def _screen_snapshot(path: Path, revision: tuple) -> tuple[list[dict], str | None]:
    """Reuse the parsed current summary until the pipeline replaces the file."""
    data = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)
    return (data["screen_rows"] if path.name == "catalog.json" else data["companies"], data.get("build_id"))


def _catalog(path: Path) -> dict:
    return lookup.overlay_catalog(_portfolio_snapshot(path, _revision(path)))


def _lookup_online() -> bool:
    return os.environ.get("IPO_READY_LOOKUP_OFFLINE") != "1"


@app.get("/api/company-lookup")
def search_company():
    if request.remote_addr not in {"127.0.0.1", "::1"}:
        return jsonify({"error": "Company lookup is available in the local demo."}), 403
    try:
        return jsonify(lookup.search(request.args.get("q", ""), online=_lookup_online()))
    except lookup.LookupError as exc:
        return jsonify({"error": str(exc)}), exc.status
    except OSError:
        return jsonify({"error": "The local source directory could not be opened."}), 503


@app.post("/api/company-lookup")
def add_company():
    if request.remote_addr not in {"127.0.0.1", "::1"}:
        return jsonify({"error": "Company lookup is available in the local demo."}), 403
    if request.content_length is None or request.content_length > 512:
        return jsonify({"error": "Send a directory symbol as a short JSON request."}), 400
    body = request.get_json(silent=True)
    symbol = body.get("symbol") if isinstance(body, dict) and set(body) == {"symbol"} else None
    if not isinstance(symbol, str) or not lookup.SYMBOL.fullmatch(symbol.strip().upper()):
        return jsonify({"error": "Select a valid NSE symbol from the directory results."}), 400
    symbol = symbol.strip().upper()
    try:
        path = _snapshot_file("catalog.json")
        base = _portfolio_snapshot(path, _revision(path))
        listed = next((row for row in base["companies"] if row["identity"].get("symbol") == symbol), None)
        if listed:
            return jsonify({"state": "already_added", "row": listed})
        record, state = lookup.acquire(symbol, online=_lookup_online())
        existing = next((row for row in base["companies"] if row["identity"].get("isin") and
                         row["identity"]["isin"] == record["row"]["identity"]["isin"]), None)
        if existing:
            return jsonify({"state": "already_added", "row": existing})
        return jsonify({"state": state, "row": record["row"], "sources": record["company"]["lookup"]})
    except lookup.LookupError as exc:
        return jsonify({"error": str(exc)}), exc.status
    except (OSError, ValueError, KeyError, ArithmeticError):
        return jsonify({"error": "The company could not be added. Existing dashboard data is still available."}), 503


@app.get("/api/screen")
def run_screen():
    try:
        groups = screener.parse_query(request.args.get("query", ""))
    except screener.QueryError as exc:
        return jsonify({"error": str(exc)}), 400
    market = request.args.get("market", "unlisted")
    if market not in {"unlisted", "listed", "mixed"}:
        return jsonify({"error": "Choose listed, unlisted or mixed."}), 400
    try:
        path = _snapshot_file("companies.json" if market == "unlisted" else "catalog.json")
        if market == "unlisted":
            rows, build_id = _screen_snapshot(path, _revision(path))
        else:
            catalog = _catalog(path)
            rows, build_id = catalog["screen_rows"], catalog["build_id"]
    except (OSError, ValueError, KeyError):
        return jsonify({"error": "Company data is unavailable. Run python -m ipo_ready.pipeline --offline and try again."}), 503
    exclusions = {
        company["id"]: company["screen_exclusion"]
        for company in load_universe()["unlisted"]
        if "screen_exclusion" in company
    }
    if market == "listed":
        rows = [row for row in rows if row["listing"] == "listed"]
    return jsonify(screener.screen(groups, rows, exclusions) | {"build_id": build_id})


@app.get("/api/agent/disclosure")
def run_agent():
    cid = request.args.get("company", "")
    field = request.args.get("field", "")
    uni = {c["id"]: c for c in load_universe()["unlisted"]}
    if cid not in uni:
        return jsonify({"error": f"unknown company '{cid}'"}), 400
    if field not in agent.FIELDS:
        return jsonify({"error": f"field must be one of {list(agent.FIELDS)}"}), 400
    from .pipeline import provider_fields_for

    t0 = time.perf_counter()
    out = agent.run(uni[cid], provider_fields_for(cid), field)
    out["ran_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    out["duration_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    return jsonify(out)


@lru_cache(maxsize=1)
def _portfolio_snapshot(path: Path, revision: tuple) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)


@app.get("/api/portfolio/allocate")
def run_allocation():
    args = request.args
    if any(key not in ("amount", "tolerance", "company", "include_unlisted") or len(values) != 1
           for key, values in args.lists()):
        return jsonify({"error": "Use amount, tolerance, company and include_unlisted once each."}), 400
    tolerance = args.get("tolerance", allocation.DEFAULT_TOLERANCE)
    try:
        amount, include = allocation.validate_parameters(args.get("amount", allocation.DEFAULT_AMOUNT), tolerance,
                                                        args.get("include_unlisted", "true"))
        path = _snapshot_file("portfolio.json")
        snapshot = _portfolio_snapshot(path, _revision(path))
        company = args.get("company", snapshot["default_company"])
        return jsonify(allocation.allocate(snapshot, amount, tolerance, company, include))
    except allocation.AllocationInputError as exc:
        return jsonify({"error": str(exc)}), 400
    except (OSError, ValueError, TypeError, KeyError, ArithmeticError):
        return jsonify({"error": "Portfolio data is unavailable. Run python -m ipo_ready.pipeline --offline and try again."}), 503


@app.get("/api/workspace/allocate")
def run_workspace_allocation():
    allowed = {"amount", "tolerance", "company", "include_unlisted", "shortlist", "horizon", "cash_reserve"}
    if any(key not in allowed or len(values) != 1 for key, values in request.args.lists()):
        return jsonify({"error": "Use each workspace scenario parameter once."}), 400
    try:
        paths = [_snapshot_file(name) for name in ("portfolio.json", "catalog.json")]
        snapshot = _portfolio_snapshot(paths[0], _revision(paths[0]))
        catalog = _catalog(paths[1])
        if snapshot["build_id"] != catalog["build_id"]:
            raise ValueError("Data build mismatch")
        return jsonify(allocation.workspace_scenario(snapshot, catalog["companies"], request.args))
    except allocation.AllocationInputError as exc:
        return jsonify({"error": str(exc)}), 400
    except (OSError, ValueError, TypeError, KeyError, ArithmeticError):
        return jsonify({"error": "Workspace data is unavailable. Rebuild from the retained captures and try again."}), 503


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--open-browser", action="store_true", help="open the home page after binding the server")
    a = ap.parse_args()
    if a.open_browser:
        with make_server(a.host, a.port, app, threaded=True) as server:
            host = "127.0.0.1" if a.host == "0.0.0.0" else a.host
            url = f"http://{host}:{server.server_port}/"
            print(f"IPO-Ready on {url}  (Page 1)  /compare.html  /portfolio.html", flush=True)
            webbrowser.open(url)
            server.serve_forever()
    else:
        print(f"IPO-Ready on http://{a.host}:{a.port}/  (Page 1)  /compare.html  /portfolio.html")
        app.run(host=a.host, port=a.port, debug=False)


if __name__ == "__main__":
    main()
