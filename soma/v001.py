"""V001: read-only, F007 saved-world-state projection for research visualization.

This module never steps physics or alters F007 source runs. It is not a cell sensor.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

from experiments.F007.verify import audit_run, read_csv
from soma.f007 import STATE_COLUMNS, LINK_COLUMNS, provenance

SCHEMA = "v001.frame.v1"
FRAME_FIELDS = (
    "step_index", "time_s", "x_a_m", "x_b_m", "v_a_m_s", "v_b_m_s",
    "attached", "balance_a_uj", "balance_b_uj", "motor_command_n",
    "motor_applied_n", "decision_reason", "link_event_kind",
)
NUMERIC_FIELDS = (
    "time_s", "x_a_m", "x_b_m", "v_a_m_s", "v_b_m_s",
    "motor_command_n", "motor_applied_n",
)
INT_FIELDS = ("step_index", "balance_a_uj", "balance_b_uj")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(obj: object) -> bytes:
    """Stable UTF-8 serialization, including a final newline."""
    return (json.dumps(obj, ensure_ascii=True, allow_nan=False,
                       sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def project_run(source: Path, *, trusted_origin: dict | None = None) -> dict:
    """Verify saved F007 semantics, then project every original timestep verbatim.

    Default identity is recomputed from a trusted local checkout, never from the
    untrusted source manifest. Historical runs from other commits need an
    independently verified checkout/identity passed by the caller.
    """
    source = Path(source)
    identity = provenance() if trusted_origin is None else trusted_origin
    audit_run(source, trusted_origin=identity)

    states = read_csv(
        source / "states.csv", STATE_COLUMNS,
        strings=("decision_reason",), flags=("attached",),
        integers={"step_index", "spent_a_uj", "balance_a_uj",
                  "balance_b_uj", "ledger_event_index"},
    )
    links = read_csv(
        source / "link_events.csv", LINK_COLUMNS,
        strings=("kind",), flags=("attached_before", "attached_after"),
    )
    config = json.loads((source / "config.json").read_text(encoding="utf-8"))
    events = {}
    for event in links:
        stamp = event["time_s"]
        if stamp in events:
            raise ValueError("duplicate link event time")
        events[stamp] = event["kind"]

    frames = []
    for i, row in enumerate(states):
        if row["step_index"] != i:
            raise ValueError("non-consecutive steps")
        if not all(math.isfinite(row[k]) for k in NUMERIC_FIELDS):
            raise ValueError("non-finite projected numeric field")
        frame = {k: row[k] for k in FRAME_FIELDS if k != "link_event_kind"}
        frame["link_event_kind"] = events.get(row["time_s"])
        if set(frame) != set(FRAME_FIELDS):
            raise AssertionError("incomplete V001 frame")
        if any(type(frame[k]) is not int for k in INT_FIELDS):
            raise ValueError("frame integer type")
        if type(frame["attached"]) is not bool:
            raise ValueError("frame link type")
        frames.append(frame)
    if len(frames) != len(states) or not frames:
        raise ValueError("frame count mismatch")
    if any(key not in {f["time_s"] for f in frames} for key in events):
        raise ValueError("orphan link event")
    return {
        "schema_version": SCHEMA,
        "experiment_id": config["experiment_id"],
        "f007_schema_version": config["schema_version"],
        "source_hashes": {
            name: sha256(source / name) for name in (
                "config.json", "states.csv", "link_events.csv",
                "ledger/events.csv", "manifest.json",
            )
        },
        "frames": frames,
    }


def verify_frame_projection(source: Path, payload: dict,
                            *, trusted_origin: dict | None = None) -> dict:
    """Independent field-by-field check against saved CSV after F007 audit.

    The verifier uses the original data, not the viewer's rendered coordinates.
    A repacked/rehashed tampered frames.json must still fail.
    """
    identity = provenance() if trusted_origin is None else trusted_origin
    audit_run(Path(source), trusted_origin=identity)
    target = project_run(source, trusted_origin=identity)
    if set(payload) != set(target) or payload["schema_version"] != SCHEMA:
        raise ValueError("unexpected frame envelope")
    for k in ("experiment_id", "f007_schema_version", "source_hashes"):
        if payload[k] != target[k]:
            raise ValueError("wrong frame provenance: " + k)
    given, expected = payload["frames"], target["frames"]
    if type(given) is not list or len(given) != len(expected):
        raise ValueError("missing/extra frames")
    for i, (actual, original) in enumerate(zip(given, expected)):
        if type(actual) is not dict or set(actual) != set(FRAME_FIELDS):
            raise ValueError("wrong frame fields at step " + str(i))
        for field in FRAME_FIELDS:
            value, reference = actual[field], original[field]
            if type(value) is not type(reference) or value != reference:
                raise ValueError("frame mismatch at step %d, %s" % (i, field))
    return {
        "source_steps": len(expected), "frames_checked": len(given),
        "coverage": 1.0, "max_projection_error": 0,
        "link_event_mismatch_count": 0, "verdict": "supported",
    }
