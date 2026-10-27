"""Offline, read-only V002 visualizer of *already verified* projection JSON.

Only called by the source-verifying project/publish pathway. Never opens
original archives, simulates motion, interpolates off-grid events or sends state
to an agent. Browser is for researcher observation, not an evidence oracle.
"""
from __future__ import annotations

import html
import json


def render(view):
    if view.get("schema_version") != "v002.view.v1" or view.get("status") != "verified_projection":
        raise ValueError("refuse unverified/wrong-version view")
    if len(view.get("worlds", [])) != 2 or view["evidence"]["archive_semantics_oracle"] != "pass":
        raise ValueError("refuse nonverified side-by-side comparison")
    raw = json.dumps(view, sort_keys=True, separators=(",", ":"), allow_nan=False)
    # The payload has been schema-checked and is displayed via textContent only.
    # Escape script delimiters to prevent data-derived HTML/JS injection.
    raw = raw.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    shell = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'nonce-v002'; style-src 'nonce-v002'; img-src 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'">
<title>SOMA · V002 Counterfactual Observatory (read-only)</title>
<style nonce="v002">
:root{font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;color:#e5e5e5;background:#101113}
*{box-sizing:border-box}
html,body{height:100%;width:100%;margin:0;overflow:hidden}
body{display:flex;flex-direction:column;background:#101113;font-size:13px;line-height:1.4}
header{height:54px;flex:none;display:flex;align-items:center;justify-content:space-between;padding:0 18px;border-bottom:1px solid #353638;background:#161719;min-width:0}
header h1{font-size:15px;letter-spacing:.12em;font-weight:650;margin:0}
header .status{font-size:10px;letter-spacing:.11em;border:1px solid #565758;padding:5px 9px;border-radius:3px;color:#c7c7c7}
main.workspace{flex:1;min-height:0;display:grid;grid-template-columns:minmax(226px,250px) minmax(0,1fr) minmax(254px,282px);grid-template-rows:minmax(0,1fr) minmax(0,.72fr) 168px;grid-template-areas:"setup arena evidence" "cells arena system" "timeline timeline timeline";gap:10px;padding:10px}
section{min-height:0;min-width:0;display:flex;flex-direction:column;background:#1d1e20;border:1px solid #38393b;border-radius:7px;overflow:hidden}
section[data-panel="setup"]{grid-area:setup}
section[data-panel="arena"]{grid-area:arena;background:radial-gradient(ellipse at 50% 38%,#292b2e 0%,#1b1c1e 55%,#101113 100%);box-shadow:inset 0 0 85px #0008,0 4px 20px #0005;border-color:#55575a}
section[data-panel="cells"]{grid-area:cells}
section[data-panel="evidence"]{grid-area:evidence}
section[data-panel="system"]{grid-area:system}
section[data-panel="timeline"]{grid-area:timeline}
h2{flex:none;font-size:11px;font-weight:650;text-transform:uppercase;letter-spacing:.15em;color:#c8c8c8;margin:0;padding:11px 13px;border-bottom:1px solid #393a3b}
h3{font-size:11px;color:#d8d8d8;font-weight:550;letter-spacing:.05em;margin:10px 0 5px}
p{margin:6px 0 10px}
small,.muted{font-size:10px;color:#a1a2a3}
#setup,#cells,#evidence,#system{padding:11px 13px;overflow:auto;min-height:0;scrollbar-color:#656668 transparent;scrollbar-width:thin}
#diff{flex:1;overflow:auto;max-height:none;min-height:0}
table{border-collapse:collapse;width:100%;font-size:10.5px}
th,td{text-align:left;font-weight:400;padding:6px 4px;border-bottom:1px solid #37383a;vertical-align:top;overflow-wrap:anywhere}
th{font-weight:550;color:#bfc0c0;position:sticky;top:0;background:#1d1e20}
code{color:#d5d5d5;overflow-wrap:anywhere}
.tag{display:inline-block;padding:3px 6px;border:1px solid #535455;border-radius:4px}
.pass,.warning{color:#e5e5e5}
details{min-width:0}
summary{cursor:pointer;color:#c6c6c6;padding:5px 0}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:10px;color:#ccc;margin:4px}
a,button,select{font:inherit}
button,select{border:1px solid #5a5b5c;border-radius:4px;background:#292a2c;color:#e8e8e8;padding:6px 9px}
button{cursor:pointer}
button:hover,select:hover{background:#424345}
button:focus-visible,select:focus-visible,summary:focus-visible{outline:2px solid #e5e5e5;outline-offset:2px}
label{display:inline-flex;align-items:center;gap:7px;color:#bdbdbd}
#arena{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px;padding:13px}
.scene{min-width:0;min-height:0;display:flex;flex-direction:column;gap:6px;border:1px solid #4b4d50;border-radius:5px;padding:12px;background:radial-gradient(ellipse at 50% 43%,#292b2e 0%,#1d1f22 60%,#131416 100%);box-shadow:inset 0 0 48px #0007}
.scenetitle{font-size:11px;letter-spacing:.12em;color:#f0f0f0;font-weight:650}
.scene svg{flex:1;min-height:0;max-height:100%;width:100%;display:block;background:radial-gradient(ellipse at center,#303236 0%,#1b1d20 57%,#101112 100%);border:1px solid #414245;border-radius:5px}
.scene small{white-space:normal;line-height:1.35;overflow-wrap:anywhere;max-height:32px;overflow:hidden}
.arenalegend{flex:none;padding:0 13px 10px;font-size:10px;color:#9c9c9c;letter-spacing:.02em}
#cells table,#evidence small,#system small{display:block}
#cells td{min-width:42px}
.future-slot{border:1px dashed #58595a;border-radius:4px;padding:8px;margin-top:9px;color:#929393;font-size:10px}
.future-slot strong{color:#bbbbbb;font-size:10px}
.time-head{display:flex;flex-wrap:wrap;align-items:center;gap:10px;padding:8px 12px;border-bottom:1px solid #393a3b;flex:none}
.time-head h2{border:0;padding:0;margin-right:10px}
.time-body{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:12px;padding:7px 12px 9px}
.log-shell,.event-inspector{min-height:0;min-width:0;overflow:hidden;display:flex;flex-direction:column}
.log-header{flex:none;font-size:9px;letter-spacing:.14em;color:#9d9d9d;padding-bottom:5px}
#eventLog{flex:1;min-height:0;overflow:auto;scrollbar-color:#707070 #252627;border:1px solid #37383a;border-radius:4px;padding:2px}
.log-row{display:flex;align-items:center;border-bottom:1px solid #353638;gap:10px;min-height:22px;padding:2px 8px;font-size:10px}
.log-row span{width:48px;flex:none;color:#b4b4b4;font-variant-numeric:tabular-nums}
.log-row button{flex:1;text-align:left;padding:2px 3px;background:transparent;border:0;color:#ddd;font-size:10px}
.log-row button:hover{background:#444}
#eventNote{font-size:10.5px;overflow-wrap:anywhere;flex:none;color:#dfdfdf;padding:0 0 5px}
#eventDetails{flex:1;min-height:0;overflow:auto;border-top:1px solid #343536;scrollbar-color:#656668 transparent}
#eventDetails details{padding:2px}
@media(max-width:1100px){main.workspace{grid-template-columns:205px minmax(0,1fr) 222px;gap:7px;padding:7px}.scene{padding:6px}#arena{padding:7px;gap:6px}}
@media(max-height:680px){main.workspace{grid-template-rows:minmax(0,1fr) minmax(0,.65fr) 140px}.time-head{gap:6px;padding:5px 8px}.scene small{max-height:20px}}
@media(max-width:900px){body{overflow:auto}main.workspace{min-height:700px;grid-template-columns:190px minmax(430px,1fr) 190px;overflow:auto}header{min-width:820px}}
</style></head><body>
<header><h1>SOMA / OBSERVATORY</h1><span class="status">V002 · VERIFIED ARCHIVE · READ ONLY</span></header>
<main class="workspace">
<section data-panel="setup"><h2>Setup</h2><div id="setup"></div><div id="diff"></div></section>
<section data-panel="arena"><h2>Arena <span class="muted">/ TWO ARCHIVED WORLDS</span></h2>
<div class="scenes" id="arena"></div><div class="arenalegend">XY in metres · same X/Y scale · circles = physical radius · crosses = symbolic centres</div></section>
<section data-panel="cells"><h2>Cells</h2><div id="cells"></div></section>
<section data-panel="evidence"><h2>Evidence</h2><div id="evidence"></div></section>
<section data-panel="system"><h2>System/Data</h2><div id="system"><div class="future-slot"><strong>LOCAL OBSERVATION / POLICY</strong><div>RESERVED · NO API</div></div><div class="future-slot"><strong>LEARNING</strong><div>RESERVED · NOT IMPLEMENTED</div></div></div></section>
<section data-panel="timeline">
<div class="time-head"><h2>Timeline</h2>
<label>Sample <button type="button" id="prevSample" aria-label="Previous saved sample">◀</button>
<select id="sampleTime" aria-label="Common saved sample"></select>
<button type="button" id="nextSample" aria-label="Next saved sample">▶</button></label>
<label>Exact event <select id="eventPicker" aria-label="Archived event"></select></label>
</div>
<div class="time-body"><div class="log-shell"><div class="log-header">ARCHIVED HISTORY · SCROLL</div><div id="eventLog" role="log" aria-label="Archived chronological records"></div></div>
<div class="event-inspector"><div class="log-header">SELECTED EVENT · SOURCE TIME</div><div id="eventNote"></div><div id="eventDetails"></div></div></div>
</section>
</main>
<script nonce="v002">const BUNDLE=__V002_JSON__;
const $=id=>document.getElementById(id);
function node(tag,txt,parent){const x=document.createElement(tag);if(txt!==null)x.textContent=String(txt);if(parent)parent.appendChild(x);return x}
function fmt(v){return String(v)}
function table(head,rows,el){const t=node("table",null,el),h=node("tr",null,t);head.forEach(v=>node("th",v,h));rows.forEach(row=>{const tr=node("tr",null,t);row.forEach(v=>node("td",v,tr))});return t}
const worlds=BUNDLE.worlds, clocks=BUNDLE.joint_sample_times_s;
const setup=$("setup");node("p",worlds.map(w=>w.side.toUpperCase()+" / "+w.world_id).join("    ×    "),setup);
node("p",BUNDLE.pair_inference+" · "+BUNDLE.parameter_diff.filter(x=>!x.equal).length+" changed fields",setup);
const dd=BUNDLE.parameter_diff;
if(dd.length)table(["Frozen input field","Left","Right","Same?"],dd.map(x=>[x.field_path,fmt(x.left),fmt(x.right),x.equal?"unchanged":"DIFF"]),$("diff"));
else node("p","No input fields found: invalid view",$("diff"));
const choose=$("sampleTime");clocks.forEach(t=>{const o=node("option",fmt(t)+" s",choose);o.value=String(t)});
const allxy=worlds.flatMap(w=>w.samples.flatMap(x=>[x.record.x_a_m,x.record.y_a_m,x.record.x_b_m,x.record.y_b_m]));
const xyx=worlds.flatMap(w=>w.samples.flatMap(x=>[x.record.x_a_m,x.record.x_b_m]));
const xyy=worlds.flatMap(w=>w.samples.flatMap(x=>[x.record.y_a_m,x.record.y_b_m]));
const minx=Math.min(...xyx)-1,maxx=Math.max(...xyx)+1,miny=Math.min(...xyy)-1,maxy=Math.max(...xyy)+1;
const span=Math.max(maxx-minx,maxy-miny,1),cx=(minx+maxx)/2,cy=(miny+maxy)/2;
function point(x,y){return [120+(x-(cx-span/2))/span*360,390-(y-(cy-span/2))/span*360]}
function draw(){
 const arena=$("arena");arena.replaceChildren();
 for(const w of worlds){
 const div=node("div",null,arena);div.className="scene";
 node("div",w.side.toUpperCase()+" · "+w.world_id,div).className="scenetitle";
 const item=w.samples.find(x=>x.record.time_s===Number(choose.value));
 if(!item){node("p","NO_RECORDED_SNAPSHOT_AT_TIME",div);continue}
 const rec=item.record,svg=document.createElementNS("http://www.w3.org/2000/svg","svg");
 svg.setAttribute("viewBox","0 0 600 420");svg.setAttribute("role","img");
 svg.setAttribute("aria-label",w.world_id+" source sample at "+choose.value+" seconds: cells A and B, X and Y in metres");
 div.appendChild(svg);
 const E=(tag,attrs)=>{const e=document.createElementNS("http://www.w3.org/2000/svg",tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));svg.appendChild(e);return e};
 for(const x of [0,1]){const [a,b]=point(x?cx+span/2:cx-span/2,cy);E("line",{x1:a,y1:10,x2:a,y2:400,stroke:"#505155"})}
 const ax=E("text",{x:300,y:413,fill:"#b5b5b5","font-size":13});ax.textContent="X (m)";
 const ay=E("text",{x:15,y:210,fill:"#bcd0ea","font-size":13});ay.textContent="Y (m)";
 for(const [who,color] of [["a","#dddddd"],["b","#858585"]]){
 const [x,y]=point(rec["x_"+who+"_m"],rec["y_"+who+"_m"]);
 // Geometric radius is measured on the SAME XY physical scale, without a visibility clamp.
 // A tiny source disk remains tiny; thin crosshair + label are symbolic centre annotations.
 const radiusMetres=w.scenario["radius_"+who+"_m"];
 const rr=radiusMetres/span*360;
 E("circle",{cx:x,cy:y,r:rr,fill:color,opacity:.8,stroke:"none"});
 E("line",{x1:x-4,y1:y,x2:x+4,y2:y,stroke:"#e7e7e7","stroke-width":1});
 E("line",{x1:x,y1:y-4,x2:x,y2:y+4,stroke:"#e7e7e7","stroke-width":1});
 const text=E("text",{x:x+9,y:y-10,fill:"#f1f1f1","font-size":17});text.textContent=who.toUpperCase();
 }
 node("small","sample t="+fmt(rec.time_s)+" s · row "+item.source_row+" · "+rec.phase,div);
 node("small","A ("+rec.x_a_m+", "+rec.y_a_m+")   B ("+rec.x_b_m+", "+rec.y_b_m+") m",div);
 }
}
choose.addEventListener("change",draw);draw();
for(const w of worlds){
 const el=$("cells");node("h3",w.side+" / "+w.world_id,el);
 if(w.cell_model.kind==="not_modeled")node("p","NOT MODELED · F022 has no motor or ledger",el);
 else table(["Cell","Decision","Charge µJ","Private balance after µJ"],w.cell_model.actions.map(a=>{
 const e=w.cell_model.ledger.find(z=>z.record.cell_id===a.record.cell_id);
 return [a.record.cell_id,a.record.decision,a.record.charge_uj,e?e.record.balance_after_uj:"MISSING"];
 }),el);
}
const evs=BUNDLE.timeline.filter(x=>x.kind!=="sample"),evsel=$("eventPicker");
const none=node("option","(sample-only view; select event to inspect)",evsel);none.value="-1";
evs.forEach((x,i)=>{const o=node("option",x.side+" "+x.kind+" at "+fmt(x.time_s)+" s · row "+x.source_row,evsel);o.value=String(i)});
function showEvent(){
 const i=Number(evsel.value),details=$("eventDetails");details.replaceChildren();
 if(i<0){$("eventNote").textContent="Archived samples · select an exact event.";return}
 const v=evs[i],w=worlds.find(x=>x.side===v.side);
 const list=v.kind==="contact"?w.contacts:w.cell_model.actions;
 const original=list.find(x=>x.source_row===v.source_row);
 if(!original){$("eventNote").textContent="REFUSED: archived provenance pointer missing";return}
 const other=worlds.find(x=>x.side!==v.side);
 const exists=other.samples.some(x=>x.record.time_s===v.time_s);
 const otherState=exists?"EXACT_POST_SAMPLE_AT_TIME (a saved post-event/post-action frame, not a synchronized pre-event snapshot)":"NO_RECORDED_SNAPSHOT_AT_TIME";
 $("eventNote").textContent=v.side.toUpperCase()+" "+v.kind+" / exact source time "+fmt(v.time_s)+" s. Other side: "+otherState+". No extrapolation/interpolation.";
 const disclosure=node("details",null,details);node("summary","Original source record · "+v.source_file+" #"+v.source_row,disclosure);node("pre",JSON.stringify(original.record,null,2),disclosure);
}
evsel.addEventListener("change",showEvent);showEvent();

function refreshLog(){
 const log=$("eventLog");log.replaceChildren();const t=Number(choose.value);
 const items=BUNDLE.timeline.filter(p=>p.time_s<=t).sort((x,y)=>x.time_s-y.time_s);
 for(const p of items){
  const line=node("div",null,log);line.className="log-row";
  node("span",fmt(p.time_s)+" s",line);
  const action=node("button",p.side.toUpperCase()+" / "+p.kind+" · row "+p.source_row,line);
  action.type="button";
  action.addEventListener("click",()=>{
   if(p.kind==="sample"){choose.value=String(p.time_s);draw();refreshLog();return}
   const ix=evs.findIndex(x=>x.side===p.side&&x.kind===p.kind&&x.source_file===p.source_file&&x.source_row===p.source_row);
   if(ix>=0){evsel.value=String(ix);showEvent()}
  });
 }
 log.scrollTop=log.scrollHeight;
}
choose.addEventListener("change",refreshLog);
for(const [id,d] of [["prevSample",-1],["nextSample",1]]){
 $(id).addEventListener("click",()=>{const ix=clocks.indexOf(Number(choose.value));const next=clocks[Math.max(0,Math.min(clocks.length-1,ix+d))];choose.value=String(next);draw();refreshLog();});
}
refreshLog();
const evid=$("evidence");
for(const e of BUNDLE.evidence.sources){
 node("p","PASS · "+e.side+" / "+e.source_schema_version+" · independent from-disk oracle "+e.verifier,evid).className="pass";
 const proof=node("details",null,evid);node("summary","Source / protocol / trust",proof);node("small","Expected SHA: "+e.expected_source_sha+" · protocol: "+e.expected_protocol_sha+" · anchor: "+e.trusted_anchor_ref,proof);
}
node("p","Projection oracle: "+BUNDLE.evidence.view_projection_oracle+" · Archive oracle: "+BUNDLE.evidence.archive_semantics_oracle,evid);
node("p","v002.view.v1 · "+BUNDLE.contract_id,$("system"));node("small","Verified archive → projection → six read-only owners. No agent truth feedback.",$("system"));
</script></body></html>"""
    return shell.replace("__V002_JSON__", raw)
