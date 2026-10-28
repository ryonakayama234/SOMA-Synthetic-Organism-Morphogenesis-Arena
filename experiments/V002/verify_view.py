"""Independent V002 derived-view verifier; DOES NOT import the projector or viewer.

Check every derived numerical record/source index and metadata against *freshly*
source-verified archives and the externally supplied source identity. A
self-consistent or rehashed view.json alone is never trusted as evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from experiments.F022.verify import verify as verify_f022, read_lines, read_one
from experiments.F023.verify import verify as verify_f023

SCHEMAS = {"f022.archive.v1": verify_f022, "f023.archive.v1": verify_f023}
FREEZES = {"f022.archive.v1": "3984e9dcb2cb420abab5ca92b4d029b31b5173f8",
           "f023.archive.v1": "76dcc1db7ae12737705da06c155933d0a8251853"}


def _hash(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _expected_rows(root, name, world_id):
    return [{"source_row": n, "record": record}
            for n, record in enumerate(read_lines(Path(root) / name))
            if record["world_id"] == world_id]


def verify_view(view_file, left_root, right_root, *, expected_left_sha, expected_right_sha,
                trusted_left_anchor, trusted_right_anchor):
    path = Path(view_file)
    source = path.read_bytes()
    view = json.loads(source.decode("utf-8"),
                      parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))
    canonical = (json.dumps(view, sort_keys=True, separators=(",", ":"), allow_nan=False)
                 + "\n").encode("utf-8")
    if source != canonical:
        raise AssertionError("noncanonical derived V002 artifact")
    frozen_schema = json.loads(
        (Path(__file__).resolve().parents[2] / "contracts/v002.view.v1.schema.json")
        .read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(frozen_schema)
    Draft202012Validator(frozen_schema).validate(view)
    if view["schema_version"] != "v002.view.v1" or view["status"] != "verified_projection":
        raise AssertionError("unqualified view status")
    roots = [Path(left_root), Path(right_root)]
    external_shas = [expected_left_sha, expected_right_sha]
    anchors = [trusted_left_anchor, trusted_right_anchor]
    for sha, anchor in zip(external_shas, anchors):
        if type(sha) is not str or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError("invalid external expected-source identity")
        if type(anchor) is not str or not anchor.strip():
            raise ValueError("external trusted-anchor note required")
    expected_timeline = []
    inputs = []
    families = []
    order = {"action": 0, "contact": 1, "sample": 2}
    for index, (root, w) in enumerate(zip(roots, view["worlds"])):
        side = ("left", "right")[index]
        if w["side"] != side or view["evidence"]["sources"][index]["side"] != side:
            raise AssertionError("side identity swapped")
        manifest = read_one(root / "manifest.json")
        family = manifest["schema_version"]
        if family not in SCHEMAS or family != w["source_schema_version"]:
            raise AssertionError("wrong source family")
        families.append(family)
        if manifest["frozen_protocol_commit_sha"] != FREEZES[family]:
            raise AssertionError("wrong immutable protocol")
        if manifest["implementation_commit_sha"] != external_shas[index]:
            raise AssertionError("externally expected SHA differs from archived identity")
        names = ["scenario.json", "states.jsonl", "contacts.jsonl",
                 "audit.json", "manifest.json"]
        if family == "f023.archive.v1":
            names += ["actions.jsonl", "ledger.jsonl"]
        if {p.name for p in root.iterdir() if p.is_file()} != set(names):
            raise AssertionError("wrong source archive file set")
        SCHEMAS[family](root, expected_source_sha=external_shas[index])
        expected_hashes = {name.replace(".jsonl", "").replace(".json", "") + "_sha256":
                           _hash(root / name) for name in names}
        expected_hashes = dict(zip(
            ({"scenario.json": "scenario_sha256", "states.jsonl": "states_sha256",
              "contacts.jsonl": "contacts_sha256", "audit.json": "audit_sha256",
              "manifest.json": "manifest_sha256", "actions.jsonl": "actions_sha256",
              "ledger.jsonl": "ledger_sha256"}[x] for x in names),
            (_hash(root / x) for x in names)))
        e = view["evidence"]["sources"][index]
        fields = {"side": side, "expected_source_sha": external_shas[index],
                  "expected_protocol_sha": FREEZES[family],
                  "verifier": "experiments.F022.verify" if family == "f022.archive.v1"
                              else "experiments.F023.verify",
                  "verdict": "pass", "trusted_anchor_ref": anchors[index],
                  "source_schema_version": family, "file_hashes": expected_hashes}
        if e != fields:
            raise AssertionError("derived evidence/provenance differs from checked source")
        scene = [v for v in read_one(root / "scenario.json")["worlds"]
                 if v["world_id"] == w["world_id"]]
        if len(scene) != 1 or scene[0] != w["scenario"]:
            raise AssertionError("derivative scenario substitution")
        inputs.append(scene[0])
        if w["trusted_source_sha"] != external_shas[index] or (
            w["frozen_protocol_sha"] != FREEZES[family] or
            w["manifest_sha256"] != expected_hashes["manifest_sha256"]
        ):
            raise AssertionError("world provenance overwritten")
        for key, filename, kind in [
            ("samples", "states.jsonl", "sample"),
            ("contacts", "contacts.jsonl", "contact"),
        ]:
            expected = _expected_rows(root, filename, w["world_id"])
            if w[key] != expected:
                raise AssertionError(f"edited or omitted archived {filename}")
            for row in expected:
                expected_timeline.append({
                    "side": side, "kind": kind, "time_s": row["record"]["time_s"],
                    "source_file": filename, "source_row": row["source_row"]})
        if family == "f022.archive.v1":
            if w["cell_model"] != {"kind": "not_modeled"}:
                raise AssertionError("F022 private ledger fabricated")
        else:
            if w["cell_model"]["kind"] != "f023_private":
                raise AssertionError("F023 private ledger dropped")
            for key, file in (("actions", "actions.jsonl"), ("ledger", "ledger.jsonl")):
                if w["cell_model"][key] != _expected_rows(root, file, w["world_id"]):
                    raise AssertionError("modified/pooled private budget or action")
            for row in w["cell_model"]["actions"]:
                expected_timeline.append({
                    "side": side, "kind": "action", "time_s": row["record"]["time_s"],
                    "source_file": "actions.jsonl", "source_row": row["source_row"]})
    if families[0] != families[1]:
        raise AssertionError("cross-family scene pairs prohibited in frozen v1")
    expected_timeline.sort(key=lambda z: (z["time_s"], order[z["kind"]],
                                          0 if z["side"] == "left" else 1, z["source_row"]))
    if view["timeline"] != expected_timeline:
        raise AssertionError("edited event/source timeline or ordering")
    joint = sorted({v["record"]["time_s"] for v in view["worlds"][0]["samples"]}
                   & {v["record"]["time_s"] for v in view["worlds"][1]["samples"]})
    if len(joint) != 9 or view["joint_sample_times_s"] != joint:
        raise AssertionError("fake or dropped joint sample instant")
    expected_diffs = [
        {"field_path": k, "left": inputs[0][k], "right": inputs[1][k],
         "equal": type(inputs[0][k]) is type(inputs[1][k]) and inputs[0][k] == inputs[1][k]}
        for k in sorted(set(inputs[0]) - {"world_id"})
    ]
    if view["parameter_diff"] != expected_diffs:
        raise AssertionError("edited counterfactual input difference")
    changed = sum(not x["equal"] for x in expected_diffs)
    expected_inference = "identical" if changed == 0 else (
        "single_field" if changed == 1 else "multi_field")
    if view["pair_inference"] != expected_inference:
        raise AssertionError("false single-factor or causal contrast")
    if view["evidence"]["archive_semantics_oracle"] != "pass" or (
        view["evidence"]["view_projection_oracle"] != "pass"
    ):
        raise AssertionError("view acceptance flags differ")
    return {"source_oracles": 2, "view_oracle": "pass", "samples": 18,
            "world_ids": [x["world_id"] for x in view["worlds"]]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--view", type=Path, required=True)
    p.add_argument("--left-root", type=Path, required=True)
    p.add_argument("--right-root", type=Path, required=True)
    p.add_argument("--expected-left-sha", required=True)
    p.add_argument("--expected-right-sha", required=True)
    p.add_argument("--trusted-left-anchor", required=True)
    p.add_argument("--trusted-right-anchor", required=True)
    a = p.parse_args()
    print(json.dumps(verify_view(a.view, a.left_root, a.right_root,
                                 expected_left_sha=a.expected_left_sha,
                                 expected_right_sha=a.expected_right_sha,
                                 trusted_left_anchor=a.trusted_left_anchor,
                                 trusted_right_anchor=a.trusted_right_anchor),
                     sort_keys=True))


if __name__ == "__main__":
    main()
