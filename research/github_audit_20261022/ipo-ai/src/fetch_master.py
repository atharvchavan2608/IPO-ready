"""Step 1: pull the full NSE past-issues list, keep mainboard IPOs in window."""
import re
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from nse import NSE, ROOT

START = date(2023, 1, 1)   # ~3.5 years so every calendar year is complete


def parse_dt(s):
    if not s or s in ("-", ""):
        return None
    for fmt in ("%d-%b-%Y", "%d-%B-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    return None


def main():
    n = NSE()
    rows = n.past_issues()
    if not rows:
        sys.exit("NSE past-issues fetch failed")
    df = pd.DataFrame(rows)
    df["ipo_start"] = df["ipoStartDate"].map(parse_dt)
    df["ipo_end"] = df["ipoEndDate"].map(parse_dt)
    df["listing_date"] = df["listingDate"].map(parse_dt)
    # recent rows populate `company` but leave `companyName` blank
    df["company_name"] = df["companyName"].fillna("").replace("", pd.NA).fillna(df["company"])
    df["is_sme"] = df["securityType"].str.upper().str.contains("SME", na=False)

    # NSE's past-issues feed is every public issue, not just IPOs: NCD tranches
    # (securityType N0/NZ/ND/..., symbols like 860IIFL27), InvITs/REITs (IV),
    # rights issues (RR), muni bonds and FPOs all live in here. Equity IPOs are
    # securityType EQ or BE; the rest is filtered by type, then by name.
    EQUITY_TYPES = {"EQ", "BE"}
    NOT_AN_IPO = re.compile(
        r"\b(?:fpo|ncd|debenture|municipal corporation|invit|reit|trust)\b", re.I)

    out = df[(~df["is_sme"])
             & df["securityType"].isin(EQUITY_TYPES)
             & df["listing_date"].notna()
             & (df["listing_date"] >= START)
             & (df["listing_date"] <= date.today())].copy()
    out = out[~out["company_name"].str.contains(NOT_AN_IPO, na=False)]
    # partly-paid FPO tranches carry a PP1/PP2 symbol suffix (ADANIENPP1)
    out = out[~out["symbol"].str.contains(r"PP\d$", regex=True, na=False)]
    # a symbol can appear more than once (FPO after IPO, re-listing); the IPO is
    # the first time it shows up anywhere in the feed
    first = df.sort_values("listing_date").groupby("symbol")["listing_date"].first()
    out = out[out.apply(lambda r: first.get(r["symbol"]) == r["listing_date"], axis=1)]
    out = out.drop_duplicates("symbol").sort_values("listing_date").reset_index(drop=True)

    # fold in IPOs recovered from the equity master (see fill_gaps.py); NSE's
    # feed is missing a dozen real listings including NTPC Green and Tata Capital
    gap = ROOT / "data/raw/master_gapfill.csv"
    if gap.exists():
        extra = pd.read_csv(gap)
        for c in ("listing_date", "ipo_start", "ipo_end"):
            if c in extra:
                extra[c] = pd.to_datetime(extra[c], errors="coerce").dt.date
        out = pd.concat([out, extra[[c for c in extra.columns if c in out.columns
                                     or c in ("issuePrice", "priceRange")]]],
                        ignore_index=True)
        # the same company can carry two symbols across NSE's own files
        # (LEAP / LEAPIND); name + listing date is the real identity
        out["_key"] = (out["company_name"].map(
            lambda x: re.sub(r"[^a-z0-9]", "", str(x).lower()))
            + "|" + out["listing_date"].astype(str))
        out = out.drop_duplicates("_key").drop(columns="_key")
        out = out.sort_values("listing_date").reset_index(drop=True)
        print(f"folded in {len(extra)} gap-filled IPOs")

    (ROOT / "data/raw").mkdir(parents=True, exist_ok=True)
    df.to_csv(ROOT / "data/raw/nse_past_issues_all.csv", index=False)
    out.to_csv(ROOT / "data/raw/master_mainboard.csv", index=False)

    print(f"total past issues on NSE : {len(df)}")
    print(f"mainboard, listed >= {START}: {len(out)}")
    print(out.groupby(out["listing_date"].map(lambda d: d.year)).size().to_string())
    print(out[["symbol", "company_name", "listing_date", "issuePrice", "priceRange"]].tail(8).to_string())


if __name__ == "__main__":
    main()
