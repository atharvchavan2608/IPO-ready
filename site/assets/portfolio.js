/* Portfolio evidence and scenario rendering. Python sizes holdings and calculates risk. */
(() => {
  const { $, esc, fmtDate, fmtDateTime, fmtInr, fmtNum, fmtPct } = IR;
  const status = $("#portfolio-status");
  const cards = $("#portfolio-instruments");
  const form = $("#portfolio-controls");
  const amountInput = $("#portfolio-amount");
  const tolerance = $("#portfolio-tolerance");
  const select = $("#portfolio-company");
  const include = $("#portfolio-include");
  const companyDetail = $("#portfolio-company-detail");
  const resultPanel = $("#portfolio-scenario-result");
  const message = $("#portfolio-scenario-message");
  const jsonLink = $("#portfolio-scenario-json");
  const bands = ["low", "medium", "high"];
  const bandLabels = { low: "Low", medium: "Medium", high: "High" };
  const names = { FRSB2020T: "Floating Rate Savings Bonds", HDFCBANK: "HDFC Bank", GOLDBEES: "Gold BeES", MCX: "MCX" };
  let allocationRequest;
  let activeView = "scenario";

  function fact(label, value, note = "") {
    return `<div><dt>${esc(label)}</dt><dd>${esc(value)}</dd>${note ? `<dd class="small muted">${esc(note)}</dd>` : ""}</div>`;
  }

  function quoteFact(quote) {
    return fact("NSE closing price", quote.state === "reported" ? fmtInr(quote.price_inr) : "Unavailable",
      quote.as_of ? fmtDate(quote.as_of) : "");
  }

  function couponFact(coupon) {
    if (coupon.state === "unavailable") return fact("Annual coupon before tax", "Unavailable", "RBI release required");
    return fact(coupon.state === "reported" ? "Annual coupon before tax" : "Past annual coupon before tax",
      fmtPct(coupon.rate_pct_pa, 2), `${fmtDate(coupon.from)} to ${fmtDate(coupon.to)}`);
  }

  function historyFacts(history) {
    const ok = history.state === "ok";
    return fact("Annualized volatility", ok ? fmtPct(history.ann_vol_pct, 2) : "Unavailable",
      ok ? `${history.return_count} weekly returns` : "") + fact("Sampled max drawdown",
      ok ? fmtPct(history.max_drawdown_pct, 2) : "Unavailable");
  }

  function instrumentCard(instrument) {
    const { id, name, kind, exposure, risk_band, description, history, quote, coupon, liquidity, evidence } = instrument;
    const bond = kind === "sovereign_bond";
    const facts = bond ? couponFact(coupon) + fact("Face value", liquidity.face_value_inr == null ? "Unavailable" : fmtInr(liquidity.face_value_inr, 0))
      : quoteFact(quote) + historyFacts(history) + fact("Turnover on close date",
        liquidity.turnover_crore == null ? "Unavailable" : `₹${fmtNum(liquidity.turnover_crore)} cr`);
    let gap = "";
    if (bond) gap = "Weekly price risk unavailable because the bond has no exchange series.";
    else if (history.state === "corporate_action_review") gap = "A possible corporate action needs review before price risk can be shown.";
    else if (history.state !== "ok") gap = "Insufficient adjacent weekly returns for price risk.";
    const missingTerms = Object.values(evidence).some(source => source.state === "unavailable");
    return `<article class="card portfolio-instrument" data-instrument="${esc(id)}">
      <div class="portfolio-instrument-top"><span class="portfolio-band">${esc(risk_band)}</span><span class="num muted">${esc(id)}</span></div>
      <h2>${esc(name)}</h2><p class="portfolio-exposure muted">${esc(exposure)}</p>
      <p>${esc(description)}</p><dl class="portfolio-facts">${facts}</dl>
      <p class="small muted">${esc(liquidity.note)}${gap ? ` ${esc(gap)}` : ""}</p>
      ${history.verified_split ? `<p class="small muted">Prices before ${esc(fmtDate(history.verified_split.date))} adjusted for the ${esc(history.verified_split.factor)}-for-1 stock split.</p>` : ""}
      ${missingTerms ? '<p class="small muted">Some product documents have no retained capture.</p>' : ""}
      <button type="button" class="btn ghost portfolio-evidence" data-evidence="${esc(id)}">View evidence<span class="portfolio-sr-only"> for ${esc(name)}</span></button>
    </article>`;
  }

  function showEvidence(instrument) {
    const evidence = Object.fromEntries(Object.entries(instrument.evidence).filter(([, source]) => source.state !== "unavailable"));
    const evIds = Object.keys(evidence);
    const detail = evIds.length
      ? Object.values(evidence).map(source => source.file_note).filter(Boolean).join(" ")
      : "No supporting capture is available for this holding.";
    IR.openEvidence({ title: `${instrument.name} evidence`, evidence, evIds,
      extra: detail ? `<p class="small muted">${esc(detail)}</p>` : "" });
  }

  function selectCompany(company) {
    const { id, name, quote, liquidity, status_note } = company;
    const price = quote.price_inr == null ? (quote.state === "suspect_quote" ? "Withheld after source checks" : "Unavailable") : fmtInr(quote.price_inr);
    const lot = liquidity.lot_shares == null ? (liquidity.lot_raw ? `Provider text: ${liquidity.lot_raw}` : "Unavailable") : `${fmtNum(liquidity.lot_shares, 0)} shares`;
    companyDetail.innerHTML = `<h3>${esc(name)}</h3>
      ${status_note ? `<p class="notice">${esc(status_note)}</p>` : ""}
      <dl class="portfolio-facts">${fact("Indicative dealer quote", price, quote.as_of ? `Captured ${fmtDateTime(quote.as_of)}` : "")}
      ${fact("Dealer lot size", lot)}${fact("Weekly price risk", "Unavailable", "No verified trade series")}</dl>
      <p class="small muted">${esc(liquidity.note)}</p>
      <div class="portfolio-links"><button type="button" class="btn ghost portfolio-evidence">View evidence<span class="portfolio-sr-only"> for ${esc(name)}</span></button>
      <a href="index.html?company=${encodeURIComponent(id)}">Open company dashboard</a></div>`;
    $(".portfolio-evidence", companyDetail).addEventListener("click", () => showEvidence(company));
  }

  function allocationNote({ unlisted, scenario }) {
    if (unlisted.state === "minimum_lot_exceeds_limit") {
      return `One dealer lot costs ${allocationCurrency(unlisted.min_lot_inr)} (${fmtPct(unlisted.min_lot_weight_pct, 2)} of the portfolio). The scenario limit is ${allocationCurrency(unlisted.effective_limit_inr)}.`;
    }
    if (unlisted.state === "quote_unavailable") return "The dealer quote is unavailable or withheld after source checks.";
    if (unlisted.state === "lot_unavailable") return "The dealer lot size is unavailable.";
    if (unlisted.state === "allocated") {
      const size = fmtNum(unlisted.lots, 0);
      return `${size} dealer ${unlisted.lots === 1 ? "lot fits" : "lots fit"} at the indicative quote. The modeled exit haircut adds ${allocationCurrency(scenario.unlisted_exit_haircut_loss_inr)} of loss after the price shock.`;
    }
    return "The scenario excludes the unlisted holding.";
  }

  function allocationCurrency(value) {
    return fmtInr(value, Number.isInteger(Number(value)) ? 0 : 2);
  }

  function setMessage(text, type = "small muted") {
    message.className = type;
    message.textContent = text;
    message.hidden = !text;
  }

  function holdingsTable(holdings, label, total) {
    const notes = { below_unit_size: "Below unit size", input_unavailable: "Price or terms unavailable",
      minimum_lot_exceeds_limit: "Lot exceeds limit", quote_unavailable: "Quote unavailable",
      lot_unavailable: "Lot size unavailable", excluded: "Excluded" };
    return `<table class="data portfolio-holdings">
      <caption class="portfolio-sr-only">${label} holdings</caption>
      <thead><tr><th scope="col">Holding</th><th scope="col">Units</th><th scope="col">Amount (₹)</th><th scope="col">Weight</th></tr></thead>
      <tbody>${holdings.map(row => `<tr data-holding="${esc(row.id)}">
        <th scope="row">${esc(names[row.id] || row.name)}<small class="muted">${bandLabels[row.risk_band]} risk${notes[row.status] ? ` · ${notes[row.status]}` : ""}</small></th>
        <td class="num">${row.units == null ? "—" : fmtNum(row.units, 0)}</td>
        <td class="num">${allocationCurrency(row.amount_inr)}</td><td class="num">${fmtPct(row.weight_pct, 2)}</td>
      </tr>`).join("")}</tbody>
      <tfoot><tr><th scope="row">Total</th><td></td><td class="num">${allocationCurrency(total)}</td><td class="num">100%</td></tr></tfoot>
    </table>`;
  }

  function showComparison(result, view) {
    activeView = view;
    const allocation = result[view];
    const label = view === "scenario" ? "Scenario" : "Baseline";
    let start = 0;
    const slices = bands.map(band => {
      const end = start + Number(allocation.risk_mix[band].weight_pct);
      const slice = `var(--risk-${band}) ${start}% ${end}%`;
      start = end;
      return slice;
    });
    $("#portfolio-pie").style.backgroundImage = `conic-gradient(${slices.join(", ")})`;
    $("#portfolio-pie-label").textContent = `${label} risk mix`;
    $("#portfolio-holdings").innerHTML = holdingsTable(allocation.holdings, label, result.amount_inr);
    for (const button of resultPanel.querySelectorAll("[data-allocation-view]")) {
      button.setAttribute("aria-pressed", String(button.dataset.allocationView === view));
    }
  }

  function renderScenario(result) {
    const { amount_inr, tolerance, unlisted, scenario, baseline, policy } = result;
    const label = tolerance[0].toUpperCase() + tolerance.slice(1);
    const compared = amount => `${allocationCurrency(amount)} without unlisted`;
    const listedRates = scenario.holdings.filter(row => row.loss_basis === "sampled_drawdown" || row.loss_basis === "scenario_floor")
      .map(row => `${esc(names[row.id] || row.name)} ${fmtPct(row.loss_pct, 2)}`).join(", ");
    resultPanel.innerHTML = `
      <div class="portfolio-result-context"><strong>${label} · ${allocationCurrency(amount_inr)}</strong><span>Illustrative allocation</span></div>
      <dl class="portfolio-facts portfolio-outcomes">
        ${fact("Modeled stress loss", `${fmtPct(scenario.stress_loss_pct, 2)} · ${allocationCurrency(scenario.stress_loss_inr)}`, `${fmtPct(baseline.stress_loss_pct, 2)} without unlisted · limit ${fmtPct(policy.max_loss_pct, 0)}`)}
        ${fact("Exchange exposure", allocationCurrency(scenario.exchange_exposure_inr), compared(baseline.exchange_exposure_inr))}
        ${fact("Restricted capital", allocationCurrency(scenario.restricted_capital_inr), compared(baseline.restricted_capital_inr))}
      </dl>
      <p class="portfolio-lot-note"><strong>${esc(unlisted.name)}</strong> · ${esc(allocationNote(result))} <a href="#portfolio-unlisted">Dealer evidence</a></p>
      ${scenario.exchange_cap_applied ? `<p class="small muted">The ${fmtPct(policy.exchange_cap_pct, 0)} exchange cap reduced the MCX target. Combined limit ${allocationCurrency(scenario.exchange_limit_inr)}.</p>` : ""}
      ${scenario.stress_budget_applied ? `<p class="small muted">The stress budget reduced listed targets to ${fmtPct(scenario.listed_target_scale_pct, 2)} of their planned amounts.</p>` : ""}
      <div class="portfolio-breakdown">
        <div class="portfolio-breakdown-head">
          <h3>Holdings and risk mix</h3>
          <div class="seg" role="group" aria-label="Allocation view">
            <button type="button" data-allocation-view="scenario" aria-controls="portfolio-breakdown-content">Scenario</button>
            <button type="button" data-allocation-view="baseline" aria-controls="portfolio-breakdown-content">Baseline</button>
          </div>
        </div>
        <div class="portfolio-breakdown-content" id="portfolio-breakdown-content">
          <figure class="portfolio-mix">
            <figcaption id="portfolio-pie-label">Scenario risk mix</figcaption>
            <div class="portfolio-pie" id="portfolio-pie" aria-hidden="true"></div>
            <table class="data portfolio-legend">
              <caption class="portfolio-sr-only">Risk mix by share of total capital</caption>
              <thead><tr><th scope="col">Risk</th><th scope="col">Scenario</th><th scope="col">Baseline</th></tr></thead>
              <tbody>${bands.map(band => `<tr data-risk-band="${band}"><th scope="row"><span class="portfolio-swatch" aria-hidden="true"></span>${bandLabels[band]}</th>
                <td class="num">${fmtPct(scenario.risk_mix[band].weight_pct, 2)}</td>
                <td class="num">${fmtPct(baseline.risk_mix[band].weight_pct, 2)}</td></tr>`).join("")}</tbody>
            </table>
          </figure>
          <div id="portfolio-holdings"></div>
        </div>
      </div>
      <details class="portfolio-assumptions" id="portfolio-assumptions">
        <summary>How the allocation works</summary>
        <p>The baseline uses the same amount and tolerance with the unlisted holding excluded. The pie uses the whole-unit allocations, including unallocated cash.</p>
        <p>Targets for capital left after the unlisted purchase: ${Object.entries(policy.targets_pct).map(([id, pct]) => `${esc(names[id] || id)} ${fmtPct(pct, 0)}`).join(", ")}.</p>
        <p>The unlisted position is limited to ${fmtPct(policy.unlisted_cap_pct, 0)} of the amount. MCX and any unlisted exchange share a ${fmtPct(policy.exchange_cap_pct, 0)} cap. Unlisted stress assumes a ${fmtPct(policy.unlisted_shock_pct, 0)} price fall and a ${fmtPct(policy.exit_haircut_pct, 0)} haircut on the remaining value. This scenario uses ${allocationCurrency(scenario.unlisted_shock_loss_inr)} of price shock and ${allocationCurrency(scenario.unlisted_exit_haircut_loss_inr)} of haircut.</p>
        <p>Listed stress uses the larger of sampled drawdown and the model floor (${listedRates}). Bond principal and cash are held at par in the model. Restricted capital includes the bond and the unlisted holding. Interest, taxes and trading costs are excluded.</p>
      </details>`;
    showComparison(result, activeView);
    for (const button of resultPanel.querySelectorAll("[data-allocation-view]")) {
      button.addEventListener("click", () => showComparison(result, button.dataset.allocationView));
    }
  }

  async function showAllocation(buildId) {
    allocationRequest?.abort();
    const controller = new AbortController();
    allocationRequest = controller;
    const params = new URLSearchParams({ amount: amountInput.value.trim(), tolerance: tolerance.value,
      company: select.value, include_unlisted: String(include.checked) });
    const path = `/api/portfolio/allocate?${params}`;
    jsonLink.hidden = true;
    amountInput.removeAttribute("aria-invalid");
    amountInput.setAttribute("aria-describedby", "portfolio-amount-help");
    resultPanel.replaceChildren();
    resultPanel.setAttribute("aria-busy", "true");
    setMessage("Calculating the allocation…");
    try {
      const response = await fetch(path, { signal: controller.signal, cache: "no-store" });
      if (response.status === 400) {
        const invalid = await response.json();
        if (controller.signal.aborted) return;
        amountInput.setAttribute("aria-invalid", "true");
        amountInput.setAttribute("aria-describedby", "portfolio-amount-help portfolio-scenario-message");
        setMessage(invalid.error || "Check the scenario amount and try again.", "notice");
        return;
      }
      if (!response.ok) throw new Error("Allocation request failed");
      const result = await response.json();
      if (controller.signal.aborted) return;
      if (result.build_id !== buildId) {
        setMessage("Portfolio inputs changed. Reload to compare the latest allocation.", "notice");
        return;
      }
      renderScenario(result);
      const url = new URL(location.href);
      for (const [name, value] of params) url.searchParams.set(name, value);
      history.replaceState(null, "", url);
      jsonLink.href = path;
      jsonLink.hidden = false;
      setMessage("Allocation updated.", "portfolio-sr-only");
    } catch (error) {
      if (error.name !== "AbortError" && !controller.signal.aborted) {
        setMessage("Allocation is unavailable. Try calculating again. If the issue persists, rebuild the data and reload the page.", "notice");
      }
    } finally {
      if (!controller.signal.aborted) resultPanel.removeAttribute("aria-busy");
    }
  }

  async function init() {
    IR.chrome();
    let data;
    try {
      data = await IR.load("portfolio.json");
    } catch {
      status.className = "notice";
      status.textContent = "Portfolio inputs are unavailable. Rebuild the dashboard data and reload this page.";
      return;
    }
    const notes = data.market_date ? [`NSE closes through ${fmtDate(data.market_date)}`] : ["NSE closing prices unavailable"];
    if (data.using_previous_market_capture && data.market_date) notes.push("Using a previous NSE capture");
    if (data.terms_fallbacks.some(item => item.used_run)) notes.push("Using a previous product document capture");
    if (notes.length > 1) status.className = "notice";
    status.textContent = `${notes.join(". ")}. Risk bands are illustrative.`;
    cards.innerHTML = data.instruments.map(instrumentCard).join("");
    for (const button of cards.querySelectorAll("[data-evidence]")) {
      button.addEventListener("click", () => showEvidence(data.instruments.find(i => i.id === button.dataset.evidence)));
    }

    const companies = new Map(data.unlisted.map(i => [i.id, i]));
    if (companies.size) {
      const url = new URLSearchParams(location.search);
      select.innerHTML = data.unlisted.map(i => `<option value="${esc(i.id)}">${esc(i.name)}</option>`).join("");
      const requested = url.get("company");
      select.value = companies.has(requested) ? requested : (companies.has(data.default_company) ? data.default_company : data.unlisted[0].id);
      amountInput.value = url.get("amount") ?? amountInput.defaultValue;
      const requestedTolerance = url.get("tolerance");
      if (Array.from(tolerance.options).some(option => option.value === requestedTolerance)) tolerance.value = requestedTolerance;
      include.checked = url.get("include_unlisted") !== "false";
      form.addEventListener("submit", event => {
        event.preventDefault();
        showAllocation(data.build_id);
      });
      form.addEventListener("change", event => {
        if (event.target === select) selectCompany(companies.get(select.value));
        if (event.target !== amountInput) showAllocation(data.build_id);
      });
      $("#portfolio-scenario").hidden = false;
      $("#portfolio-unlisted").hidden = false;
      selectCompany(companies.get(select.value));
      showAllocation(data.build_id);
    }

    const coverage = data.history_coverage;
    const dates = coverage.points ? `${coverage.points} shared weekly closes from ${fmtDate(coverage.from)} to ${fmtDate(coverage.to)}. ${coverage.missing_weeks} missing weeks within that span.`
      : "No comparable weekly closing prices were retained.";
    $("#portfolio-method-body").innerHTML = `<p>${esc(dates)} Price risk requires at least ${esc(coverage.min_returns)} adjacent weekly returns.</p><p>${esc(coverage.method)}</p>`;
    $("#portfolio-method").hidden = false;
  }
  init();
})();
