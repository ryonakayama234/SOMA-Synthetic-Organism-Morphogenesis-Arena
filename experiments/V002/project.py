"""V002.v1: source-verified, observer-only, two-world 2D archive projection.

This module MUST NOT import soma.f022/f023 or the experiment producers.
It invokes the separately implemented source-independent archived-data oracles.
No physical integration, interpolation, agent observation or archive write exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from experiments.F022.verify import verify as verify_f022, read_lines, read_one
from experiments.F023.verify import verify as verify_f023

SCHEMA_VERSION = "v002.view.v1"
FROZEN_V002 = "4ba05357a426edaa7ec6e9d1d5f905ad64893de8"
FREEZES = {
    "f022.archive.v1": "3984e9dcb2cb420abab5ca92b4d029b31b5173f8",
    "f023.archive.v1": "76dcc1db7ae12737705da06c155933d0a8251853",
}
FILE_STEMS = ("scenario", "states", "contacts", "audit", "manifest")
SOURCE_KEYS = ("scenario_sha256", "states_sha256", "contacts_sha256", "audit_sha256",
               "manifest_sha256")


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _source_files(schema):
    names = ["scenario.json", "states.jsonl", "contacts.jsonl",
             "audit.json", "manifest.json"]
    if schema == "f023.archive.v1":
        names += ["actions.jsonl", "ledger.jsonl"]
    return names


def _reject_extra_files(root, expected):
    actual = {p.name for p in root.iterdir() if p.is_file()}
    if actual != set(expected):
        raise AssertionError(f"source file set differs: {actual ^ set(expected)}")


def _trusted_source(root, side, expected_sha, trusted_anchor):
    """Trust identity supplied by caller, never by the archive manifest."""
    if not isinstance(trusted_anchor, str) or not trusted_anchor.strip():
        raise ValueError("trusted anchor reference required")
    if not isinstance(expected_sha, str) or len(expected_sha) != 40 or any(
        x not in "0123456789abcdef" for x in expected_sha
    ):
        raise ValueError("expected source SHA must be externally supplied")
    root = Path(root)
    manifest = read_one(root / "manifest.json")
    version = manifest["schema_version"]
    if version not in FREEZES:
        raise ValueError("unsupported archive schema")
    if manifest["frozen_protocol_commit_sha"] != FREEZES[version]:
        raise AssertionError("untrusted frozen-protocol identity")
    names = _source_files(version)
    _reject_extra_files(root, names)
    oracle = verify_f022 if version == "f022.archive.v1" else verify_f023
    oracle(root, expected_source_sha=expected_sha)
    # Verify the archive has not changed since oracle execution.
    mapping = {"scenario.json": "scenario_sha256", "states.jsonl": "states_sha256",
               "contacts.jsonl": "contacts_sha256", "audit.json": "audit_sha256",
               "manifest.json": "manifest_sha256", "actions.jsonl": "actions_sha256",
               "ledger.jsonl": "ledger_sha256"}
    hashes = {mapping[name]: digest(root / name) for name in names}
    return version, {
        "side": side,
        "expected_source_sha": expected_sha,
        "expected_protocol_sha": FREEZES[version],
        "verifier": "experiments.F022.verify" if version == "f022.archive.v1"
                    else "experiments.F023.verify",
        "verdict": "pass",
        "trusted_anchor_ref": trusted_anchor,
        "source_schema_version": version,
        "file_hashes": hashes,
    }


def _indexed_rows(root, file_name, world_id):
    rows = read_lines(root / file_name)
    return [{"source_row": i, "record": row} for i, row in enumerate(rows)
            if row["world_id"] == world_id]


def _one_world(root, side, world_id, schema, evidence):
    root = Path(root)
    settings = read_one(root / "scenario.json")["worlds"]
    scene_list = [s for s in settings if s["world_id"] == world_id]
    if len(scene_list) != 1:
        raise ValueError(f"unrecognized/duplicate world {world_id}")
    states = _indexed_rows(root, "states.jsonl", world_id)
    events = _indexed_rows(root, "contacts.jsonl", world_id)
    if len(states) != 9 or len(events) > 1:
        raise AssertionError("frozen world row count differs")
    if any(row["record"]["phase"] != "post" for row in states):
        raise AssertionError("sample phase is not post")
    cell = {"kind": "not_modeled"}
    if schema == "f023.archive.v1":
        actions = _indexed_rows(root, "actions.jsonl", world_id)
        ledger = _indexed_rows(root, "ledger.jsonl", world_id)
        if len(actions) != 2 or len(ledger) != 2:
            raise AssertionError("private cell source cardinality")
        cell = {"kind": "f023_private", "actions": actions, "ledger": ledger}
    return {
        "side": side, "world_id": world_id,
        "trusted_source_sha": evidence["expected_source_sha"],
        "frozen_protocol_sha": evidence["expected_protocol_sha"],
        "manifest_sha256": evidence["file_hashes"]["manifest_sha256"],
        "samples": states, "contacts": events,
        "source_schema_version": schema,
        "scenario": scene_list[0], "cell_model": cell,
    }


def _timeline(worlds):
    order = {"action": 0, "contact": 1, "sample": 2}
    result = []
    for w in worlds:
        for name, kind in [("samples", "sample"), ("contacts", "contact")]:
            for row in w[name]:
                result.append({
                    "side": w["side"], "kind": kind,
                    "time_s": row["record"]["time_s"],
                    "source_file": "states.jsonl" if kind == "sample" else "contacts.jsonl",
                    "source_row": row["source_row"],
                })
        if w["cell_model"]["kind"] == "f023_private":
            for row in w["cell_model"]["actions"]:
                result.append({
                    "side": w["side"], "kind": "action",
                    "time_s": row["record"]["time_s"],
                    "source_file": "actions.jsonl",
                    "source_row": row["source_row"],
                })
    return sorted(result, key=lambda x: (x["time_s"], order[x["kind"]],
                                         0 if x["side"] == "left" else 1,
                                         x["source_row"]))


def _parameter_diff(a, b):
    keys = sorted((set(a) | set(b)) - {"world_id"})
    if set(a) != set(b):
        raise AssertionError("mixed world input schema")
    return [{"field_path": k, "left": a[k], "right": b[k],
             "equal": type(a[k]) is type(b[k]) and a[k] == b[k]} for k in keys]


def _assert_exact_oracle(view, left_root, right_root):
    """Distinct read-back source comparison: checks copied rows and provenance."""
    for w, root in zip(view["worlds"], (left_root, right_root)):
        scenario = read_one(Path(root) / "scenario.json")["worlds"]
        originals = [x for x in scenario if x["world_id"] == w["world_id"]]
        if len(originals) != 1 or w["scenario"] != originals[0]:
            raise AssertionError("viewer scenario differs from verified source")
        for prop, name in (("samples", "states.jsonl"), ("contacts", "contacts.jsonl")):
            expected = _indexed_rows(root, name, w["world_id"])
            if w[prop] != expected:
                raise AssertionError("viewer projected records differ from source")
        if w["source_schema_version"] == "f023.archive.v1":
            for prop, name in (("actions", "actions.jsonl"), ("ledger", "ledger.jsonl")):
                if w["cell_model"][prop] != _indexed_rows(root, name, w["world_id"]):
                    raise AssertionError("viewer private cell records differ")
        else:
            if w["cell_model"] != {"kind": "not_modeled"}:
                raise AssertionError("F022 private motor values invented")
    a, b = (w["scenario"] for w in view["worlds"])
    diffs = _parameter_diff(a, b)
    if view["parameter_diff"] != diffs:
        raise AssertionError("viewer input diff differs")
    if view["timeline"] != _timeline(view["worlds"]):
        raise AssertionError("viewer timeline differs")


def project(left_root, right_root, left_id, right_id, *, expected_left_sha,
            expected_right_sha, trusted_left_anchor, trusted_right_anchor):
    left_root, right_root = Path(left_root), Path(right_root)
    ltype, lp = _trusted_source(left_root, "left", expected_left_sha, trusted_left_anchor)
    rtype, rp = _trusted_source(right_root, "right", expected_right_sha, trusted_right_anchor)
    if ltype != rtype:
        raise ValueError("cross-family 2D comparison prohibited by v1 freeze")
    worlds = [_one_world(left_root, "left", left_id, ltype, lp),
              _one_world(right_root, "right", right_id, rtype, rp)]
    t1 = {x["record"]["time_s"] for x in worlds[0]["samples"]}
    t2 = {x["record"]["time_s"] for x in worlds[1]["samples"]}
    common = sorted(t1 & t2)
    if len(common) != 9:
        raise AssertionError("frozen common sample grid differs")
    differences = _parameter_diff(worlds[0]["scenario"], worlds[1]["scenario"])
    count = sum(not d["equal"] for d in differences)
    view = {
        "schema_version": SCHEMA_VERSION, "status": "verified_projection",
        "contract_id": "V002", "worlds": worlds,
        "joint_sample_times_s": common, "timeline": _timeline(worlds),
        "parameter_diff": differences,
        "pair_inference": "identical" if count == 0 else
                          ("single_field" if count == 1 else "multi_field"),
        "evidence": {"sources": [lp, rp], "archive_semantics_oracle": "pass",
                     "view_projection_oracle": "pass"},
    }
    _assert_exact_oracle(view, left_root, right_root)
    # Use frozen schema as executable contract; never add undocumented view keys.
    from jsonschema import Draft202012Validator
    schema_path = Path(__file__).resolve().parents[2] / "contracts/v002.view.v1.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(view)
    # Verify complete schema constraints, including two same-family sides.
    return view


def publish(dest, view):
    """Single successful immutable output. Never replace/partially publish."""
    dest = Path(dest)
    if dest.exists():
        raise FileExistsError(f"refuse existing V002 output: {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f".{dest.name}-v002-", dir=dest.parent))
    try:
        (tmp / "view.json").write_text(canonical(view) + "\n", encoding="utf-8", newline="\n")
        from experiments.V002.viewer import render
        (tmp / "index.html").write_text(render(view), encoding="utf-8", newline="\n")
        if dest.exists():
            raise FileExistsError("output was concurrently created")
        os.rename(tmp, dest)
    finally:
        if tmp.exists():
            shutil.rmtree(tmp)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--left-root", type=Path, required=True)
    p.add_argument("--right-root", type=Path, required=True)
    p.add_argument("--left-world", required=True)
    p.add_argument("--right-world", required=True)
    p.add_argument("--expected-left-sha", required=True)
    p.add_argument("--expected-right-sha", required=True)
    p.add_argument("--trusted-left-anchor", required=True)
    p.add_argument("--trusted-right-anchor", required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    bundle = project(args.left_root, args.right_root, args.left_world, args.right_world,
                     expected_left_sha=args.expected_left_sha,
                     expected_right_sha=args.expected_right_sha,
                     trusted_left_anchor=args.trusted_left_anchor,
                     trusted_right_anchor=args.trusted_right_anchor)
    publish(args.out, bundle)
    print(canonical({"out": str(args.out), "schema": bundle["schema_version"],
                     "comparison": bundle["pair_inference"]}))


if __name__ == "__main__":
    main()
