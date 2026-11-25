"""Dated headlines from captured Google News RSS: headline, publisher, date and link only."""
from __future__ import annotations

import email.utils
import xml.etree.ElementTree as ET
from pathlib import Path

from .sources import latest_good_items


def parse_rss(path: Path, limit: int = 8) -> list[dict]:
    root = ET.fromstring(Path(path).read_bytes())
    items = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        src = it.find("source")
        publisher = (src.text or "").strip() if src is not None else ""
        if publisher and title.endswith(" - " + publisher):
            title = title[: -len(" - " + publisher)]
        pub = it.findtext("pubDate")
        try:
            when = email.utils.parsedate_to_datetime(pub).date().isoformat() if pub else None
        except (TypeError, ValueError):
            when = None
        items.append({"title": title, "publisher": publisher, "date": when, "link": (it.findtext("link") or "").strip()})
    seen, out = set(), []
    for i in sorted(items, key=lambda x: x["date"] or "", reverse=True):
        k = i["title"].lower()[:80]
        if k in seen:
            continue
        seen.add(k)
        out.append(i)
    return out[:limit]


def build_news() -> dict:
    items, fallbacks = latest_good_items("news")
    out = {}
    for iid, it in items.items():
        cid = it.get("company")
        try:
            out[cid] = {"query": it.get("query"), "retrieved_at": it["retrieved_at"], "items": parse_rss(Path(it["abs_path"])),
                        "source": {"name": "Google News RSS search", "url": it["url"], "sha256": it["sha256"], "run": it["run"]}}
        except ET.ParseError as exc:
            out[cid] = {"state": "parse_error", "error": str(exc)}
    return {"by_company": out, "fallbacks": fallbacks}
