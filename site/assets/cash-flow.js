/* Shared company detail. Render the Python projection into a Page 1 or Page 2 container. */
const renderCashFlow = (target, company, period) => {
  const { esc, fmtNum, openEvidence, stateText } = IR;
  const view = company.cash_flow?.by_period[period];
  if (!view) {
    target.innerHTML = '<p class="cash-coverage">Cash flow is unavailable for this period.</p>';
    return;
  }

  const totals = {
    opening: "Opening cash and equivalents", cfo: "Operating cash flow",
    cfi: "Investing cash flow", cff: "Financing cash flow", other_effects: "Other reconciling effects",
    net_change: "Net change in cash", closing: "Closing cash and equivalents",
  };
  const groups = {
    "Working capital and tax": {
      before_working_capital: "Operating profit before working capital changes",
      receivables: "Trade receivables movement", other_assets: "Other assets movement",
      payables_and_liabilities: "Payables, provisions and other liabilities movement",
      tax_paid: "Income tax paid, net of refunds",
    },
    "Investing activity": { capex: "Cash paid for capital expenditure", net_investment_purchases: "Net purchases or sales of investments" },
    "Financing activity": {
      debt_principal: "Debt principal repayment (excluding leases)", lease_principal: "Lease principal paid",
      lease_interest: "Lease interest paid", overdraft_interest: "Overdraft and other interest paid",
      ...(view.lines.debt_interest ? { debt_interest: "Borrowing interest paid" } : {}),
      share_proceeds: "Proceeds from issue of shares", dividends: "Dividends paid",
    },
    "Closing cash composition": { current_accounts: "Current accounts", settlement_accounts: "Settlement accounts" },
  };
  const issuer = view.origin === "issuer_restated";
  const digits = cell => company.evidence[cell.ev]?.raw_unit === "INR million" ? 3 : undefined;
  const unavailable = {
    included_in_activity_totals: "No separate line", dash: "Dash in source",
    not_in_source: "Unavailable", blank: "Unavailable (blank)", conflict: "Conflicting source rows",
  };
  const present = (cell, label) => {
    const value = cell.value === null ? (unavailable[cell.state] || "Unavailable") : fmtNum(cell.value, digits(cell) || 2);
    const ev = company.evidence[cell.ev];
    if (!ev) return `<span class="muted">${esc(value)}</span>`;
    return `<button type="button" class="cash-evidence ${cell.value === null ? "muted" : "num"}" data-evidence="${esc(cell.ev)}"
      data-label="${esc(label)}" data-value="${esc(value)}" aria-label="${esc(`${label}: ${value}, open evidence`)}">${esc(value)}</button>`;
  };
  const rows = labels => `<dl class="cash-lines">${Object.entries(labels).map(([key, label]) =>
    `<div data-line="${key}"><dt>${esc(label)}</dt><dd>${present(view.lines[key], label)}</dd></div>`).join("")}</dl>`;
  const { state, activity_residual: activity, balance_residual: balance } = view.reconciliation;
  const messages = {
    reconciled: view.effects_after_net
      ? "Reconciled. Activities sum to the reported movement. Opening cash, movement and the separate FX effect sum to closing cash."
      : "Reconciled. Activities sum to the reported movement and opening cash plus movement equals closing cash.",
    rounding_difference: `Reported amounts differ at displayed precision. Activity residual ${activity} and closing balance residual ${balance} (₹ crore).`,
    partial: "Partial disclosure. A complete reconciliation requires the missing cash-flow lines.",
    conflict: `Reconciliation differs. Activity residual ${activity} and closing balance residual ${balance} (₹ crore).`,
  };
  const net = view.lines.net_change.value;
  const opening = view.lines.opening.value;
  const closing = view.lines.closing.value;
  const effect = view.effects_after_net ? Number(view.lines.other_effects.value) : 0;
  const signed = value => `${Number(value) < 0 ? "−" : "+"} ${fmtNum(Math.abs(Number(value)), 3)}`;
  const formula = state === "reconciled"
    ? ` <span class="num">${fmtNum(opening, 3)} ${signed(net)}${effect ? ` ${signed(effect)}` : ""} = ${fmtNum(closing, 3)}</span>`
    : "";
  const comparison = view.provider_comparison;
  const comparisonRows = comparison && Object.entries(comparison.lines).map(([key, cell]) => {
    const delta = comparison.differences[key];
    const difference = delta ? fmtNum(delta.issuer_minus_provider, 3) : "Unavailable";
    return `<tr><th scope="row">${totals[key]}</th><td class="num">${present(view.lines[key], `Issuer ${totals[key]}`)}</td>
      <td class="num">${present(cell, `WWIPL ${totals[key]}`)}</td><td class="num ${delta?.state === "differs" ? "cash-difference" : ""}">${difference}</td></tr>`;
  }).join("");
  const basis = issuer ? "Restated · IGX and employee share trust" : `${view.provider_name || "WWIPL"} · ${view.basis} basis`;
  target.innerHTML = `
    <div class="cash-heading">
      <h3>Cash flow <span>· ${esc(period)}</span></h3><span class="small muted">₹ crore</span>
    </div>
    <p class="cash-basis small muted">${esc(basis)}${issuer ? " · Ind AS 7 indirect method" : ""}</p>
    ${rows(totals)}
    <p class="cash-coverage ${state}" data-reconciliation="${state}">${esc(messages[state])}${formula}</p>
    ${issuer ? '<p class="small cash-context">Settlement accounts are included in closing cash. Review the grouped liabilities and settlement balance before treating operating inflows as recurring.</p>' : ""}
    ${view.note ? `<p class="small cash-context">${esc(view.note)}</p>` : ""}
    <details class="cash-detail">
      <summary>Cash flow details</summary>
      ${Object.entries(groups).map(([label, items]) => `<h4>${esc(label)}</h4>${rows(items)}`).join("")}
    </details>
    ${comparison ? `<details class="cash-detail"><summary>Compare with WWIPL</summary>
      <p class="small muted">WWIPL reporting basis is unspecified for IGX. Differences are issuer minus WWIPL in ₹ crore.</p>
      <div class="tbl-wrap"><table class="data cash-compare"><thead><tr><th scope="col">Activity</th>
      <th scope="col">Issuer</th><th scope="col">WWIPL</th><th scope="col">Difference</th></tr></thead>
      <tbody>${comparisonRows}</tbody></table></div>
    </details>` : ""}
  `;
  target.querySelectorAll("[data-evidence]").forEach(button => button.addEventListener("click", () => {
    const { evidence: id, label, value } = button.dataset;
    openEvidence({ title: `${label} · ${period}`, value: esc(value), evIds: [id], evidence: company.evidence,
      extra: issuer && company.evidence[id]?.page === 7
        ? '<p class="small">Physical page 7. The filing reports ₹ million. Displayed values are in ₹ crore (÷10).</p>'
        : "" });
  }));
};
