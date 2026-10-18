"""F008: strictly local A-only motion response observations and anomaly detection.

The observer receives no world topology, partner state, external force or link force.
This is deterministic post-processing of F007 discrete traces, NOT online control.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

SCHEMA = "f008.local.v1"
COLUMNS = (
    "step_index", "time_s", "dt_s", "v_prev_m_s", "v_a_m_s",
    "motor_command_n", "motor_applied_n", "balance_a_uj",
    "observed_accel_m_s2", "expected_accel_m_s2", "residual_m_s2",
    "status",
)
TOLERANCE_M_S2 = 1e-12  # Frozen A-E rational controls, not a universal sensor specification.


@dataclass(frozen=True, slots=True)
class LocalObservation:
    step_index: int
    time_s: float
    dt_s: float
    v_prev_m_s: float
    v_a_m_s: float
    motor_command_n: float
    motor_applied_n: float
    balance_a_uj: int


def project_local(previous: dict, current: dict) -> LocalObservation:
    """Explicit allowlist; never forward arbitrary F007 world-truth columns."""
    step = current["step_index"]
    dt = current["time_s"] - previous["time_s"]
    if type(step) is not int or type(previous["step_index"]) is not int or step != previous["step_index"] + 1:
        raise ValueError("nonconsecutive step")
    if not math.isfinite(dt) or dt <= 0:
        raise ValueError("nonpositive local clock interval")
    data = LocalObservation(
        step_index=step,
        time_s=current["time_s"],
        dt_s=dt,
        v_prev_m_s=previous["v_a_m_s"],
        v_a_m_s=current["v_a_m_s"],
        motor_command_n=current["motor_command_n"],
        motor_applied_n=current["motor_applied_n"],
        balance_a_uj=current["balance_a_uj"],
    )
    validate(data)
    return data


def validate(obs: LocalObservation) -> None:
    if type(obs.step_index) is not int or obs.step_index < 1:
        raise ValueError("invalid step")
    if type(obs.balance_a_uj) is not int or obs.balance_a_uj < 0:
        raise ValueError("invalid local battery")
    for name in ("time_s", "dt_s", "v_prev_m_s", "v_a_m_s",
                 "motor_command_n", "motor_applied_n"):
        value = getattr(obs, name)
        if type(value) not in (float, int) or not math.isfinite(value):
            raise ValueError("invalid local value: " + name)
    if obs.dt_s <= 0 or obs.time_s < obs.dt_s:
        raise ValueError("invalid local time")


def detect(obs: LocalObservation, *, nominal_mass_kg: float = 1.0) -> dict:
    """One-cell prediction residual. Anomaly NEVER means 'attached'.

    Applied force is an explicitly permitted A-local actuator feedback channel.
    The fixed nominal mass is A's prior calibration, not inferred link mass.
    """
    validate(obs)
    if type(nominal_mass_kg) not in (int, float) or not math.isfinite(nominal_mass_kg) or nominal_mass_kg <= 0:
        raise ValueError("invalid nominal mass")
    observed = (obs.v_a_m_s - obs.v_prev_m_s) / obs.dt_s
    if not math.isfinite(observed):
        raise ValueError("unrepresentable acceleration")
    if obs.motor_applied_n == 0:
        predicted, residual, status = None, None, "not_excited"
    else:
        predicted = obs.motor_applied_n / nominal_mass_kg
        residual = observed - predicted
        if not math.isfinite(predicted) or not math.isfinite(residual):
            raise ValueError("unrepresentable response")
        status = "anomaly" if abs(residual) > TOLERANCE_M_S2 else "nominal"
    return {
        "step_index": obs.step_index, "time_s": obs.time_s, "dt_s": obs.dt_s,
        "v_prev_m_s": obs.v_prev_m_s, "v_a_m_s": obs.v_a_m_s,
        "motor_command_n": obs.motor_command_n,
        "motor_applied_n": obs.motor_applied_n,
        "balance_a_uj": obs.balance_a_uj,
        "observed_accel_m_s2": observed,
        "expected_accel_m_s2": predicted,
        "residual_m_s2": residual,
        "status": status,
    }


def analyze(world_rows: list[dict]) -> list[dict]:
    """Adapter only: world rows are discarded after creating A-local records."""
    return [detect(project_local(a, b)) for a, b in zip(world_rows, world_rows[1:])]
