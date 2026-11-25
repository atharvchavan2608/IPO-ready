"""Select the latest good capture per item, with fallback, and record what was used."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from .config import CAPTURES


def runs(source: str) -> list[Path]:
    return sorted(p for p in (CAPTURES / source).glob("*/manifest.json") if p.parent.name != "store")


def latest_good_items(source: str) -> tuple[dict[str, dict], list[dict]]:
    """Return ({item_id: item+abs_path+run}, fallbacks).

    Walk runs newest-first; the first run where an item succeeded supplies it. If the newest run
    attempted an item and failed, the fallback is recorded with both run ids.
    """
    chosen: dict[str, dict] = {}
    failed_newer: dict[str, dict] = {}
    for m in reversed(runs(source)):
        man = json.loads(m.read_text(encoding="utf-8"))
        for it in man.get("items", []):
            iid = it.get("id")
            if iid is None or iid in chosen:
                continue
            ok = it.get("status") == 200 and "error" not in it and it.get("path")
            if ok:
                run = it.get("reused_from_run") or m.parent.name
                path = CAPTURES / source / run / it["path"]
                if path.exists():
                    chosen[iid] = {**it, "run": run, "abs_path": str(path)}
                    continue
            failed_newer.setdefault(iid, {"run": m.parent.name, "error": it.get("error") or f"HTTP {it.get('status')}"})
    fallbacks = []
    for iid, f in failed_newer.items():
        if iid in chosen:
            fallbacks.append({"source": source, "item": iid, "failed_run": f["run"], "error": f["error"],
                              "used_run": chosen[iid]["run"], "state": "fallback_to_previous_capture"})
        else:
            fallbacks.append({"source": source, "item": iid, "failed_run": f["run"], "error": f["error"],
                              "used_run": None, "state": "unavailable"})
    return chosen, fallbacks


def write_simulated_failure(source: str, item_ids: list[str]) -> Path:
    """Write a run manifest in which every item failed, to exercise the fallback path offline."""
    rid = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-simfail"
    folder = CAPTURES / source / rid
    folder.mkdir(parents=True, exist_ok=True)
    items = [{"id": i, "status": None, "error": "simulated failure (pipeline --simulate-failure)",
              "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")} for i in item_ids]
    p = folder / "manifest.json"
    p.write_text(json.dumps({"source": source, "run_id": rid, "simulated": True, "items": items,
                             "summary": {"attempted": len(items), "ok": 0, "failed": len(items)}}, indent=2), encoding="utf-8")
    return p
