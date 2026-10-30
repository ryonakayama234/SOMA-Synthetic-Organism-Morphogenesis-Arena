"""Self-contained offline V003 six-owner workspace. Researcher-only.

Never opens physical source files, runs a solver, interpolates an unsampled
snapshot, dispatches control to an agent or sends a browser request to Python.
The publishing caller MUST complete independent source/view verification first.
"""
from __future__ import annotations
import json

SHELL = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none';script-src 'nonce-v003';style-src 'nonce-v003';img-src 'none';connect-src 'none';form-action 'none';base-uri 'none'">
<title>SOMA / V003 CAUSAL FORK LAB</title>
<style nonce="v003">
:root{font-family:system-ui,"Segoe UI",sans-serif;color:#e4e4e4;background:#101113}
*{box-sizing:border-box}
html,body{height:100%;margin:0;overflow:hidden}
body{display:flex;flex-direction:column;font-size:12px}
header{height:58px;flex:none;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #393a3b;padding:0 18px;background:#171819}
h1{font-size:16px;letter-spacing:.1em;margin:0}
header span{font-size:11px;color:#b7b7b7}
main{flex:1;min-height:0;display:grid;grid-template-columns:minmax(215px,250px) minmax(0,1fr) minmax(245px,280px);
grid-template-rows:minmax(0,1fr) minmax(0,.72fr) 168px;grid-template-areas:"setup arena evidence" "cells arena system" "timeline timeline timeline";gap:10px;padding:10px}
section{border:1px solid #3c3e40;border-radius:6px;background:#1d1e20;min-width:0;min-height:0;overflow:hidden;display:flex;flex-direction:column}
section h2{font-size:11px;letter-spacing:.12em;margin:0;padding:11px 13px;border-bottom:1px solid #424345;flex:none;text-transform:uppercase}
.owner-body{overflow:auto;min-height:0;padding:10px 12px}
[data-panel=setup]{grid-area:setup}[data-panel=cells]{grid-area:cells}[data-panel=arena]{grid-area:arena;background:#151719;border-color:#666}
[data-panel=evidence]{grid-area:evidence}[data-panel=system]{grid-area:system}[data-panel=timeline]{grid-area:timeline}
label,button,select{font:inherit}button,select{background:#2b2d2e;color:#eee;border:1px solid #606164;border-radius:4px;padding:6px;cursor:pointer}
button:focus-visible,select:focus-visible{outline:2px solid #ddd}
.muted,small{color:#ababab;font-size:10px}
table{width:100%;border-collapse:collapse;font-size:10px;table-layout:fixed}
th,td{text-align:left;border-bottom:1px solid #3b3d3f;padding:5px 4px;overflow-wrap:anywhere}
th{position:sticky;top:0;background:#1d1e20}
.key{font-size:11px;color:#b5b5b5}
.value{font-variant-numeric:tabular-nums;overflow-wrap:anywhere;margin:4px 0 10px}
#arena-scenes{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:12px;flex:1;min-height:0}
.scene{display:flex;flex-direction:column;min-width:0;min-height:0;background:#1d2022;border:1px solid #4a4c4e;border-radius:5px;padding:8px}
.scene h3{margin:0 0 6px;font-size:11px}
.scene svg{width:100%;min-height:0;flex:1;display:block;background:#202326;border:1px solid #47494c}
.scene .muted{padding-top:5px}
#timeline-body{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:7px 12px;flex:1;min-height:0}
#timeline-list{overflow:auto;border:1px solid #3e4142;min-height:0}
.time-row{padding:4px 8px;border-bottom:1px solid #333;font-size:10px}
#event-detail{overflow:auto;min-height:0;white-space:pre-wrap;font:10px ui-monospace,monospace}
.time-tools{padding:7px 12px;display:flex;gap:10px;align-items:center;flex:none}
#inputdiff{max-height:65%;overflow:auto}
.note{margin:8px 0;padding:7px;border:1px solid #5a5a5a;color:#d0d0d0}
.disabled{border:1px dashed #5b5b5b;padding:8px;margin-top:8px;color:#aaa}
@media(max-width:1050px){main{grid-template-columns:210px minmax(0,1fr) 235px;gap:6px;padding:6px}#arena-scenes{gap:5px;padding:6px}}
</style></head><body>
<header><h1>SOMA · CAUSAL FORK LAB</h1><span id="header-status">VERIFICATION REQUIRED</span></header>
<main>
<section data-panel="setup"><h2>Setup</h2><div class="owner-body">
<div class="key">Approved single-coordinate fork · B initial Y [m]</div>
<label><select id="candidate" aria-label="approved B Y candidate"></select></label>
<button id="export" type="button">Export request JSON</button>
<div class="muted">Export only. No browser-to-simulator command.</div>
<div class="key" style="margin-top:10px">All 16 frozen physical fields</div><div id="inputdiff"></div></div></section>
<section data-panel="arena"><h2>Arena · same physical metre scale</h2><div id="arena-scenes">
<div class="scene"><h3>ORIGINAL · C05</h3><svg id="world-original" viewBox="0 0 340 260" aria-label="verified original stored XY"></svg><div class="muted">Source sample only</div></div>
<div class="scene"><h3>DERIVED · V003</h3><svg id="world-derived" viewBox="0 0 340 260" aria-label="verified derived stored XY"></svg><div class="muted" id="derived-status">NOT GENERATED</div></div>
</div><div class="muted" style="padding:0 12px 8px">Equal XY scale · radius = 0.5 m · archived sample positions only · no interpolation</div></section>
<section data-panel="cells"><h2>Cells</h2><div class="owner-body" id="cell-values"></div></section>
<section data-panel="evidence"><h2>Evidence</h2><div class="owner-body" id="evidence-values"></div></section>
<section data-panel="system"><h2>System/Data</h2><div class="owner-body" id="system-values"></div></section>
<section data-panel="timeline"><div class="time-tools"><h2 style="border:0;padding:0;margin-right:12px">Timeline</h2><label>Saved sample <select id="time-select"></select></label><span class="muted">Event clock is independent; no invented event snapshot</span></div>
<div id="timeline-body"><div id="timeline-list" aria-label="bounded archived event history"></div><div id="event-detail">Choose exact recorded event</div></div></section>
</main>
<script nonce="v003">
"use strict";
const MODEL=__V003_DATA__;
const isView=MODEL.mode==="verified_comparison", view=MODEL.view, orig=MODEL.original, der=isView?view.derived:null;
const $=x=>document.getElementById(x);
const add=(parent,tag,txt)=>{let e=document.createElement(tag);e.textContent=String(txt);parent.appendChild(e);return e};
const kv=(el,k,v)=>{add(el,"div",k).className="key";add(el,"div",v).className="value"};
const fmt=x=>x===null?"null":typeof x==="number"?String(x):String(x);
$("header-status").textContent=isView?"V003 VERIFIED COMPARISON / RESEARCHER ONLY":"V003 PREPARE REQUEST / NO DERIVED WORLD";
const yValues=Array.from({length:11},(_,i)=>((95+i)/100).toFixed(2));
for(const y of yValues){const opt=add($("candidate"),"option",y);opt.value=y;}
if(isView)$("candidate").value=view.derived.scenario.y_b_m.toFixed(2);else $("candidate").value="1.01";
$("export").onclick=()=>{
 const y=$("candidate").value;
 const request={schema_version:"v003.fork-request.v1",operation:"export_request_for_offline_runner",
 source_family:"f022.archive.v1",source_world_id:"C05",candidate_y_b_decimal:y,
 fork_id:"V003-Y"+y.replace(".",""),expected_source_commit_sha:"824a8621944ea438388c54949a2b65719be2e419",
 expected_frozen_protocol_sha:"3984e9dcb2cb420abab5ca92b4d029b31b5173f8"};
 const sorted=Object.fromEntries(Object.keys(request).sort().map(k=>[k,request[k]]));
 const blob=new Blob([JSON.stringify(sorted)+"\n"],{type:"application/json"});
 const a=document.createElement("a");a.href=URL.createObjectURL(blob);
 a.download=request.fork_id+".json";a.click();URL.revokeObjectURL(a.href);
};
function physicalTable(){
 const scene=isView?view.original.scenario:orig.scenario;
 const target=isView?view.derived.scenario:null;
 const t=add($("inputdiff"),"table","");
 let hr=add(t,"tr","");["Physical key","Original","Derived"].forEach(v=>add(hr,"th",v));
 for(const key of Object.keys(scene)){
   const tr=add(t,"tr","");
   add(tr,"td",key);add(tr,"td",fmt(scene[key]));add(tr,"td",target?fmt(target[key]):"NOT GENERATED");
 }
 const n=isView?view.full_parameter_diff.length:"NOT GENERATED";
 add($("inputdiff"),"div","Changed physical fields: "+n).className="muted";
} physicalTable();
for(let i=0;i<9;i++){const opt=add($("time-select"),"option",(i/4).toFixed(2)+" s");opt.value=String(i);}
function scene(svg,row){
 while(svg.firstChild)svg.removeChild(svg.firstChild);
 if(!row){add(svg,"text","NOT GENERATED").setAttribute("x","90");return;}
 const NS="http://www.w3.org/2000/svg", scale=44;
 const origin=[170,130];
 const el=(tag,attrs)=>{const e=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,String(v));svg.appendChild(e);return e};
 el("path",{d:"M0 130H340 M170 0V260",stroke:"#686b6f","stroke-width":0.7});
 for(const [label,x,y]of [["A",row.x_a_m,row.y_a_m],["B",row.x_b_m,row.y_b_m]]){
   const cx=origin[0]+x*scale,cy=origin[1]-y*scale;
   el("circle",{cx,cy,r:scale*0.5,fill:"#74797e","fill-opacity":0.2,stroke:"#bdbdbd","stroke-width":1.4});
   const text=el("text",{x:cx,y:cy+4,"text-anchor":"middle",fill:"#f0f0f0","font-size":13});text.textContent=label;
 }
}
function select(i){
 const old=isView?view.original.states[i]:orig.states[i];
 const current=isView?view.derived.states[i]:null;
 scene($("world-original"),old);scene($("world-derived"),current);
 $("derived-status").textContent=isView?"Verified derived saved sample":"NOT GENERATED";
 const target=$("cell-values");target.textContent="";
 for(const [side,row]of [["Original",old],["Derived",current]]){
   kv(target,side,row?"A x,y = "+row.x_a_m+", "+row.y_a_m+" m; v = "+row.vx_a_mps+", "+row.vy_a_mps+" m/s | B x,y = "+row.x_b_m+", "+row.y_b_m+" m; v = "+row.vx_b_mps+", "+row.vy_b_mps+" m/s":"NOT GENERATED");
 }
 kv(target,"Battery / motor","NOT MODELED in F022 (not zero)");
}
$("time-select").onchange=()=>select(Number($("time-select").value));
select(0);
const evidence=$("evidence-values");
if(isView){
 const e=view.evidence,c=view.mechanical_contrast;
 kv(evidence,"Original / derived / view oracle",e.original_oracle+" / "+e.derived_oracle+" / "+e.projection_oracle);
 kv(evidence,"Geometry · nominal FREE-flight clearance",fmt(c.free_flight_clearance_m)+" m (NOT actual penetration)");
 kv(evidence,"Physical contact class",c.contact_kind);
 kv(evidence,"Exact TOI / impulse",fmt(c.time_of_impact_s)+" s / "+fmt(c.normal_impulse_ns)+" N·s");
 kv(evidence,"A terminal Δvelocity (norm)",fmt(c.a_terminal_velocity_delta_norm_mps)+" m/s");
 kv(evidence,"A terminal Δposition (norm)",fmt(c.a_terminal_position_delta_norm_m)+" m");
 kv(evidence,"Raw derived provenance",view.derived.fork_id+" · "+e.derived_manifest_sha256.slice(0,16)+"...");
}else{
 kv(evidence,"Original source oracle","PASS · full frozen F022 archive");
 kv(evidence,"Derived source","NOT GENERATED");
 kv(evidence,"Projection","NOT RUN · nothing to display");
}
const sys=$("system-values");
kv(sys,"Interface contract","v003.workspace.layout.v1 · six V002 owners");
kv(sys,"Data contract",isView?"v003.lab.v1 · verified_projection":"v003.fork-request.v1 · export only");
kv(sys,"Original source commit","824a8621944ea438388c54949a2b65719be2e419");
kv(sys,"Source acquisition","GitHub Actions 40176213718 / artifact 12592745454");
add(sys,"div","LOCAL OBSERVATION / POLICY · RESERVED / NO API").className="disabled";
add(sys,"div","LEARNING · RESERVED / NOT IMPLEMENTED").className="disabled";
const log=$("timeline-list"), detail=$("event-detail");
if(isView){
 for(const row of view.timeline){
   const div=add(log,"div",row.time_s+"s · "+row.source+" / "+row.kind+" · source row "+row.source_row);
   div.className="time-row";
   if(row.kind==="contact")div.onclick=()=>{
     const event=view[row.source].contacts[row.source_row];
     detail.textContent="ACTUAL ARCHIVED EVENT (not a sampled frame)\n"+JSON.stringify(event,null,2);
   };
 }
}else{
 for(const row of orig.states)add(log,"div","Original saved sample · "+row.time_s+"s").className="time-row";
 detail.textContent="NO DERIVED EVENT / NOT GENERATED";
}
</script></body></html>'''

def render(view):
    if (view.get("schema_version")!="v003.lab.v1" or
        view.get("status")!="verified_projection" or
        any(view.get("evidence",{}).get(k)!="pass"
            for k in ("original_oracle","derived_oracle","projection_oracle"))):
        raise ValueError("refuse unverified view")
    data=dict(mode="verified_comparison",view=view,original=None)
    return _render(data)

def render_prepare(original_scene,original_states):
    if len(original_states)!=9 or original_scene.get("world_id")!="C05":
        raise ValueError("original-only preparation requires a verified C05")
    return _render(dict(mode="prepare_request",original=dict(
        scenario=original_scene,states=original_states),view=None))

def _render(data):
    raw=json.dumps(data,sort_keys=True,separators=(",",":"),allow_nan=False)
    raw=raw.replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    return SHELL.replace("__V003_DATA__",raw)
