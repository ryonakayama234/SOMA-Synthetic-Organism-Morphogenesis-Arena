"""Reproducible F002 conditions A-F. Does not overwrite previous evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from soma.f002 import Cell, Event, apply_event, git_provenance, new_ledger, save_run


def common(name: str, events: list[dict], *, cells: list[dict] | None = None) -> dict:
    if cells is None:
        cells = [{"cell_id": "A", "balance_uj": 10_000_000, "capacity_uj": 20_000_000},
                 {"cell_id": "B", "balance_uj": 2_000_000, "capacity_uj": 20_000_000}]
    return {"schema_version": "f002.v1", "experiment_id": name, "seed": 1,
            "cells": cells, "events": events}


def transfer(amount: int, eta: int) -> dict:
    return {"kind": "transfer", "source_id": "A", "target_id": "B",
            "amount_uj": amount, "eta_bps": eta}


def rejection_checks() -> dict:
    """Control E: explicitly record failures while checking state was not modified."""
    first = new_ledger([Cell("A", 20_000_000, 10_000_000), Cell("B", 20_000_000, 19_000_000)])
    trials = {
        "insufficient": Event("spend", 10_000_001, source_id="A"),
        "capacity": Event("acquire", 1_000_001, target_id="B"),
        "transfer_capacity": Event("transfer", 3_000_000, "A", "B", 8000),
        "negative": Event("spend", -1, source_id="A"),
        "zero": Event("spend", 0, source_id="A"),
        "bool": Event("spend", True, source_id="A"),
        "missing_id": Event("spend", 1, source_id="missing"),
        "self_transfer": Event("transfer", 1, "A", "A", 10000),
        "bad_efficiency": Event("transfer", 1, "A", "B", 10001),
        "fractional_amount": Event("spend", 1.5, source_id="A"),
        "fractional_efficiency": Event("transfer", 1, "A", "B", 5000.5),
        "nonfinite_amount": Event("spend", float("nan"), source_id="A"),
        "nonfinite_efficiency": Event("transfer", 1, "A", "B", float("inf")),
    }
    records = []
    for name, event in trials.items():
        try:
            apply_event(first, event)
        except ValueError as exc:
            records.append({"case": name, "rejected": True, "error": str(exc),
                            "state_unchanged": first.event_index == 0 and first.residual_uj == 0 and first.cell("A").balance_uj == 10_000_000 and first.cell("B").balance_uj == 19_000_000})
        else:
            records.append({"case": name, "rejected": False, "error": None, "state_unchanged": False})
    if not all(item["rejected"] and item["state_unchanged"] for item in records):
        raise AssertionError("invalid E control")
    return {"experiment_id": "E-invalid-events", "cases": records, "passed": len(records)}


def validate_expected_results(results: dict[str, dict]) -> None:
    """Check every preregistered manifest measurement, even with Python -O."""
    expected = {
        "A-rest": {
            "final_balances_uj": {"A": 10_000_000},
            "acquired_uj": 0, "spent_uj": 0, "loss_uj": 0,
            "residual_uj": 0, "event_count": 0,
        },
        "B-acquire": {
            "final_balances_uj": {"A": 15_000_000},
            "acquired_uj": 5_000_000, "spent_uj": 0, "loss_uj": 0,
            "residual_uj": 0, "event_count": 1,
        },
        "C-spend": {
            "final_balances_uj": {"A": 7_000_000},
            "acquired_uj": 0, "spent_uj": 3_000_000, "loss_uj": 0,
            "residual_uj": 0, "event_count": 1,
        },
        "D-transfer": {
            "final_balances_uj": {"A": 7_000_000, "B": 4_400_000},
            "acquired_uj": 0, "spent_uj": 0, "loss_uj": 600_000,
            "residual_uj": 0, "event_count": 1,
        },
        "F-bulk": {
            "final_balances_uj": {"A": 9_999_997, "B": 2_000_001},
            "acquired_uj": 0, "spent_uj": 0, "loss_uj": 2,
            "residual_uj": 0, "event_count": 1,
        },
        "F-split": {
            "final_balances_uj": {"A": 9_999_997, "B": 2_000_000},
            "acquired_uj": 0, "spent_uj": 0, "loss_uj": 3,
            "residual_uj": 0, "event_count": 3,
        },
    }
    if results.keys() != expected.keys():
        raise AssertionError("A-F: missing or unexpected experiment outcomes")
    for name, predicted in expected.items():
        for field, value in predicted.items():
            if results[name].get(field) != value:
                raise AssertionError(
                    f"{name}: {field} differs from preregistered prediction"
                )

    # Preserve the preregistered contrast as well as both absolute predictions.
    bulk_b = results["F-bulk"]["final_balances_uj"]["B"]
    split_b = results["F-split"]["final_balances_uj"]["B"]
    if bulk_b - split_b != 1:
        raise AssertionError("F: bulk/split received-energy difference must be 1 µJ")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run F002 controlled experiments A-F")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir
    provenance = git_provenance()  # Capture before the suite creates any output.
    out.mkdir(parents=True, exist_ok=False)
    single_cell = [{"cell_id": "A", "balance_uj": 10_000_000, "capacity_uj": 20_000_000}]
    plans = {
        "A-rest": common("A-rest", [], cells=single_cell),
        "B-acquire": common("B-acquire", [{"kind": "acquire", "target_id": "A", "amount_uj": 5_000_000}], cells=single_cell),
        "C-spend": common("C-spend", [{"kind": "spend", "source_id": "A", "amount_uj": 3_000_000}], cells=single_cell),
        "D-transfer": common("D-transfer", [transfer(3_000_000, 8000)]),
        "F-bulk": common("F-bulk", [transfer(3, 5000)]),
        "F-split": common("F-split", [transfer(1, 5000)] * 3),
    }
    results = {name: save_run(config, out / name, provenance=provenance)
               for name, config in plans.items()}
    # Replay the exact same F configurations, not simply compare different partitions.
    artifact_names = ("config.json", "events.csv", "balances.csv", "energy.svg", "manifest.json")
    replay_checks = {}
    for name in ("F-bulk", "F-split"):
        replay_dir = out / (name + "-replay")
        save_run(plans[name], replay_dir, provenance=provenance)
        hashes = {}
        for filename in artifact_names:
            original = (out / name / filename).read_bytes()
            repeat = (replay_dir / filename).read_bytes()
            original_sha = hashlib.sha256(original).hexdigest()
            repeat_sha = hashlib.sha256(repeat).hexdigest()
            if original_sha != repeat_sha:
                raise AssertionError(f"nondeterministic F replay: {name}/{filename}")
            hashes[filename] = original_sha
        replay_checks[name] = {
            "replay_run": name + "-replay",
            "same_config": True,
            "byte_identical": True,
            "matching_artifact_sha256": hashes,
        }
    e = rejection_checks()
    (out / "E-invalid-events.json").write_text(json.dumps(e, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    validate_expected_results(results)
    manifest = {"experiment_id": "F002-A-F", "runs": {name: {field: r[field] for field in ("event_count", "final_balances_uj", "acquired_uj", "spent_uj", "loss_uj", "residual_uj")} for name, r in results.items()},
                "invalid_control_count": e["passed"],
                "f_replay_checks": replay_checks,
                "e_checksum_sha256": hashlib.sha256((out / "E-invalid-events.json").read_bytes()).hexdigest()}
    (out / "comparison.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
