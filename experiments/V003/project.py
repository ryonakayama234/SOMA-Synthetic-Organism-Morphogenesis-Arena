"""V003 independent-authority researcher view assembler; NOT physics evidence.

Only publish after source + derived + view oracle checks. Never imports F022
producer or calls simulation; the existing V002 view schema remains untouched.
"""
from __future__ import annotations
import argparse
import math
import os
import shutil
import tempfile
from pathlib import Path

from experiments.V003.verify import (
    ORIGINAL_SHA, ORIGINAL_HASHES, RUN_ID, ARTIFACT_ID,
    read, read_rows, original, accept_source_receipt,
    verify_derived, hash_file, encode, schema,
)

def timeline(original_all, derived_samples, derived_contacts):
    pairs=[]
    for physical_index,row in original_all:
        pairs.append(dict(source="original",kind="sample",
                          source_row=physical_index,time_s=row["time_s"],phase="post"))
    for index,row in enumerate(derived_samples):
        pairs.append(dict(source="derived",kind="sample",
                          source_row=index,time_s=row["time_s"],phase="post"))
    for index,row in enumerate(derived_contacts):
        pairs.append(dict(source="derived",kind="contact",
                          source_row=index,time_s=row["time_s"],phase="event_pre_post"))
    return sorted(pairs,key=lambda x: (x["time_s"], 0 if x["kind"]=="contact" else 1,
                                       0 if x["source"]=="original" else 1))

def build_view(original_root,source_receipt,derived_root,derived_receipt):
    original_scenes=original(original_root)
    source_sha=accept_source_receipt(original_root,source_receipt)
    audit=verify_derived(derived_root,original_root,source_receipt)
    if read(derived_receipt)!=audit:
        raise AssertionError("derived independent oracle receipt not matched")
    old_scene=next(s for s in original_scenes if s["world_id"]=="C05")
    old_all=[(i,s) for i,s in enumerate(read_rows(Path(original_root)/"states.jsonl"))
             if s["world_id"]=="C05"]
    old_events=[c for c in read_rows(Path(original_root)/"contacts.jsonl")
                if c["world_id"]=="C05"]
    d=read(Path(derived_root)/"manifest.json")
    rows=read_rows(Path(derived_root)/"states.jsonl")
    events=read_rows(Path(derived_root)/"contacts.jsonl")
    if len(old_all)!=9 or old_events or len(rows)!=9 or len(events)>1:
        raise AssertionError("unexpected source/derived cardinality")
    ys=d["request"]["candidate_y_b_decimal"]
    changed=ys!="1.01"
    diff=([dict(field="y_b_m",original_m=old_scene["y_b_m"],
                derived_m=d["scenario"]["y_b_m"],changed=True)] if changed else [])
    a0=old_all[-1][1]
    a1=rows[-1]
    event=events[0] if events else None
    contrast=dict(
        free_flight_clearance_m=d["scenario"]["y_b_m"]-1.,
        contact_kind=event["kind"] if event else "no_contact",
        time_of_impact_s=event["time_s"] if event else None,
        normal_impulse_ns=event["impulse_ns"] if event else None,
        a_terminal_velocity_delta_norm_mps=math.hypot(
            a1["vx_a_mps"]-a0["vx_a_mps"],a1["vy_a_mps"]-a0["vy_a_mps"]),
        a_terminal_position_delta_norm_m=math.hypot(
            a1["x_a_m"]-a0["x_a_m"],a1["y_a_m"]-a0["y_a_m"]))
    view=dict(
        schema_version="v003.lab.v1",status="verified_projection",contract_id="V003",
        original=dict(authority="original_frozen_f022",scenario=old_scene,
                      states=[row for _,row in old_all],contacts=old_events,
                      manifest_sha256=ORIGINAL_HASHES["manifest.json"]),
        derived=dict(authority="derived_v003_independently_verified",
                     scenario=d["scenario"],states=rows,contacts=events,
                     manifest_sha256=hash_file(Path(derived_root)/"manifest.json"),
                     fork_id=d["fork_id"]),
        full_parameter_diff=diff,
        joint_sample_times_s=[i/4. for i in range(9)],
        timeline=timeline(old_all,rows,events),
        mechanical_contrast=contrast,cell_energy="not_modeled",
        evidence=dict(
            original_oracle="pass",derived_oracle="pass",projection_oracle="pass",
            original_manifest_sha256=ORIGINAL_HASHES["manifest.json"],
            derived_manifest_sha256=hash_file(Path(derived_root)/"manifest.json"),
            source_anchor="externally_inspected_checkout",
            producer_commit_sha=d["producer_commit_sha"],
            derived_oracle_receipt_sha256=hash_file(derived_receipt),
            original_source_commit_sha=ORIGINAL_SHA,
            original_workflow_run_id=RUN_ID,
            original_artifact_id=ARTIFACT_ID))
    schema(view,"v003.lab.v1.schema.json")
    return view

def publish(original_root,source_receipt,derived_root,derived_receipt,out):
    """Fail closed: independent view oracle BEFORE HTML publication."""
    from experiments.V003.verify_view import verify_view
    from experiments.V003.viewer import render
    out=Path(out)
    if out.exists(): raise FileExistsError(out)
    view=build_view(original_root,source_receipt,derived_root,derived_receipt)
    out.parent.mkdir(parents=True,exist_ok=True)
    tmp=Path(tempfile.mkdtemp(prefix="."+out.name+"-stage-",dir=out.parent))
    try:
        (tmp/"view.json").write_bytes(encode(view))
        verify_view(tmp/"view.json",original_root,source_receipt,derived_root,derived_receipt)
        (tmp/"index.html").write_text(render(view),encoding="utf-8",newline="\n")
        if out.exists(): raise FileExistsError(out)
        os.rename(tmp,out)
    finally:
        if tmp.exists(): shutil.rmtree(tmp)
    return {"fork_id":view["derived"]["fork_id"],"status":"verified_projection",
            "view_sha256":hash_file(out/"view.json")}

def main():
    p=argparse.ArgumentParser()
    for name in ("original-root","source-receipt","derived-root",
                 "derived-receipt","out"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    print(publish(a.original_root,a.source_receipt,a.derived_root,
                  a.derived_receipt,a.out))

if __name__=="__main__": main()
