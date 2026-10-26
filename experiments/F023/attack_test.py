"""F023 source-independent semantic forgery negatives with manifests repacked."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from experiments.F023.verify import verify
from experiments.F022.verify import canonical


def _write(path, value, multiple=False):
    value = (''.join(canonical(v)+'\n' for v in value)
             if multiple else canonical(value)+'\n')
    path.write_text(value, encoding="utf-8", newline="\n")


def attack(root: Path):
    root=Path(root)
    tests = [
        ("impulse", "contacts.jsonl", lambda x:x[0].__setitem__("impulse_ns",x[0]["impulse_ns"]+.1)),
        ("contact_time", "contacts.jsonl", lambda x:x[0].__setitem__("time_s",x[0]["time_s"]+.01)),
        ("lost_contact", "contacts.jsonl", lambda x:x.pop(0)),
        ("world_state", "states.jsonl", lambda x:x[12].__setitem__("vx_a_mps",x[12]["vx_a_mps"]+.01)),
        ("own_action", "actions.jsonl", lambda x:x[2].__setitem__("applied_y_ns",.03)),
        ("own_charge", "actions.jsonl", lambda x:x[2].__setitem__("charge_uj",201)),
        ("private_balance", "ledger.jsonl", lambda x:x[2].__setitem__("balance_after_uj",199)),
        ("fake_scenario", "scenario.json", lambda x:x["worlds"][1].__setitem__("command_ay_ns",.03)),
        # Codex P1 regression: a difference below F022 float tolerance
        # changes exact decimal billing from 200 to 201 microjoules.
        ("fake_boundary_200_to_201_uj", "scenario.json",
         lambda x:x["worlds"][1].__setitem__("command_ay_ns",.0200000001)),
        ("fake_nearby_initial_velocity_billing", "scenario.json",
         lambda x:x["worlds"][1].__setitem__("vy_a_mps",1e-10)),
        ("fake_tiny_action_command", "actions.jsonl",
         lambda x:x[2].__setitem__("command_y_ns",.0200000001)),
        ("fake_tiny_applied_impulse", "actions.jsonl",
         lambda x:x[2].__setitem__("applied_y_ns",.0200000001)),

        ("wrong_audit", "audit.json", lambda x:x["world_results"][1].__setitem__("contact_count",0)),
        ("wrong_freeze", "manifest.json", lambda x:x.__setitem__("frozen_protocol_commit_sha","0"*40)),
    ]
    mapping = {
        "scenario.json":"config_sha256",
        "states.jsonl":"states_sha256",
        "contacts.jsonl":"contacts_sha256",
        "actions.jsonl":"actions_sha256",
        "ledger.jsonl":"ledger_sha256",
        "audit.json":"audit_sha256",
    }
    with tempfile.TemporaryDirectory(prefix="f023-attacks-") as tmp:
        for index, (name,file,change) in enumerate(tests):
            work=Path(tmp)/f"case-{index:02d}"
            shutil.copytree(root,work)
            p=work/file
            lines=file.endswith(".jsonl")
            value=([json.loads(s) for s in p.read_text().splitlines()]
                   if lines else json.loads(p.read_text()))
            change(value)
            _write(p,value,lines)
            if file!="manifest.json":
                manifest_file=work/"manifest.json"
                manifest=json.loads(manifest_file.read_text())
                manifest[mapping[file]]=hashlib.sha256(p.read_bytes()).hexdigest()
                _write(manifest_file,manifest)
            try:
                verify(work)
            except (AssertionError,ValueError,KeyError,TypeError):
                pass
            else:
                raise AssertionError(f"forged-rehashed {name} escaped verifier")
    return {"rehash_semantic_attacks_rejected":len(tests)}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    args=p.parse_args()
    print(canonical(attack(args.root)))
