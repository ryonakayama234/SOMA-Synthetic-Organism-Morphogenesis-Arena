"""V003 independent source-to-view semantic checker.

Never imports the projector, viewer, F022 producer, or any simulator.
Every displayed value is independently linked to two separately audited
source files; producer PASS flags or schema syntax never establish authority.
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path

from experiments.V003.verify import (
    ORIGINAL_SHA, ORIGINAL_HASHES, RUN_ID, ARTIFACT_ID, YS,
    original, accept_source_receipt, verify_derived, read, read_rows,
    encode, hash_file, schema, close,
)

def copied(got,ref,where):
    if encode(got)!=encode(ref): raise AssertionError(f"{where}: view/source substitution")

def source_rows(root,name,world):
    return [(i,row) for i,row in enumerate(read_rows(Path(root)/name))
            if row["world_id"]==world]

def expect_timeline(ori,derived,events):
    rows=[]
    for i,row in ori:
        rows.append(dict(source="original",kind="sample",source_row=i,
                         time_s=row["time_s"],phase="post"))
    for i,row in enumerate(derived):
        rows.append(dict(source="derived",kind="sample",source_row=i,
                         time_s=row["time_s"],phase="post"))
    for i,row in enumerate(events):
        rows.append(dict(source="derived",kind="contact",source_row=i,
                         time_s=row["time_s"],phase="event_pre_post"))
    rows.sort(key=lambda p:(p["time_s"],0 if p["kind"]=="contact" else 1,
                            0 if p["source"]=="original" else 1))
    return rows

def verify_view(view_file,original_root,source_receipt,derived_root,derived_receipt):
    all_original=original(original_root)
    trusted_source_digest=accept_source_receipt(original_root,source_receipt)
    independent_audit=verify_derived(derived_root,original_root,source_receipt)
    if read(derived_receipt)!=independent_audit:
        raise AssertionError("untrusted derived independent receipt")
    view=read(view_file)
    schema(view,"v003.lab.v1.schema.json")
    scene=next(s for s in all_original if s["world_id"]=="C05")
    original_with_idx=source_rows(original_root,"states.jsonl","C05")
    original_contacts=source_rows(original_root,"contacts.jsonl","C05")
    derived=read(Path(derived_root)/"manifest.json")
    d_scene=read(Path(derived_root)/"scenario.json")
    d_states=read_rows(Path(derived_root)/"states.jsonl")
    d_contacts=read_rows(Path(derived_root)/"contacts.jsonl")
    if len(original_with_idx)!=9 or original_contacts or len(d_states)!=9:
        raise AssertionError("source/sample mismatch")
    y=derived["request"]["candidate_y_b_decimal"]
    if y not in YS: raise AssertionError("non-frozen candidate")
    original_expected=dict(authority="original_frozen_f022",scenario=scene,
                           states=[row for _,row in original_with_idx],contacts=[],
                           manifest_sha256=ORIGINAL_HASHES["manifest.json"])
    derived_expected=dict(authority="derived_v003_independently_verified",
                          scenario=d_scene,states=d_states,contacts=d_contacts,
                          manifest_sha256=hash_file(Path(derived_root)/"manifest.json"),
                          fork_id=derived["fork_id"])
    copied(view["original"],original_expected,"original")
    copied(view["derived"],derived_expected,"derived")
    # Full 16-field diff rebuilt independently from the raw physical maps.
    keys=set(scene)
    if keys!=set(d_scene) or len(keys)!=16:
        raise AssertionError("16 fixed input fields")
    differences=[k for k in scene if (scene[k]!=d_scene[k] or
                                        type(scene[k])!=type(d_scene[k]))]
    if differences != ([] if y=="1.01" else ["y_b_m"]):
        raise AssertionError("not the exact one-variable intervention")
    expected_diff=([{"field":"y_b_m","original_m":scene["y_b_m"],
                     "derived_m":d_scene["y_b_m"],"changed":True}]
                   if differences else [])
    copied(view["full_parameter_diff"],expected_diff,"parameter diff")
    copied(view["joint_sample_times_s"],[i/4. for i in range(9)],"common saved grid")
    copied(view["timeline"],expect_timeline(original_with_idx,d_states,d_contacts),
           "true source-row chronology")
    event=d_contacts[0] if d_contacts else None
    ref_a=original_with_idx[-1][1]
    fork_a=d_states[-1]
    expected_contrast=dict(
        free_flight_clearance_m=d_scene["y_b_m"]-1.,
        contact_kind=event["kind"] if event else "no_contact",
        time_of_impact_s=event["time_s"] if event else None,
        normal_impulse_ns=event["impulse_ns"] if event else None,
        a_terminal_velocity_delta_norm_mps=math.hypot(
            fork_a["vx_a_mps"]-ref_a["vx_a_mps"],
            fork_a["vy_a_mps"]-ref_a["vy_a_mps"]),
        a_terminal_position_delta_norm_m=math.hypot(
            fork_a["x_a_m"]-ref_a["x_a_m"],
            fork_a["y_a_m"]-ref_a["y_a_m"]))
    # Signed A physics is checked by derived closed-form audit before the norms.
    # Physical predictions may use SI tolerance; a projected archive value
    # must instead copy its independently verified source *exactly*.
    if event is not None and event["kind"] == "grazing_zero_impulse":
        if type(event["impulse_ns"]) is not float or event["impulse_ns"] != 0.0:
            raise AssertionError("view source: grazing impulse must be exactly 0.0")
    copied(view["mechanical_contrast"]["normal_impulse_ns"],
           expected_contrast["normal_impulse_ns"],
           "exact source-to-view normal impulse")
    close(view["mechanical_contrast"],expected_contrast,"independent contrast")
    expected_evidence=dict(
        original_oracle="pass",derived_oracle="pass",projection_oracle="pass",
        original_manifest_sha256=ORIGINAL_HASHES["manifest.json"],
        derived_manifest_sha256=hash_file(Path(derived_root)/"manifest.json"),
        source_anchor="externally_inspected_checkout",
        producer_commit_sha=derived["producer_commit_sha"],
        derived_oracle_receipt_sha256=hash_file(derived_receipt),
        original_source_commit_sha=ORIGINAL_SHA,
        original_workflow_run_id=RUN_ID,original_artifact_id=ARTIFACT_ID)
    copied(view["evidence"],expected_evidence,"source/verifier authority")
    if view["cell_energy"]!="not_modeled":
        raise AssertionError("F022 battery/agent was fabricated")
    # Embedded controls use original full-roster evidence; they are NOT
    # independent physics proofs and cannot substitute the derived analytic audit.
    for source_id in (["C05"] if y=="1.01" else ["C06"] if y=="0.99"
                      else ["C07"] if y=="1.00" else []):
        archived_scene=next(s for s in all_original if s["world_id"]==source_id)
        for k in archived_scene:
            if k!="world_id" and (
                type(archived_scene[k])!=type(d_scene[k]) or
                archived_scene[k]!=d_scene[k]):
                raise AssertionError("archived positive-control scene")
        archived_states=[dict(row,world_id="C05")
                         for _,row in source_rows(original_root,"states.jsonl",source_id)]
        archived_events=[dict(row,world_id="C05")
                         for _,row in source_rows(original_root,"contacts.jsonl",source_id)]
        close(d_states,archived_states,"C05/C06/C07 physical frames")
        close(d_contacts,archived_events,"C05/C06/C07 true events")
    # Re-read both roots after verifying, so an untrusted view cannot overwrite.
    original(original_root)
    if hash_file(derived_receipt)!=expected_evidence["derived_oracle_receipt_sha256"]:
        raise AssertionError("receipt changed during comparison")
    return {"verified":"source-independent-v003-view","fork_id":derived["fork_id"],
            "source_receipt_sha256":trusted_source_digest,
            "view_sha256":hash_file(view_file)}

def main():
    p=argparse.ArgumentParser()
    for name in ("view","original-root","source-receipt","derived-root","derived-receipt"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    print(verify_view(a.view,a.original_root,a.source_receipt,
                      a.derived_root,a.derived_receipt))

if __name__=="__main__": main()
