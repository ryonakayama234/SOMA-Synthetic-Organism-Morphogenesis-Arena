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
:root{font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#e4ecf8;background:#101722}
*{box-sizing:border-box}body{max-width:1480px;margin:auto;padding:22px;line-height:1.5}
h1{font-size:1.55rem;letter-spacing:.02em}h2{font-size:1.05rem;margin:0 0 10px;color:#d8e8ff}
small,.muted{color:#a7b7ce}p{margin:6px 0 12px}
.panels{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px}
section{background:#1b2736;border:1px solid #35465c;border-radius:11px;padding:15px;min-width:0}
.span2{grid-column:1/-1}
.scenes{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.scene{border:1px solid #3c5772;background:#111c29;border-radius:8px;padding:8px}
.scenetitle{font-size:.93rem;font-weight:650}
svg{width:100%;height:auto;aspect-ratio:10/7;display:block;background:#101925;border-radius:5px}
label{display:inline-flex;align-items:center;gap:9px;margin:5px 12px 5px 0}
select{padding:7px;color:#e7edfa;background:#111c29;border:1px solid #6183a5;border-radius:6px}
table{width:100%;border-collapse:collapse;font-size:.83rem}td,th{border-bottom:1px solid #334458;text-align:left;padding:6px;word-break:break-word}
ul{margin:6px 0;padding-left:22px}code{white-space:pre-wrap;overflow-wrap:anywhere;color:#b5defe}
.tag{display:inline-block;border-radius:5px;background:#293f55;padding:2px 7px;margin:2px}
.warning{color:#ffd6a6}.pass{color:#a6f1cb}
#eventNote{font-size:.9rem;padding:8px;border-left:3px solid #7caddc}
button{background:#27445f;color:white;border:1px solid #5d92bb;border-radius:6px;padding:5px 9px;cursor:pointer}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.79rem}
@media(max-width:850px){.panels,.scenes{grid-template-columns:1fr}.span2{grid-column:1}}
</style></head><body>
<header><h1>SOMA · V002 Counterfactual Observatory</h1>
<p class="muted">Frozen v002.view.v1 · Source-verified archive projection · Researcher-only, read-only. Not a physical simulation or evidence of spontaneous agency.</p></header>
<main class="panels">
<section class="span2"><h2>Setup · archived worlds & complete input difference</h2>
<div id="setup"></div><div id="diff"></div></section>
<section class="span2"><h2>Arena · exactly saved XY samples (metres)</h2>
<label>Common saved sample: <select id="sampleTime"></select></label>
<div class="scenes" id="arena"></div><p class="muted">A/B are source disk centres. Both views use identical world-coordinate scale. No physical interpolation or animated off-grid samples.</p></section>
<section><h2>Cells · private action / ledger</h2><div id="cells"></div></section>
<section><h2>Timeline · exact events, never invented frames</h2>
<label>Inspect archived record: <select id="eventPicker"></select></label><div id="eventNote"></div><div id="eventDetails"></div></section>
<section><h2>Evidence · saved-source validation</h2><div id="evidence"></div></section>
<section><h2>System/Data · schema & access boundary</h2><p><code>v002.view.v1</code> → Setup / Arena / Cells / Timeline / Evidence / System/Data</p>
<p>Source archive → independent from-disk verifier → immutable projection → researcher display. Never feeds LocalObservation, policy, simulator or archived source files.</p>
<div id="system"></div></section>
</main>
<script nonce="v002">const BUNDLE=__V002_JSON__;
const $=id=>document.getElementById(id);
function node(tag,txt,parent){const x=document.createElement(tag);if(txt!==null)x.textContent=String(txt);if(parent)parent.appendChild(x);return x}
function fmt(v){return typeof v==="number"?Number(v).toPrecision(10).replace(/\\.?0+$/,""):String(v)}
function table(head,rows,el){const t=node("table",null,el),h=node("tr",null,t);head.forEach(v=>node("th",v,h));rows.forEach(row=>{const tr=node("tr",null,t);row.forEach(v=>node("td",v,tr))});return t}
const worlds=BUNDLE.worlds, clocks=BUNDLE.joint_sample_times_s;
const setup=$("setup");node("p",worlds.map(w=>w.side.toUpperCase()+" = "+w.source_schema_version+" / "+w.world_id).join("   |   "),setup);
node("p","Input-diff classification: "+BUNDLE.pair_inference+" ("+BUNDLE.parameter_diff.filter(x=>!x.equal).length+" physical input fields differ)",setup);
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
 for(const x of [0,1]){const [a,b]=point(x?cx+span/2:cx-span/2,cy);E("line",{x1:a,y1:10,x2:a,y2:400,stroke:"#294158"})}
 const ax=E("text",{x:300,y:413,fill:"#bcd0ea","font-size":13});ax.textContent="X (m)";
 const ay=E("text",{x:15,y:210,fill:"#bcd0ea","font-size":13});ay.textContent="Y (m)";
 for(const [who,color] of [["a","#65bbf1"],["b","#ffbf77"]]){
 const [x,y]=point(rec["x_"+who+"_m"],rec["y_"+who+"_m"]);
 // Geometric radius is measured on the SAME XY physical scale, without a visibility clamp.
 // A tiny source disk remains tiny; thin crosshair + label are symbolic centre annotations.
 const radiusMetres=w.scenario["radius_"+who+"_m"];
 const rr=radiusMetres/span*360;
 E("circle",{cx:x,cy:y,r:rr,fill:color,opacity:.8,stroke:"none"});
 E("line",{x1:x-4,y1:y,x2:x+4,y2:y,stroke:"#ffffff","stroke-width":1});
 E("line",{x1:x,y1:y-4,x2:x,y2:y+4,stroke:"#ffffff","stroke-width":1});
 const text=E("text",{x:x+9,y:y-10,fill:"#f1f8ff","font-size":17});text.textContent=who.toUpperCase();
 }
 node("small","sample t="+fmt(rec.time_s)+" s · source row "+item.source_row+" · phase="+rec.phase,div);
 node("small","XY centres (m)  A: ("+rec.x_a_m+", "+rec.y_a_m+")  B: ("+rec.x_b_m+", "+rec.y_b_m+"). Circles = physical disk radii; crosshairs/labels = symbolic centre annotations.",div);
 }
}
choose.addEventListener("change",draw);draw();
for(const w of worlds){
 const el=$("cells");node("h3",w.side+" / "+w.world_id,el);
 if(w.cell_model.kind==="not_modeled")node("p","NOT MODELED (F022): no motor, private budget, action or ledger in this source archive.",el);
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
 if(i<0){$("eventNote").textContent="Sample grid is synchronized; contact/action markers reference their original exact archived timestamps.";return}
 const v=evs[i],w=worlds.find(x=>x.side===v.side);
 const list=v.kind==="contact"?w.contacts:w.cell_model.actions;
 const original=list.find(x=>x.source_row===v.source_row);
 if(!original){$("eventNote").textContent="REFUSED: archived provenance pointer missing";return}
 const other=worlds.find(x=>x.side!==v.side);
 const exists=other.samples.some(x=>x.record.time_s===v.time_s);
 $("eventNote").textContent=v.side.toUpperCase()+" "+v.kind+" / exact source time "+fmt(v.time_s)+" s. Other side: "+(exists?"EXACT_ARCHIVED_SAMPLE_AT_TIME":"NO_RECORDED_SNAPSHOT_AT_TIME")+". No extrapolation/interpolation.";
 node("pre",JSON.stringify(original.record,null,2),details);
}
evsel.addEventListener("change",showEvent);showEvent();
const evid=$("evidence");
for(const e of BUNDLE.evidence.sources){
 node("p","PASS · "+e.side+" / "+e.source_schema_version+" · independent from-disk oracle "+e.verifier,evid).className="pass";
 node("small","Expected source SHA: "+e.expected_source_sha+" · frozen protocol: "+e.expected_protocol_sha+" · trusted anchor: "+e.trusted_anchor_ref,evid);
}
node("p","Projection oracle: "+BUNDLE.evidence.view_projection_oracle+" · Archive oracle: "+BUNDLE.evidence.archive_semantics_oracle,evid);
node("p","Read-only rendering; visible graphics are not additional physics evidence.",$("system"));
</script></body></html>"""
    return shell.replace("__V002_JSON__", raw)
