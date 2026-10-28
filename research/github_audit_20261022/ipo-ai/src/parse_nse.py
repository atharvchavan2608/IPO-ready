"""Step 2b: turn cached NSE ipo-detail JSON into flat issue + subscription rows.

Subscription is the part NSE gives away that the aggregators paywall, so this is
the authoritative leg of the dataset. Category is keyed off srNo, not the label
text, because the labels drift between issues while the numbering does not.
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from nse import ROOT

CACHE = ROOT / "data/raw/nse_detail"

SR_MAP = {                      # srNo -> column stem
    "1": "qib", "1(a)": "qib_fii", "1(b)": "qib_dfi", "1(c)": "qib_mf",
    "2": "nii", "2.1": "nii_big", "2.2": "nii_small",
    "3": "retail",
}


def f(x):
    try:
        return float(str(x).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def clean(v):
    return re.sub(r'\s+', " ", str(v).replace('"', "").strip())


def issue_fields(d):
    """issueInfo.dataList is an ordered list of {title, value} rendered as a
    table. Long values wrap onto follow-on rows whose `title` is really a
    fragment of the previous value (see Swiggy's BRLM list), so titles are
    matched loosely and only the first hit for each field is taken."""
    out, raw = {}, {}
    for item in d.get("issueInfo", {}).get("dataList", []):
        t, v = item.get("title"), item.get("value")
        if t and v:
            raw.setdefault(clean(t), clean(v))
    g = lambda *keys: next((raw[k] for k in raw for kk in keys
                            if kk.lower() == k.lower()), None)
    out["nse_issue_period"] = g("Issue Period")
    out["nse_issue_size_text"] = g("Issue Size")
    out["nse_issue_type"] = g("Issue Type")
    out["nse_price_range"] = g("Price Range")
    out["nse_face_value"] = f(re.sub(r"[^\d.]", " ", g("Face Value") or "").split()[0]
                              if g("Face Value") and re.search(r"\d", g("Face Value")) else None)
    out["nse_bid_lot"] = f((re.search(r"\d[\d,]*", g("Bid Lot") or "") or [None])[0]
                           if g("Bid Lot") else None)
    out["nse_registrar"] = g("Name of the Registrar")
    out["nse_brlm"] = g("Book Running Lead Managers")
    out["nse_rhp_url"] = g("Red Herring Prospectus")
    out["nse_anchor_url"] = g("Anchor Allocation Report")

    # Fresh-issue / OFS wording is free text and inconsistent across issues, so
    # this is a cross-check on Chittorgarh's structured split, not the source.
    txt = out["nse_issue_size_text"] or ""
    mf = re.search(r"fresh\s+issue\s+of\s+(?:up\s+to\s+)?(?:rs\.?\s*)?([\d,.]+)\s*(million|crore|mn|cr)?",
                   txt, re.I)
    if mf:
        val, unit = f(mf.group(1)), (mf.group(2) or "").lower()
        out["nse_fresh_cr"] = val / 10 if unit in ("million", "mn") else val
    mo = re.search(r"offer\s+for\s+sale\s+(?:of\s+)?(?:up\s+to\s+)?([\d,]+)\s*(equity\s+shares)?",
                   txt, re.I)
    if mo:
        out["nse_ofs_shares"] = f(mo.group(1))
    return out


def subs(d):
    """Category-wise x-times from bidDetails is NSE-side bids only - Swiggy's
    QIB reads 2.6x here against the 6.0x that was reported, because roughly half
    the book went through BSE. demandGraphALL carries all-exchange bid volume,
    so the headline combined number is recovered from that over the same shares
    offered; spot-checks reconcile exactly (Swiggy 3.59x, Mankind 15.32x,
    IKIO 66.30x). Category splits stay NSE-only and are comparable across IPOs
    but are not the published figures."""
    out = {}
    for b in d.get("bidDetails", []):
        sr, cat = b.get("srNo"), (b.get("category") or "")
        stem = SR_MAP.get(sr)
        if stem is None:
            if sr is None and cat.strip().lower() == "total":
                stem = "total"
            elif re.fullmatch(r"[45]", str(sr) or ""):
                stem = "employee" if "employee" in cat.lower() else "shareholder"
            else:
                continue
        out[f"sub_{stem}_x"] = f(b.get("noOfTime"))
        out[f"sub_{stem}_offered"] = f(b.get("noOfSharesOffered"))
        out[f"sub_{stem}_bid"] = f(b.get("noOfsharesBid"))

    offered = out.get("sub_total_offered")
    all_bids = f(d.get("demandGraphALL", {}).get("TOTAL_BIDS"))
    out["sub_total_bids_allexch"] = all_bids
    out["sub_total_x_allexch"] = (all_bids / offered) if offered and all_bids else None

    # NSE serves whatever snapshot it last stored; for some older issues that is
    # mid-bidding, not the final book. Flag it rather than quietly reporting an
    # under-subscribed IPO that in fact closed many times over.
    ts = (d.get("demandGraphALL", {}).get("timestamp")
          or d.get("demandGraph", {}).get("timestamp") or "")
    m = re.search(r"(\d{2}-[A-Za-z]{3}-\d{4})", ts)
    out["sub_asof"] = m.group(1) if m else None
    return out


def main():
    m = pd.read_csv(ROOT / "data/raw/master_mainboard.csv")
    rows, missing = [], []
    for sym in m["symbol"]:
        p = CACHE / f"{sym}.json"
        if not p.exists():
            missing.append(sym)
            continue
        d = json.loads(p.read_text())
        r = {"symbol": sym, "isin": d.get("metaInfo", {}).get("isin"),
             "industry": d.get("metaInfo", {}).get("industry")}
        r.update(issue_fields(d))
        r.update(subs(d))
        rows.append(r)
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "data/raw/nse_parsed.csv", index=False)
    print(f"parsed {len(df)} / {len(m)}   no detail json: {len(missing)}")
    if missing:
        print("missing:", ", ".join(missing[:20]))
    # a snapshot taken before the issue closed understates the final book
    m2 = pd.read_csv(ROOT / "data/raw/master_mainboard.csv",
                     parse_dates=["ipo_end"])[["symbol", "ipo_end"]]
    df = df.merge(m2, on="symbol", how="left")
    asof = pd.to_datetime(df["sub_asof"], format="%d-%b-%Y", errors="coerce")
    df["sub_is_final"] = asof >= df["ipo_end"]
    df = df.drop(columns=["ipo_end"])
    df.to_csv(ROOT / "data/raw/nse_parsed.csv", index=False)

    print(f"with subscription data: {df['sub_total_x_allexch'].notna().sum()}")
    print(f"snapshot taken at/after issue close: {int(df['sub_is_final'].sum())}")
    print(df[["symbol", "sub_qib_x", "sub_nii_x", "sub_retail_x",
              "sub_total_x", "sub_total_x_allexch", "sub_asof",
              "sub_is_final"]].head(8).to_string(index=False))


if __name__ == "__main__":
    main()
