/* The browser requests a verified NSE symbol; Python chooses and retains the source URLs. */
const CompanyLookup = (() => {
  const { $, esc, fmtDate } = IR;
  function mount(root, onAdded, query = () => "") {
    root.innerHTML = `<summary>Look up on NSE</summary>
      <form class="company-lookup-form">
        <label>Company name, NSE symbol or ISIN <input name="q" required minlength="2" maxlength="96" type="search" autocomplete="off"></label>
        <button type="submit" class="btn ghost">Search NSE</button>
      </form>
      <p class="small muted">NSE verifies the listing. Annual statements come from Screener.in, and prices use dated NSE closes where available.</p>
      <p class="small lookup-status" role="status"></p>
      <ul class="lookup-results"></ul>`;
    const form = $(".company-lookup-form", root);
    const status = $(".lookup-status", root);
    const results = $(".lookup-results", root);
    let sequence = 0, adding = false;
    async function submit(url, options) {
      const response = await fetch(url, options);
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Lookup unavailable. Try again.");
      return data;
    }
    root.addEventListener("toggle", () => {
      if (root.open && !form.elements.q.value && query()) form.elements.q.value = query();
    });
    form.addEventListener("submit", async e => {
      e.preventDefault();
      const turn = ++sequence;
      if (adding) return;
      status.textContent = "Searching the NSE directory…";
      results.replaceChildren();
      try {
        const data = await submit(`api/company-lookup?${new URLSearchParams({ q: form.elements.q.value })}`, { cache: "no-store" });
        if (turn !== sequence) return;
        const offline = data.mode === "retained_nse_closes";
        const scope = offline ? "Retained NSE close coverage" : "NSE directory";
        status.textContent = data.count
          ? `Showing ${data.matches.length} of ${data.count} · ${scope} · ${fmtDate(data.retrieved_at)}`
          : offline ? "No match in the retained NSE coverage. A wider directory requires online access."
            : "No supported NSE equity matched. Try its exchange symbol or ISIN.";
        results.innerHTML = data.matches.map(row => `<li>
          <div><strong>${esc(row.name)}</strong><span class="small muted">${esc(row.symbol)}${row.isin ? ` · ${esc(row.isin)}` : ""}</span></div>
          <button type="button" class="btn small" data-symbol="${esc(row.symbol)}">Add ${esc(row.symbol)}</button>
        </li>`).join("");
      } catch (error) {
        if (turn === sequence) status.textContent = error.message;
      }
    });
    results.addEventListener("click", async e => {
      const button = e.target.closest("[data-symbol]");
      if (!button || adding) return;
      adding = true;
      const submitButton = $("button[type=submit]", form);
      submitButton.disabled = true;
      results.querySelectorAll("button").forEach(item => { item.disabled = true; });
      status.textContent = `Checking the identity, annual statements and close for ${button.dataset.symbol}…`;
      try {
        const data = await submit("api/company-lookup", { method: "POST",
          headers: { "Content-Type": "application/json" }, body: JSON.stringify({ symbol: button.dataset.symbol }) });
        await onAdded(data.row);
        const coverage = data.row.coverage === "annual" ? "Annual statements available" : "Annual statements unavailable";
        const price = data.row.price_inr ? `close dated ${fmtDate(data.row.quote_as_of)}` : "price unavailable";
        const reused = data.state === "already_added" ? "Opened existing record" : "Added verified record";
        const source = data.sources?.financials === "retained" ? " · using retained financial data" : "";
        status.textContent = `${reused} · ${data.row.short}. ${coverage} · ${price}${source}.`;
      } catch (error) {
        status.textContent = error.message;
      } finally {
        adding = false;
        submitButton.disabled = false;
        results.querySelectorAll("button").forEach(item => { item.disabled = false; });
      }
    });
  }
  return { mount };
})();
