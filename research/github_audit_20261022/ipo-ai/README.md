# Indian mainboard IPO dataset (NSE, 2023 →)

One row per mainboard IPO listed on NSE since 2023-01-01: issue structure, where
the money went, category-wise subscription, pre-IPO financials, valuation at
offer, and listing-day plus post-listing returns.

## Where the data comes from

Nothing here is paid or scraped from a paywall. Each field comes from the source
that is authoritative for it:

| leg | source | notes |
|---|---|---|
| universe, issue dates, final issue price | NSE `api/public-past-issues` | needs a cookie from an HTML page load first |
| issue size, price band, lot, BRLMs, registrar, RHP link | NSE `api/ipo-detail?symbol=` → `issueInfo` | free text, parsed best-effort |
| **subscription**, category-wise, x-times | same → `bidDetails` | authoritative; aggregators paywall this |
| **fresh issue vs OFS**, restated financials, EPS/PE pre-post, promoter dilution, use of proceeds, issue expenses | Chittorgarh IPO page | RHP-derived, server-rendered HTML |
| listing-day and post-listing OHLC | NSE bhavcopy `sec_bhavdata_full_DDMMYYYY.csv` | no auth, one file per trading day |

Paid alternative worth knowing about: **Prime Database** sells all of this
pre-joined. This pipeline exists to avoid that subscription, not to beat it.

## Two things that will silently corrupt this dataset if you skip them

**1. NSE's past-issues feed is not a list of IPOs, and it is also incomplete.**
It is every public issue: NCD tranches (`securityType` N0/NZ/ND…, symbols like
`860IIFL27`), InvITs and REITs, rights issues, municipal bonds, FPOs and
partly-paid tranches (`…PP1`). Unfiltered it returns 382 rows for this window.

It also omits real IPOs outright — NTPC Green, Afcons Infrastructure and Tata
Capital all listed on NSE and appear nowhere in it. So `fetch_master.py` filters
the feed down to equity IPOs, and `fill_gaps.py` then sweeps NSE's equity master
(`EQUITY_L.csv`) for listings the feed missed, admitting one only when a
Chittorgarh IPO page exists whose own listing date matches and which is not an
SME-platform issue. That recovers 12.

Final count: **298 mainboard IPOs** — 57 in 2023, 90 in 2024, 104 in 2025, 47 in
2026 to date. The 2023 and 2024 figures match published mainboard counts, which
is the check that the filtering is neither over- nor under-inclusive.

**2. Name matching to any aggregator is unsafe on its own.** Chittorgarh files
companies under brand names (Brainbees → firstcry, Honasa → mamaearth, Zinka
Logistics → blackbuck), and one name can map to several pages — Sai Silks has
both its withdrawn 2013 attempt and its 2023 IPO, and two unrelated companies
trade as Fabtech. Naive fuzzy matching produced confidently wrong rows (Jana
Small Finance Bank → ESAF, HDB Financial → Usha Financial, Exicom → EMS).

So `cg_urls.py` emits *ranked candidates* and `cg_scrape.py` fetches each one and
verifies the page's company name **and** issue month against NSE before keeping
any number. Rejects land in `data/raw/cg_rejected.csv` — that file should stay
empty; anything in it is a row you do not have data for, not a row to guess at.

## Run it

```bash
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt

./.venv/bin/python src/fetch_master.py    # universe from NSE's feed   (~10s)
./.venv/bin/python src/cg_urls.py         # symbol → candidate CG URLs
./.venv/bin/python src/fill_gaps.py       # recover IPOs the feed omits (~8 min)
./.venv/bin/python src/fetch_master.py    # re-run: folds the recovered rows in
./.venv/bin/python src/fetch_detail.py    # NSE per-IPO JSON     (~30 min, cached)
./.venv/bin/python src/parse_nse.py       # → nse_parsed.csv
./.venv/bin/python src/cg_urls.py         # re-map with the fuller universe
./.venv/bin/python src/cg_scrape.py       # fetch + verify + parse (~6 min, cached)
./.venv/bin/python src/fetch_prices.py    # bhavcopy panel        (~20 min, cached)
./.venv/bin/python src/build_dataset.py   # → data/out/ipos.{csv,parquet}

./.venv/bin/python src/export_web.py      # → web/public/data/ipos.json + schema
./.venv/bin/python src/fetch_upcoming.py  # → web/public/data/upcoming.json

./.venv/bin/jupyter notebook notebooks/analysis.ipynb
```

Every fetch step caches to `data/raw/`, so re-runs are cheap and the parse steps
can be reworked without re-hitting any server. Re-running later only pulls what
is new. Requests are rate-limited to roughly 1/sec; Chittorgarh's robots.txt
allows this path for generic agents.

## Explore it

A Next.js + D3 front end over this dataset is in `web/`, deployed at
**https://ipo-explorer-steel.vercel.app**:

- `/` — sortable, groupable, filterable table across all 98 fields, with charts
  that follow the filters
- `/upcoming` — IPOs open or opening now, each with a configurable comparables
  engine: pick what makes a past IPO similar (size, subscription, valuation, OFS
  mix, growth, margins…) and see what actually happened to those matches

See `web/README.md`. Re-export after a pipeline run with
`./.venv/bin/python src/export_web.py`.

## Output

`data/out/ipos.csv` — one row per IPO. Column groups:

- **issue**: `issue_price`, `price_band`, `face_value`, `lot_size`,
  `total_issue_size_cr`, `fresh_issue_cr`, `ofs_cr`, `fresh_pct_of_issue`,
  `ofs_pct_of_issue`, `anchor_amount_cr`, `issue_expenses_cr`, `objects_text`
- **ownership**: `shares_pre_issue`, `shares_post_issue`, `equity_dilution_pct`,
  `promoter_pre_pct`, `promoter_post_pct`, `promoter_stake_drop_pp`
- **subscription** (x-times, shares offered, shares bid): `sub_qib_*`,
  `sub_qib_fii_*`, `sub_qib_mf_*`, `sub_nii_*`, `sub_nii_big_*`,
  `sub_nii_small_*`, `sub_retail_*`, `sub_employee_*`, `sub_total_*`.
  Use **`sub_total_x_allexch`** as the headline: the per-category `sub_*_x`
  fields count NSE-side bids only (Swiggy's QIB reads 2.6x there against the
  6.0x reported, because half the book went through BSE). They stay comparable
  across IPOs but are not the published figures. `sub_total_x_ex_anchor`
  excludes the anchor tranche — that is the basis SEBI's 90% minimum applies to,
  and it is why Radiant Cash could list on a 0.53x headline (0.93x ex-anchor).
- **financials** (₹ Cr, restated, latest full FY before the IPO and the one
  before it): `revenue_*`, `pat_*`, `assets_*`, `networth_*`, `borrowing_*`,
  `reserves_*`, plus `revenue_growth_pct`, `pat_growth_pct`, `pat_margin_pct`,
  `is_lossmaking`
- **valuation at offer**: `eps_pre/post`, `pe_pre/post`, `mcap_at_offer_post`,
  `mcap_to_revenue`, `kpi_roe`, `kpi_roce`, `kpi_debt_equity`, `kpi_ronw`
- **returns**: `listing_gain_pct` (open vs issue price),
  `listing_day_close_gain_pct`, `listing_day_swing_pct`, `list_deliv_pct`, and
  `ret_{7d,1m,3m,6m,1y}_vs_issue_pct` / `_vs_listclose_pct`

## Known limits

- Financials are as printed in the RHP (restated, usually consolidated). They are
  a snapshot at offer, not a maintained series — for post-listing results use
  screener.in or the exchange filings.
- `nse_fresh_cr` / `nse_ofs_shares` are regex-parsed from NSE's free-text issue
  blurb and exist only as a cross-check on the Chittorgarh split. Trust
  `fresh_issue_cr` / `ofs_cr`.
- 8 IPOs have no subscription data: NSE simply does not retain `ipo-detail` for
  them (HMAAGRO, ASKAUTOLTD, MUTHOOTMF, PLATIND, GOPAL, STYLEBAAZA, BALAJEE,
  IGIL). 3 more have a subscription snapshot stored before the issue closed —
  check `sub_is_final` before using those.
- `pe_post` is null for loss-making issues by definition, not by omission.
- Returns are absolute, not benchmark-relative. A 2023 cohort 1-year number
  flatters itself against a rising Nifty.
- Recent listings have no 1-year number yet; `ret_1y_*` is null by design, so
  filter on it rather than treating nulls as zeros.
