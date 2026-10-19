"""F009 independent exact-Fraction oracle for saved evidence.

Does not import or call soma.f009. It trusts the current checkout as a source
comparison anchor only; CI/Git HEAD identity must be verified separately.
"""
from __future__ import annotations
import csv
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

SCHEMA = "f009.momentum.v1"
NAMES = ("A","B","C","D","E","F")
COLUMNS = (
    "step_index","time_s","x_a_m","x_b_m","v_a_m_s","v_b_m_s",
    "external_force_a_n","external_force_b_n","internal_force_a_n",
    "internal_force_b_n","ground_traction_n","ground_reaction_n",
    "link_force_a_n","link_force_b_n","p_before_kg_m_s",
    "p_after_kg_m_s","external_impulse_ns","momentum_residual_ns",
)
SOURCES = (
    "soma/f009.py","experiments/F009/run_suite.py","experiments/F009/verify.py",
    "tests/test_f009.py",".github/workflows/f009.yml",
    "topics/F009-reaction-momentum/SPEC.md","experiments/F009/PLAN.md",
    "findings/F009-validation.md","experiments/F009/README.md",
    "docs/ARCHITECTURE.md","docs/DATA_CONTRACTS.md","README.md","AGENTS.md",
)
FINAL = {
    "A":(Q(5,8),Q(9,8),Q(1),Q(1)),
    "B":(Q(0),Q(1,2),Q(0),Q(0)),
    "C":(Q(5,8),Q(9,8),Q(1),Q(1)),
    "D":(Q(0),Q(1,2),Q(0),Q(0)),
    "E":(Q(5,4),Q(1,2),Q(2),Q(0)),
    "F":(Q(5,16),Q(13,16),Q(1,2),Q(1,2)),
}


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def trusted_sources(root: Path | None = None) -> dict[str,str]:
    checkout = root or Path(__file__).resolve().parents[2]
    return {p: sha(checkout/p) for p in SOURCES}


def oracle(case: str) -> list[dict]:
    check(case in NAMES, "unknown case")
    h = Q(1,4)
    is_linked = case != "E"
    external = Q(2) if case in "ACE" else Q(1) if case == "F" else Q(0)
    traction = external if case in "CEF" else Q(0)
    internal_a,internal_b = (Q(2),Q(-2)) if case == "B" else (Q(0),Q(0))
    fa, fb = external + internal_a, internal_b
    out = []
    for k in range(5):
        if k:
            v_a = k*h*(fa+fb)/2 if is_linked else k*h*fa
            v_b = v_a if is_linked else k*h*fb
            x_a = h*h*k*(k+1)*(fa+fb)/4 if is_linked else h*h*k*(k+1)*fa/2
            x_b = Q(1,2)+(x_a if is_linked else h*h*k*(k+1)*fb/2)
            link_b = (fa-fb)/2 if is_linked else Q(0)
            before = (k-1)*h*(fa+fb)
            after = k*h*(fa+fb)
            impulse = h*external
            fields = (k,k*h,x_a,x_b,v_a,v_b,external,Q(0),
                      internal_a,internal_b,traction,-traction,-link_b,link_b,
                      before,after,impulse,Q(0))
        else:
            fields = (0,Q(0),Q(0),Q(1,2),Q(0),Q(0))+(Q(0),)*12
        out.append(dict(zip(COLUMNS,fields)))
    return out


def verify_run(folder: Path) -> dict:
    folder = Path(folder)
    c = json.loads((folder/"config.json").read_text(encoding="utf-8"))
    m = json.loads((folder/"manifest.json").read_text(encoding="utf-8"))
    check(type(c) is dict and set(c)=={
        "schema_version","experiment_id","seed","dt_s","duration_s",
        "mass_a_kg","mass_b_kg","x_a0_m","x_b0_m","v_a0_m_s","v_b0_m_s",
        "link_length_m","attached","force_origin","drive_command_n",
        "contact_enabled","traction_limit_n"}, "config schema")
    check(c["schema_version"]==SCHEMA and type(c["experiment_id"]) is str
          and c["experiment_id"].startswith("F009-"),"config ID")
    case=c["experiment_id"][5:]
    check(case in NAMES, "unknown case")
    normal={
        "schema_version":SCHEMA,"experiment_id":"F009-"+case,"seed":None,
        "dt_s":0.25,"duration_s":1.0,"mass_a_kg":1.0,"mass_b_kg":1.0,
        "x_a0_m":0.0,"x_b0_m":0.5,"v_a0_m_s":0.0,"v_b0_m_s":0.0,
        "link_length_m":0.5,"attached":case!="E",
        "force_origin":"legacy_effective" if case=="A" else
            "internal_pair" if case=="B" else "ground_contact",
        "drive_command_n":2.0,"contact_enabled":case in "CEF",
        "traction_limit_n":1.0 if case=="F" else 2.0,
    }
    check(c==normal and all(type(c[k]) is type(v) for k,v in normal.items()),"fixed configuration changed")
    expected_manifest={
        "schema_version":"f009.evidence.v1","case":c["experiment_id"],
        "artifacts":{p:sha(folder/p) for p in ("config.json","steps.csv")},
        "source_hashes":trusted_sources(),
        "status":"model_result_candidate_not_adopted",
    }
    check(m==expected_manifest,"evidence origin, semantics or hash mismatch")
    with (folder/"steps.csv").open(newline="",encoding="utf-8") as stream:
        reader=csv.DictReader(stream)
        check(tuple(reader.fieldnames or ())==COLUMNS,"CSV columns changed")
        rows=list(reader)
    expect=oracle(case)
    check(len(rows)==5,"missing or extra steps")
    for actual, reference in zip(rows,expect):
        check(set(actual)==set(COLUMNS),"unknown CSV fields")
        for name,want in reference.items():
            raw=actual[name]
            check(raw is not None and raw!="","empty numeric field")
            try:
                value=Q(raw)
            except (ValueError,ZeroDivisionError) as exc:
                raise ValueError("invalid numeric field "+name) from exc
            check(abs(value-want)<=Q(1,10**12),f"step {reference['step_index']} {name} differs")
    last=expect[-1]
    check(tuple(last[k] for k in ("x_a_m","x_b_m","v_a_m_s","v_b_m_s"))==FINAL[case],
          "frozen Wolfram terminal reference mismatch")
    return {"case":case,"rows":len(rows),"final":{k:float(last[k]) for k in
        ("x_a_m","x_b_m","v_a_m_s","v_b_m_s")}}


def verify_suite(root: Path) -> dict:
    root=Path(root)
    summary=json.loads((root/"comparison.json").read_text(encoding="utf-8"))
    cases=[verify_run(root/name) for name in NAMES]
    check(summary=={"schema_version":"f009.comparison.v1",
                    "science_status":"model_result_candidate_not_adopted",
                    "cases":cases}, "comparison semantic mismatch")
    actual={p.relative_to(root).as_posix():sha(p) for p in sorted(root.rglob("*"))
            if p.is_file() and p.name!="suite_manifest.json"}
    manifest=json.loads((root/"suite_manifest.json").read_text(encoding="utf-8"))
    check(manifest=={"schema_version":"f009.suite.v1","cases":list(NAMES),
                     "artifacts":actual,"source_hashes":trusted_sources()},
          "suite manifest or files altered")
    check(set(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
          ==set(actual)|{"suite_manifest.json"},"unexpected suite file")
    return summary
