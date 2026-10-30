"""V003 independent from-disk derived physics oracle. No simulator/producer import."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator
from experiments.F022.verify import verify as verify_f022

ORIGINAL_SHA = "824a8621944ea438388c54949a2b65719be2e419"
F022_FREEZE = "3984e9dcb2cb420abab5ca92b4d029b31b5173f8"
V003_FREEZE = "46860b42846e434a54c10e906c2212d2c24e4ab3"
RUN_ID, ARTIFACT_ID = 40176213718, 12592745454
ORIGINAL_HASHES = {
    "scenario.json": "498a16056ad7220aaee19080c1fd8064ba6d9c9c161808864cda94c3da565605",
    "states.jsonl": "ea2ead1117fe55d53d79791dbf190dc0740d02676d5bc79df7ff0d71d29c102c",
    "contacts.jsonl": "cee1c52bab4d9d0ca6dda92185a93fae8a7bb09be7660d14c87e4621da15b530",
    "audit.json": "dad1dd5891d0815c61980e4fc48f667458fbb87a51ac719ccd06b5c65b858d52",
    "manifest.json": "f0d5d9fd4e1d126b0f0e0f77fb5e796b7b3a0860118891c10c70d919e05fadc0",
}
YS = tuple(f"{n/100:.2f}" for n in range(95,106))
DIGESTS = dict(zip(YS, (
    "57c94a0dbcd474da5d985a7feb5b6bf3609e73e07751e4cc24751e19ce5baeff",
    "d11c7a99544efd02fb6d7a0ca9a8e91f469a7a1d5ebcfbc4a5267e30872efdf8",
    "bf26386b743043421658a64e9bcea0902fca56565a85a6d65c1b4dd71dc2796a",
    "ffea73dc4fd83feebb9f6537a510b00afc05caabe51fc534bbe1e5c437b07547",
    "ed943c86e037af97d57ae2702331b75e3c8f42c391034dbf9a3a43c77f743b44",
    "0b4911b8deb7882d6c92b474e77cca193d6c3190f66c6dfc5961bf163d817f60",
    "680e7366d781ce7f8e61272e91616ee70ce92f711b457a17b267ce2edd0daac7",
    "e9e1f5f1123c6540f3a3e94741f3de1fc84f1c06605af878b8756488e01751c6",
    "63857fea662ab3bd08a2d553261174cac778516f06ab97e6a9993e5aad079b7c",
    "0e375fafde7888f2c6f0c2320863cdd530a976189f1ac1d2e972c4377f4bc3bf",
    "9163ad3e75893913e1ef4c7bb5b802c1b106acdf8ece13e2d5eb66e769d78ec4",
)))
CONTRACTS = Path(__file__).resolve().parents[2] / "contracts"

def encode(obj):
    return (json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode("utf-8")

def hash_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def read(p):
    b=Path(p).read_bytes()
    v=json.loads(b,parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
    if b!=encode(v): raise AssertionError(f"noncanonical JSON: {p}")
    return v

def read_rows(p):
    b=Path(p).read_bytes()
    v=[json.loads(t,parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
       for t in b.decode("utf-8").splitlines()]
    if b!=b"".join(encode(row) for row in v):
        raise AssertionError(f"noncanonical JSONL: {p}")
    return v

def schema(obj,file):
    s=json.loads((CONTRACTS/file).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(s)
    Draft202012Validator(s).validate(obj)

def original(root):
    root=Path(root)
    if {p.name for p in root.iterdir()}!=set(ORIGINAL_HASHES):
        raise AssertionError("F022 original complete source file set")
    for name,expected in ORIGINAL_HASHES.items():
        if hash_file(root/name)!=expected: raise AssertionError(f"original SHA pin: {name}")
    manifest=read(root/"manifest.json")
    if (manifest["implementation_commit_sha"]!=ORIGINAL_SHA or
        manifest["frozen_protocol_commit_sha"]!=F022_FREEZE or
        manifest["schema_version"]!="f022.archive.v1"):
        raise AssertionError("untrusted original source identity")
    result=verify_f022(root,expected_source_sha=ORIGINAL_SHA)
    if (result["worlds"],result["states"],result["contacts"])!=(13,117,10):
        raise AssertionError("F022 full original roster")
    return read(root/"scenario.json")["worlds"]

def source_receipt(root):
    original(root)
    return dict(kind="v003.original-source-audit.v1",verdict="pass",
                original_source_commit_sha=ORIGINAL_SHA,
                original_frozen_protocol_sha=F022_FREEZE,
                workflow_run_id=RUN_ID,artifact_id=ARTIFACT_ID,
                source_file_sha256=ORIGINAL_HASHES,
                independent_verifier="experiments.F022.verify and external file pin")

def accept_source_receipt(root,receipt):
    if read(receipt)!=source_receipt(root):
        raise AssertionError("source receipt is not independently reproduced")
    return hash_file(receipt)

def close(got,ref,key="root"):
    if isinstance(ref,bool) or isinstance(got,bool):
        if type(got)!=type(ref) or got!=ref: raise AssertionError(key)
    elif isinstance(ref,(int,float)):
        if type(got) not in (int,float) or not math.isfinite(got) or not math.isfinite(ref):
            raise AssertionError(f"{key}: nonfinite/type")
        if abs(got-ref)>1e-9*max(1,abs(ref)):
            raise AssertionError(f"{key}: {got} vs {ref}")
    elif isinstance(ref,dict):
        if type(got)!=dict or set(got)!=set(ref): raise AssertionError(f"{key}: keys")
        for k in ref: close(got[k],ref[k],f"{key}.{k}")
    elif isinstance(ref,list):
        if type(got)!=list or len(got)!=len(ref): raise AssertionError(f"{key}: length")
        for i,(x,y) in enumerate(zip(got,ref)): close(x,y,f"{key}[{i}]")
    elif type(got)!=type(ref) or got!=ref: raise AssertionError(key)

def require_exact_grazing_impulse(event, key="contact"):
    """Enforce the frozen discrete j=0 meaning, never SI float tolerance."""
    if event["kind"] == "grazing_zero_impulse":
        impulse = event["impulse_ns"]
        if type(impulse) is not float or impulse != 0.0:
            raise AssertionError(f"{key}: grazing impulse must be exactly 0.0")


def physics(c05,y):
    """Closed-form independent mechanics for the fixed V003 predeclared geometry."""
    if y not in YS: raise AssertionError("unregistered coordinate")
    yy=float(y)
    s=dict(c05,y_b_m=yy)
    event=None
    if yy<=1.:
        q=math.sqrt(max(0.,1.-yy*yy))
        hit_time=1.-q/2.
        impulse=2.*q
        va=(1.-impulse*q,-impulse*yy)
        vb=(-1.+impulse*q,impulse*yy)
        pa=(-1.+hit_time,0.)
        pb=(1.-hit_time,yy)
        event=dict(world_id="C05",event_index=0,time_s=hit_time,
                   kind="grazing_zero_impulse" if yy==1. else "impulse",
                   normal_x=q,normal_y=yy,impulse_ns=impulse,
                   pre_x_a_m=pa[0],pre_y_a_m=pa[1],
                   pre_x_b_m=pb[0],pre_y_b_m=pb[1],
                   pre_vx_a_mps=1.,pre_vy_a_mps=0.,
                   pre_vx_b_mps=-1.,pre_vy_b_mps=0.,
                   post_vx_a_mps=va[0],post_vy_a_mps=va[1],
                   post_vx_b_mps=vb[0],post_vy_b_mps=vb[1],
                   restitution=1.)
    rows=[]
    for k in range(9):
        t=k/4.
        if event is not None and t>=event["time_s"]:
            dt=t-event["time_s"]
            va=(event["post_vx_a_mps"],event["post_vy_a_mps"])
            vb=(event["post_vx_b_mps"],event["post_vy_b_mps"])
            a=(event["pre_x_a_m"]+dt*va[0],event["pre_y_a_m"]+dt*va[1])
            b=(event["pre_x_b_m"]+dt*vb[0],event["pre_y_b_m"]+dt*vb[1])
        else:
            va,vb=(1.,0.),(-1.,0.)
            a,b=(-1.+t,0.),(1.-t,yy)
        rows.append(dict(world_id="C05",sample_index=k,time_s=t,phase="post",
                         x_a_m=a[0],y_a_m=a[1],x_b_m=b[0],y_b_m=b[1],
                         vx_a_mps=va[0],vy_a_mps=va[1],
                         vx_b_mps=vb[0],vy_b_mps=vb[1],
                         total_ke_j=.5*sum(z*z for z in (*va,*vb))))
    return s,rows,[] if event is None else [event]

def verify_derived(root,original_root,source_receipt_file):
    root=Path(root)
    original_scenes=original(original_root)
    source_hash=accept_source_receipt(original_root,source_receipt_file)
    if {p.name for p in root.iterdir()}!={
        "scenario.json","states.jsonl","contacts.jsonl","manifest.json"}:
        raise AssertionError("derived source file set")
    record=read(root/"manifest.json")
    schema(record,"v003.derived.v1.schema.json")
    y=record["request"]["candidate_y_b_decimal"]
    if (y not in DIGESTS or record["request"]["request_sha256"]!=DIGESTS[y] or
        record["fork_id"]!="V003-Y"+y.replace(".","")):
        raise AssertionError("not a frozen candidate/digest/ID")
    if record["source"]!=dict(
        source_family="f022.archive.v1",source_world_id="C05",
        original_manifest_sha256=ORIGINAL_HASHES["manifest.json"],
        original_source_commit_sha=ORIGINAL_SHA,
        original_frozen_protocol_sha=F022_FREEZE,
        external_trust_receipt_sha256=source_hash):
        raise AssertionError("derived has untrusted original pointer")
    raw_scene=read(root/"scenario.json")
    raw_samples=read_rows(root/"states.jsonl")
    raw_contacts=read_rows(root/"contacts.jsonl")
    for name in ("scenario.json","states.jsonl","contacts.jsonl"):
        if record["files_sha256"][name]!=hash_file(root/name):
            raise AssertionError(f"file SHA mismatched: {name}")
    if encode(record["scenario"])!=(root/"scenario.json").read_bytes():
        raise AssertionError("embedded scene differs from physical file")
    if b"".join(encode(row) for row in record["samples"])!=(root/"states.jsonl").read_bytes():
        raise AssertionError("embedded states differ from physical file")
    if b"".join(encode(row) for row in record["contacts"])!=(root/"contacts.jsonl").read_bytes():
        raise AssertionError("embedded contacts differ from physical file")
    c05=next(s for s in original_scenes if s["world_id"]=="C05")
    expected_s,expected_samples,expected_events=physics(c05,y)
    for key in c05:
        if key!="y_b_m" and (
            key not in raw_scene or type(raw_scene[key])!=type(c05[key])
            or raw_scene[key]!=c05[key]):
            raise AssertionError(f"second changed physical input: {key}")
    if type(raw_scene["y_b_m"]) is not float or raw_scene["y_b_m"]!=float(y):
        raise AssertionError("scene/request mismatch")
    close(raw_scene,expected_s,"scene")
    close(raw_samples,expected_samples,"samples")
    # The frozen grazing class requires exact j=0 even for rehashed archives.
    for i, event in enumerate(raw_contacts):
        require_exact_grazing_impulse(event, f"contacts[{i}]")
    close(raw_contacts,expected_events,"contacts")
    for row in raw_samples:
        if abs(row["vx_a_mps"]+row["vx_b_mps"])>1e-9:
            raise AssertionError("x momentum")
        if abs(row["vy_a_mps"]+row["vy_b_mps"])>1e-9:
            raise AssertionError("y momentum")
        if abs(row["total_ke_j"]-1.)>1e-9:
            raise AssertionError("kinetic energy")
        if math.hypot(row["x_a_m"]-row["x_b_m"],
                      row["y_a_m"]-row["y_b_m"])<1.-1e-9:
            raise AssertionError("penetration")
    original(original_root)
    return dict(kind="v003.derived-audit.v1",verdict="pass",
                fork_id=record["fork_id"],source_manifest_sha256=ORIGINAL_HASHES["manifest.json"],
                derived_manifest_sha256=hash_file(root/"manifest.json"),
                source_receipt_sha256=source_hash,
                files_sha256={k:hash_file(root/k) for k in
                              ("scenario.json","states.jsonl","contacts.jsonl")},
                independent_oracle="closed_form_all_rows_and_events")

def write_new(p,obj):
    with Path(p).open("xb") as f: f.write(encode(obj))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-root",type=Path,required=True)
    p.add_argument("--source-receipt",type=Path,required=True)
    p.add_argument("--derived-root",type=Path)
    p.add_argument("--derived-receipt",type=Path)
    a=p.parse_args()
    if a.derived_root:
        if not a.derived_receipt: p.error("--derived-receipt required")
        write_new(a.derived_receipt,verify_derived(a.derived_root,a.original_root,a.source_receipt))
        print("V003 derived audited PASS")
    else:
        write_new(a.source_receipt,source_receipt(a.original_root))
        print("F022 complete original audited PASS")

if __name__=="__main__": main()
