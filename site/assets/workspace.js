/* Page 2 state and presentation. The Python build supplies research and scenario calculations. */
(() => {
  const { $, esc, fmtNum, fmtInr, fmtDate, load, openEvidence, ratioDisplay, stateText } = IR;
  const host = $("#workspace"), scenario = $("#workspace-allocation"), columns = $("#compare-columns");
  const scrollHint = $("#compare-scroll-hint");
  const updateScrollHint = () => { scrollHint.hidden = columns.scrollWidth <= columns.clientWidth + 1; };
  new ResizeObserver(updateScrollHint).observe(columns);
  const modal = $("#company-details"), frame = $("#company-frame");
  const KEY = "ipo-ready-workspace-v2";
  const defaultRatios = ["revenue_growth", "net_profit_ratio", "cfo_to_pat", "pe"];
  const defaults = { path: "budget", company: "", amount: "1000000", tolerance: "balanced",
    horizon: "36", cash_reserve: "0", include_unlisted: true };
  const queryParams = new URLSearchParams(location.search);
  let saved;
  try { saved = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch { saved = {}; }
  const state = {
    companies: Array.isArray(saved.companies) ? saved.companies : ["igx"],
    periods: saved.periods || {}, statements: saved.statements || {}, attached: saved.attached || [],
    shortlist: Array.isArray(saved.shortlist) ? saved.shortlist : [],
    inputs: { ...defaults, ...saved.inputs }, query: saved.query || "", market: saved.market || "unlisted",
    queryBuild: saved.queryBuild || null,
    ratioPicks: Array.isArray(saved.ratioPicks) ? saved.ratioPicks : defaultRatios,
  };
  const facts = new Map(), catalog = new Map();
  const registered = row => catalog.get(row.id);
  const record = id => catalog.get(id) || state.attached.find(row => row.id === id);
  const period = id => {
    const row = record(id), selected = state.periods[id];
    return row?.periods.includes(selected) ? selected : row?.latest_period || "";
  };
  const safeURL = value => {
    try { const parsed = new URL(value); return parsed.protocol === "https:" ? parsed.href : ""; }
    catch { return ""; }
  };
  const norm = value => String(value || "").trim().toUpperCase();
  const overview = [
    { id: "revenue", label: "Operating revenue", unit: "₹ crore" },
    { id: "cfo", label: "Operating cash flow", unit: "₹ crore" },
  ];
  const quotedRatios = new Set(["pe", "pb", "ps", "ev_ebitda", "ev_revenue", "dividend_yield"]);
  const knownBases = new Set(["standalone", "consolidated", "issuer_and_esos_trust"]);
  const basisName = basis => basis === "issuer_and_esos_trust" ? "issuer + employee trust" : basis || "basis unavailable";
  const marketDay = new Intl.DateTimeFormat("en-IN", { timeZone: "Asia/Kolkata", dateStyle: "medium" });
  function quoteDay(quote) {
    const date = Date.parse(quote?.as_of);
    return Number.isFinite(date) ? marketDay.format(date) : "";
  }
  let ratioGroups = {}, reviewedBenchmarks = {}, selections = [];
  const focusStates = {
    allocated: "Fits the model", quote_unavailable: "Verified quote or annual data unavailable",
    lot_unavailable: "Dealer lot unavailable", minimum_lot_exceeds_limit: "Minimum lot exceeds the position limit",
    liquidity_horizon: "Horizon is too short for the modeled unlisted exit", excluded: "Unlisted lots excluded by your settings",
    cash_reserve_limit: "Position exceeds investable cash after the reserve", listing_issue: "Listing or liquidity status needs verification",
    quote_stale: "Quote date differs from the scenario's market snapshot", sector_unclassified: "Sector needs review before scenario sizing",
  };
  let catalogBuild, renderNumber = 0, calculating = 0;
  const persist = () => { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch {} };
  function invalidateAllocation() {
    calculating++;
    if ($("#allocation-result").children.length || $("#allocation-status").textContent.startsWith("Calculating")) {
      $("#allocation-status").textContent = "Inputs changed. Calculate to update the scenario.";
    }
  }
  function get(id) {
    if (!facts.has(id)) facts.set(id, load(`company/${id}.json`).catch(() => null));
    return facts.get(id);
  }

  function add(id, scroll = false) {
    if (!record(id)) return;
    if (!state.companies.includes(id)) {
      if (state.companies.length >= 8) { $("#workspace-status").textContent = "Remove a column before adding a ninth company."; return; }
      state.companies.push(id);
    }
    persist();
    render();
    if (scroll) host.scrollIntoView({ block: "start" });
  }
  function shortlist(id) {
    if (!record(id)) return;
    if (state.shortlist.includes(id)) state.shortlist = state.shortlist.filter(key => key !== id);
    else if (state.shortlist.length < 20) state.shortlist.push(id);
    invalidateAllocation();
    persist();
    renderControls();
    render();
    document.dispatchEvent(new Event("ipo-ready:shortlist"));
  }
  function requestCompany(id) {
    if (!record(id)) return;
    state.inputs.path = "company";
    state.inputs.company = id;
    invalidateAllocation();
    add(id);
    persist();
    renderControls();
    $("#allocation").scrollIntoView({ block: "start" });
  }
  window.IPO_WORKSPACE = {
    add: id => add(id, true), shortlist, requestCompany,
    has: id => state.shortlist.includes(id), query: state.query, market: state.market,
    attachCount: () => state.attached.length,
    recordQuery(query, market, build) {
      Object.assign(state, { query, market, queryBuild: build || catalogBuild });
      persist();
    },
  };

  function search() {
    const term = $("#workspace-search").value.trim().toLowerCase();
    const all = [...catalog.values(), ...state.attached];
    const rows = term ? all.filter(row => [row.name, row.short, row.identity.key, row.identity.isin, row.identity.cin,
      ...row.hierarchy].some(value => String(value || "").toLowerCase().includes(term))).slice(0, 10)
      : ["igx", "oyo", "nse-iex", "nse-mcx", "polymatech", "herofincorp", "nse-aether"].map(record).filter(Boolean);
    $("#workspace-matches").innerHTML = rows.map(row =>
      `<button type="button" class="btn ghost small" data-add="${esc(row.id)}" ${state.companies.includes(row.id) ? "disabled" : ""}>${esc(row.short)}</button>`
    ).join("") || '<p class="small muted">No company matched. Attach a sourced record to continue.</p>';
  }

  function benchmarksFor(person) {
    const published = person.company?.issuer_case?.benchmarks;
    if (Array.isArray(published)) return published;
    return (reviewedBenchmarks[person.row.id]?.peers || []).filter(peer => peer.status === "eligible").map(peer => ({
      id: `nse-${peer.symbol.toLowerCase()}`, rationale: peer.rationale, scope: "operating",
    }));
  }
  function renderBenchmarks() {
    const target = $("#workspace-benchmarks");
    const groups = selections.flatMap(person => {
      const available = benchmarksFor(person).filter(item => catalog.has(item.id));
      if (!available.length) return [];
      return [`<div class="benchmark-group"><h3>${esc(person.row.short)} benchmarks</h3><ul>${available.map(item => {
        const name = item.label || record(item.id).short;
        const added = state.companies.includes(item.id);
        return `<li><button type="button" class="btn ghost small" data-add="${esc(item.id)}" ${added ? "disabled" : ""}>
          ${added ? `${esc(name)} added` : `Add ${esc(name)}`}</button>
          <p class="small muted"><strong>${item.scope === "operating" ? "Operating reference" : "Context only"}</strong> · ${esc(item.rationale)}</p></li>`;
      }).join("")}</ul></div>`];
    });
    target.hidden = !groups.length;
    target.innerHTML = groups.join("");
  }
  function renderRatioPicker() {
    const filter = $("#compare-ratio-filter").value.trim().toLowerCase();
    const groups = Object.entries(ratioGroups);
    const known = groups.flatMap(([, defs]) => defs);
    const picks = new Set(state.ratioPicks);
    const count = known.filter(def => picks.has(def.id)).length;
    $("#compare-ratio-controls").hidden = !known.length;
    $("#compare-ratio-count").textContent = `${count} selected`;
    $("#compare-ratio-options").innerHTML = groups.map(([group, definitions]) => {
      const matches = definitions.filter(def => `${group} ${def.label} ${def.formula}`.toLowerCase().includes(filter));
      return matches.length ? `<fieldset><legend>${esc(group)}</legend>${matches.map(def =>
        `<label><input type="checkbox" value="${esc(def.id)}" ${picks.has(def.id) ? "checked" : ""}> ${esc(def.label)}</label>`
      ).join("")}</fieldset>` : "";
    }).join("") || '<p class="small muted">No ratios match this filter.</p>';
  }
  function comparisonMetrics() {
    return [...overview, ...Object.values(ratioGroups).flat().filter(def => state.ratioPicks.includes(def.id))];
  }
  function metricCell(person, definition) {
    const { id, formula, unit } = definition;
    const cell = formula ? person.company?.ratios?.by_period[person.period]?.[id] : person.research?.comparison[id];
    if (!cell) return { value: null, unit };
    const quote = quotedRatios.has(id) ? person.company?.quote : null;
    const resolvedUnit = cell.unit === "x" ? "×" : cell.unit || unit;
    return { ...cell, unit: resolvedUnit, currency: cell.currency || person.company?.currency || "INR", quote };
  }
  function reviewFor(left, right) {
    return benchmarksFor(left).find(item => item.id === right.row.id) ||
      benchmarksFor(right).find(item => item.id === left.row.id);
  }
  function mismatches(left, right, definition, metric, review) {
    const other = metricCell(right, definition);
    const sameSector = left.row.model && left.row.model !== "unknown" && left.row.model === right.row.model &&
      left.row.hierarchy.at(-1) === right.row.hierarchy.at(-1) && left.row.model !== "exchange";
    const reasons = [];
    if (review?.scope === "context") reasons.push("context only");
    else if (!review && !sameSector) reasons.push("business model or market differs");
    if (!left.period || left.period !== right.period || left.period.endsWith("?")) reasons.push("reporting period differs or is unverified");
    const scopedOperating = ["revenue", "revenue_growth"].includes(definition.id) &&
      review?.scope === "operating" && [left.row.id, right.row.id].includes("igx");
    const matchBasis = cell => scopedOperating && cell.basis === "issuer_and_esos_trust" ? "standalone" : cell.basis;
    if (!knownBases.has(matchBasis(metric)) || matchBasis(metric) !== matchBasis(other)) reasons.push("reporting basis differs or is unverified");
    if (metric.unit !== other.unit || metric.currency !== other.currency) reasons.push("unit or currency differs");
    if (metric.formula !== other.formula || metric.eps_basis !== other.eps_basis) reasons.push("metric definition differs");
    if (quotedRatios.has(definition.id) && (!quoteDay(metric.quote) || metric.quote.kind !== other.quote?.kind ||
      quoteDay(metric.quote) !== quoteDay(other.quote))) {
      reasons.push("quote type or date differs");
    }
    return reasons;
  }
  function metricStatus(person, definition, metric) {
    if (metric.value == null) {
      const note = ({ missing_input: "Required inputs missing", inapplicable: "Outside this business model" })[metric.state];
      return { note: note || stateText(metric.state) || "No reviewed value", style: "missing" };
    }
    if (selections.length < 2) return { note: basisName(metric.basis), style: "individual" };
    const options = selections.filter(other => other !== person && metricCell(other, definition).value != null)
      .map(other => {
        const review = reviewFor(person, other);
        return { name: other.row.short, review, reasons: mismatches(person, other, definition, metric, review) };
      });
    const comparable = options.filter(other => !other.reasons.length).map(other => other.name);
    if (comparable.length) return { note: `Comparable with ${comparable.join(", ")}`, style: "comparable", options };
    const closest = options.find(other => other.review?.scope === "operating") || options.find(other => other.review) || options[0];
    return { note: `View individually · ${closest?.reasons[0] || "matching values unavailable"}`, style: "individual", options };
  }
  function metricValue(definition, metric) {
    if (metric.state === "inapplicable") return "Inapplicable";
    if (metric.unit === "₹ crore" && metric.value != null) return `₹${fmtNum(metric.value, definition.id === "cfo" ? 3 : 2)} crore`;
    return ratioDisplay(metric.value, metric.unit);
  }
  function renderMetric(person, definition) {
    const metric = metricCell(person, definition);
    const { note, style } = metricStatus(person, definition, metric);
    const display = esc(metricValue(definition, metric));
    const accessible = `${person.row.short} · ${definition.label} · ${metricValue(definition, metric)}`;
    return `<div class="comparison-metric" data-compare-metric="${esc(definition.id)}"><dt>${esc(definition.label)}</dt>
      <dd>${metric.ev?.length || metric.formula ?
        `<button type="button" class="cash-evidence num" data-act="evidence" data-metric="${esc(definition.id)}" aria-label="${esc(accessible)}">${display}</button>` : display}
      <small class="comparison-status ${style}">${esc(note)}</small></dd></div>`;
  }
  function column(person, index, measures) {
    const { row, company, period: selected, research } = person;
    const risk = company?.research?.risk;
    const listing = row.identity.listing;
    const stage = row.ipo_stage;
    const report = listing === "reference" ? "Status under review" : listing === "listed" ? "Listed" : "Unlisted";
    const badge = stage ? `<button class="badge ok" type="button" data-act="ipo-stage" aria-label="${esc(row.short)} IPO stage" title="${esc(stage.milestone)}">${esc(stage.label)}</button>`
      : `<span class="badge">${report}</span>`;
    return `<article class="workspace-column" data-company="${esc(row.id)}">
      <div class="workspace-column-head">${badge}
      <h3>${esc(row.name)}</h3><p class="small muted">${esc(row.hierarchy.at(-1))}</p>
      ${row.periods.length ? `<label>Period <select data-period="${esc(row.id)}">${[...row.periods].reverse().map(p =>
        `<option value="${esc(p)}" ${p === selected ? "selected" : ""}>${esc(p)}</option>`).join("")}</select></label>`
        : '<p class="small muted">Identity coverage · statements and quote unavailable</p>'}
      <div class="workspace-actions"><button type="button" class="btn small" data-act="detail">Company detail</button></div>
      <div class="workspace-management">
        <button type="button" class="btn small ghost" data-act="left" ${index === 0 ? "disabled" : ""} aria-label="Move ${esc(row.short)} left">←</button>
        <button type="button" class="btn small ghost" data-act="right" ${index === selections.length - 1 ? "disabled" : ""} aria-label="Move ${esc(row.short)} right">→</button>
        <button type="button" class="btn small ghost" data-act="remove" aria-label="Remove ${esc(row.short)}" title="Remove ${esc(row.short)}">×</button>
      </div></div>
      <dl class="workspace-measures">${measures.map(definition => renderMetric(person, definition)).join("")}</dl>
      <div class="workspace-column-detail">
      <p class="small"><strong>${esc(risk?.summary || "Coverage risk")}</strong> · ${esc(risk?.horizon || "Verify the issuer and its latest disclosure before setting a timeline.")}</p>
      <div class="workspace-actions">
        <button type="button" class="btn small ghost" data-act="allocate">Model holding</button>
        <button type="button" class="btn small ghost" data-act="shortlist" aria-pressed="${state.shortlist.includes(row.id)}">${state.shortlist.includes(row.id) ? "Shortlisted" : "Shortlist"}</button>
      </div>
      <details>
        <summary>Pros, cons and risk</summary>
        ${research?.claims.length ? `<ul>${research.claims.map((item, i) => `<li><strong>${esc(item.category)} · ${esc(item.title)}</strong>
        <p class="small">${esc(item.interpretation)} <button type="button" class="cash-evidence" data-act="claim" data-claim="${i}">Evidence</button></p></li>`).join("")}</ul>`
          : '<p class="small muted">Coverage is too sparse for a sourced operating claim.</p>'}
        ${risk ? `<dl class="kv"><dt>Business</dt><dd>${esc(risk.business)}</dd><dt>Financial</dt><dd>${esc(research?.financial_risk ||
          "Annual statement coverage is incomplete.")}</dd><dt>Valuation</dt><dd>${esc(research?.valuation_risk || "Price or earnings coverage is incomplete.")}</dd>
          <dt>Liquidity</dt><dd>${esc(risk.liquidity)}</dd><dt>Restrictions</dt><dd>${esc(risk.restriction)}</dd><dt>Event</dt><dd>${research?.event
           ? `<a href="${esc(safeURL(research.event.url))}" target="_blank" rel="noopener">Proposed offer · retained DRHP</a>` : "Monitor issuer and exchange announcements."}</dd></dl>` : ""}
        ${research?.scenario ? `<p class="small"><strong>Operating revenue sensitivity · ₹ crore</strong><br>
          Downside ${fmtNum(research.scenario.downside)} · Base ${fmtNum(research.scenario.base)} · Upside ${fmtNum(research.scenario.upside)}.
          ${esc(research.scenario.note)}</p>` : ""}
      </details></div>
    </article>`;
  }
  async function render() {
    const turn = ++renderNumber;
    const ids = state.companies.filter(id => record(id));
    const expanded = [...columns.querySelectorAll("details[open]")].map(el => el.closest("[data-company]").dataset.company);
    const activePeriod = document.activeElement?.dataset.period;
    const offset = columns.scrollLeft;
    const companyRecords = await Promise.all(ids.map(id => registered(record(id)) ? get(id) : null));
    if (turn !== renderNumber) return;
    if (!Object.keys(ratioGroups).length) {
      const alternate = companyRecords.find(company => company?.ratios?.groups);
      if (alternate) {
        ratioGroups = alternate.ratios.groups;
        renderRatioPicker();
      }
    }
    selections = ids.map((id, i) => {
      const company = companyRecords[i], p = period(id), research = company?.research?.by_period[p];
      return { row: record(id), period: p, company, research };
    });
    const measures = comparisonMetrics();
    columns.style.setProperty("--compare-metrics", measures.length);
    columns.innerHTML = selections.map((person, index) => column(person, index, measures)).join("")
      || '<p class="muted">Add a company above or from query results.</p>';
    for (const el of columns.querySelectorAll("[data-company]")) {
      if (expanded.includes(el.dataset.company)) el.querySelector("details").open = true;
    }
    columns.scrollLeft = offset;
    if (activePeriod) $(`[data-period="${CSS.escape(activePeriod)}"]`, columns)?.focus({ preventScroll: true });
    updateScrollHint();
    search();
    renderBenchmarks();
  }
  function detail(id) {
    const row = record(id);
    $("#company-details-title").textContent = row.name;
    frame.hidden = !registered(row);
    $("#attached-detail").hidden = !frame.hidden;
    if (registered(row)) {
      const params = new URLSearchParams({ company: id, embedded: "1", period: period(id),
        statement: state.statements[id] || "profit-loss" });
      frame.src = `index.html?${params}`;
    } else {
      $("#attached-detail").innerHTML = `<p>${esc(row.identity.key)} · ${esc(row.hierarchy.at(-1))}</p>
        <p>Annual statements, quotes and allocation inputs are unavailable.</p>
        <p><a href="${esc(safeURL(row.url))}" target="_blank" rel="noopener">User-supplied identity source</a></p>`;
    }
    modal.showModal();
  }
  window.addEventListener("message", e => {
    if (e.origin !== location.origin || e.source !== frame.contentWindow || e.data?.type !== "ipo-ready:detail") return;
    const { company, period: picked, statement } = e.data;
    if (!catalog.has(company)) return;
    if (catalog.get(company).periods.includes(picked)) state.periods[company] = picked;
    if (["cash-flow", "balance-sheet", "profit-loss"].includes(statement)) state.statements[company] = statement;
    persist();
    render();
  });

  function renderControls() {
    scenario.elements.company.innerHTML = '<option value="">Select a company</option>' + [...catalog.values(), ...state.attached]
      .map(row => `<option value="${esc(row.id)}">${esc(row.short)} · ${esc(row.identity.listing)}</option>`).join("");
    for (const [key, value] of Object.entries(state.inputs)) {
      const input = scenario.elements[key];
      if (!input) continue;
      if (input.type === "checkbox") input.checked = value === true;
      else input.value = value;
    }
    $("#requested-label").hidden = state.inputs.path !== "company";
    $("#workspace-shortlist").innerHTML = state.shortlist.map(id => record(id) ?
      `<button type="button" class="btn small ghost" data-remove-shortlist="${esc(id)}" aria-label="Remove ${esc(record(id).short)} from shortlist">${esc(record(id).short)} ×</button>` : "").join("")
      || '<span class="small muted">Add companies from query results, or run the diversified baseline.</span>';
  }
  function renderAllocation(result) {
    const { scenario: allocation, baseline, focus, candidates, notes } = result;
    const focusName = focus ? esc(record(focus.id)?.name || focus.name) : "";
    const note = focus ? `<p><strong>${focus.state === "allocated" ? focusName :
      `<button type="button" class="cash-evidence" data-holding-evidence="${esc(focus.id)}">${focusName}</button>`}</strong> · ${esc(focusStates[focus.state] || focus.state)}.
      ${focus.min_lot_inr != null ? `Minimum lot ${fmtInr(focus.min_lot_inr)} for ${focus.lot_shares} ${focus.lot_shares === 1 ? "share" : "shares"}. ` : ""}${focus.effective_limit_inr != null ?
      `Modeled limit ${fmtInr(focus.effective_limit_inr)}. ` : ""}Allocation ${fmtInr(focus.amount_inr)}.
      ${focus.unit_price_inr != null && focus.listing === "unlisted" ? `Indicative dealer quote ${fmtInr(focus.unit_price_inr)} per share (${fmtDate(focus.price_as_of)}). ` : ""}
      ${focus.state !== "allocated" ? "The diversified baseline is the alternative." : ""}</p>`
      : `<p>Using the diversified baseline${candidates.length ? " because the shortlist had no eligible candidates" : ""}.</p>`;
    const holding = allocation.holdings.filter(row => Number(row.amount_inr) > 0);
    const bond = holding.find(row => row.kind === "sovereign_bond");
    const offExchange = holding.find(row => row.kind === "unlisted_equity");
    const cashReason = {
      whole_units: "The remainder is smaller than one eligible Liquid BeES unit.",
      stress_cap: "Adding another Liquid BeES unit would exceed modeled stress headroom.",
      liquidity_cap: "Additional Liquid BeES units would exceed the modeled daily-turnover cap.",
      liquid_input_unavailable: "The dated close, turnover or lot evidence for Liquid BeES is unavailable.",
    }[allocation.cash_reason];
    function historical(row) {
      const history = row.history || {};
      if (history.state === "ok") return `${fmtNum(history.return_pct)}% price return<br><small>${fmtDate(history.from)} to ${fmtDate(history.to)}</small>`;
      if (history.state === "issuer_reported") return `${fmtNum(history.return_pct)}% 1-year fund return<br><small>Reinvested IDCW to ${fmtDate(history.as_of)}</small>`;
      if (row.coupon_rate != null) return `${fmtNum(row.coupon_rate)}% dated annual coupon<br><small>From ${fmtDate(row.coupon_as_of)} · resets every six months</small>`;
      if (row.kind === "unlisted_equity") return "No verified trades";
      if (history.state === "corporate_action_review") return "Corporate action needs review";
      return row.kind === "cash" ? "—" : "Series unavailable";
    }
    const forecast = ["base", "downside", "upside"].map(key => {
      const value = allocation.returns[key];
      return `<div><dt>${key[0].toUpperCase() + key.slice(1)}</dt><dd>${fmtInr(value.ending_value_inr)}</dd>
        <small>${fmtNum(value.horizon_return_pct)}% over ${result.horizon_months} months · ${fmtNum(value.annualized_return_pct)}% annualized</small></div>`;
    }).join("");
    $("#allocation-result").innerHTML = `${note}
      <dl class="allocation-summary">
        <div><dt>Budget invested</dt><dd>${fmtInr(allocation.invested_inr)}</dd><small>Budget ${fmtInr(result.amount_inr)}</small></div>
        <div><dt>Cash remaining</dt><dd>${fmtInr(allocation.cash_inr)}</dd><small>Set aside ${fmtInr(result.reserve_inr)} · unspent ${fmtInr(allocation.unspent_inr)}</small></div>
        <div><dt>Modeled stress loss</dt><dd>${fmtNum(allocation.stress_loss_pct)}%</dd><small>Baseline ${fmtNum(baseline.stress_loss_pct)}% · limit ${result.max_loss_pct}%</small></div>
        <div><dt>Exchange exposure</dt><dd>${fmtInr(allocation.exchange_exposure_inr)}</dd><small>Limit ${fmtInr(allocation.exchange_limit_inr)}</small></div>
      </dl>
      ${cashReason ? `<p class="small muted">${esc(cashReason)}</p>` : ""}
      <p class="small">Modeled risk mix, including any cash · ${["low", "medium", "high"].map(band =>
        `${band} ${fmtNum(allocation.risk_mix[band].weight_pct)}%`).join(" · ")}
        ${bond ? ` · Seven-year bond lockup ${fmtInr(bond.amount_inr)}` : ""}
        ${offExchange ? ` · Off-exchange position ${fmtInr(offExchange.amount_inr)}` : ""}</p>
      <h3>Illustrative return scenarios</h3>
      <dl class="allocation-summary return-scenarios" aria-label="Ending portfolio value">${forecast}</dl>
      <p class="small muted">The base case uses assumed annual rates. The downside and upside show sensitivity without probabilities. Each case values the basket before investor fees and taxes. Unlisted values depend on finding a buyer.</p>
      <p class="allocation-scroll-hint tiny muted">Scroll the holdings table to see prices and returns.</p>
      <div class="tbl-wrap" tabindex="0" aria-label="Illustrative holdings"><table class="data"><thead><tr>
        <th>Holding</th><th>Units</th><th>Amount</th><th>Weight</th><th>Risk</th><th>Unit price</th><th>Annual assumptions<br><small>Downside / base / upside</small></th><th>Dated history</th></tr></thead><tbody>
        ${holding.map(row => `<tr><th scope="row">${row.id !== "CASH" ?
          `<button type="button" class="cash-evidence" data-holding-evidence="${esc(row.id)}">${esc(row.name)}</button>` : esc(row.name)}</th><td>${row.units ?? "—"}</td>
          <td>${fmtInr(row.amount_inr)}</td><td>${fmtNum(row.weight_pct)}%</td><td>${esc(row.risk_band)}</td>
          <td>${row.unit_price_inr ? fmtInr(row.unit_price_inr) : "—"}${row.price_as_of ? `<br><small>${fmtDate(row.price_as_of)}</small>` : ""}</td>
          <td>${row.kind === "cash" ? "—" : ["downside", "base", "upside"].map(caseName => fmtNum(row.return_scenarios[caseName].annual_assumption_pct) + "%").join(" / ") +
            `<br><small>Base value ${fmtInr(row.return_scenarios.base.ending_value_inr)}</small>`}</td>
          <td>${historical(row)}</td></tr>`).join("")}</tbody></table></div>
      <details open><summary>Shortlist decisions and assumptions</summary>
        ${candidates.length ? `<ul>${candidates.map(row => `<li>${esc(record(row.id)?.short || row.name)} · ${esc(row.selection === "alternate" ?
          "Eligible alternative" : focusStates[row.state] || row.state)}</li>`).join("")}</ul>` : ""}
        <ul>${notes.map(text => `<li>${esc(text)}</li>`).join("")}
          <li>Review the result after a new financial filing, an offer-price announcement or a change in quote, lot, risk tolerance or liquidity needs.</li></ul>
      </details><details><summary>Baseline without a selected company</summary>
      <p class="small">${fmtInr(baseline.invested_inr)} invested · base ending value ${fmtInr(baseline.returns.base.ending_value_inr)} · ${fmtNum(baseline.stress_loss_pct)}% modeled stress loss</p>
      <ul>${baseline.holdings.filter(row => Number(row.amount_inr) > 0).map(row =>
        `<li>${esc(row.name)} · ${fmtInr(row.amount_inr)} · ${fmtNum(row.weight_pct)}%</li>`).join("")}</ul></details>`;
  }
  async function calculate() {
    const turn = ++calculating;
    const { path, company, ...fields } = state.inputs;
    if (path === "company" && !company) { $("#allocation-status").textContent = "Choose the company to carry into this scenario."; return; }
    $("#allocation-status").textContent = "Calculating with the local Python model…";
    try {
      const params = new URLSearchParams({ ...fields, company: path === "company" ? company : "", shortlist: state.shortlist.join(",") });
      const response = await fetch(`api/workspace/allocate?${params}`, { cache: "no-store" });
      const result = await response.json();
      if (turn !== calculating) return;
      if (!response.ok) throw new Error(result.error);
      renderAllocation(result);
      $("#allocation-status").textContent = `Illustrative · ${result.horizon_months} months · prices through ${fmtDate(result.market_date)} · build ${result.build_id}`;
    } catch (error) {
      if (turn === calculating) $("#allocation-status").textContent = `${error.message} Previous results remain available if shown.`;
    }
  }

  $("#workspace-search").addEventListener("input", search);
  for (const list of [$("#workspace-matches"), $("#workspace-benchmarks")]) {
    list.addEventListener("click", e => { const id = e.target.closest("button[data-add]")?.dataset.add; if (id) add(id); });
  }
  $("#compare-ratio-filter").addEventListener("input", renderRatioPicker);
  $("#compare-ratio-reset").addEventListener("click", () => {
    state.ratioPicks = defaultRatios;
    $("#compare-ratio-filter").value = "";
    renderRatioPicker();
    persist();
    render();
  });
  $("#compare-ratio-options").addEventListener("change", e => {
    if (!e.target.matches('input[type="checkbox"]')) return;
    const { checked, value } = e.target;
    state.ratioPicks = checked ? [...new Set([...state.ratioPicks, value])] : state.ratioPicks.filter(id => id !== value);
    $("#compare-ratio-count").textContent = `${comparisonMetrics().length - overview.length} selected`;
    persist();
    render();
  });
  CompanyLookup.mount($("#company-lookup"), row => {
    catalog.set(row.id, row);
    facts.set(row.id, load(`company/${row.id}.json`, true).catch(() => null));
    const aliases = state.attached.filter(item => [row.identity.key, row.identity.isin].includes(item.identity.key))
      .map(item => item.id);
    const replace = id => aliases.includes(id) ? row.id : id;
    state.companies = [...new Set(state.companies.map(replace))];
    state.shortlist = [...new Set(state.shortlist.map(replace))];
    state.inputs.company = replace(state.inputs.company);
    state.attached = state.attached.filter(item => !aliases.includes(item.id));
    invalidateAllocation();
    add(row.id);
    persist();
    renderControls();
    document.dispatchEvent(new Event("ipo-ready:catalog"));
  }, () => $("#workspace-search").value.trim());
  $("#workspace-attach").addEventListener("submit", e => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.currentTarget));
    const identity = norm(data.identity).replace(/^(CIN|ISIN):/, "");
    const securityId = /^(?:[LU][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}|IN[A-Z0-9]{10})$/;
    const key = /^[A-Z][A-Z0-9&-]{0,19}$/.test(identity) && !securityId.test(identity) ? `NSE:${identity}` : identity;
    const url = safeURL(data.source);
    if (!url || !/^(?:NSE:[A-Z0-9&-]{1,20}|BSE:[0-9]{6}|[LU][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}|IN[A-Z0-9]{10})$/.test(key)
        || !data.name.trim() || !data.sector.trim()) {
      $("#workspace-status").textContent = "Enter a company name, sector, recognised identifier and HTTPS evidence URL.";
      return;
    }
    const existing = [...catalog.values(), ...state.attached].find(row =>
      [row.identity.key, row.identity.cin, row.identity.isin].some(candidate => norm(candidate) === key));
    if (existing) {
      add(existing.id);
      $("#workspace-status").textContent = `${existing.short} already has a company record. Its existing column was used.`;
      return;
    }
    const id = `attached-${key.toLowerCase().replace(/[^a-z0-9]/g, "-")}`;
    state.attached.push({ id, url, name: data.name.trim(), short: data.name.trim(),
      hierarchy: ["Attached", data.sector.trim()], identity: { key, listing: data.listing }, periods: [] });
    $("#workspace-status").textContent = "Attached an identity-only company from your source.";
    add(id);
    e.currentTarget.reset();
  });
  columns.addEventListener("change", e => {
    if (e.target.dataset.period) {
      state.periods[e.target.dataset.period] = e.target.value;
      persist();
      render();
    }
  });
  columns.addEventListener("click", e => {
    const button = e.target.closest("button[data-act]");
    if (!button) return;
    const id = button.closest("[data-company]").dataset.company, action = button.dataset.act;
    const i = state.companies.indexOf(id);
    if (action === "remove") state.companies.splice(i, 1);
    else if (action === "left" || action === "right") {
      const j = i + (action === "left" ? -1 : 1);
      [state.companies[i], state.companies[j]] = [state.companies[j], state.companies[i]];
    } else if (action === "detail") return detail(id);
    else if (action === "allocate") return requestCompany(id);
    else if (action === "shortlist") return shortlist(id);
    else if (action === "ipo-stage") {
      const person = selections.find(item => item.row.id === id);
      const stage = person?.row.ipo_stage;
      if (stage && person.company) openEvidence({ title: `${person.row.short} IPO stage · ${fmtDate(stage.as_of)}`,
        evIds: [stage.ev], evidence: person.company.evidence, extra: `<p>${esc(stage.milestone)}</p>` });
      return;
    }
    else if (action === "claim") {
      const person = selections.find(item => item.row.id === id);
      const item = person?.research?.claims[button.dataset.claim];
      if (item) openEvidence({ title: item.title, evIds: item.ev, evidence: person.company.evidence,
        extra: `<p>${esc(item.interpretation)}</p>` });
      return;
    } else if (action === "evidence") {
      const person = selections.find(item => item.row.id === id);
      const definition = comparisonMetrics().find(item => item.id === button.dataset.metric);
      if (!person?.company || !definition) return;
      const cell = metricCell(person, definition);
      const quote = quoteDay(cell.quote) ? `<p class="small">${esc(cell.quote.kind)} · ${esc(quoteDay(cell.quote))} IST</p>` : "";
      const { options } = metricStatus(person, definition, cell);
      const scope = options?.length ? `<ul class="comparison-pairings">${options.map(item => `<li><strong>${esc(item.name)}</strong> ·
        ${item.reasons.length ? esc(item.reasons.join(" · ")) : "Comparable on this measure"}</li>`).join("")}</ul>` : "";
      const earnings = cell.eps_basis ? ` · ${esc(cell.eps_basis.replaceAll("_", " "))} EPS` : "";
      openEvidence({ title: `${person.row.short} · ${definition.label}`, value: esc(metricValue(definition, cell)),
        metric: cell.formula ? cell : undefined, evIds: cell.ev, evidence: person.company.evidence,
        extra: `<p class="small">${esc(person.period)} · ${esc(basisName(cell.basis))} · ${esc(cell.unit)}${earnings}</p>${quote}${scope}` });
      return;
    }
    persist();
    render();
  });
  $("#company-details-close").addEventListener("click", () => modal.close());
  $("#workspace-shortlist").addEventListener("click", e => {
    if (e.target.dataset.removeShortlist) shortlist(e.target.dataset.removeShortlist);
  });
  scenario.addEventListener("change", e => {
    const input = e.target;
    if (!input.name) return;
    state.inputs[input.name] = input.type === "checkbox" ? input.checked : input.value;
    persist();
    if (input.name === "path") renderControls();
    invalidateAllocation();
  });
  scenario.addEventListener("submit", e => {
    e.preventDefault();
    Object.assign(state.inputs, Object.fromEntries(new FormData(scenario)), {
      include_unlisted: scenario.elements.include_unlisted.checked,
    });
    persist();
    calculate();
  });
  $("#allocation-result").addEventListener("click", async e => {
    const button = e.target.closest("button[data-holding-evidence]");
    if (!button) return;
    const id = button.dataset.holdingEvidence;
    try {
      const portfolio = await load("portfolio.json");
      const instrument = [...portfolio.instruments, ...(portfolio.workspace_instruments || []), ...portfolio.unlisted].find(item => item.id === id);
      const symbol = record(id)?.identity?.symbol || id;
      const datedSources = portfolio.listed_history?.[symbol]?.history?.sources || {};
      const historySources = Object.fromEntries(Object.entries(datedSources).map(([date, url]) =>
        [`history-${date}`, { source: "NSE historical close", url, anchor: `${symbol} · ${date} · CLOSE_PRICE` }]));
      if (instrument) {
        const evidence = { ...Object.fromEntries(Object.entries(instrument.evidence).filter(([, item]) => item.url)), ...historySources };
        openEvidence({ title: button.textContent, evidence, evIds: Object.keys(evidence),
          extra: `<p>${esc(instrument.liquidity?.note || "See the dated price and instrument terms.")}</p>` });
        return;
      }
      const company = catalog.has(id) ? await get(id) : null;
      if (company?.quote.ev) {
        openEvidence({ title: button.textContent, evidence: { ...company.evidence, ...historySources },
          evIds: [company.quote.ev, ...Object.keys(historySources)] });
        return;
      }
    } catch {}
    openEvidence({ title: button.textContent, extra: "<p>Holding evidence is unavailable from the retained data.</p>" });
  });
  load("companies.json").then(data => data.catalog_available ? Promise.all([
    load("catalog.json"), load("peers.json").catch(() => null),
  ]) : [null, null]).then(async ([data, peerData]) => {
    if (!data) return;
    catalogBuild = data.build_id;
    reviewedBenchmarks = peerData?.cohorts || {};
    for (const row of data.companies) catalog.set(row.id, row);
    state.companies = state.companies.filter(id => record(id));
    state.shortlist = state.shortlist.filter(id => record(id));
    const legacyPeer = location.hash === "#peer-coverage" || queryParams.has("company");
    const requested = queryParams.get("add") || queryParams.get("company");
    if (record(requested)) {
      if (record(requested).periods.includes(queryParams.get("period"))) state.periods[requested] = queryParams.get("period");
      add(requested);
    }
    const migrated = queryParams.get("workspace_company");
    if (migrated) { state.inputs.path = "company"; state.inputs.company = migrated; }
    for (const key of ["amount", "tolerance"]) if (queryParams.has(key)) state.inputs[key] = queryParams.get(key);
    if (queryParams.has("include_unlisted")) state.inputs.include_unlisted = queryParams.get("include_unlisted") !== "false";
    if (catalog.has("igx")) ratioGroups = (await get("igx"))?.ratios?.groups || {};
    const allowedRatios = new Set(Object.values(ratioGroups).flat().map(def => def.id));
    if (allowedRatios.size) state.ratioPicks = state.ratioPicks.filter(id => allowedRatios.has(id));
    host.hidden = $("#allocation").hidden = false;
    renderRatioPicker();
    renderControls();
    render();
    if (data.retained_build) $("#workspace-status").textContent = `Using retained data build ${data.build_id}.`;
    if (state.queryBuild && state.queryBuild !== data.build_id) $("#workspace-status").textContent = "Data build updated. Query results use the current build.";
    if (legacyPeer) {
      const url = new URL(location.href);
      if (!url.hash || url.hash === "#peer-coverage") url.hash = "workspace";
      if (record(requested)) url.searchParams.set("add", requested);
      url.searchParams.delete("company");
      history.replaceState(null, "", url);
      if (url.hash === "#workspace") host.scrollIntoView({ block: "start" });
    }
    if (record(migrated)) calculate();
  }).catch(() => {
    host.hidden = false;
    $("#workspace-status").textContent = "Company data is unavailable. Rebuild the retained sources and reload.";
  });
})();
