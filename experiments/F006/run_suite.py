"""F006: preregistered A-E timestep sweeps + F006/F005 independent evidence checks.

F is the adversarial validation suite in tests/test_f006.py.
F005 dynamics, logs and accepted history are never modified by this module.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from soma.f005 import Config, provenance, save_run
from experiments.F006.diagnostics import (
    DTS, SCHEMA, SWEEP_ID, REFERENCE_ID, audit_suite, csv_bytes, json_bytes,
    recompute, sha, source_hashes, svg_bytes, validate_identity,
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


def _generate(output_dir: Path, settings: dict, identity: dict) -> dict:
    """Write and audit an unpublished, disposable staging directory."""
    source = Path(__file__).read_bytes()
    src_hash = hashlib.sha256(source).hexdigest()
    output_dir.mkdir(exist_ok=False)
    (output_dir / "suite_source.py").write_bytes(source)
    sweep = {
        "schema_version": SCHEMA, "sweep_id": SWEEP_ID,
        "seed": None, "source_model": "f005.v1",
        "reference_id": REFERENCE_ID,
        "runs": settings,
    }
    (output_dir / "sweep.json").write_bytes(json_bytes(sweep))
    for key, raw in settings.items():
        save_run(Config.from_dict(raw), output_dir / key,
                 identity=identity, suite_sha256=src_hash)
    records, diagnostics = recompute(output_dir, settings)
    (output_dir / "comparison.csv").write_bytes(csv_bytes(records))
    (output_dir / "diagnostics.json").write_bytes(json_bytes(diagnostics))
    (output_dir / "comparison.svg").write_bytes(svg_bytes(records))
    files = ("sweep.json", "suite_source.py", "comparison.csv",
             "diagnostics.json", "comparison.svg")
    manifest = {
        "schema_version": SCHEMA, "source_model": "f005.v1",
        "sweep_id": SWEEP_ID, "seed": None,
        "runs": len(records), "verdict": diagnostics["verdict"],
        "suite_sha256": src_hash,
        **identity, "source_hashes": source_hashes(),
        "artifacts": {name: sha(output_dir / name) for name in files},
    }
    (output_dir / "manifest.json").write_bytes(json_bytes(manifest))
    audit_suite(output_dir, settings, expected_identity=identity)
    return manifest


def _destinations(paths: list[Path]) -> list[Path]:
    """Resolve aliases before containment checks; reject even dangling symlinks."""
    destinations = []
    for path in paths:
        if os.path.lexists(path):
            raise FileExistsError("F006 evidence is immutable; choose an unused directory")
        target = path.resolve()
        if os.path.lexists(target):
            raise FileExistsError("F006 output already exists")
        destinations.append(target)
    for i, first in enumerate(destinations):
        for second in destinations[i+1:]:
            if first == second or first in second.parents or second in first.parents:
                raise ValueError("F006 output directories must be disjoint")
    return destinations


def _publish(staged: Path, target: Path) -> None:
    """Linux/WSL2 renameat2: atomic directory publication without replacement."""
    rename = getattr(ctypes.CDLL(None, use_errno=True), "renameat2", None)
    if rename is None:
        raise OSError(errno.ENOSYS, "F006 requires Linux renameat2 for no-replace publication")
    rename.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)
    rename.restype = ctypes.c_int
    if rename(-100, os.fsencode(staged), -100, os.fsencode(target), 1) != 0:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code), str(target))


def run_pair(output_dir: Path, replay_output_dir: Path | None = None, *,
             identity: dict | None = None) -> dict:
    """Validate and replay privately, then publish. Roll back this invocation on errors.

    Two independent directory renames are not crash-atomic as a pair; a process or
    machine crash between them may leave a complete audited primary without replay.
    Ordinary caught exceptions remove only directories published by this invocation.
    """
    paths = [output_dir] if replay_output_dir is None else [output_dir, replay_output_dir]
    targets = _destinations(paths)
    settings = build_settings()
    snapshot = provenance() if identity is None else dict(identity)
    validate_identity(snapshot)
    published = []
    with ExitStack() as stack:
        staged, manifests = [], []
        for target in targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            temp = stack.enter_context(tempfile.TemporaryDirectory(prefix=".f006-", dir=target.parent))
            stage = Path(temp) / "payload"
            manifests.append(_generate(stage, settings, snapshot))
            staged.append(stage)
        if len(staged) == 2 and not identical_files(*staged):
            raise ValueError("F006 deterministic byte-for-byte replay mismatch")
        try:
            for stage, target in zip(staged, targets):
                stat = stage.stat()
                _publish(stage, target)
                published.append((target, stat.st_dev, stat.st_ino))
        except BaseException:
            for target, device, inode in reversed(published):
                # Never delete a path replaced by a concurrent writer.
                if target.exists() and not target.is_symlink():
                    current = target.stat()
                    if (current.st_dev, current.st_ino) == (device, inode):
                        shutil.rmtree(target)
            raise
    return manifests[0]


def run(output_dir: Path, *, identity: dict | None = None) -> dict:
    return run_pair(output_dir, identity=identity)


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
    first = run_pair(args.output_dir, args.replay_output_dir)
    print(json.dumps({
        "schema_version": SCHEMA,
        "runs": first["runs"],
        "diagnosis": first["verdict"],
        "independent_saved_log_audit": True,
        "replay_bytes_identical": args.replay_output_dir is not None,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
