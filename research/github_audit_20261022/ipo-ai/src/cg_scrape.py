"""Step 3b: fetch each IPO's Chittorgarh page and pull the issue structure,
financials, valuation and use-of-proceeds tables.

Chittorgarh pages are keyed on a numeric id from the sitemap. Name matching is
never trusted on its own - every fetched page is verified against NSE's company
name and issue dates before its numbers are kept, because a near-miss slug
(JSFB -> ESAF Small Finance Bank) otherwise poisons the dataset silently.
"""
import difflib
import html as htmllib
import json
import re
import sys
import time
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent))
from nse import UA, ROOT
from cg_urls import norm, OVERRIDES

ALIASED = set(OVERRIDES)

CACHE = ROOT / "data/raw/cg_pages"
PAUSE = 1.0          # polite: chittorgarh robots.txt allows *, keep it ~1 rps


# ---------- table location -------------------------------------------------

def _labels(t):
    return [str(x).strip().lower() for x in t.iloc[:, 0]]


def find_by_rows(tables, *needles):
    """First table whose first column contains all of `needles`."""
    for t in tables:
        lab = " | ".join(_labels(t))
        if all(n.lower() in lab for n in needles):
            return t
    return None


def find_by_cols(tables, *needles):
    for t in tables:
        cols = " | ".join(str(c).strip().lower() for c in t.columns)
        if all(n.lower() in cols for n in needles):
            return t
    return None


def kv(t):
    """Two-column label/value table -> dict."""
    if t is None or t.shape[1] < 2:
        return {}
    return {str(a).strip(): str(b).strip() for a, b in zip(t.iloc[:, 0], t.iloc[:, 1])}


NUM = re.compile(r"-?[\d,]+\.?\d*")
SIZE_SHARES = re.compile(r"^\s*([\d,]+)\s*shares", re.I)
SIZE_AMOUNT = re.compile(r"(?:₹|&#8377;|Rs\.?)\s*([\d,]+(?:\.\d+)?)\s*(Cr|Crore)", re.I)


def size_row(v):
    """Issue-size cells read '9,52,55,598 shares (agg. up to Rs 3,000 Cr)'.
    A bare number grab returns the share count, which is off by orders of
    magnitude from the rupee figure everything downstream assumes."""
    if v is None or str(v).strip().lower() in ("", "nan"):
        return None, None
    txt = str(v)
    sh = SIZE_SHARES.search(txt)
    amt = SIZE_AMOUNT.search(txt)
    return (float(sh.group(1).replace(",", "")) if sh else None,
            float(amt.group(1).replace(",", "")) if amt else None)


def num(s):
    if s is None:
        return None
    s = str(s).replace(",", "")
    m = NUM.search(s)
    if not m:
        return None
    try:
        v = float(m.group().replace(",", ""))
    except ValueError:
        return None
    return -v if str(s).strip().startswith("(") else v


# ---------- fetch + verify -------------------------------------------------

def fetch(url, symbol):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{symbol}.html"
    if f.exists() and f.stat().st_size > 5000:
        return f.read_text(encoding="utf-8", errors="ignore")
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=40)
    except requests.RequestException:
        return None
    time.sleep(PAUSE)
    if r.status_code != 200 or len(r.text) < 5000:
        return None
    f.write_text(r.text, encoding="utf-8")
    return r.text


def page_identity(html):
    """(company name from <title>, IPO open date string) as printed on the page."""
    m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    title = htmllib.unescape(re.sub(r"\s+", " ", m.group(1))) if m else ""
    name = re.split(r"\s+IPO\b", title, 1)[0].strip()
    try:
        tabs = pd.read_html(StringIO(html))
    except ValueError:
        return name, None, []
    d = kv(find_by_rows(tabs, "ipo date"))
    return name, d.get("IPO Date"), tabs


def verify(nse_name, nse_open, page_name, page_ipo_date, aliased=False):
    """Accept a page only when the company identity is corroborated.

    Neither signal is sufficient alone. Names legitimately differ (Chittorgarh
    files Billionbrains Garage Ventures under "Groww"), and issue windows
    legitimately collide - dozens of IPOs open in the same month. So the rule is
    that the issue month must line up, and on top of that either the name
    matches or the symbol was explicitly aliased by hand.

    Substring matching is length-guarded: without it "EMS" tests as a substring
    of "exicom telesystems" and pulls a completely unrelated company's numbers.
    """
    a, b = norm(nse_name), norm(page_name)
    if not b:
        return False, "no page name"
    ratio = difflib.SequenceMatcher(None, a, b).ratio()
    shorter = min(len(a), len(b))
    name_ok = (a == b
               or (shorter >= 8 and (a in b or b in a))
               or ratio >= 0.90)

    month_ok = year_ok = None
    if page_ipo_date and pd.notna(nse_open):
        want = pd.to_datetime(nse_open)
        year_ok = str(want.year) in re.findall(r"\b(20\d{2})\b", page_ipo_date)
        months = re.findall(r"\b([A-Z][a-z]{2})\b", page_ipo_date)
        month_ok = (want.strftime("%b") in months) if months else None

    dates_agree = year_ok is not False and month_ok is not False
    dates_confirm = year_ok is True and month_ok is True
    # an exact issue-window hit is strong evidence on its own; it rescues cases
    # where name normalisation eats a distinguishing word ("WeWork India
    # Management" -> "wework" once India/Management are stripped as noise)
    if dates_agree and (name_ok or aliased or dates_confirm and ratio >= 0.35):
        return True, "ok"
    return (False, f"name_ok={name_ok} ratio={ratio:.2f} year_ok={year_ok} "
                   f"month_ok={month_ok} page='{page_name}'")


# ---------- parse ----------------------------------------------------------

FIN_UNIT = re.compile(r"Company Financials.{0,4000}?Amount in\s*(?:&#8377;|\u20b9|Rs\.?)\s*(Crore|Lakh)", re.I | re.S)


def fin_scale(html):
    """Mainboard pages report ₹ Crore, SME pages ₹ Lakh. Read the footnote
    rather than assuming, so a stray SME-style page can't inflate a company by
    100x."""
    m = FIN_UNIT.search(html)
    if m and m.group(1).lower().startswith("lakh"):
        return 0.01
    return 1.0


def parse(tabs, scale=1.0):
    out = {}
    basic = kv(find_by_rows(tabs, "ipo date", "face value"))
    out["cg_ipo_date"] = basic.get("IPO Date")
    out["cg_listing_date"] = basic.get("Listed on") or basic.get("Listing Date")
    out["face_value"] = num(basic.get("Face Value"))
    out["price_band"] = basic.get("Price Band")
    out["issue_price_cg"] = num(basic.get("Issue Price"))
    out["lot_size"] = num(basic.get("Lot Size"))

    # --- the split the whole question hangs on: new money vs promoter cash-out
    size = kv(find_by_rows(tabs, "total issue size"))
    total_sh, total_cr = size_row(size.get("Total Issue Size"))
    fresh_key = next((k for k in size if k.lower().startswith("fresh issue")), None)
    fresh_sh, fresh_cr = size_row(size.get(fresh_key))
    ofs_sh, ofs_cr = size_row(size.get("Offer for Sale"))

    # A pure-OFS book (Mankind, Tata Tech, Cello) simply has no Fresh Issue row,
    # and a pure-fresh book has no Offer for Sale row. That absence means zero,
    # not unknown - reading it as null would drop ~16% of the book from any
    # fresh-vs-OFS cut, and exactly the rows where the answer is most extreme.
    if total_cr is not None:
        if fresh_key is None and ofs_cr is not None:
            fresh_sh, fresh_cr = 0.0, 0.0
        if "Offer for Sale" not in size and fresh_cr is not None:
            ofs_sh, ofs_cr = 0.0, 0.0

    out["total_issue_size_cr"] = total_cr
    out["total_issue_shares"] = total_sh
    out["fresh_issue_cr"] = fresh_cr
    out["fresh_issue_shares"] = fresh_sh
    out["ofs_cr"] = ofs_cr
    out["ofs_shares"] = ofs_sh
    if None not in (total_cr, fresh_cr, ofs_cr) and total_cr:
        out["size_split_error_pct"] = round(
            abs(fresh_cr + ofs_cr - total_cr) / total_cr * 100, 2)
    out["shares_pre_issue"] = num(size.get("Share Holding Pre Issue"))
    out["shares_post_issue"] = num(size.get("Share Holding Post Issue"))

    # --- financials: rows are line items, columns are period-end dates
    fin = find_by_rows(tabs, "profit after tax")
    if fin is not None and fin.shape[1] >= 2:
        periods = [str(c).strip() for c in fin.columns[1:]]
        lab = {str(r).strip().lower(): i for i, r in enumerate(fin.iloc[:, 0])}
        def row(name):
            i = lab.get(name)
            return [num(fin.iloc[i, j + 1]) for j in range(len(periods))] if i is not None else []
        sc = lambda vs: [None if v is None else v * scale for v in vs]
        out["fin_periods"] = periods
        out["fin_unit"] = "cr"
        out["fin_assets"] = sc(row("assets"))
        out["fin_total_income"] = sc(row("total income") or row("revenue"))
        out["fin_pat"] = sc(row("profit after tax"))
        out["fin_networth"] = sc(row("net worth"))
        out["fin_reserves"] = sc(row("reserves and surplus"))
        out["fin_borrowing"] = sc(row("total borrowing"))

    kpi = find_by_cols(tabs, "kpi")
    if kpi is not None:
        d = kv(kpi)
        for k, dest in [("ROE", "roe"), ("ROCE", "roce"), ("Debt/Equity", "debt_equity"),
                        ("RoNW", "ronw"), ("PAT Margin", "pat_margin"), ("NAV", "nav"),
                        ("EBITDA Margin", "ebitda_margin"), ("Price to Book Value", "pb")]:
            out[f"kpi_{dest}"] = num(d.get(k))

    val = find_by_cols(tabs, "pre ipo", "post ipo")
    if val is not None:
        lab = {str(r).strip().lower(): i for i, r in enumerate(val.iloc[:, 0])}
        for key, dest in [("eps (₹)", "eps"), ("p/e (x)", "pe"),
                          ("market cap at offer price", "mcap_at_offer")]:
            i = lab.get(key)
            if i is not None:
                out[f"{dest}_pre"] = num(val.iloc[i, 1])
                out[f"{dest}_post"] = num(val.iloc[i, 2])

    hold = find_by_rows(tabs, "promoter and promoter group")
    if hold is not None and hold.shape[1] >= 3:
        i = _labels(hold).index("promoter and promoter group")
        out["promoter_pre_pct"] = num(hold.iloc[i, 1])
        out["promoter_post_pct"] = num(hold.iloc[i, 2])

    obj = find_by_cols(tabs, "issue objects")
    if obj is not None:
        col = [c for c in obj.columns if "est amt" in str(c).lower()]
        items = []
        for _, r in obj.iterrows():
            txt = str(r["Issue Objects"]).strip()
            amt = num(r[col[0]]) if col else None
            if txt and txt.lower() != "nan":
                items.append({"object": txt, "amt_cr": amt})
        out["issue_objects"] = items

    anch = kv(find_by_rows(tabs, "anchor portion"))
    for k, dest in [("Shares Offered", "anchor_shares"),
                    ("Anchor Portion (₹ Cr.)", "anchor_amount_cr")]:
        v = next((vv for kk, vv in anch.items() if kk.startswith(k.split(" (")[0])), None)
        out[dest] = num(v)

    exp = find_by_cols(tabs, "issue expenses")
    if exp is not None:
        col = [c for c in exp.columns if "est amt" in str(c).lower()]
        if col:
            out["issue_expenses_cr"] = float(pd.to_numeric(
                exp[col[0]].map(num), errors="coerce").sum())
    return out


# ---------- driver ---------------------------------------------------------

def main():
    mp = pd.read_csv(ROOT / "data/raw/cg_map.csv")
    master = pd.read_csv(ROOT / "data/raw/master_mainboard.csv")[["symbol", "ipo_start"]]
    mp = mp.merge(master, on="symbol", how="inner")
    recs, bad = [], []
    for i, r in mp.iterrows():
        cands = json.loads(r["cg_candidates"]) if isinstance(r["cg_candidates"], str) else []
        if not cands:
            bad.append((r["symbol"], r["company_name"], "no candidate url"))
            continue
        chosen = html = pname = None
        why = "no candidate verified"
        for url in cands:
            h = fetch(url, r["symbol"])
            if not h:
                why = "fetch failed"
                continue
            n_, d_, t_ = page_identity(h)
            ok, why = verify(r["company_name"], r["ipo_start"], n_, d_,
                             aliased=r["symbol"] in ALIASED)
            if ok:
                chosen, html, pname, tabs = url, h, n_, t_
                break
            (CACHE / f"{r['symbol']}.html").unlink(missing_ok=True)
        if chosen is None:
            bad.append((r["symbol"], r["company_name"], why))
            continue
        rec = {"symbol": r["symbol"], "cg_url": chosen, "cg_name": pname}
        rec.update(parse(tabs, fin_scale(html)))
        recs.append(rec)
        if (i + 1) % 25 == 0:
            print(f"{i+1}/{len(mp)} kept={len(recs)} rejected={len(bad)}", flush=True)

    df = pd.DataFrame(recs)
    df.to_json(ROOT / "data/raw/cg_parsed.json", orient="records", indent=1)
    print(f"\nkept {len(df)} / {len(mp)}")
    pd.DataFrame(bad, columns=["symbol", "company", "reason"]).to_csv(
        ROOT / "data/raw/cg_rejected.csv", index=False)
    print("rejected written to data/raw/cg_rejected.csv")


if __name__ == "__main__":
    main()
