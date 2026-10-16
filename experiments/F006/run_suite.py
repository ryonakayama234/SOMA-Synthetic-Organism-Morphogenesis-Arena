"""F006: preregistered A-E timestep sweeps + F006/F005 independent evidence checks.

F is the adversarial validation suite in tests/test_f006.py.
F005 dynamics, logs and accepted history are never modified by this module.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from soma.f005 import Config, provenance, save_run
from experiments.F006.diagnostics import (
    DTS, SCHEMA, audit_suite, csv_bytes, json_bytes, recompute, sha, svg_bytes,
)


def build_settings() -> dict:
    """Deterministic, frozen settings: vary dt and nothing else within a case."""
    base = {
        "schema_version": "f005.v1", "seed": None,
        "mass_kg": 1., "drag_per_s": 0., "duration_s": 1.,
        "initial_x_m": 0., "initial_v_m_s": 0.,
        "motor_force_n": 1., "external_force_n": 0.,
        "capacity_uj": 2_000_000, "initial_balance_uj": 2_000_000,
    }
    overrides = {
        "A": {},
        "B": {"capacity_uj": 400_000, "initial_balance_uj": 400_000},
        "C": {"initial_v_m_s": 1., "motor_force_n": 1e-6,
              "external_force_n": -1e-6,
              "capacity_uj": 1000, "initial_balance_uj": 1000},
        "D": {"initial_v_m_s": 1., "motor_force_n": -2.},
        "E": {"motor_force_n": 0., "external_force_n": 1.,
              "capacity_uj": 1000, "initial_balance_uj": 1000},
    }
    settings = {}
    for case, dts in DTS.items():
        for index, dt in enumerate(dts):
            key = "%s-dt-%02d" % (case, index)
            raw = {**base, **overrides[case],
                   "experiment_id": "F006-" + key, "dt_s": dt}
            # Validate every case BEFORE touching an output directory.
            Config.from_dict(raw)
            settings[key] = raw
    return settings


def run(output_dir: Path, *, identity: dict | None = None) -> dict:
    settings = build_settings()
    source = Path(__file__).read_bytes()
    src_hash = hashlib.sha256(source).hexdigest()
    provenance_snapshot = provenance() if identity is None else identity
    if output_dir.exists():
        raise FileExistsError("F006 evidence is immutable; choose an unused directory")
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "suite_source.py").write_bytes(source)
    sweep = {
        "schema_version": SCHEMA, "sweep_id": "F006-A-E-v1",
        "seed": None, "source_model": "f005.v1",
        "reference_id": "Wolfram-exact-fractions-2026-10-16",
        "runs": settings,
    }
    (output_dir / "sweep.json").write_bytes(json_bytes(sweep))
    for key, raw in settings.items():
        save_run(Config.from_dict(raw), output_dir / key,
                 identity=provenance_snapshot, suite_sha256=src_hash)
    records, diagnostics = recompute(output_dir, settings)
    (output_dir / "comparison.csv").write_bytes(csv_bytes(records))
    (output_dir / "diagnostics.json").write_bytes(json_bytes(diagnostics))
    (output_dir / "comparison.svg").write_bytes(svg_bytes(records))
    files = ("sweep.json", "suite_source.py", "comparison.csv",
             "diagnostics.json", "comparison.svg")
    manifest = {
        "schema_version": SCHEMA, "source_model": "f005.v1",
        "sweep_id": "F006-A-E-v1", "seed": None,
        "runs": len(records), "verdict": diagnostics["verdict"],
        "suite_sha256": src_hash,
        **provenance_snapshot,
        "artifacts": {name: sha(output_dir / name) for name in files},
    }
    (output_dir / "manifest.json").write_bytes(json_bytes(manifest))
    audit_suite(output_dir, settings)
    return manifest


def identical_files(first: Path, second: Path) -> bool:
    files_a = sorted(p.relative_to(first).as_posix() for p in first.rglob("*")
                     if p.is_file())
    files_b = sorted(p.relative_to(second).as_posix() for p in second.rglob("*")
                     if p.is_file())
    return files_a == files_b and all(
        (first / name).read_bytes() == (second / name).read_bytes()
        for name in files_a
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="SOMA F006 dt-dependence diagnostic")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--replay-output-dir", type=Path)
    args = parser.parse_args()
    if args.replay_output_dir is not None:
        if args.output_dir.resolve() == args.replay_output_dir.resolve():
            parser.error("replay output must differ from the primary output")
        if (args.output_dir in args.replay_output_dir.parents or
                args.replay_output_dir in args.output_dir.parents):
            parser.error("replay directories must be disjoint")
    identity = provenance()
    first = run(args.output_dir, identity=identity)
    if args.replay_output_dir is not None:
        run(args.replay_output_dir, identity=identity)
        if not identical_files(args.output_dir, args.replay_output_dir):
            raise ValueError("F006 deterministic byte-for-byte replay mismatch")
    print(json.dumps({
        "schema_version": SCHEMA,
        "runs": first["runs"],
        "diagnosis": first["verdict"],
        "independent_saved_log_audit": True,
        "replay_bytes_identical": args.replay_output_dir is not None,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
