/* Shared helpers: data loading, formatting, SVG charts, evidence drawer, ticker, nav. */
const IR = (() => {
  const DATA = "data/current/";
  const cache = {};
  async function load(path, refresh = false) {
    if (refresh) delete cache[path];
    if (!cache[path]) {
      cache[path] = fetch(DATA + path, { cache: "no-store" }).then(r => {
        if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
        return r.json().then(value => r.headers.get("X-IPO-Ready-Data") === "retained-build"
          ? { ...value, retained_build: true } : value);
      });
    }
    return cache[path];
  }
  const $ = (sel, el = document) => el.querySelector(sel);
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const n = v => (v === null || v === undefined || v === "" ? null : Number(v));

  function fmtNum(v, digits = 2) {
    const x = n(v);
    if (x === null || Number.isNaN(x)) return "—";
    return x.toLocaleString("en-IN", { minimumFractionDigits: digits, maximumFractionDigits: digits });
  }
  function fmtCr(v, digits = 2) { const x = n(v); return x === null ? "—" : `₹${fmtNum(x, Math.abs(x) >= 1000 ? 0 : digits)} cr`; }
  function fmtInr(v, digits = 2) { const x = n(v); return x === null ? "—" : `₹${fmtNum(x, digits)}`; }
  function fmtPct(v, digits = 1) { const x = n(v); return x === null ? "—" : `${fmtNum(x, digits)}%`; }
  function fmtX(v, digits = 2) { const x = n(v); return x === null ? "—" : `${fmtNum(x, digits)}×`; }
  function ratioDisplay(value, unit) {
    if (value == null) return "Unavailable";
    if (unit === "%") return fmtPct(value, 2);
    if (unit === "×") return fmtX(value);
    if (unit === "₹/share") return fmtInr(value);
    return `${fmtNum(value)} ${unit}`;
  }
  function fmtDate(iso) {
    if (!iso) return "—";
    const d = new Date(iso.length <= 10 ? iso + "T00:00:00" : iso);
    return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
  }
  function fmtDateTime(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleString("en-IN", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit", timeZone: "Asia/Kolkata" }) + " IST";
  }
  function ageDays(iso) { return iso ? Math.floor((Date.now() - new Date(iso).getTime()) / 864e5) : null; }

  const STATE_TEXT = {
    ok: "", reported: "", derived: "derived from listed lines",
    missing_input: "not available", not_in_source: "not in source", zero_denominator: "zero denominator",
    negative_base: "not meaningful (negative base)", inapplicable: "not applicable", explicit_zero: "reported as zero",
    dash: "shown as '–' in source", suspect_quote: "quote unreliable", blank: "blank in source", provider_error: "provider error (#DIV/0!)", unavailable: "unavailable",
    withheld_review: "Withheld pending review",
  };
  const stateText = s => STATE_TEXT[s] ?? s?.replace(/_/g, " ") ?? "";

  /* ---------- SVG charts ---------- */
  const PALETTE = ["#13203b", "#d97a14", "#3c7d8c", "#9a6200", "#7a3fb0", "#18794e"];
  function niceTicks(min, max, count = 4) {
    if (min === max) { max = min + 1; }
    const span = max - min, step0 = span / count, mag = 10 ** Math.floor(Math.log10(step0));
    const step = [1, 2, 2.5, 5, 10].map(m => m * mag).find(s => s >= step0) || step0;
    const lo = Math.floor(min / step) * step, hi = Math.ceil(max / step) * step, out = [];
    for (let v = lo; v <= hi + step / 2; v += step) out.push(+v.toFixed(10));
    return out;
  }
  /** Grouped bars (categories x series) with optional line series on the same axis. */
  function barChart(el, { categories, series, height = 230, fmt = v => fmtNum(v, 0), onClick }) {
    const W = Math.max(300, Math.round(el.clientWidth || 640)), H = height, pad = { l: 52, r: 10, t: 12, b: 28 };
    const vals = series.flatMap(s => s.values).filter(v => v !== null && v !== undefined);
    if (!vals.length) { el.innerHTML = `<p class="muted">No data for this selection.</p>`; return; }
    const ticks = niceTicks(Math.min(0, ...vals), Math.max(0, ...vals));
    const y0 = ticks[0], y1 = ticks[ticks.length - 1];
    const y = v => pad.t + (H - pad.t - pad.b) * (1 - (v - y0) / (y1 - y0));
    const bw = (W - pad.l - pad.r) / categories.length, gap = 0.28, inner = bw * (1 - gap) / series.length;
    let g = ticks.map(t => `<line x1="${pad.l}" x2="${W - pad.r}" y1="${y(t)}" y2="${y(t)}" stroke="${t === 0 ? "#b9b2a3" : "#ece6da"}"/><text x="${pad.l - 6}" y="${y(t) + 4}" text-anchor="end">${esc(fmt(t))}</text>`).join("");
    categories.forEach((c, i) => {
      g += `<text x="${pad.l + bw * i + bw / 2}" y="${H - 8}" text-anchor="middle">${esc(c)}</text>`;
      series.forEach((s, j) => {
        const v = s.values[i];
        const x = pad.l + bw * i + bw * gap / 2 + inner * j;
        if (v === null || v === undefined) {
          g += `<text x="${x + inner / 2}" y="${y(0) - 4}" text-anchor="middle" style="font-size:9px">n/a</text>`;
          return;
        }
        const top = Math.min(y(v), y(0)), h = Math.max(1, Math.abs(y(v) - y(0)));
        g += `<rect data-i="${i}" data-j="${j}" x="${x + 1}" y="${top}" width="${Math.max(2, inner - 2)}" height="${h}" rx="2" fill="${s.color || PALETTE[j]}" opacity="${s.opacity ?? 1}" style="cursor:${onClick ? "pointer" : "default"}"><title>${esc(s.name)} ${esc(c)}: ${esc(fmt(v))}</title></rect>`;
      });
    });
    el.innerHTML = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(series.map(s => s.name).join(", "))} by period">${g}</svg>` +
      `<div class="legend">${series.map((s, j) => `<span><i style="background:${s.color || PALETTE[j]}"></i>${esc(s.name)}</span>`).join("")}</div>`;
    if (onClick) el.querySelectorAll("rect[data-i]").forEach(r => r.addEventListener("click", () => onClick(+r.dataset.i, +r.dataset.j)));
  }
  function lineChart(el, { points, height = 120, color = PALETTE[0], fmt = v => fmtNum(v, 0), xLabel = p => p.date, area = true }) {
    const W = Math.max(240, Math.round(el.clientWidth || 320)), H = height, pad = { l: 4, r: 4, t: 10, b: 18 };
    const vals = points.map(p => p.close).filter(v => v !== null);
    if (vals.length < 2) { el.innerHTML = `<p class="muted small">Not enough points for a chart.</p>`; return; }
    const lo = Math.min(...vals), hi = Math.max(...vals), span = hi - lo || 1;
    const x = i => pad.l + (W - pad.l - pad.r) * i / (points.length - 1);
    const y = v => pad.t + (H - pad.t - pad.b) * (1 - (v - lo) / span);
    const d = points.map((p, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(p.close).toFixed(1)}`).join("");
    const up = vals[vals.length - 1] >= vals[0];
    const col = color === "auto" ? (up ? "#18794e" : "#b4362f") : color;
    el.innerHTML = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="price line">
      ${area ? `<path d="${d}L${x(points.length - 1)},${H - pad.b}L${x(0)},${H - pad.b}Z" fill="${col}" opacity=".08"/>` : ""}
      <path d="${d}" fill="none" stroke="${col}" stroke-width="1.6"/>
      <text x="${pad.l}" y="${H - 4}">${esc(xLabel(points[0]))}</text><text x="${W - pad.r}" y="${H - 4}" text-anchor="end">${esc(xLabel(points[points.length - 1]))}</text>
      <text x="${W - pad.r}" y="${pad.t}" text-anchor="end">${esc(fmt(hi))}</text><text x="${W - pad.r}" y="${H - pad.b - 3}" text-anchor="end">${esc(fmt(lo))}</text>
    </svg>`;
  }
  function spark(points, w = 70, h = 22) {
    const vals = (points || []).map(p => p.close).filter(v => v !== null);
    if (vals.length < 2) return "";
    const lo = Math.min(...vals), hi = Math.max(...vals), span = hi - lo || 1;
    const d = vals.map((v, i) => `${i ? "L" : "M"}${(w * i / (vals.length - 1)).toFixed(1)},${(h - 2 - (h - 4) * (v - lo) / span).toFixed(1)}`).join("");
    const col = vals[vals.length - 1] >= vals[0] ? "#18794e" : "#b4362f";
    return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" aria-hidden="true"><path d="${d}" fill="none" stroke="${col}" stroke-width="1.4"/></svg>`;
  }

  /* ---------- evidence drawer ---------- */
  function drawer() {
    let d = $("#drawer");
    if (!d) {
      d = document.createElement("dialog");
      d.id = "drawer"; d.className = "drawer";
      d.setAttribute("aria-labelledby", "drawer-title");
      d.innerHTML = `<div class="drawer-head"><h2 id="drawer-title"></h2><button class="btn ghost" id="drawer-close" aria-label="Close">Close</button></div><div class="drawer-body" id="drawer-body"></div>`;
      document.body.appendChild(d);
      d.querySelector("#drawer-close").addEventListener("click", () => d.close());
      d.addEventListener("click", e => { if (e.target === d) d.close(); });
    }
    return d;
  }
  function evidenceBlock(e) {
    if (!e) return `<div class="ev-block muted">Evidence record not found.</div>`;
    const a = e.anchor;
    const anchor = typeof a === "string" ? a : a?.section ? `${a.section} · ${a.row} · column ${a.column}`
      : a?.symbol ? `${a.symbol} · ${a.field}`
      : a?.table_index != null ? `table ${a.table_index}, row ${a.row_index}${a.heading ? ` · “${a.heading}”` : ""}`
      : e.page ? `PDF page ${e.page}` : "";
    const comps = e.components ? `<details><summary>${e.components.length} component lines</summary><table class="data">${e.components.map(c => `<tr><td>${esc(c.label)}</td><td class="num">${fmtNum(c.value)}</td></tr>`).join("")}</table></details>` : "";
    return `<div class="ev-block"><dl class="kv">
      <dt>Source</dt><dd>${esc(e.source)}</dd>
      <dt>URL</dt><dd><a href="${esc(e.url)}" target="_blank" rel="noopener">${esc(e.url)}</a></dd>
      ${e.raw_label ? `<dt>Reported label</dt><dd>${esc(e.raw_label)}</dd>` : ""}
      ${e.raw_text !== undefined && e.raw_text !== null ? `<dt>Reported text</dt><dd class="num">${esc(e.raw_text)} ${esc(e.raw_unit || "")}</dd>` : ""}
      ${e.period ? `<dt>Period</dt><dd>${esc(e.period)} (column “${esc(e.period_label)}”)</dd>` : ""}
      ${e.basis ? `<dt>Basis</dt><dd>${esc(e.basis)}</dd>` : ""}
      ${anchor ? `<dt>Location</dt><dd>${esc(anchor)}</dd>` : ""}
      ${e.source_date ? `<dt>Source date</dt><dd>${fmtDate(e.source_date)}</dd>` : ""}
      <dt>Retrieved</dt><dd>${fmtDateTime(e.retrieved_at)}${e.capture_run ? ` · run ${esc(e.capture_run)}` : ""}</dd>
      <dt>Capture</dt><dd>${e.file ? `<code>${esc(e.file)}</code> · ` : ""}SHA-256 ${esc((e.sha256 || "").slice(0, 16))}…</dd>
      ${e.derived ? `<dt>Note</dt><dd>Derived in Python from the source components.</dd>` : ""}
    </dl>${comps}</div>`;
  }
  function openEvidence({ title, value, metric, evIds = [], evidence = {}, extra = "" }) {
    const d = drawer();
    $("#drawer-title", d).textContent = title;
    let html = value !== undefined ? `<p style="font-size:22px;font-weight:700;margin:0 0 6px" class="num">${value}</p>` : "";
    if (metric) {
      html += `<p class="small muted">${metric.state && metric.state !== "ok" ? `<b>State:</b> ${esc(stateText(metric.state))}. ` : ""}${esc(metric.note || "")}</p>`;
      if (metric.formula) html += `<div class="formula">${esc(metric.formula)}</div>`;
      if (metric.inputs) html += `<dl class="kv">${Object.entries(metric.inputs).map(([k, v]) => `<dt>${esc(k.replace(/_/g, " "))}</dt><dd class="num">${v === null ? "<i>missing</i>" : esc(v)}</dd>`).join("")}</dl>`;
      html += `<p class="tiny muted">Computed in Python (ipo_ready/metrics.py, Decimal arithmetic) during the pipeline build.</p>`;
    }
    html += extra;
    if (evIds.length) html += `<h3 style="font-size:12px;text-transform:uppercase;color:var(--muted)">Evidence (${evIds.length})</h3>` + evIds.map(id => evidenceBlock(evidence[id])).join("");
    $("#drawer-body", d).innerHTML = html;
    d.showModal();
  }

  /* ---------- ticker + build stamp ---------- */
  function mountTicker(ticker, items) {
    const figures = items.join("");
    ticker.classList.add("ticker-ready");
    ticker.innerHTML = `<div class="ticker-window" id="ticker-figures" role="region" aria-label="Market figures" tabindex="0">
      <div class="ticker-track">
        <div class="ticker-inner">${figures}</div>
        <div class="ticker-inner ticker-copy" aria-hidden="true">${figures}</div>
      </div>
    </div>
    <button class="ticker-control" type="button" aria-controls="ticker-figures"></button>`;

    const viewport = $(".ticker-window", ticker);
    const content = $(".ticker-inner", ticker);
    const control = $(".ticker-control", ticker);
    const reduced = matchMedia("(prefers-reduced-motion: reduce)");
    const storageKey = "ipo-market-ticker-paused";
    let paused = false;
    try { paused = localStorage.getItem(storageKey) === "true"; } catch {}

    function update() {
      const stopped = paused || reduced.matches;
      const wasMoving = ticker.dataset.moving === "true";
      const offset = wasMoving
        ? viewport.getBoundingClientRect().left - content.getBoundingClientRect().left
        : 0;
      if (!stopped && !wasMoving) {
        const duration = Number.parseFloat(getComputedStyle(ticker).getPropertyValue("--ticker-duration"));
        const elapsed = viewport.scrollLeft / Math.max(1, content.offsetWidth) * duration;
        ticker.style.setProperty("--ticker-delay", `-${elapsed}s`);
      }
      ticker.dataset.moving = String(!stopped);
      if (stopped && wasMoving) viewport.scrollLeft = Math.max(0, offset);
      if (!stopped) viewport.scrollLeft = 0;
      control.hidden = reduced.matches;
      control.textContent = paused ? "Resume" : "Pause";
      control.setAttribute("aria-label", paused ? "Resume market ticker" : "Pause market ticker");
    }

    control.addEventListener("click", () => {
      paused = !paused;
      try { localStorage.setItem(storageKey, String(paused)); } catch {}
      update();
    });
    reduced.addEventListener("change", update);
    update();
  }

  async function chrome() {
    try {
      const [m, man] = await Promise.all([load("market.json"), load("manifest.json")]);
      const t = $("#ticker");
      if (t && m.state === "ok") {
        const items = [];
        const s = m.sensex;
        const one = (name, close, change) => {
          const changeValue = n(change);
          const direction = changeValue < 0 ? "down" : changeValue > 0 ? "up" : "flat";
          const movement = Number.isFinite(changeValue) ? `<span class="${direction} num">${direction === "down" ? "−" : direction === "up" ? "+" : ""}${fmtNum(Math.abs(changeValue))}%</span>` : "";
          return `<span class="tick"><b>${esc(name)}</b><span class="num">${fmtNum(close)}</span>${movement}</span>`;
        };
        const nifty = m.indices.find(i => i.name === "Nifty 50");
        if (nifty?.state === "ok") items.push(one("NIFTY 50", nifty.close, nifty.change_pct));
        if (s.state === "ok") items.push(one("SENSEX", s.close, s.change_pct));
        else items.push(`<span class="tick"><b>SENSEX</b><span class="asof">not captured</span></span>`);
        m.indices.filter(i => i.state === "ok" && i.name !== "Nifty 50").forEach(i => items.push(one(i.name.replace("Nifty ", "NIFTY ").toUpperCase(), i.close, i.change_pct)));
        m.stocks.filter(x => x.state === "ok").forEach(x => items.push(one(x.symbol, x.close, x.change_pct)));
        items.push(`<span class="tick asof">NSE end-of-day ${fmtDate(m.as_of)}${s.state === "ok" ? ` · Sensex delayed ${fmtDateTime(s.market_time)}` : ""}${m.simulated_failure ? " · FALLBACK DRILL" : ""}</span>`);
        mountTicker(t, items);
      } else if (t) {
        t.innerHTML = '<div class="ticker-inner"><span class="tick">Market data unavailable</span></div>';
      }
      const b = $("#build-stamp");
      if (b) b.innerHTML = `Data build <b>${esc(man.build_id)}</b> · ${esc(man.mode)}${man.retained_build ? " · retained fallback" : ""}${man.simulated_failures.length ? ` · drill: ${esc(man.simulated_failures.join(","))}` : ""}<br>${man.checks_summary.pass} checks pass · ${man.checks_summary.fail + man.checks_summary.conflict} flagged`;
    } catch (e) {
      const t = $("#ticker");
      if (t) t.innerHTML = `<div class="ticker-inner"><span class="tick">Market data unavailable: ${esc(e.message)}</span></div>`;
    }
  }

  return { load, $, esc, n, fmtNum, fmtCr, fmtInr, fmtPct, fmtX, ratioDisplay, fmtDate, fmtDateTime, ageDays, stateText, barChart, lineChart, spark, openEvidence, evidenceBlock, chrome, PALETTE };
})();
