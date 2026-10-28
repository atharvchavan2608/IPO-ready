"""Step 5: join every source into one row per IPO and derive the metrics.

Sources and what each is trusted for:
  master      - NSE past-issues: the universe, dates, final issue price
  nse_parsed  - NSE ipo-detail: category-wise subscription (authoritative)
  cg_parsed   - Chittorgarh: fresh/OFS split, financials, valuation, objects
  price_panel - NSE bhavcopy: listing-day and post-listing prices
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from nse import ROOT

HORIZONS = {"7d": 7, "1m": 30, "3m": 91, "6m": 182, "1y": 365}


def first_full_year(periods):
    """Chittorgarh lists the stub period the RHP was filed on (e.g. '29 Feb
    2024') alongside full years. Index of the newest 31-Mar year-end, and of the
    one before it, so growth is measured year-on-year and not against a stub."""
    if not isinstance(periods, list):
        return None, None
    fy = [i for i, p in enumerate(periods)
          if re.search(r"\b31\s+mar", str(p), re.I)]
    return (fy[0] if fy else None), (fy[1] if len(fy) > 1 else None)


def at(lst, i):
    if not isinstance(lst, list) or i is None or i >= len(lst):
        return None
    v = lst[i]
    return v if v is not None and not (isinstance(v, float) and np.isnan(v)) else None


def price_at(panel, sym, d, offset_days):
    """Close on the first trading day at or after listing + offset."""
    sub = panel[(panel["SYMBOL"] == sym) & (panel["date"] >= d + pd.Timedelta(days=offset_days))]
    if not len(sub):
        return None, None
    r = sub.nsmallest(1, "date").iloc[0]
    return float(r["CLOSE_PRICE"]), r["date"]


def main():
    m = pd.read_csv(ROOT / "data/raw/master_mainboard.csv", parse_dates=["listing_date", "ipo_start", "ipo_end"])
    m = m[["symbol", "company_name", "securityType", "ipo_start", "ipo_end",
           "listing_date", "issuePrice", "priceRange"]].rename(
        columns={"issuePrice": "issue_price"})
    m["issue_price"] = pd.to_numeric(m["issue_price"], errors="coerce")

    nse = pd.read_csv(ROOT / "data/raw/nse_parsed.csv")
    cg = pd.read_json(ROOT / "data/raw/cg_parsed.json")
    df = m.merge(nse, on="symbol", how="left").merge(cg, on="symbol", how="left")

    panel = pd.read_parquet(ROOT / "data/raw/price_panel.parquet")
    panel["date"] = pd.to_datetime(panel["date"])
    for c in ["OPEN_PRICE", "HIGH_PRICE", "LOW_PRICE", "CLOSE_PRICE",
              "TTL_TRD_QNTY", "TURNOVER_LACS", "DELIV_PER"]:
        panel[c] = pd.to_numeric(panel[c], errors="coerce")

    # ---- listing day -------------------------------------------------------
    ld = panel.sort_values("date").groupby("SYMBOL").first().reset_index()
    listing = panel.merge(m[["symbol", "listing_date"]], left_on="SYMBOL",
                          right_on="symbol")
    listing = listing[listing["date"] == listing["listing_date"]]
    listing = listing[["symbol", "OPEN_PRICE", "HIGH_PRICE", "LOW_PRICE",
                       "CLOSE_PRICE", "TTL_TRD_QNTY", "TURNOVER_LACS", "DELIV_PER"]]
    listing.columns = ["symbol", "list_open", "list_high", "list_low",
                       "list_close", "list_volume", "list_turnover_lacs", "list_deliv_pct"]
    df = df.merge(listing, on="symbol", how="left")

    # ---- returns -----------------------------------------------------------
    for name, days in HORIZONS.items():
        vals = []
        for _, r in df.iterrows():
            p, _ = price_at(panel, r["symbol"], r["listing_date"], days)
            vals.append(p)
        df[f"close_{name}"] = vals

    ip = df["issue_price"]
    df["listing_gain_pct"] = (df["list_open"] - ip) / ip * 100
    df["listing_day_close_gain_pct"] = (df["list_close"] - ip) / ip * 100
    df["listing_day_swing_pct"] = (df["list_high"] - df["list_low"]) / df["list_open"] * 100
    for name in HORIZONS:
        df[f"ret_{name}_vs_issue_pct"] = (df[f"close_{name}"] - ip) / ip * 100
        df[f"ret_{name}_vs_listclose_pct"] = (
            (df[f"close_{name}"] - df["list_close"]) / df["list_close"] * 100)

    # ---- issue structure: new money vs promoter cash-out -------------------
    tot, fresh, ofs = df["total_issue_size_cr"], df["fresh_issue_cr"], df["ofs_cr"]
    df["fresh_pct_of_issue"] = fresh / tot * 100
    df["ofs_pct_of_issue"] = ofs / tot * 100
    df["equity_dilution_pct"] = (df["shares_post_issue"] / df["shares_pre_issue"] - 1) * 100
    df["promoter_stake_drop_pp"] = df["promoter_pre_pct"] - df["promoter_post_pct"]

    # ---- financials --------------------------------------------------------
    idx = df["fin_periods"].map(first_full_year)
    df["fy_latest_label"] = [at(p, i[0]) for p, i in zip(df["fin_periods"], idx)]
    for src, dest in [("fin_total_income", "revenue"), ("fin_pat", "pat"),
                      ("fin_assets", "assets"), ("fin_networth", "networth"),
                      ("fin_borrowing", "borrowing"), ("fin_reserves", "reserves")]:
        df[f"{dest}_fy_latest_cr"] = [at(v, i[0]) for v, i in zip(df[src], idx)]
        df[f"{dest}_fy_prior_cr"] = [at(v, i[1]) for v, i in zip(df[src], idx)]
    df["revenue_growth_pct"] = (df["revenue_fy_latest_cr"] / df["revenue_fy_prior_cr"] - 1) * 100
    df["pat_growth_pct"] = (df["pat_fy_latest_cr"] / df["pat_fy_prior_cr"] - 1) * 100
    df["pat_margin_pct"] = df["pat_fy_latest_cr"] / df["revenue_fy_latest_cr"] * 100
    df["is_lossmaking"] = df["pat_fy_latest_cr"] < 0
    df["mcap_to_revenue"] = df["mcap_at_offer_post"] / df["revenue_fy_latest_cr"]
    df["issue_size_to_revenue"] = tot / df["revenue_fy_latest_cr"]

    # Two subscription conventions are in circulation and they differ a lot.
    # sub_total_x_allexch counts the anchor tranche in both bids and shares
    # offered - that is the figure the press prints, and it reproduces the
    # published numbers exactly (Swiggy 3.59x, Mankind 15.32x, IKIO 66.30x).
    # SEBI's 90% minimum, however, applies to the net offer excluding anchor.
    # Radiant Cash reads 0.53x on the headline basis and 0.93x ex-anchor, which
    # is how a book that looks failed was legally able to list.
    net = df["sub_total_offered"] - df["anchor_shares"]
    df["sub_total_x_ex_anchor"] = df["sub_total_bids_allexch"] / net.where(net > 0)
    df["sub_suspect"] = (df["sub_total_x_ex_anchor"] < 0.9) & df["sub_total_x_ex_anchor"].notna()
    df["sub_is_final"] = df["sub_is_final"].astype("boolean")

    # NSE types the registrar name freehand per issue, so one firm arrives as up
    # to six strings: casing drift (KFin/Kfin/KFIN), a truncation ("Limite"),
    # "Pvt." vs "Private", and "(formerly known as ...)" tails. Left raw, the
    # registrar facet splits KFin's 107 issues across six buckets. India has a
    # short, fixed list of registrars, so an explicit keyword map is both
    # correct and auditable; nse_registrar keeps the original string.
    # Link Intime was renamed MUFG Intime in 2024 - same entity, so it folds in.
    REGISTRARS = [
        ("kfin",               "KFin Technologies"),
        ("mufg",               "MUFG Intime (formerly Link Intime)"),
        ("link intime",        "MUFG Intime (formerly Link Intime)"),
        ("bigshare",           "Bigshare Services"),
        ("cameo",              "Cameo Corporate Services"),
        ("mas services",       "MAS Services"),
        ("integrated registry", "Integrated Registry Management"),
        ("skyline",            "Skyline Financial Services"),
        ("purva",              "Purva Sharegistry"),
        ("maashitla",          "Maashitla Securities"),
        ("beetal",             "Beetal Financial"),
    ]

    def canon_registrar(v):
        if not isinstance(v, str) or not v.strip():
            return None
        low = v.lower()
        for needle, name in REGISTRARS:
            if needle in low:
                return name
        # unknown registrar: strip the parenthetical tail and legal suffix so it
        # at least stops splitting on punctuation
        base = re.sub(r"\s*\(.*", "", v).strip()
        return re.sub(r"\s+(Private\s+)?(Limited|Ltd\.?)$", "", base, flags=re.I).strip()

    df["registrar"] = df["nse_registrar"].map(canon_registrar)

    df["objects_text"] = df["issue_objects"].map(
        lambda v: " | ".join(f"{o['object']} ({o['amt_cr']})" for o in v)
        if isinstance(v, list) else None)
    df["listing_year"] = df["listing_date"].dt.year

    drop = ["fin_periods", "fin_assets", "fin_total_income", "fin_pat",
            "fin_networth", "fin_reserves", "fin_borrowing", "issue_objects"]
    wide = df.drop(columns=[c for c in drop if c in df.columns])
    out = ROOT / "data/out"
    out.mkdir(parents=True, exist_ok=True)
    wide.to_csv(out / "ipos.csv", index=False)
    df.to_parquet(out / "ipos.parquet", index=False)

    print(f"rows={len(df)}  cols={len(wide.columns)}")
    cov = {"issue_price": "issue_price", "listing gain": "listing_gain_pct",
           "fresh/OFS split": "fresh_pct_of_issue", "subscription": "sub_total_x",
           "revenue": "revenue_fy_latest_cr", "PAT": "pat_fy_latest_cr",
           "assets": "assets_fy_latest_cr", "P/E post": "pe_post",
           "1y return": "ret_1y_vs_issue_pct"}
    print("\ncoverage:")
    for k, c in cov.items():
        if c in df:
            print(f"  {k:18} {df[c].notna().sum():4}/{len(df)}")
    print("\n", df.groupby("listing_year")["listing_gain_pct"]
          .agg(["count", "mean", "median"]).round(1).to_string())


if __name__ == "__main__":
    main()
