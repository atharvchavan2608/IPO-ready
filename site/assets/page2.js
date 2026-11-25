/* Unlisted company screening. The Python API evaluates every query. */
(() => {
  const { $, esc, fmtDate, fmtDateTime, stateText } = IR;
  const input = $("#screen-query");
  const status = $("#screen-status");
  const market = $("#screen-market");
  const output = $("#screen-output");
  const coverage = $("#screen-coverage");
  const example = input.defaultValue;
  const workspace = window.IPO_WORKSPACE;
  if (workspace?.query) input.value = workspace.query;
  if (workspace?.market) market.value = workspace.market;
  const numbers = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 4 });
  const valuationFields = new Set(["market_cap_cr", "pe", "pe_reported", "pe_proxy", "pb", "ps"]);
  const shortLabels = { market_cap_cr: "Market cap", pe: "P/E", pb: "P/B", roe_pct: "ROE", roce_pct: "ROCE" };
  let pending;

  function renderValue(cell) {
    const basis = { reported_basic: "Reported EPS", pat_share_proxy: "EPS proxy", provider_annual_eps: "Provider EPS",
      issuer_and_esos_trust: "IGX + employee trust" }[cell.basis];
    return cell.value === null
      ? `<span class="state">${esc(stateText(cell.state))}</span>`
      : `${numbers.format(Number(cell.value))}${basis ? `<small class="muted">${basis}</small>` : ""}`;
  }

  function renderResults({ fields, columns, matches, evaluated, no_match, unresolved, excluded, coverage: counts }) {
    const summary = `${matches.length} of ${evaluated} companies matched. ${no_match} fell outside the filters.`;
    const gap = unresolved ? ` Missing inputs left ${unresolved} undecided.` : "";
    status.textContent = summary + gap;

    const withQuotes = columns.some(key => valuationFields.has(key));
    if (matches.length) {
      output.innerHTML = `${columns.length > 3 ? '<p class="screen-scroll-hint tiny muted">Scroll the table to see all columns.</p>' : ""}
        <div class="tbl-wrap" role="region" aria-label="Matching companies" tabindex="0"><table class="data">
          <thead><tr><th scope="col">Company</th>
            ${columns.map(key => `<th scope="col" aria-label="${esc(fields[key].label)} in ${esc(fields[key].unit)}">${esc(shortLabels[key] ?? fields[key].label)}<br>${esc(fields[key].unit)}</th>`).join("")}
          </tr></thead>
          <tbody>${matches.map(row => `<tr>
            <th scope="row"><a href="index.html?company=${encodeURIComponent(row.id)}">${esc(row.name)}</a>
              ${row.ipo_stage?.label ? `<small class="screen-ipo-stage" title="${esc(row.ipo_stage.milestone)}">${esc(row.ipo_stage.label)}</small>` : ""}
              <small class="muted">${esc(row.hierarchy?.[2] || "")}</small>
              <small class="muted">${esc(row.latest_period || "Period unavailable")} · ${esc(row.basis || "unknown")} basis</small>
              ${withQuotes ? `<small class="muted" title="${esc(fmtDateTime(row.quote_as_of))}">Quote captured ${esc(fmtDate(row.quote_as_of))}</small>` : ""}
              ${workspace ? `<div class="screen-result-actions">
                <button type="button" class="btn ghost small" data-act="compare" data-id="${esc(row.id)}">Compare</button>
                <button type="button" class="btn ghost small" data-act="shortlist" data-id="${esc(row.id)}"
                  aria-pressed="${workspace.has(row.id)}">${workspace.has(row.id) ? "Shortlisted" : "Shortlist"}</button>
                <button type="button" class="btn ghost small" data-act="allocate" data-id="${esc(row.id)}">Model</button></div>` : ""}
              ${row.checks_flagged.length ? `<small class="chip-diff">Data checks flagged</small>` : ""}</th>
            ${columns.map(key => `<td class="num">${renderValue(row.metrics[key])}</td>`).join("")}
            </tr>`).join("")}</tbody></table></div>`;
    } else {
      output.innerHTML = '<p class="notice info">No results for this query. Try widening a threshold or removing a condition. Open data coverage to see which inputs were missing.</p>';
    }

    $("#screen-fields").innerHTML = Object.values(fields).map(({ label, unit, aliases }) =>
      `<dt>${esc(label)}${aliases.length ? ` <span class="muted">(${esc(aliases.join(", "))})</span>` : ""}</dt><dd>${esc(unit)}</dd>`).join("");
    $("#screen-field-guide").hidden = false;
    $("#screen-coverage-body").innerHTML = `<ul>${columns.map(key => {
      const { available, gaps } = counts[key];
      const details = Object.entries(gaps).map(([state, count]) => `${count} ${stateText(state)}`).join(", ");
      return `<li>${esc(fields[key].label)} available for ${available} of ${evaluated}${details ? ` (${esc(details)})` : ""}.</li>`;
    }).join("")}</ul>${excluded.map(({ name, reason, source_url }) =>
      `<p class="small">Excluded ${esc(name)}. ${esc(reason)} <a href="${esc(source_url)}" target="_blank" rel="noopener">Issuer evidence</a></p>`).join("")}`;
    coverage.hidden = false;
  }

  async function runScreen() {
    pending?.abort();
    const request = new AbortController();
    pending = request;
    status.textContent = "Running screen…";
    status.className = "";
    output.replaceChildren();
    coverage.hidden = true;
    input.removeAttribute("aria-invalid");
    try {
      const run = { query: input.value, market: market.value };
      const params = new URLSearchParams(run);
      const response = await fetch(`api/screen?${params}`, { signal: request.signal, cache: "no-store" });
      const data = await response.json();
      if (request.signal.aborted) return;
      if (response.ok) {
        renderResults(data);
        workspace?.recordQuery(run.query, run.market, data.build_id);
      } else {
        status.textContent = data.error || "Screen unavailable. Try again.";
        status.className = "notice";
        if (response.status === 400) input.setAttribute("aria-invalid", "true");
      }
    } catch {
      if (request.signal.aborted) return;
      status.textContent = "Screen unavailable. Check that the local Python server is running and try again.";
      status.className = "notice";
    }
  }

  $("#screen-form").addEventListener("submit", event => {
    event.preventDefault();
    runScreen();
  });
  $("#screen-example").addEventListener("click", () => {
    input.value = example;
    market.value = "unlisted";
    runScreen();
  });
  market.addEventListener("change", runScreen);
  document.addEventListener("ipo-ready:catalog", runScreen);
  output.addEventListener("click", e => {
    const button = e.target.closest("button[data-act]");
    if (!button) return;
    const { act, id } = button.dataset;
    if (act === "compare") workspace?.add(id);
    if (act === "shortlist") workspace?.shortlist(id);
    if (act === "allocate") workspace?.requestCompany(id);
  });
  document.addEventListener("ipo-ready:shortlist", () => {
    for (const button of output.querySelectorAll('button[data-act="shortlist"]')) {
      const selected = workspace.has(button.dataset.id);
      button.setAttribute("aria-pressed", selected);
      button.textContent = selected ? "Shortlisted" : "Shortlist";
    }
  });
  IR.chrome();
  runScreen();
})();
