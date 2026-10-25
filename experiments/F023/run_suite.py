"""F023.v1 immutable 15-scene archive producer; no overwrite, no agent UI."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

from soma.f023 import FREEZE_COMMIT, SCHEMA, grid, simulate, validate


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _write(path, obj, jsonl=False):
    text = (''.join(canonical(x) + '\n' for x in obj) if jsonl
            else canonical(obj) + '\n')
    path.write_text(text, encoding="utf-8", newline="\n")


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source():
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("unknown source SHA")
    return sha


def invalid_probes():
    base = grid()[0]
    alterations = [
        {"x_a_m": -.2, "y_a_m": 0., "x_b_m": .2, "y_b_m": 0.},
        {"x_a_m": -.5, "y_a_m": 0., "x_b_m": .5, "y_b_m": 0.},
        {"x_a_m": float("nan")},
        {"command_ax_ns": .26},
        {"initial_balance_a_uj": -1},
    ]
    result = {}
    for idx, patch in enumerate(alterations, 1):
        try:
            validate(dict(base, **patch))
        except ValueError:
            result[f"J{idx:02d}"] = "rejected"
        else:
            raise AssertionError(f"J{idx:02d} invalid primary input accepted")
    return result


def produce(dest: Path, *, source_sha: str | None = None):
    dest = Path(dest)
    if dest.exists():
        raise FileExistsError("refuse overwrite")
    if source_sha is None:
        source_sha = _source()
    if type(source_sha) is not str or len(source_sha) != 40 or any(
        c not in "0123456789abcdef" for c in source_sha
    ):
        raise ValueError("bad source SHA")
    scenarios = grid()
    if len(scenarios) != 15 or [s["world_id"] for s in scenarios] != [
        f"Q{i:02d}" for i in range(1, 16)
    ]:
        raise AssertionError("primary fixed roster drift")
    states, contacts, actions, ledgers, results = [], [], [], [], []
    for s in scenarios:
        validate(s)
        frames, act, event, ledger, audit = simulate(s)
        states.extend(frames)
        contacts.extend(event)
        actions.extend(act)
        ledgers.extend(ledger)
        results.append(audit)
    if len(states) != 135 or len(actions) != 30 or len(ledgers) != 30:
        raise AssertionError("missing primary saved evidence")
    audit = dict(schema_version=SCHEMA, world_results=results,
                 invalid_probe_results=invalid_probes(),
                 momentum_residual_kg_mps=max(r["momentum_residual_kg_mps"] for r in results),
                 energy_residual_j=max(abs(r["energy_residual_j"]) for r in results),
                 overlap_bound_m=max(r["overlap_bound_m"] for r in results))
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=f".{dest.name}-staging-", dir=dest.parent))
    try:
        _write(temp / "scenario.json", {"schema_version": SCHEMA, "worlds": scenarios})
        for path, rows in (("states.jsonl", states), ("contacts.jsonl", contacts),
                           ("actions.jsonl", actions), ("ledger.jsonl", ledgers)):
            _write(temp / path, rows, True)
        _write(temp / "audit.json", audit)
        manifest = dict(schema_version=SCHEMA, frozen_protocol_commit_sha=FREEZE_COMMIT,
                        implementation_commit_sha=source_sha,
                        python_version=".".join(str(i) for i in sys.version_info[:2]),
                        platform="linux" if sys.platform.startswith("linux")
                        else platform.system().lower(),
                        config_sha256=_sha(temp/"scenario.json"),
                        states_sha256=_sha(temp/"states.jsonl"),
                        contacts_sha256=_sha(temp/"contacts.jsonl"),
                        actions_sha256=_sha(temp/"actions.jsonl"),
                        ledger_sha256=_sha(temp/"ledger.jsonl"),
                        audit_sha256=_sha(temp/"audit.json"))
        _write(temp / "manifest.json", manifest)
        if dest.exists():
            raise FileExistsError("existing output")
        os.rename(temp, dest)
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    return dict(worlds=len(scenarios), frames=len(states), contacts=len(contacts),
                actions=len(actions), ledgers=len(ledgers), invalid_probes=5)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--source-sha")
    args = p.parse_args()
    print(canonical(produce(args.out, source_sha=args.source_sha)))
