/* Company history from the same scoped observations used by the dashboard. */
const CompanyCharts = (() => {
  const { esc, n, fmtNum, fmtDate } = IR;
  const catalogue = [
    { id: "revenue-growth", title: "Revenue growth", unit: "%", ratio: "revenue_growth", primary: true },
    { id: "share-price", title: "Share price", unit: "₹ per share", primary: true },
    { id: "operating-revenue", title: "Operating revenue", unit: "₹ crore", fields: [["revenue_ops"]], primary: true },
    { id: "total-income", title: "Total income", unit: "₹ crore", fields: [["total_income"]] },
    { id: "profit", title: "Profit after tax", unit: "₹ crore", fields: [["pat"]] },
    { id: "margin", title: "Profit / operating revenue", unit: "%", ratio: "net_profit_ratio" },
    { id: "cash-vs-profit", title: "Cash vs profit", unit: "₹ crore", fields: [["cfo", "Operating cash flow"], ["pat", "Profit after tax"]] },
    { id: "cash-movement", title: "Cash movement", unit: "₹ crore" },
    { id: "liquidity", title: "Liquidity", unit: "₹ crore", fields: [["current_assets", "Current assets"], ["current_liabilities", "Current liabilities"]] },
  ];
  function annual(company, period, definition) {
    const { ratio, fields, title, unit } = definition;
    const basis = ratio ? company.ratios?.by_period?.[period]?.[ratio]?.basis : company.analysis?.[period]?.basis || company.basis;
    const periods = company.periods.filter(p => p !== undefined && p <= period && !p.endsWith("?") &&
      (p.startsWith("FY") === period?.startsWith("FY"))).slice(-6);
    const series = (fields || [[ratio]]).map(([key, label = title]) => ({
      label, values: periods.map(p => {
        if (ratio) {
          const metric = company.ratios?.by_period?.[p]?.[key];
          return metric?.basis === basis && metric?.state === "ok" ? n(metric.value) : null;
        }
        const analysis = company.analysis?.[p];
        if ((analysis?.basis || company.basis) !== basis) return null;
        return n(analysis ? analysis.facts[key]?.value : company.fields[key]?.by_period?.[p]?.value);
      }),
    }));
    const basisLabel = { issuer_and_esos_trust: "Restated issuer and employee share trust", unspecified: "Provider reporting basis unspecified" }[basis] || basis;
    return { title, unit, labels: periods.map(p => p.replace("PE:", "")), series, note: basisLabel,
      breaks: periods.map((p, i) => i > 0 && p.startsWith("FY") && Number(p.slice(2)) - Number(periods[i - 1].slice(2)) !== 1) };
  }
  function price(company, market) {
    const stock = market?.stocks?.find(s => company.identity?.symbol && s.symbol === company.identity.symbol);
    const history = (company.price_history?.length ? company.price_history : stock?.series_1m || [])
      .filter(item => Number.isFinite(n(item.close))).slice(-31);
    const quote = company.quote;
    const points = history.length ? history : quote.price_inr != null && quote.as_of
      ? [{ date: quote.as_of, close: quote.price_inr }] : [];
    return { title: "Share price", unit: "₹ per share", labels: points.map(p => fmtDate(p.date)),
      series: [{ label: "Share price", values: points.map(p => n(p.close)) }],
      note: history.length > 1 ? "Dated NSE end-of-day prices" :
        points.length ? company.identity?.listing === "listed" ? "One dated NSE close available" : "One dated indicative dealer quote available"
          : "No dated price available" };
  }
  function graph(data) {
    const { title, unit, labels, series, note, breaks = [] } = data;
    const values = series.flatMap(s => s.values).filter(Number.isFinite);
    const fmt = value => fmtNum(value, Math.abs(value) >= 100 ? 0 : 2);
    const footer = note ? `<p class="tiny muted chart-caption">${esc(note)}</p>` : "";
    const heading = `<h3>${esc(title)}</h3><p class="small muted chart-unit">${esc(unit)}</p>`;
    if (!values.length) {
      return `${heading}<p class="chart-empty small muted">History is unavailable for this selection.</p>${footer}`;
    }
    const chartMin = Math.min(...values), chartMax = Math.max(...values);
    const padding = (chartMax - chartMin || Math.abs(chartMax) || 1) * 0.08;
    const lo = chartMin - padding, hi = chartMax + padding;
    const margin = 64, right = 445, width = 462, height = 157, top = 16, bottom = 126;
    const x = (i) => labels.length === 1 ? (margin + right) / 2 : margin + (right - margin) * i / (labels.length - 1);
    const y = value => bottom - (value - lo) / (hi - lo) * (bottom - top);
    const ticks = [chartMin, (chartMin + chartMax) / 2, chartMax].filter((v, i, all) => i === 0 || v !== all[i - 1]);
    const colors = ["var(--plot-main, #286658)", "var(--plot-contrast, #9a591d)"];
    const paths = series.map(({ values, label }, j) => {
      const color = colors[j % colors.length];
      const d = values.map((value, i) => Number.isFinite(value)
        ? `${i === 0 || breaks[i] || !Number.isFinite(values[i - 1]) ? "M" : "L"}${x(i).toFixed(1)} ${y(value).toFixed(1)}` : "").join(" ");
      const dots = values.map((value, i) => Number.isFinite(value) && (labels.length <= 12 || i === labels.length - 1)
        ? `<circle cx="${x(i)}" cy="${y(value)}" r="3" fill="${color}"><title>${esc(label)} · ${esc(labels[i])} · ${fmt(value)} ${esc(unit)}</title></circle>`
        : "").join("");
      return `<path class="history-line" d="${d}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linejoin="round"/>${dots}`;
    }).join("");
    const tickLabels = [0, Math.floor((labels.length - 1) / 2), labels.length - 1].filter((v, i, all) => i === 0 || v !== all[i - 1]);
    const noteGaps = series.some(s => s.values.some(v => v === null)) || breaks.some(Boolean);
    const accessibility = labels.map((p, i) => `<li>${esc(p)} · ${series.map(s => `${esc(s.label)} ${Number.isFinite(s.values[i]) ? fmt(s.values[i]) : "Unavailable"}`).join(" · ")}</li>`).join("");
    return `${heading}<svg class="chart company-line" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(title)}, ${esc(unit)}">
      ${ticks.map(t => `<line x1="${margin}" x2="${right}" y1="${y(t)}" y2="${y(t)}" stroke="var(--line)"/><text x="${margin - 7}" y="${y(t) + 4}" text-anchor="end">${fmt(t)}</text>`).join("")}
      ${tickLabels.map(i => `<text x="${x(i)}" y="149" text-anchor="${tickLabels.length === 1 ? "middle" : i === 0 ? "start" : i === labels.length - 1 ? "end" : "middle"}">${esc(labels[i])}</text>`).join("")}
      ${paths}</svg>${series.length > 1 ? `<p class="small chart-key">${series.map((s, j) => `<span style="--chart-key:${colors[j] || colors[0]}">${esc(s.label)}</span>`).join("")}</p>` : ""}
      ${noteGaps ? '<p class="tiny muted chart-caption">Gaps indicate unavailable or non-comparable periods.</p>' : ""}${footer}
      <details class="chart-values"><summary>Chart values</summary><ul>${accessibility}</ul></details>`;
  }
  return { catalogue, annual, price, graph };
})();
