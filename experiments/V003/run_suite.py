"""V003.v1 bounded offline fork request/export and unverified passive F022 producer.

One approved B initial Y coordinate only; all original evidence immutable.
Simulation uses existing soma.f022.simulate without modification. No self-audit.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from soma.f022 import simulate
from experiments.V003.verify import (
    ORIGINAL_SHA,F022_FREEZE,ORIGINAL_HASHES,YS,DIGESTS,
    encode,hash_file,read,schema,original,accept_source_receipt,
)

def producer_sha():
    s=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    if len(s)!=40 or any(c not in "0123456789abcdef" for c in s):
        raise ValueError("invalid implementation provenance")
    return s

def frozen_request(y):
    if y not in YS:
        raise ValueError("not a frozen V003 y")
    obj=dict(schema_version="v003.fork-request.v1",
             operation="export_request_for_offline_runner",
             source_family="f022.archive.v1",
             source_world_id="C05",candidate_y_b_decimal=y,
             fork_id="V003-Y"+y.replace(".",""),
             expected_source_commit_sha=ORIGINAL_SHA,
             expected_frozen_protocol_sha=F022_FREEZE)
    schema(obj,"v003.fork-request.v1.schema.json")
    if hashlib.sha256(encode(obj)).hexdigest()!=DIGESTS[y]:
        raise AssertionError("preregistered canonical request digest mismatch")
    return obj

def export_requests(path):
    """Write eleven bounded JSON request files only; NO simulation."""
    path=Path(path)
    if path.exists(): raise FileExistsError(path)
    path.mkdir(parents=True)
    for y in YS:
        obj=frozen_request(y)
        (path/(obj["fork_id"]+".json")).write_bytes(encode(obj))
    return len(YS)

def accept_request(path):
    obj=read(path)
    schema(obj,"v003.fork-request.v1.schema.json")
    y=obj["candidate_y_b_decimal"]
    if obj!=frozen_request(y) or hashlib.sha256(Path(path).read_bytes()).hexdigest()!=DIGESTS[y]:
        raise AssertionError("request changed from frozen register")
    return obj

def produce(original_root,source_receipt_file,request_file,out,*,sha=None):
    """Produce one RAW unverified derived root; independent oracle separately required."""
    out=Path(out)
    if out.exists(): raise FileExistsError(out)
    source_receipt_sha=accept_source_receipt(original_root,source_receipt_file)
    req=accept_request(request_file)
    baseline=next(s for s in original(original_root) if s["world_id"]=="C05")
    scene=dict(baseline,y_b_m=float(req["candidate_y_b_decimal"]))
    samples,contacts=simulate(scene)
    if len(samples)!=9 or len(contacts)>1:
        raise AssertionError("unexpected new F022 cardinality")
    source_sha=producer_sha() if sha is None else sha
    if not isinstance(source_sha,str) or len(source_sha)!=40 or any(
        c not in "0123456789abcdef" for c in source_sha):
        raise ValueError("invalid producer source commit")
    out.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix="."+out.name+"-stage-",dir=out.parent))
    try:
        (stage/"scenario.json").write_bytes(encode(scene))
        (stage/"states.jsonl").write_bytes(b"".join(encode(x) for x in samples))
        (stage/"contacts.jsonl").write_bytes(b"".join(encode(x) for x in contacts))
        manifest=dict(
            schema_version="v003.derived.v1",status="unverified_derived",
            fork_id=req["fork_id"],
            request={"candidate_y_b_decimal":req["candidate_y_b_decimal"],
                     "request_sha256":DIGESTS[req["candidate_y_b_decimal"]]},
            source={"source_family":"f022.archive.v1","source_world_id":"C05",
                    "original_manifest_sha256":ORIGINAL_HASHES["manifest.json"],
                    "original_source_commit_sha":ORIGINAL_SHA,
                    "original_frozen_protocol_sha":F022_FREEZE,
                    "external_trust_receipt_sha256":source_receipt_sha},
            scenario=scene,samples=samples,contacts=contacts,
            energy_model="not_modeled",producer_commit_sha=source_sha,
            independent_derived_oracle="not_run",original_archive_unchanged=True,
            files_sha256={k:hash_file(stage/k) for k in
                          ("scenario.json","states.jsonl","contacts.jsonl")})
        schema(manifest,"v003.derived.v1.schema.json")
        (stage/"manifest.json").write_bytes(encode(manifest))
        original(original_root)
        if out.exists(): raise FileExistsError(out)
        os.rename(stage,out)
    finally:
        if stage.exists(): shutil.rmtree(stage)
    return {"fork_id":req["fork_id"],"status":"unverified_derived",
            "sample_count":len(samples),"event_count":len(contacts),
            "manifest_sha256":hash_file(out/"manifest.json")}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--export-requests",type=Path,help="Export 11 frozen requests only")
    p.add_argument("--original-root",type=Path)
    p.add_argument("--source-receipt",type=Path)
    p.add_argument("--request",type=Path)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    if a.export_requests:
        print("V003 request files exported:",export_requests(a.export_requests))
    else:
        if not all((a.original_root,a.source_receipt,a.request,a.out)):
            p.error("--original-root --source-receipt --request --out all required")
        print(json.dumps(produce(a.original_root,a.source_receipt,a.request,a.out),
                         sort_keys=True))

if __name__=="__main__": main()
