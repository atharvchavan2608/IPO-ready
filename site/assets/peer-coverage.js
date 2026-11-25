/* Render the exact period, basis and evidence selected by the Python comparison build. */
(async () => {
  const { $, esc, load, fmtDate, fmtNum, fmtPct, fmtX, stateText, openEvidence } = IR;
  const domainSelect = $("#peer-domain");
  const companySelect = $("#peer-company");
  const status = $("#peer-status");
  const output = $("#peer-output");
  const comparison = $("#peer-comparison");
  const explanations = {
    different_business_model: "Different business model",
    capture_unavailable: "Annual capture unavailable",
    issuer_period_unavailable: "Issuer annual period unavailable",
    issuer_basis_unverified: "Issuer reporting basis unverified",
    issuer_inputs_unavailable: "Verified issuer revenue or profit is unavailable",
    incompatible_reporting_basis: "Compatible reporting basis unavailable",
    no_same_annual_period: "Different annual period",
    annual_profit_unavailable: "Annual profit unavailable",
  };
  const labels = { eligible: "Operating comparison", context_only: "Industry context", excluded: "Unavailable" };
  const rows = [
    { id: "revenue_ops", label: "Operating revenue", unit: "₹ cr", fmt: fmtNum, fields: ["revenue_ops"] },
    { id: "pat", label: "Profit after tax", unit: "₹ cr", fmt: fmtNum, fields: ["pat"] },
    { id: "pat_to_revenue_pct", label: "PAT / operating revenue", unit: "%", fmt: fmtPct, fields: ["pat", "revenue_ops"] },
    { id: "other_income_share_pct", label: "Other-income share", unit: "%", fmt: fmtPct,
      fields: ["other_income", "other_gains", "job_work_revenue", "revenue_ops"] },
    { id: "pe", label: "Annual P/E", unit: "×", fmt: fmtX, fields: ["eps"] },
  ];
  let snapshot;
  let cohort;
  let columns = [];
  try {
    snapshot = await load("peers.json");
    if (!snapshot.domains?.length) throw new Error("Comparison data needs rebuild");
  } catch {
    status.textContent = "Peer comparison data is unavailable. Rebuild the local data to load the latest checks.";
    return;
  }

  function evidenceLink(url, label) {
    if (!url || !/^https?:\/\//i.test(url)) return "";
    return `<a href="${esc(url)}" target="_blank" rel="noopener">${esc(label)}</a>`;
  }

  function basisText(basis) {
    if (basis === "issuer_and_esos_trust") return "Restated issuer + share trust";
    if (basis === "standalone" || basis === "consolidated") return `${basis[0].toUpperCase()}${basis.slice(1)}`;
    return "Basis unverified";
  }

  function renderCoverage() {
    const refMeta = [cohort.period_end ? `Year ended ${fmtDate(cohort.period_end)}` : "Annual period unavailable",
      basisText(cohort.basis), cohort.market_status].filter(Boolean);
    const scope = cohort.scope
      ? `<p class="small peer-scope">${esc(cohort.scope.note)} ${evidenceLink(cohort.scope.url, "Issuer scope")} · ${evidenceLink(cohort.scope.relationship_url, "IEX relationship")}</p>`
      : cohort.annual_source ? `<p class="small peer-scope">${evidenceLink(cohort.annual_source.url, "Issuer consolidated P&L")}</p>` : "";
    const fallbacks = snapshot.fallbacks.filter(item => item.used_run && cohort.peers.some(peer => item.item === `${peer.symbol}-${peer.basis}`));
    const fallback = fallbacks.length
      ? `<p class="notice">Retained capture fallback for ${esc(fallbacks.map(item => item.item).join(", "))}.</p>` : "";
    output.innerHTML = `
      <div class="crumbs">${cohort.hierarchy.map(part => `<span>${esc(part)}</span>`).join("")}</div>
      <p class="small muted peer-scope">${esc(refMeta.join(" · "))}</p>${scope}${fallback}`;
    const eligible = cohort.peers.filter(peer => peer.status === "eligible");
    status.textContent = !cohort.peers.length ? "No listed candidates are available for this business."
      : eligible.length ? `${eligible.length} of ${cohort.peers.length} candidates cleared the operating comparison checks.`
      : "No candidates cleared the operating comparison checks.";
    columns = [cohort, ...eligible];
  }

  function renderCandidates() {
    if (!cohort.peers.length) return "";
    return `<details class="peer-support"><summary>Candidate fit and exclusions (${cohort.peers.length})</summary>
      <ul class="peer-list">${cohort.peers.map(peer => {
        const meta = [peer.period_end && fmtDate(peer.period_end), peer.basis && `${basisText(peer.basis).toLowerCase()} basis`,
          peer.source?.retrieved_at && `captured ${fmtDate(peer.source.retrieved_at)}`].filter(Boolean);
        const source = peer.source && evidenceLink(
          peer.source.url + (peer.source.provider === "Screener.in" ? "#profit-loss" : ""), "Annual source");
        const reason = peer.reasons.map(key => explanations[key]).filter(Boolean).join(" · ");
        return `<li class="peer-item" data-symbol="${esc(peer.symbol)}">
          <header><strong>${esc(peer.name)}</strong><span class="badge ${peer.status === "eligible" ? "ok" : "warn"}">${labels[peer.status]}</span></header>
          <p class="small">${esc(peer.rationale)}</p>
          ${reason ? `<p class="small scope-gaps">${esc(reason)}</p>` : ""}
          ${meta.length ? `<p class="tiny muted">${esc(meta.join(" · "))}${source ? ` · ${source}` : ""}</p>` : ""}</li>`;
      }).join("")}</ul></details>`;
  }

  function cell(row, company) {
    if (row.id === "pe") return company.pe;
    if (company.metrics[row.id]) return company.metrics[row.id];
    if (company === cohort && !cohort.comparison_basis) {
      return { state: "issuer_basis_unverified", value: null, note: "The issuer operating statement requires a verified annual basis." };
    }
    return company.facts[row.id];
  }

  function renderTable() {
    if (!cohort.comparison_basis) return `<p class="notice info">The annual operating comparison needs verified issuer period, scope and earnings inputs. Use the company dashboard to inspect the available statements.</p>`;
    return `${columns.length > 2 ? '<p class="peer-scroll-hint tiny muted">Scroll the table to see all peers.</p>' : ""}
      <div class="tbl-wrap peer-table" role="region" aria-label="Annual peer metrics" tabindex="0">
      <table class="data"><thead><tr><th scope="col">Metric</th>${columns.map(company => `<th scope="col">
        ${esc(company.short || company.symbol)}<small>${esc(basisText(company.basis))}</small></th>`).join("")}</tr></thead>
      <tbody>${rows.map((row, i) => `<tr><th scope="row">${esc(row.label)}${row.unit === "₹ cr" ? " <small>₹ crore</small>" : ""}</th>
        ${columns.map((company, j) => {
          const metric = cell(row, company);
          const heading = `${company.name} · ${row.label} evidence`;
          if (metric?.value == null) {
            const text = metric?.state === "negative_base" ? "Loss-making" : "Unavailable";
            return `<td>${metric ? `<button class="peer-cell muted" type="button" data-row="${i}" data-col="${j}" aria-label="${esc(heading)}">${text}</button>`
              : `<span class="state">${text}</span>`}</td>`;
          }
          return `<td><button class="peer-cell" type="button" data-row="${i}" data-col="${j}" aria-label="${esc(heading + " " + row.fmt(metric.value))}">${esc(row.fmt(metric.value))}</button></td>`;
        }).join("")}</tr>`).join("")}</tbody></table></div>
      <p class="small muted">Select a value to inspect its inputs. P/E uses reported annual EPS and dated prices. The unlisted price is an indicative dealer quote.</p>`;
  }

  function renderDrivers() {
    const { benchmark, percentage_point_differences: diff } = cohort.drivers;
    function statement(key, label) {
      const change = diff?.[key];
      if (change == null) return "";
      const delta = Number(change);
      return delta === 0 ? `${label} matched ${benchmark}.`
        : `${label} was ${fmtNum(Math.abs(delta))} percentage points ${delta > 0 ? "above" : "below"} ${benchmark}.`;
    }
    const notes = [statement("pat_to_revenue_pct", "PAT / operating revenue"),
      statement("other_income_share_pct", "Other-income share"), cohort.operating_note].filter(Boolean);
    return notes.length ? `<p class="small peer-driver">${esc(notes.join(" "))}</p>` : "";
  }

  function renderUpdates() {
    const entries = [cohort, ...cohort.peers].flatMap(company => (company.updates || []).map(note => ({ ...note, company: company.short || company.symbol })));
    entries.sort((a, b) => b.date.localeCompare(a.date));
    const reviewed = entries.length ? `<ul class="peer-updates">${entries.map(note => `<li>
      <div class="tiny muted">${esc(note.company)} · ${esc(note.kind)} · ${fmtDate(note.date)} · ${esc(note.publisher)}</div>
      <strong>${evidenceLink(note.evidence.url, note.title)}</strong><p class="small">${esc(note.summary)}</p>
      <div class="tiny muted">${esc(note.evidence.anchor)} · captured ${fmtDate(note.evidence.retrieved_at)}</div></li>`).join("")}</ul>`
      : '<p class="small muted">No reviewed company disclosure or article in this snapshot.</p>';
    const headlines = (cohort.news || []).filter(item => item.date && /^https?:\/\//i.test(item.link));
    return `<details class="peer-support"${entries.length ? " open" : ""}><summary>Company plans and news</summary>${reviewed}
      ${headlines.length ? `<details><summary>Additional captured headlines</summary>
        <ul class="peer-updates">${headlines.map(item => `<li>${evidenceLink(item.link, item.title)}
          <div class="tiny muted">${fmtDate(item.date)} · ${esc(item.publisher)} · headline only</div></li>`).join("")}</ul>
      </details>` : ""}</details>`;
  }

  function rowEvidence(company, field) {
    const fact = company.facts[field];
    if (!fact) return null;
    if (fact.evidence) return { ...fact.evidence, period: company.period_end, basis: basisText(fact.basis) };
    const source = company.source;
    if (!source) return null;
    return { ...fact, source: source.provider, url: source.url + (fact.anchor?.section || ""),
      retrieved_at: source.retrieved_at, capture_run: source.run, file: source.file, sha256: source.sha256,
      period: company.period_end, basis: basisText(fact.basis) };
  }

  comparison.addEventListener("click", event => {
    const button = event.target.closest(".peer-cell");
    if (!button) return;
    const row = rows[button.dataset.row], company = columns[button.dataset.col], metric = cell(row, company);
    const evidence = row.fields.map(field => rowEvidence(company, field)).filter(Boolean);
    const price = company.pe.price;
    let extra = "";
    if (row.id === "pe" && price) {
      evidence.push({ ...price.evidence, source: price.kind, raw_label: "Price input",
        raw_text: price.value, raw_unit: "INR", sha256: price.evidence.sha256 || price.evidence.original_sha256 });
      extra = `<p class="small">${esc(price.kind)} · ${fmtDate(price.date)}</p>`;
    }
    const keys = evidence.map((_, i) => i);
    openEvidence({ title: `${company.name} · ${row.label}`,
      value: metric?.value != null ? row.fmt(metric.value) : esc(stateText(metric?.state) || "Unavailable"),
      metric: metric?.formula ? metric : null, evIds: keys, evidence, extra });
  });

  const current = new URL(location.href);
  let selected = snapshot.cohorts[current.searchParams.get("company")]?.id || snapshot.default;
  let domain = snapshot.domains.find(group => group.companies.includes(selected));
  const options = (entries, key, label) => entries.map(item =>
    `<option value="${esc(item[key])}">${esc(item[label])}</option>`).join("");
  domainSelect.innerHTML = options(snapshot.domains, "id", "label");
  domainSelect.value = domain.id;
  function populateCompanies() {
    companySelect.innerHTML = options(domain.companies.map(id => snapshot.cohorts[id]), "id", "name");
    companySelect.value = selected;
  }
  function render() {
    cohort = snapshot.cohorts[selected];
    const dashboard = $("#peer-dashboard");
    dashboard.href = `index.html?company=${encodeURIComponent(selected)}`;
    dashboard.hidden = false;
    renderCoverage();
    comparison.innerHTML = renderTable() + renderDrivers();
    $("#peer-context").innerHTML = renderCandidates() + renderUpdates();
  }
  function selectCompany(id) {
    selected = id;
    current.searchParams.set("company", selected);
    history.replaceState(null, "", current);
    render();
  }
  domainSelect.addEventListener("change", () => {
    domain = snapshot.domains.find(group => group.id === domainSelect.value);
    selectCompany(domain.companies[0]);
    populateCompanies();
  });
  companySelect.addEventListener("change", () => selectCompany(companySelect.value));
  populateCompanies();
  domainSelect.disabled = companySelect.disabled = false;
  render();
})();
