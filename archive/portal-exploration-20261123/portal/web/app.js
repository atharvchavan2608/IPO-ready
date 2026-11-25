'use strict';
const $ = id => document.getElementById(id);
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let snapshots = {}, data, period, unit = 'crore', view = 'research', scenarioResult = null;
const fmt = (value, digits=2) => value == null ? 'Unavailable' : Number(value).toLocaleString('en-IN', {minimumFractionDigits:digits,maximumFractionDigits:digits});
const money = value => fmt(value == null ? null : Number(value) * (unit === 'million' ? 10 : 1));
const unitName = () => 'INR ' + unit;
const facts = () => data.observations.filter(f=>f.period_end === period);
const fact = id => facts().find(f=>f.metric_id === id);
const metric = id => data.periods.find(p=>p.period_end===period).metrics.find(m=>m.id===id);
const names = {operating_revenue:'Operating revenue',provider_total_income:'Provider total income',other_income:'Other income',continuing_profit:'Continuing-operations profit',cfo:'Cash from operating activities'};

function showView(next) {
  view = next;
  document.querySelectorAll('.view').forEach(el=>el.hidden = el.id !== 'view-'+view);
  document.querySelectorAll('.nav-item').forEach(el=>{el.classList.toggle('active',el.dataset.view===view);if(el.dataset.view===view)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');});
  $('breadcrumb').textContent = {research:'Company research',scenario:'Scenario lab',references:'IPO references',evidence:'Evidence & coverage'}[view];
}
function changeCompany(id) {
  data = snapshots[id];
  period = data.periods.at(-1).period_end;
  scenarioResult = null;
  document.querySelectorAll('[data-company]').forEach(el=>el.classList.toggle('selected',el.dataset.company===id));
  $('period').innerHTML = [...data.periods].reverse().map(p=>`<option value="${p.period_end}">${p.label}</option>`).join('');
  $('period').value=period;
  resetScenario();render();
}
function resetScenario() {
  $('profit-pct').value=Number(metric('continuing_profit_to_revenue').value).toFixed(1);
  $('growth').value=10;
  scenarioResult=null; updateRangeLabels();
}
function updateRangeLabels() {
  $('growth-output').textContent=$('growth').value+'%';
  $('profit-output').textContent=$('profit-pct').value+'%';
}
function render() {
  $('company-name').textContent=data.company.name;
  $('company-status').textContent=data.company.status.toUpperCase();
  $('company-subtitle').textContent=data.company.sector+' · '+(data.company.id==='igx'?'Free-source pre-IPO research':'Listed 24 Sep 2026 · Historical financial reference');
  document.querySelectorAll('.unit-text').forEach(el=>el.textContent=unitName());
  $('snapshot-id').textContent=data.snapshot_id;
  $('scenario-year').textContent=data.periods.find(p=>p.period_end===period).label;
  const yoy=metric('operating_revenue_yoy'), share=metric('continuing_profit_to_revenue'),cash=metric('cash_conversion');
  const cards=[['Operating revenue',money(fact('operating_revenue').raw_value.replaceAll(',','')),unitName(),'Source observation','fact:operating_revenue'],
    ['Operating-revenue YoY',yoy?fmt(yoy.value)+'%':'Unavailable','',yoy?'Consecutive annual periods':'Prior year outside this slice','metric:operating_revenue_yoy'],
    ['Continuing profit / revenue',fmt(share.value)+'%','','Operating-revenue denominator','metric:continuing_profit_to_revenue'],
    ['CFO / continuing profit',fmt(cash.value)+'×','','Settlement-flow review pending','metric:cash_conversion']];
  $('metrics').innerHTML=cards.map(([label,value,suffix,foot,target])=>`<button class="metric-card" data-evidence="${target}"><span class="metric-label">${label}<span>↗</span></span><div class="metric-value ${value.startsWith('-')?'negative':''}">${value}<small>${suffix}</small></div><div class="metric-foot">${foot}</div></button>`).join('');
  renderChart();
  $('cagr').textContent=fmt(data.summary_metrics[0].value)+'%';
  $('insights').innerHTML=`<div class="insight"><span>OBSERVED · ${period.slice(0,4)}</span><p>${yoy?'Operating revenue '+(Number(yoy.value)<0?'fell':'grew')+' '+fmt(Math.abs(Number(yoy.value)))+'% over the previous year.':'The prior annual period is outside this three-year slice.'}</p></div><div class="insight"><span>CALCULATED</span><p>Continuing profit equals ${fmt(share.value)}% of operating revenue. Other income contributes separately; this ratio does not isolate operating profitability.</p></div><div class="insight caution"><span>NEEDS REVIEW</span><p>Cash-flow movements require settlement and client-money context. Reporting basis remains unspecified.</p></div>`;
  const rows=Object.keys(names);
  $('financial-table').innerHTML=`<thead><tr><th>Reported item</th>${data.periods.map(p=>`<th>${p.label}</th>`).join('')}</tr></thead><tbody>${rows.map(id=>`<tr><td><button class="fact-link" data-evidence="fact:${id}">${escape(names[id])} ↗</button></td>${data.periods.map(p=>{const f=data.observations.find(f=>f.metric_id===id&&f.period_end===p.period_end);return `<td>${money(f.raw_value.replaceAll(',',''))}</td>`;}).join('')}</tr>`).join('')}</tbody>`;
  renderEvidence();renderReferences();renderScenario();
}
function renderChart() {
  const width=620,height=240,left=58,right=22,top=24,bottom=35;
  const series=['operating_revenue','continuing_profit'].map(id=>data.periods.map(p=>Number(data.observations.find(f=>f.metric_id===id&&f.period_end===p.period_end).raw_value.replaceAll(',',''))*(unit==='million'?10:1)));
  const max=Math.max(...series.flat())*1.15;
  const x=i=>left+i*(width-left-right)/2,y=v=>height-bottom-(v/max)*(height-top-bottom);
  const grid=Array.from({length:4},(_,i)=>{const value=max*i/3;return `<line x1="${left}" y1="${y(value)}" x2="${width-right}" y2="${y(value)}" stroke="#e6eade" stroke-dasharray="3 4"/><text x="${left-10}" y="${y(value)+4}" text-anchor="end" fill="#91998b" font-size="10">${fmt(value,0)}</text>`;}).join('');
  const lines=series.map((values,j)=>`<polyline points="${values.map((v,i)=>`${x(i)},${y(v)}`).join(' ')}" fill="none" stroke="${j?'#cd8857':'#1d6951'}" stroke-width="2.5"/>${values.map((v,i)=>`<circle cx="${x(i)}" cy="${y(v)}" r="4" fill="white" stroke="${j?'#cd8857':'#1d6951'}" stroke-width="2"><title>${j?'Continuing profit':'Operating revenue'} ${data.periods[i].label}: ${fmt(v)} ${unitName()}</title></circle>`).join('')}`).join('');
  $('trend').innerHTML=`<svg viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="chart-title"><title id="chart-title">Operating revenue and continuing profit, FY24 to FY26, ${unitName()}. Exact values are in the financial history table.</title>${grid}${lines}${data.periods.map((p,i)=>`<text x="${x(i)}" y="${height-10}" text-anchor="middle" fill="#828c79" font-size="11">${p.label}</text>`).join('')}</svg>`;
}
function renderEvidence() {
  $('coverage').innerHTML=[['Source observations','15','Five items × three years'],['Primary-reviewed facts','0','Issuer reconciliation pending'],['Reporting basis','Unknown','Peer valuation blocked']].map(([label,value,note])=>`<div class="panel"><span class="muted">${label}</span><strong>${value}</strong><span class="small muted">${note}</span></div>`).join('');
  $('limitations').innerHTML=data.limitations.map(l=>`<li>${escape(l)}</li>`).join('');
  const current=facts();
  $('source-facts').innerHTML=`<p class="small muted">Selected year: ${period.slice(0,4)} · ${data.snapshot_id}</p>${current.map(f=>`<details><summary>${escape(f.source_label)} · ${escape(f.raw_value)} ${escape(f.raw_unit)}</summary><p>Source ${f.source_id} · ${f.review_state} · Basis: ${f.basis}</p><p>Row: ${escape(f.locator.row)} / column: ${f.locator.column} / table: ${f.locator.table}</p><p>Retrieved: ${escape(f.retrieved_at)} · Source publication date: unknown</p><p><a href="${escape(f.source_url)}" target="_blank" rel="noopener noreferrer">Open provider financial table ↗</a></p><p><code>SHA-256 ${f.evidence_sha256}</code></p></details>`).join('')}<h3 style="margin-top:22px">Calculated results</h3>${data.periods.find(p=>p.period_end===period).metrics.map(m=>`<details><summary>${escape(m.id)} · ${m.value??'Unavailable'} ${escape(m.unit)}</summary><p class="formula">${escape(m.formula)}</p><p>Operands: ${escape(m.operand_fact_ids.join(', '))}</p><p>${escape(m.formula_version)} · ${escape(m.review_state)}</p></details>`).join('')}`;
}
function renderReferences() {
  $('references').innerHTML=`<article class="panel reference-card"><div><span class="badge">Recent IPO · 24 Sep 2026</span><h3>National Stock Exchange of India</h3><p>Three years of secondary financial observations are available as a reference. A securities exchange is not automatically a comparable gas exchange. Different business exposure and unspecified accounting basis keep peer valuation unavailable.</p><a href="https://nsearchives.nseindia.com/web/pressrelease/2026-11/PR_cc_03112026_20261103175822.pdf" target="_blank" rel="noopener noreferrer">Issuer listing-status evidence ↗</a></div><button class="button secondary" data-open-company="nse-india">Open reference ↗</button></article>${data.references.map(r=>`<article class="panel reference-card"><div><span class="badge">Recent IPO reference candidate</span><h3>${escape(r.name)}</h3><p>${escape(r.reason)}</p><p>Listed ${escape(r.listing_date)} · Financial dataset not yet reviewed.</p><a href="${escape(r.source_url)}" target="_blank" rel="noopener noreferrer">Annual report · printed page 61 ↗</a></div><span class="badge">Comparison excluded</span></article>`).join('')}`;
}
function renderScenario() {
  if(!scenarioResult){$('scenario-result').innerHTML='<h3>A scenario starts with your assumptions.</h3><p>Choose inputs, then calculate to inspect the resulting revenue and continuing profit.</p>';return;}
  const r=scenarioResult;
  $('scenario-result').innerHTML=`<p class="result-label">Hypothetical operating revenue · ${unitName()}</p><div class="result-value">${money(r.hypothetical_operating_revenue)}</div><p class="result-label">Hypothetical continuing profit · ${unitName()}</p><div class="result-value">${money(r.hypothetical_continuing_profit)}</div><p>Growth ${escape(r.inputs.growth_pct)}% · Assumed profit / operating revenue ${escape(r.inputs.profit_pct)}%</p><div class="formula">${escape(r.formula)}</div><p class="small" style="margin-top:15px">Base fact: ${escape(r.base_fact_id)}<br>${escape(r.snapshot_id)} · ${escape(r.formula_version)}<br>Provisional secondary inputs · Reporting basis unspecified</p>`;
}
function showEvidence(target) {
  const [kind,id]=target.split(':');
  let chosen, calculated;
  if(kind==='fact')chosen=fact(id);else{calculated=metric(id);if(calculated)chosen=data.observations.find(f=>f.id===calculated.operand_fact_ids[0]);}
  $('fact-detail').innerHTML=chosen?`<p class="eyebrow">${calculated?'CALCULATION LINEAGE':'SOURCE OBSERVATION'}</p><h2>${escape(calculated?calculated.id:names[id])}</h2><p class="raw">${calculated?escape(calculated.value)+' '+escape(calculated.unit):escape(chosen.raw_value)+' '+escape(chosen.raw_unit)}</p>${calculated?`<p class="formula">${escape(calculated.formula)}</p><p>Operand facts: ${escape(calculated.operand_fact_ids.join(', '))}</p>`:''}<dl><dt>Source label</dt><dd>${escape(chosen.source_label)}</dd><dt>Year / basis</dt><dd>${chosen.locator.column} / ${chosen.basis}</dd><dt>Source anchor</dt><dd>${escape(chosen.locator.table)} → ${escape(chosen.locator.row)}</dd><dt>Review</dt><dd>Transcription checked; primary reconciliation pending</dd><dt>Retrieved</dt><dd>${escape(chosen.retrieved_at)}</dd><dt>Published</dt><dd>Unknown</dd><dt>Evidence hash</dt><dd>${chosen.evidence_sha256}</dd></dl><p><a href="${escape(chosen.source_url)}" target="_blank" rel="noopener noreferrer">Open source table ↗</a></p>`:'<h2>Prior year unavailable</h2><p>The previous annual period is outside this snapshot. No value has been substituted.</p>';
  $('fact-dialog').showModal();
}
document.addEventListener('click',e=>{
  const nav=e.target.closest('[data-view]');if(nav)showView(nav.dataset.view);
  const company=e.target.closest('[data-company]');if(company){changeCompany(company.dataset.company);showView('research');}
  const open=e.target.closest('[data-open-company]');if(open){changeCompany(open.dataset.openCompany);showView('research');}
  const evidence=e.target.closest('[data-evidence]');if(evidence)showEvidence(evidence.dataset.evidence);
});
$('period').addEventListener('change',()=>{period=$('period').value;resetScenario();render();});
$('unit').addEventListener('change',()=>{unit=$('unit').value;render();});
['growth','profit-pct'].forEach(id=>$(id).addEventListener('input',()=>{updateRangeLabels();scenarioResult=null;renderScenario();}));
$('scenario-form').addEventListener('submit',async e=>{
  e.preventDefault();const button=e.submitter;button.disabled=true;
  try{
    const response=await fetch('/api/scenario',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({company_id:data.company.id,period_end:period,growth_pct:$('growth').value,profit_pct:$('profit-pct').value})});
    const payload=await response.json();if(!response.ok)throw Error(payload.error);
    scenarioResult=payload;renderScenario();
  }catch(error){$('scenario-result').textContent='Scenario unavailable: '+error.message;}finally{button.disabled=false;}
});
$('export').addEventListener('click',()=>{
  const projection={...data,export_context:{selected_period:period,display_unit:unitName(),scenario:scenarioResult}};
  const url=URL.createObjectURL(new Blob([JSON.stringify(projection,null,2)],{type:'application/json'}));
  const a=document.createElement('a');a.href=url;a.download=`ipo-ready-${data.company.id}-${period}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
async function start(){
  try{
    const responses=await Promise.all([fetch('/api/snapshot'),fetch('/api/reference')]);
    if(responses.some(r=>!r.ok))throw Error('Research snapshot could not be loaded');
    const [active,reference]=await Promise.all(responses.map(r=>r.json()));
    snapshots={[active.company.id]:active,[reference.company.id]:reference};changeCompany(active.company.id);
    $('loading').hidden=true;$('app').hidden=false;
  }catch(error){$('loading').textContent='Unable to load research: '+error.message;}
}
start();
