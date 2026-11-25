/* Page 1 — company dashboard (home). Reads pipeline JSON; agent re-run calls the Python API. */
(async () => {
  const { load, $, esc, n, fmtNum, fmtCr, fmtInr, fmtPct, fmtX, ratioDisplay, fmtDate, fmtDateTime, stateText, barChart, lineChart, spark, openEvidence } = IR;
  IR.chrome();
  const params = new URLSearchParams(location.search);
  const embedded = params.get("embedded") === "1" && window.parent !== window;
  if (embedded) document.body.classList.add("embedded-company");
  let list, co, period, peerData, mkt, mktView = "nifty";
  const chosenRatios = {};
  const chosenCharts = new Set(CompanyCharts.catalogue.filter(chart => chart.primary).map(chart => chart.id));
  const statementButtons = [...$("#statement-switch").querySelectorAll("button")];
  let statement = statementButtons.some(b => b.dataset.statement === params.get("statement"))
    ? params.get("statement") : "profit-loss";

  try {
    list = await load("companies.json");
    const [catalog, peers] = await Promise.all([list.catalog_available ? load("catalog.json").catch(() => null) : null,
      load("peers.json").catch(() => null)]);
    peerData = peers?.cohorts || {};
    if (catalog) list.companies = catalog.companies;
  } catch (e) {
    $("#co-name").textContent = "Data not built yet";
    $("#co-desc").innerHTML = `Run <code>python -m ipo_ready.pipeline --offline</code> first. (${esc(e.message)})`;
    return;
  }
  const byId = Object.fromEntries(list.companies.map(c => [c.id, c]));
  let cid = byId[params.get("company")] ? params.get("company") : list.default;

  const sel = $("#sel-company");
  function renderCompanies() {
    const groups = {};
    list.companies.forEach(c => (groups[c.ipo_stage?.state === "verified" ? "Pre-IPO · verified filings" : c.hierarchy[0]] ??= []).push(c));
    const sortedGroups = Object.entries(groups).sort(([a], [b]) => Number(b.startsWith("Pre-IPO")) - Number(a.startsWith("Pre-IPO")));
    sel.innerHTML = sortedGroups.map(([g, cs]) => `<optgroup label="${esc(g)}">${cs.map(c => `<option value="${esc(c.id)}">${esc(c.short)} — ${esc(c.name)}</option>`).join("")}</optgroup>`).join("");
  }
  renderCompanies();
  if (!embedded && list.catalog_available) CompanyLookup.mount($("#company-lookup"), async row => {
    const index = list.companies.findIndex(item => item.id === row.id);
    if (index < 0) list.companies.push(row);
    else list.companies[index] = row;
    byId[row.id] = row;
    renderCompanies();
    await openCompany(row.id, true);
  });
  sel.addEventListener("change", () => openCompany(sel.value));
  $("#sel-period").addEventListener("change", e => { period = e.target.value; syncUrl(); renderPeriod(); renderStatement(); renderTrend(); });
  statementButtons.forEach(button => button.addEventListener("click", () => {
    statement = button.dataset.statement;
    syncUrl();
    renderStatement();
  }));
  $("#trend-options").innerHTML = CompanyCharts.catalogue.map(chart =>
    `<label><input type="checkbox" value="${esc(chart.id)}" ${chosenCharts.has(chart.id) ? "checked" : ""}> ${esc(chart.title)}</label>`).join("");
  $("#trend-options").addEventListener("change", e => {
    if (!e.target.matches("input[type=checkbox]")) return;
    if (e.target.checked) chosenCharts.add(e.target.value);
    else chosenCharts.delete(e.target.value);
    renderTrend();
  });
  $("#agent-run").addEventListener("click", runAgent);
  $("#ratio-options").addEventListener("change", e => {
    const input = e.target;
    if (!input.matches("input[type=checkbox]")) return;
    const picks = chosenRatios[co.id];
    if (input.checked) picks.add(input.value);
    else picks.delete(input.value);
    renderPeriod();
  });

  function syncUrl() {
    const u = new URL(location.href);
    u.searchParams.set("company", cid);
    if (period) u.searchParams.set("period", period);
    else u.searchParams.delete("period");
    if (statement !== "profit-loss") u.searchParams.set("statement", statement);
    else u.searchParams.delete("statement");
    history.replaceState(null, "", u);
    const workspace = $("#company-workspace");
    workspace.hidden = !list.catalog_available;
    workspace.href = `compare.html?${new URLSearchParams({ add: cid, period: period || "" })}#workspace`;
    const benchmark = $("#company-peers");
    if (benchmark) benchmark.href = workspace.href;
    if (embedded) window.parent.postMessage({ type: "ipo-ready:detail", company: cid, period, statement }, location.origin);
  }

  async function openCompany(id, refresh = false) {
    cid = id;
    sel.value = id;
    const nextCompany = await load(`company/${id}.json`, refresh);
    if (id !== cid) return;
    co = nextCompany;
    const periods = [...new Set([...co.periods, ...Object.keys(co.cash_flow?.by_period || {})])].sort();
    const wanted = params.get("period");
    period = periods.includes(wanted) && id === (params.get("company") || list.default) ? wanted : periods.at(-1);
    $("#sel-period").innerHTML = periods.slice().reverse().map(p => `<option value="${p}">${esc(labelPeriod(p))}</option>`).join("") || `<option>none</option>`;
    $("#sel-period").value = period;
    $("#sel-period").disabled = !periods.length;
    renderRatioPicker();
    syncUrl();
    renderHeader(); renderIssuerCase(); renderPeriod(); renderTrend(); renderStatement(); renderDocs(); renderChecks(); renderRecon(); renderNews(); renderDiscovery();
    statementButtons.forEach(button => { button.disabled = false; });
    $("#agent-run").closest("section").hidden = !co.agent?.inventories;
    if (co.agent?.inventories) renderAgent(co.agent, false);
    document.title = `IPO-Ready · ${co.short}`;
  }
  const labelPeriod = p => p.endsWith("?") ? `${p.slice(0, -1)} (year-end assumed)` : p.startsWith("PE:") ? `Period ending ${p.slice(3)}` : `${p} (Apr ${+p.slice(2, 6) - 1} – Mar ${p.slice(2, 6)})`;

  /* ---------- header ---------- */
  function renderHeader() {
    $("#crumbs").innerHTML = co.hierarchy.map(h => `<span>${esc(h)}</span>`).join("");
    $("#co-name").textContent = co.name;
    const desc = co.profile.description || "";
    $("#co-desc").textContent = desc.length > 330 ? desc.slice(0, 320).replace(/\s+\S*$/, "") + "…" : desc;
    const q = co.quote;
    const chg = q.change_raw || "";
    $("#quote").innerHTML = q.price_inr ? `
      <div class="px num">${fmtInr(q.price_inr)}</div>
      <div class="small ${chg.includes("-") ? "delta down" : "delta up"}">${esc(chg)}</div>
      <div class="kind">${esc(q.kind)} · ${co.identity?.listing === "listed" ? fmtDate(q.as_of) : `WWIPL, captured ${fmtDateTime(q.as_of)}`}</div>
      <div class="tiny muted">52-week ${esc(q.low_52w || "—")} – ${esc(q.high_52w || "—")}</div>
      <button class="btn ghost small" id="quote-src" style="margin-top:6px">Price history &amp; source</button>` : `<div class="state">No quote captured</div>`;
    $("#quote-src")?.addEventListener("click", () => openEvidence({ title: `${co.short} quote`, value: fmtInr(q.price_inr), evIds: [q.ev], evidence: co.evidence,
      extra: `${historyPanel(CompanyCharts.price(co, mkt))}
        ${co.identity?.listing === "listed" ? "" : '<p class="small">Actual dealer prices depend on lot size and counterparty.</p>'}` }));
    const b = [];
    if (co.lookup) b.push('<span class="badge info">NSE lookup record</span>');
    b.push(`<span class="badge info">Basis: ${esc(co.basis)}</span>`);
    b.push(`<span class="badge">${esc(co.layout)} · ${co.periods.length} periods</span>`);
    if (co.documents.length) b.push(`<span class="badge ok">${co.documents.length} issuer documents retained</span>`);
    const drhp = (co.profile.drhp_filed || "").toLowerCase();
    const ipoConflict = co.checks.find(c => c.check === "ipo_status");
    if (co.ipo_stage) b.unshift(`<button type="button" class="badge ok" id="ipo-stage">${esc(co.ipo_stage.label)} · ${esc(co.ipo_stage.milestone)}</button>`);
    if (ipoConflict) b.push(`<span class="badge warn" title="${esc(ipoConflict.detail)}">IPO status conflict: issuer DRHP vs provider “No”</span>`);
    else if (!co.ipo_stage && drhp === "yes") b.push(`<span class="badge">Dealer reports draft filed · unverified</span>`);
    const flagged = co.checks.filter(c => ["fail", "conflict", "stale"].includes(c.result) && c.check !== "ipo_status");
    if (flagged.length) b.push(`<span class="badge warn">${flagged.length} data check${flagged.length > 1 ? "s" : ""} flagged</span>`);
    if (co.status_note) b.push(`<span class="badge warn" title="${esc(co.status_note)}">Listing status conflict</span>`);
    if (co.market_status) b.push(`<span class="badge warn">${esc(co.market_status)}</span>`);
    const identityEvidence = co.evidence[co.identity?.ev];
    if (identityEvidence) b.push(`<a class="badge info" href="${esc(identityEvidence.url)}" target="_blank" rel="noopener">Identity source</a>`);
    if (co.peer_annual) b.push(`<a class="badge info" href="${esc(co.peer_annual.evidence.url)}" target="_blank" rel="noopener">Issuer P&amp;L used for peer comparison</a>`);
    if (co.profile.lot_size) b.push(`<span class="badge">Min. lot ${esc(co.profile.lot_size)} shares</span>`);
    if (!embedded && list.catalog_available && (co.issuer_case?.benchmarks?.length || co.peer_reviewed)) {
      b.push(`<a class="badge info" id="company-peers" href="${esc($("#company-workspace").getAttribute("href"))}">Review benchmarks</a>`);
    }
    $("#badges").innerHTML = b.join("");
    $("#ipo-stage")?.addEventListener("click", () => openEvidence({
      title: `${co.short} IPO stage · ${fmtDate(co.ipo_stage.as_of)}`,
      extra: `<p>${esc(co.ipo_stage.milestone)}. See the current filing for offer terms.</p>`,
      evIds: [co.ipo_stage.ev], evidence: co.evidence,
    }));
  }

  function renderIssuerCase() {
    const target = $("#issuer-case");
    const study = co.issuer_case;
    target.hidden = !study;
    if (!study) {
      target.replaceChildren();
      return;
    }
    target.innerHTML = `<h2 id="issuer-case-title">${co.ipo_stage ? "Pre-IPO research" : "Benchmark research"}</h2>
      <p class="small muted issuer-case-scope">${esc(study.period)} · ${esc(study.basis)}</p>
      <div class="issuer-case-grid">${study.sections.map((section, i) => `
        <article><h3>${esc(section.question)}</h3><p>${esc(section.finding)}</p>
        <p class="small muted"><strong>Review when</strong> · ${esc(section.review_trigger)}</p>
        ${section.ev.length ? `<button type="button" class="btn ghost small" data-case-source="${i}"
          aria-label="Sources for ${esc(section.question)}">View sources</button>` : ""}</article>`).join("")}</div>`;
    target.querySelectorAll("[data-case-source]").forEach(button => button.addEventListener("click", () => {
      const section = study.sections[Number(button.dataset.caseSource)];
      openEvidence({ title: section.question, extra: `<p>${esc(section.finding)}</p>`,
        evIds: section.ev, evidence: co.evidence });
    }));
  }

  /* ---------- KPIs ---------- */
  const fieldCell = (f, p = period) => co.fields[f]?.by_period?.[p] || { value: null, state: "not_in_source" };
  const historyPanel = data => `<section class="insight-history">${CompanyCharts.graph(data)}</section>`;
  function kpi({ k, v, s = "", metric, evIds = [], na = false, flag = false, title, extra, history }) {
    const id = "k" + Math.random().toString(36).slice(2, 8);
    setTimeout(() => $("#" + id)?.addEventListener("click", () => openEvidence({
      title: title || k, value: v, metric, evIds, evidence: co.evidence,
      extra: (history ? historyPanel(CompanyCharts.annual(co, period, history)) : "") + (extra || ""),
    })));
    return `<button class="kpi ${na ? "na" : ""} ${flag ? "flag" : ""}" id="${id}" aria-label="${esc(k)}: ${esc(v)}. Open ${history ? "history and " : ""}source">
      <span class="k">${esc(k)}</span><span class="v">${v}</span><span class="s">${s}</span><span class="src">${history ? "history &amp; source" : "source"} ›</span></button>`;
  }
  function metricKpi(k, m, fmt, s = "") {
    if (!m) return kpi({ k, v: "—", s: "not computed", na: true });
    const ok = m.state === "ok";
    return kpi({ k, v: ok ? fmt(m.value) : esc(stateText(m.state)), s: ok ? (m.note ? esc(m.note.split(";")[0]).slice(0, 70) : s) : esc(m.note || s), metric: m, evIds: m.ev || [], na: !ok, flag: !!m.note && ok });
  }
  function agentKpi(field, label) {
    const a = co.agent[field];
    const short = { inapplicable: "Not applicable", found_in_provider: "Reported", found_in_issuer_document: "Found in issuer doc", not_found: "Not found", not_found_no_documents: "Not disclosed" }[a.status] || a.status;
    const cell = field === "inventories" ? fieldCell("inventories") : null;
    const v = cell && cell.value !== null ? fmtCr(cell.value) : short;
    return kpi({ k: label, v: esc(v), s: esc(a.expectation.level.replace(/_/g, " ") + " for " + co.model), na: !(cell && cell.value !== null), flag: true,
      evIds: cell?.ev ? [cell.ev] : [], title: `${label}: agent verdict`,
      extra: `<p>${esc(a.summary)}</p><p class="small"><b>Verify:</b> ${esc(a.how_to_verify)}</p>${a.evidence.slice(0, 3).map(passage).join("")}` });
  }

  function renderRatioPicker() {
    $("#ratio-controls").hidden = !co.ratios;
    if (!co.ratios) return;
    const picks = chosenRatios[co.id] ??= new Set(co.ratios.defaults);
    $("#ratio-options").innerHTML = Object.entries(co.ratios.groups).map(([group, ratios]) =>
      `<fieldset><legend>${esc(group)}</legend>${ratios.map(r =>
        `<label><input type="checkbox" value="${esc(r.id)}" ${picks.has(r.id) ? "checked" : ""}> ${esc(r.label)}</label>`).join("")}</fieldset>`).join("");
  }

  function ratioKpi(definition) {
    const { id, label, formula } = definition;
    const record = co.ratios.by_period[period]?.[id] || { value: null, state: "missing_input", formula,
      note: "A comparable annual period or required data is unavailable." };
    const unit = record.unit === "₹/MMBtu" ? record.unit : definition.unit;
    const unitValue = value => esc(ratioDisplay(value, unit));
    const displayed = record.state === "inapplicable" ? "Inapplicable" :
      record.value === null ? "Unavailable" : unitValue(record.value);
    const cohort = peerData?.[co.id];
    const metric = { net_profit_ratio: "pat_to_revenue_pct", other_income_share: "other_income_share_pct" }[id];
    const benchmarks = metric && cohort?.period_end === `${period?.slice(2)}-03-31`
      ? cohort.peers.filter(peer => peer.metrics?.[metric]?.state === "ok") : [];
    const peerNote = benchmarks.length && list.catalog_available
      ? `<div><h3>Peer reference</h3><p class="small"><a href="${esc($("#company-workspace").getAttribute("href"))}">Check side-by-side values and comparison scope</a>.</p></div>` : "";
    const earnings = id === "pe" && co.valuation ? `<dl class="kv"><dt>Reported basic EPS</dt><dd>${fmtInr(co.valuation.eps_reported_basic)}</dd>
      <dt>Reported diluted EPS</dt><dd>${fmtInr(co.valuation.eps_reported_diluted)}</dd>
      <dt>PAT / shares proxy</dt><dd>${fmtInr(co.valuation.eps?.value)} · ${fmtX(co.valuation.pe_proxy?.value)}</dd></dl>` : "";
    return kpi({ k: label, v: displayed, na: record.state !== "ok", metric: record, evIds: record.ev || [],
      history: { title: label, unit, ratio: id },
      s: esc(record.eps_basis === "reported_basic" ? "Reported annual basic EPS" :
        record.eps_basis === "pat_share_proxy" ? "Calculated EPS proxy" : record.note || record.basis || ""),
      extra: `<p class="small">Period ${esc(period || "unavailable")} · ${esc(record.basis || co.basis)} · ${esc(unit)}</p>
        ${earnings}${peerNote}` });
  }

  function renderPeriod() {
    const m = co.metrics[period] || {};
    const ratios = co.ratios?.by_period?.[period] || m;
    const v = co.valuation;
    const latest = period === co.periods[co.periods.length - 1];
    $("#kpi-aside").textContent = period ? `${labelPeriod(period)} · ₹ crore unless stated` : "Reporting period unavailable";
    const factsForPeriod = co.analysis?.[period]?.facts;
    const overview = key => factsForPeriod?.[key] || fieldCell(key);
    const rev = overview("revenue_ops"), pat = overview("pat"), ti = overview("total_income");
    const cellK = (k, field, cell, s) => kpi({ k, v: cell.value !== null ? fmtCr(cell.value) : esc(stateText(cell.state)), s,
      history: { title: k, unit: "₹ crore", fields: [[field]] }, evIds: cell.ev ? [cell.ev] : [], na: cell.value === null });
    const facts = period ? [
      cellK("Revenue from operations", "revenue_ops", rev, ratios.revenue_growth?.state === "ok" ? `<span class="delta ${n(ratios.revenue_growth.value) >= 0 ? "up" : "down"}">${n(ratios.revenue_growth.value) >= 0 ? "▲" : "▼"} ${fmtPct(Math.abs(ratios.revenue_growth.value))} YoY</span>` : esc(stateText(ratios.revenue_growth?.state)) + " growth"),
      cellK("Total income", "total_income", ti, ratios.other_income_share?.state === "ok" ? `other income ${fmtPct(ratios.other_income_share.value)} of total` : ""),
      cellK("Profit after tax", "pat", pat, esc(pat.note || (ratios.pat_margin?.state === "ok" ? `${fmtPct(ratios.pat_margin.value)} of total income` : ""))),
      ...(co.agent?.inventories ? [agentKpi("inventories", "Inventory"), agentKpi("npa", "NPA")] : []),
      latest && v.market_cap.state === "conditional_share_count"
        ? kpi({ k: "Conditional equity at quote", v: fmtCr(v.market_cap.value, 0), s: "Draft preference conversion",
          metric: v.market_cap, evIds: v.market_cap.ev })
        : latest ? metricKpi("Market cap at quote", v.market_cap, x => fmtCr(x, 0)) : "",
    ] : [];
    if (co.ratios) {
      const chosen = Object.values(co.ratios.groups).flat().filter(r => chosenRatios[co.id].has(r.id));
      $("#kpis").innerHTML = [...facts, ...chosen.map(ratioKpi)].join("") || '<p class="muted">Select a ratio to inspect coverage.</p>';
      return;
    }
    $("#kpis").innerHTML = [...facts,
      metricKpi("Current ratio", m.current_ratio, v => fmtX(v)),
      metricKpi("Quick ratio", m.quick_ratio, v => fmtX(v)),
      metricKpi("Return on equity", m.roe, v => fmtPct(v), "PAT / average equity"),
      metricKpi("ROCE", m.roce, v => fmtPct(v), "EBIT / capital employed"),
      metricKpi("CFO / PAT (provider)", m.cfo_to_pat, v => fmtX(v)),
      latest ? kpi({ k: "P/E at quote", v: v.pe.state === "ok" ? fmtX(v.pe.value) : esc(stateText(v.pe.state)),
        s: ({ reported_basic: "Reported annual basic EPS", provider_annual_eps: "Provider annual EPS" })[v.pe.eps_basis] || "Calculated EPS proxy",
        metric: v.pe, evIds: v.pe.ev,
        na: v.pe.state !== "ok", extra: `<dl class="kv">
          <dt>Reported basic EPS</dt><dd>${fmtInr(v.eps_reported_basic)}</dd>
          <dt>Reported diluted EPS</dt><dd>${fmtInr(v.eps_reported_diluted)}</dd>
          <dt>PAT / shares proxy</dt><dd>${fmtInr(v.eps.value)} · ${fmtX(v.pe_proxy?.value)}</dd></dl>` })
        : kpi({ k: "P/E at quote", v: "latest year only", na: true }),
    ].join("");
  }

  /* ---------- trend chart ---------- */
  function renderTrend() {
    const el = $("#trend-chart");
    const visible = CompanyCharts.catalogue.filter(chart => chosenCharts.has(chart.id));
    el.innerHTML = visible.map(chart => {
      if (chart.id === "cash-movement") {
        return `<section class="company-plot" data-chart="${chart.id}"><h3>Cash movement</h3>
          <p class="small muted chart-unit">₹ crore · ${esc(period || "period unavailable")}</p><div class="movement-plot"></div></section>`;
      }
      const data = chart.id === "share-price" ? CompanyCharts.price(co, mkt) : CompanyCharts.annual(co, period, chart);
      return `<section class="company-plot" data-chart="${chart.id}">${CompanyCharts.graph(data)}</section>`;
    }).join("") || '<p class="small muted">Select a chart to show it here.</p>';
    if (chosenCharts.has("cash-movement")) {
      const cash = co.cash_flow?.by_period[period];
      const keys = ["cfo", "cfi", "cff", "net_change"];
      const vals = keys.map(key => n(cash?.lines[key]?.value));
      const movement = $(".movement-plot", el);
      barChart(movement, { categories: ["Operating", "Investing", "Financing", "Net change"],
        series: [{ name: "Cash movement", values: vals }] });
      if (vals.some(v => v === null)) movement.insertAdjacentHTML("beforeend", '<p class="small muted">Some cash movements are unavailable for this period.</p>');
    }
    if (chosenCharts.has("cash-vs-profit") && ["exchange", "broker"].includes(co.model))
      $('[data-chart="cash-vs-profit"]', el).insertAdjacentHTML("beforeend", '<p class="tiny muted">Operating cash flow can include member margin and settlement movements.</p>');
  }

  /* ---------- agent ---------- */
  function passage(e) {
    return `<div class="passage"><div class="where">${esc(e.document)} · page ${e.page} · <b>${esc(e.kind.replace(/_/g, " "))}</b> · <a href="${esc(e.url)}#page=${e.page}" target="_blank" rel="noopener">open PDF at page</a></div>${esc(e.snippet)}</div>`;
  }
  function traceItem(s) {
    const o = s.output, i = s.input;
    const txt = {
      provider_lookup: () => `Checked the provider statements for <code>${esc(i.field)}</code>: ${esc(o.detail)}.`,
      applicability_rule: () => `Business model <code>${esc(i.business_model)}</code> → expectation <b>${esc(o.expectation.replace(/_/g, " "))}</b>. ${esc(o.reason)}`,
      statement_line_check: () => o.skipped ? `Balance-sheet check skipped: ${esc(o.why)}.` : `Read ${esc(o.document)} p${o.page} (title confirmed: ${o.title_confirmed}): inventories line <b>${esc(o.inventories_line.replace(/_/g, " "))}</b>.`,
      document_search: () => o.documents_searched.length ? `Searched ${o.documents_searched.map(d => `${esc(d.document)} (${d.pages}p)`).join(", ")}: ${o.pages_with_word_matches} pages match word patterns; a naive substring search would flag ${o.pages_with_naive_substring} pages.` : `No issuer documents retained for this company.`,
      classify_passages: () => `Classified ${i.passages} passages: ${Object.entries(o.by_kind).map(([k, v]) => `${v} ${k.replace(/_/g, " ")}`).join(", ") || "none"}.`,
      verdict: () => `Verdict <b>${esc(o.status.replace(/_/g, " "))}</b>.`,
    }[s.tool];
    return `<li><code>${esc(s.tool)}</code> ${txt ? txt() : ""} <span class="tiny muted">${s.ms} ms</span></li>`;
  }
  function renderAgent(agent, live) {
    $("#agent").innerHTML = ["inventories", "npa"].map(f => {
      const a = agent[f];
      return `<div class="verdict"><div style="display:flex;justify-content:space-between;gap:8px;align-items:center"><b>${f === "npa" ? "Non-performing assets" : "Inventory"}</b><span class="st ${esc(a.status)}">${esc(a.status.replace(/_/g, " "))}</span></div>
        <p class="small" style="margin:8px 0">${esc(a.summary)}</p>
        <p class="tiny muted" style="margin:0"><b>How to verify:</b> ${esc(a.how_to_verify)}</p>
        <details style="margin-top:8px"><summary>Trace (${a.trace.length} steps)</summary><ol class="trace">${a.trace.map(traceItem).join("")}</ol></details>
        ${a.evidence.length ? `<details style="margin-top:6px" ${a.status === "inapplicable" && f === "inventories" ? "open" : ""}><summary>Passages (${a.evidence_total})</summary>${a.evidence.slice(0, 4).map(passage).join("")}</details>` : ""}
        ${a.next_checks?.length ? `<p class="tiny muted" style="margin:8px 0 0"><b>Next check:</b> ${a.next_checks.map(esc).join(" · ")}</p>` : ""}
      </div>`;
    }).join("");
    $("#agent-aside").textContent = live ? `live run ${fmtDateTime(agent.inventories.ran_at ? new Date().toISOString() : null)}` : "saved with data build";
  }
  async function runAgent() {
    const btn = $("#agent-run");
    btn.disabled = true; $("#agent-status").textContent = "Running the tool sequence in Python…";
    try {
      const res = await Promise.all(["inventories", "npa"].map(f => fetch(`api/agent/disclosure?company=${cid}&field=${f}`, { cache: "no-store" }).then(async r => { const j = await r.json(); if (!r.ok) throw new Error(j.error || r.status); return j; })));
      renderAgent({ inventories: res[0], npa: res[1] }, true);
      $("#agent-status").textContent = `Ran just now via /api/agent/disclosure in ${fmtNum(res[0].duration_ms + res[1].duration_ms, 0)} ms (${res[0].executed}).`;
    } catch (e) {
      $("#agent-status").textContent = `Agent API unavailable (${e.message}). Start the server with python -m ipo_ready.server; the saved result is still shown.`;
    } finally { btn.disabled = false; }
  }

  /* ---------- statements table ---------- */
  function renderStatement() {
    const target = $("#statement-body");
    statementButtons.forEach(button => button.setAttribute("aria-pressed", button.dataset.statement === statement));
    if (statement === "cash-flow") {
      $("#fin-aside").textContent = "";
      renderCashFlow(target, co, period);
      return;
    }
    const ps = co.periods;
    const order = statement === "profit-loss"
      ? ["revenue_ops", "job_work_revenue", "other_income", "other_gains", "total_income", "total_expenses", "finance_cost", "depreciation", "pbt", "tax",
        "pat_pre_associate", "associate_profit", "pat", "pat_owners", "eps_basic", "eps_diluted", "eps"]
      : ["total_assets", "current_assets", "current_liabilities", "inventories", "cash", "loans", "fixed_assets", "borrowings", "total_equity", "total_liabilities"];
    const rows = order.filter(f => co.fields[f] && ps.some(p => co.fields[f].by_period[p]?.ev));
    if (!rows.length) {
      $("#fin-aside").textContent = "";
      target.innerHTML = '<p class="muted">Statement data is unavailable.</p>';
      return;
    }
    const missing = order.filter(f => !rows.includes(f) && co.fields[f]);
    $("#fin-aside").textContent = `${co.raw_units.join(", ") || "units n/a"} as reported, shown in ₹ crore · basis ${co.basis}`;
    target.innerHTML = `<div class="tbl-wrap"><table class="data"><thead><tr><th>Line item</th>${ps.map(p => `<th class="${p === period ? "selcol" : ""}">${esc(p.replace("?", "*"))}</th>`).join("")}</tr></thead><tbody>${rows.map(f => `<tr><td>${esc(co.fields[f].label)}</td>${ps.map(p => {
      const c = co.fields[f].by_period[p];
      const derived = c.ev && co.evidence[c.ev]?.derived;
      return `<td class="num ${c.ev ? "cell-btn" : ""}" ${c.ev ? `data-f="${f}" data-p="${p}"` : ""} style="${p === period ? "background:#fff8ec" : ""}">${c.value !== null ? (f === "eps" ? fmtNum(c.value) : fmtNum(c.value)) + (derived ? "†" : "") : `<span class="state">${esc(stateText(c.state))}</span>`}</td>`;
    }).join("")}</tr>`).join("")}</tbody></table></div>
    <p class="tiny muted">† derived by summing the provider's listed lines. * year-end assumed from a bare year label. ${missing.length ? `Not in this source: ${missing.map(f => esc(co.fields[f].label)).join(", ")}.` : ""}</p>`;
    target.querySelectorAll("td[data-f]").forEach(td => td.addEventListener("click", () => {
      const c = co.fields[td.dataset.f].by_period[td.dataset.p];
      openEvidence({ title: `${co.fields[td.dataset.f].label} · ${td.dataset.p}`, value: c.value === null ? esc(stateText(c.state)) : fmtNum(c.value),
        evIds: [c.ev], evidence: co.evidence, extra: c.note ? `<p>${esc(c.note)}</p>` : "" });
    }));
  }

  /* ---------- documents, checks, reconciliation ---------- */
  function renderDocs() {
    const prov = Object.values(co.evidence).find(e => e.source === "WWIPL financial statements page");
    const ov = Object.values(co.evidence).find(e => e.source === "WWIPL company overview");
    $("#docs").innerHTML = (co.documents.length ? co.documents.map(d => `<div class="news-item"><a href="${esc(d.url)}" target="_blank" rel="noopener">${esc(d.title)}</a>
      <div class="meta">Issuer investor-relations page · retrieved ${fmtDateTime(d.retrieved_at)} · ${fmtNum(d.bytes / 1e6, 1)} MB · SHA-256 ${esc(d.sha256.slice(0, 12))}…</div></div>`).join("")
      : `<p class="small muted">${co.identity?.listing === "listed" ? "See the dated source links on the financial rows or identity record." :
        `The provider page is the retained statement source for ${esc(co.short)}.`}</p>`) +
      `<h3>Provider pages</h3>` +
      [prov, ov].filter(Boolean).map(e => `<div class="news-item"><a href="${esc(e.url)}" target="_blank" rel="noopener">${esc(e.source)}</a><div class="meta">captured ${fmtDateTime(e.retrieved_at)} · run ${esc(e.capture_run)}</div></div>`).join("");
  }
  function renderChecks() {
    const items = co.checks.map(c => `<li><span class="pill-res ${c.result}">${c.result}</span>${esc(c.check.replace(/_/g, " "))}${c.period ? ` ${esc(c.period)}` : ""}: <span class="muted">${esc(typeof c.detail === "string" ? c.detail : Object.entries(c.detail).map(([k, v]) => `${k.replace(/_/g, " ")} ${fmtNum(v, 0)}`).join(" · "))}</span></li>`);
    const gaps = co.coverage_gaps.map(g => `<li><span class="pill-res stale">gap</span>${esc(g.label || g.field)}: ${esc(stateText(g.state))}</li>`);
    const fb = (co.fallbacks || []).map(f => `<li><span class="pill-res stale">${esc(f.state === "unavailable" ? "unavailable" : "fallback")}</span>${esc(f.item)}: ${esc(f.error)} → ${f.used_run ? `using capture ${esc(f.used_run)}` : "no earlier capture"}</li>`);
    $("#checks").innerHTML = `<ul class="checks" style="padding-left:0;list-style:none;margin:0">${[...fb, ...items.filter(x => !x.includes("pass")), ...gaps].join("") || "<li>No flagged checks.</li>"}</ul>
      <details style="margin-top:8px"><summary>All ${co.checks.length} checks</summary><ul class="checks" style="padding-left:0;list-style:none">${items.join("")}</ul></details>`;
  }
  function renderRecon() {
    const r = co.reconciliation;
    if (!r) { $("#recon-card").style.display = "none"; return; }
    $("#recon-card").style.display = "";
    $("#recon-aside").textContent = `${r.summary.match} of ${r.summary.compared} provider figures match the issuer's restated statements`;
    const rows = r.rows.filter(x => x.result === "match" || x.result === "differs");
    const byField = {};
    rows.forEach(x => ((byField[x.field] ??= { label: x.label, page: x.page, cells: {} }).cells[x.period] = x));
    const periods = [...new Set(rows.map(x => x.period))].sort();
    const scope = r.operating_scope;
    const scopeLine = scope ? `<p class="small muted"><b>${esc(scope.label)}.</b> ${esc(scope.note)} <a href="${esc(r.url)}#page=${scope.scope_page}" target="_blank" rel="noopener">Scope note</a></p>` : "";
    $("#recon").innerHTML = `<p class="small muted" style="margin-top:0">Source: <a href="${esc(r.url)}#page=5" target="_blank" rel="noopener">IGX Restated Financial Information</a> (₹ million, converted ÷10). ${esc(r.unit_note.split(". ")[1] || "")}</p>${scopeLine}
      <div class="tbl-wrap"><table class="data"><thead><tr><th>Line (issuer page)</th>${periods.map(p => `<th>${p} issuer</th><th>provider</th>`).join("")}</tr></thead><tbody>
      ${Object.values(byField).map(f => `<tr><td>${esc(f.label)} <span class="tiny muted">p${f.page}</span></td>${periods.map(p => { const c = f.cells[p]; if (!c) return "<td></td><td></td>"; return `<td class="num">${fmtNum(c.issuer_value)}</td><td class="num ${c.result === "differs" ? "chip-diff" : ""}" title="difference ${esc(c.difference)}">${fmtNum(c.provider_value)}${c.result === "differs" ? " ≠" : ""}</td>`; }).join("")}</tr>`).join("")}
      </tbody></table></div>
      <p class="small"><b>Reading.</b> FY2024 matches across the selected lines. FY2026 matches except for operating cash flow. Selected FY2025 values differ by ₹0.16–0.32 crore across assets, liabilities, PBT and PAT. The differences are consistent with the provider using the originally audited FY2025 accounts.</p>`;
  }

  /* ---------- rail ---------- */
  async function renderMarket() {
    try { mkt = await load("market.json"); } catch (e) { $("#mkt-indices").innerHTML = `<p class="state">Market data unavailable.</p>`; return; }
    if (co) renderTrend();
    if (mkt.state !== "ok") { $("#mkt-indices").innerHTML = `<p class="state">${esc(mkt.note)}</p>`; return; }
    $("#mkt-asof").textContent = `close ${fmtDate(mkt.as_of)}`;
    const draw = () => {
      const nifty = mkt.indices.find(i => i.name === "Nifty 50");
      if (mktView === "nifty") lineChart($("#mkt-chart"), { points: nifty.series_1m, color: "auto", xLabel: p => fmtDate(p.date).slice(0, 6) });
      else if (mktView === "sensex") mkt.sensex.state === "ok" ? lineChart($("#mkt-chart"), { points: mkt.sensex.series_1m, color: "auto", xLabel: p => fmtDate(p.date).slice(0, 6) }) : ($("#mkt-chart").innerHTML = `<p class="state">Sensex not captured in this build.</p>`);
      else mkt.nifty_intraday?.points?.length ? lineChart($("#mkt-chart"), { points: mkt.nifty_intraday.points, color: "auto", xLabel: p => p.t.slice(11, 16) }) : ($("#mkt-chart").innerHTML = `<p class="state">No intraday capture.</p>`);
    };
    $("#mkt-seg").addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return; mktView = b.dataset.ix; $("#mkt-seg").querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", x === b)); draw(); });
    draw();
    const s = mkt.sensex;
    const rows = mkt.indices.filter(i => i.state === "ok").map(i => ({ nm: i.name, sub: `P/E ${fmtNum(i.pe, 1)} · 1Y vol ${i.weekly_stats?.ann_vol_pct ?? "—"}%`, close: i.close, ch: i.change_pct, pts: i.series_1m }));
    if (s.state === "ok") rows.splice(1, 0, { nm: "S&P BSE Sensex", sub: `delayed · ${fmtDateTime(s.market_time)}`, close: s.close, ch: s.change_pct, pts: s.series_1m });
    $("#mkt-indices").innerHTML = rows.map(r => `<div class="mkt-row"><div><div class="nm">${esc(r.nm)}</div><div class="sub">${esc(r.sub)}</div></div><div class="px"><div class="num">${fmtNum(r.close)}</div><div class="small delta ${r.ch >= 0 ? "up" : "down"} num">${r.ch >= 0 ? "+" : ""}${fmtNum(r.ch)}%</div></div><div>${spark(r.pts)}</div></div>`).join("");
    const ix = mkt.indices[0]?.source;
    $("#mkt-src").innerHTML = `Indices: <a href="${esc(ix?.url)}" target="_blank" rel="noopener">NSE end-of-day file</a> (official), retrieved ${fmtDateTime(ix?.retrieved_at)}. Sensex and intraday: ${s.state === "ok" ? `<a href="${esc(s.source.url)}" target="_blank" rel="noopener">Yahoo chart API</a> (unofficial, delayed), retrieved ${fmtDateTime(s.source.retrieved_at)}` : "not captured"}.${mkt.simulated_failure ? ` <b>Fallback drill:</b> newest NSE day withheld and Yahoo run marked failed; older captures shown.` : ""} Not live quotes.`;
    $("#stocks").innerHTML = mkt.stocks.filter(x => x.state === "ok").map(x => `<div class="mkt-row"><div><div class="nm">${esc(x.symbol)}</div><div class="sub">delivery ${fmtNum(x.deliv_pct, 0)}% · 1Y vol ${x.weekly_stats?.ann_vol_pct ?? "—"}%</div></div><div class="px"><div class="num">${fmtInr(x.close)}</div><div class="small delta ${(x.change_pct ?? 0) >= 0 ? "up" : "down"} num">${(x.change_pct ?? 0) >= 0 ? "+" : ""}${fmtNum(x.change_pct)}%</div></div><div>${spark(x.series_1m)}</div></div>`).join("");
    $("#stk-src").textContent = `NSE equity bhavcopy (official), close ${fmtDate(mkt.as_of)}.`;
  }
  function renderNews() {
    const nw = co.news || {};
    const items = nw.items || [];
    $("#news-asof").textContent = nw.retrieved_at ? `captured ${fmtDate(nw.retrieved_at)}` : "";
    $("#news").innerHTML = items.length ? items.slice(0, 6).map(i => `<div class="news-item"><a href="${esc(i.link)}" target="_blank" rel="noopener">${esc(i.title)}</a><div class="meta">${esc(i.publisher)} · ${fmtDate(i.date)}</div></div>`).join("")
      : `<p class="state">No headlines captured for ${esc(co.short)}.</p>`;
    $("#news-src").innerHTML = nw.source ? `Google News RSS search “${esc(nw.query)}”. Headlines link to publishers; not summarised or verified by IPO-Ready.` : "";
  }
  function renderDiscovery() {
    $("#discovery").innerHTML = (co.discovery || []).map(d => `<button class="disc" data-id="${d.id}"><span class="t"><span>${esc(d.short)}</span><span class="num">${d.price_inr ? fmtInr(d.price_inr) : ""}</span></span><span class="r">${d.reasons.map(esc).join(" · ")}</span></button>`).join("") || `<p class="state">No related companies in the universe.</p>`;
    $("#discovery").querySelectorAll(".disc").forEach(b => b.addEventListener("click", () => { openCompany(b.dataset.id); window.scrollTo({ top: 0, behavior: "smooth" }); }));
    $("#discovery").insertAdjacentHTML("beforeend", `<p class="tiny muted">Ranked by same business line, provider-reported IPO filing and news since 1 Oct 2026. These are research leads, not recommendations.</p>`);
  }

  renderMarket();
  await openCompany(cid);
})();
