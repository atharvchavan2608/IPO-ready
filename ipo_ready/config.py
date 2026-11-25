"""Paths and shared constants for the IPO-Ready pipeline."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = Path(__file__).resolve().parent
CAPTURES = ROOT / "data" / "captures"
SITE = ROOT / "site"
SITE_DATA = SITE / "data"
BUILDS = SITE_DATA / "builds"
CURRENT = SITE_DATA / "current"
DEMO_FALLBACK = PKG / "demo_fallback"

USER_AGENT = "Mozilla/5.0 (compatible; IPO-Ready research prototype; bounded local capture)"
REQUEST_DELAY_S = 1.0
TIMEOUT_S = 20
MAX_BYTES = 20_000_000


def load_universe() -> dict:
    return json.loads((PKG / "universe.json").read_text(encoding="utf-8"))
