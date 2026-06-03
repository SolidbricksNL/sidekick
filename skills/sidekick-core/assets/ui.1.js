/* ===== Sidekick UI kernel — dependency-free, no network. Do not edit per-report;
   only window.SK above changes. ===== */
const IC={
 home:'<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
 users:'<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/>',
 euro:'<path d="M18 7a6.5 6.5 0 0 0-9.5 1"/><path d="M18 17a6.5 6.5 0 0 1-9.5-1"/><path d="M4 11h9"/><path d="M4 14h8"/>',
 check:'<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
 book:'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5z"/>',
 calendar:'<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M3 10h18M8 2v4M16 2v4"/>',
 grid:'<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/>',
 list:'<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
 layout:'<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>',
 search:'<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
 building:'<path d="M3 21h18M5 21V5l7-3 7 3v16"/><path d="M9 9h.01M9 13h.01M15 9h.01M15 13h.01"/>',
 trend:'<path d="M3 3v18h18"/><path d="M7 14l4-4 4 4 5-7"/>',
 mail:'<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 6L2 7"/>',
 sparkle:'<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/>'
};
const icon=(n,s)=>'<svg width="'+(s||18)+'" height="'+(s||18)+'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'+(IC[n]||IC.layout)+'</svg>';
const LOGO='<svg width="30" height="30" viewBox="0 0 32 32" fill="none"><rect x="3" y="4" width="14" height="24" rx="4.2" fill="#1493E8"/><rect x="19" y="14" width="10" height="14" rx="3.6" fill="#F47800"/><rect x="6.5" y="9.5" width="3" height="3" rx="1.5" fill="#fff" opacity=".9"/><rect x="11.5" y="9.5" width="3" height="3" rx="1.5" fill="#fff" opacity=".9"/></svg>';
/* Solidbricks maker mark — flat brick stack, brand blue + one orange brick. */
const SBLOGO='<svg width="15" height="15" viewBox="0 0 32 32" fill="none"><rect x="3" y="4" width="12" height="7" rx="1.2" fill="#1493E8"/><rect x="17" y="4" width="12" height="7" rx="1.2" fill="#1493E8"/><rect x="3" y="13" width="12" height="7" rx="1.2" fill="#1493E8"/><rect x="17" y="13" width="12" height="7" rx="1.2" fill="#43A8EE"/><rect x="3" y="22" width="12" height="7" rx="1.2" fill="#F47800"/><rect x="17" y="22" width="12" height="7" rx="1.2" fill="#1493E8"/></svg>';
const E=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const SK=window.SK, root=document.getElementById('root');
const KEY='sk.nav.sidekick';
let nav=null,selId,sortS;try{nav=JSON.parse(localStorage.getItem(KEY))}catch(e){}
const coll=id=>SK.collections.find(c=>c.id===id);
function go(cid,vid){if(!nav||nav.c!==cid){selId=undefined;sortS=null}nav={c:cid,v:vid};try{localStorage.setItem(KEY,JSON.stringify(nav))}catch(e){}render()}

function kpi(k){return '<div class="kpi"><span class="k-l">'+E(k.label)+'</span><span class="k-v">'+E(k.value)+'</span><span class="k-s '+(k.tone||'')+'">'+(k.delta?'<b>'+E(k.delta)+' </b>':'')+E(k.sub)+'</span></div>'}
function bars(d,u){const m=Math.max.apply(0,d.map(x=>+x.value||0))||1;return '<div class="bars">'+d.map(x=>'<div class="col"><span class="v">'+E(x.value)+E(u)+'</span><div class="b" style="height:'+(+x.value/m*136)+'px'+(x.color?';background:'+x.color:'')+'"></div><span class="l">'+E(x.label)+'</span></div>').join('')+'</div>'}
function hbars(d){const m=Math.max.apply(0,d.map(x=>+x.value||0))||1;return '<div class="hbar">'+d.map(x=>{const c=x.color||'var(--blue)';return '<div><div class="hl"><span class="sw" style="background:'+c+'"></span><span>'+E(x.label)+'</span><span class="n">'+E(x.value)+'</span></div><div class="track"><div class="fill" style="width:'+(+x.value/m*100)+'%;background:'+c+'"></div></div></div>'}).join('')+'</div>'}
function tbl(t){return '<table><thead><tr>'+t.cols.map(c=>'<th class="'+(c.num?'num':'')+'">'+E(c.label)+'</th>').join('')+'</tr></thead><tbody>'+t.rows.map(r=>'<tr>'+t.cols.map(c=>'<td class="'+(c.num?'num':'')+'">'+E(r[c.key])+'</td>').join('')+'</tr>').join('')+'</tbody></table>'}
function card(cd){const chart=cd.chart?(cd.chart.type==='hbars'?hbars(cd.chart.data):bars(cd.chart.data,cd.chart.unit||'')):'';const body=cd.table?tbl(cd.table):chart;return '<section class="card'+(cd.wide?' wide':'')+'"><h3>'+E(cd.title)+(cd.count!=null?'<span class="c">· '+cd.count+'</span>':'')+(cd.action?'<button class="act">'+E(cd.action)+'</button>':'')+'</h3><div class="body'+(cd.table?' p0':'')+'">'+body+'</div></section>'}

function viewDash(v){const k=(v.kpis||[]).map(kpi).join('');const cs=(v.cards||[]).map(card).join('');return '<div class="wrap">'+(v.title?'<div class="ph"><h1>'+E(v.title)+'</h1>'+(v.subtitle?'<p>'+E(v.subtitle)+'</p>':'')+'</div>':'')+(k?'<div class="kpis">'+k+'</div>':'')+(cs?'<div class="cards">'+cs+'</div>':'')+'</div>'}
function viewHome(c){const k=(c.kpis||[]).map(kpi).join('');const p=(c.panels||[]).map(pn=>'<section class="card"><h3>'+E(pn.title)+(pn.items?'<span class="c">· '+pn.items.length+'</span>':'')+'</h3><div class="body p0">'+(pn.items||[]).map(it=>'<div style="display:flex;gap:11px;align-items:center;padding:12px 16px;border-bottom:1px solid var(--bs)"><div style="flex:1;min-width:0"><div style="font-size:13.5px"><b>'+E(it.primary)+'</b> <span style="color:var(--fg2)">'+E(it.secondary)+'</span></div>'+(it.meta?'<div style="font-size:12px;color:var(--fg3)">'+E(it.meta)+'</div>':'')+'</div></div>').join('')+'</div></section>').join('');return '<div class="wrap"><div class="ph"><h1>'+E(c.greeting||'Good morning.')+'</h1>'+(c.intro?'<p>'+E(c.intro)+'</p>':'')+'</div>'+(k?'<div class="kpis">'+k+'</div>':'')+(p?'<div class="cards">'+p+'</div>':'')+'</div>'}
function pill(s){const m={Active:'ok','On site':'ok',Done:'ok',Decided:'ok','In progress':'bl',Open:'wn','At risk':'wn',Revisit:'wn'},k=m[s];const st=k==='ok'?'background:var(--ok-bg);color:var(--ok-fg)':k==='wn'?'background:var(--warn-bg);color:var(--warn-fg)':k==='bl'?'background:var(--blue-soft);color:var(--blue-text)':'';return '<span class="pill" style="'+st+'">'+E(s)+'</span>'}
