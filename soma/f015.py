"""F015: frozen multi-trial active probing; LOCAL evidence, never topology truth.

This deliberately compares observed response with a *declared ideal linked
two-mass reference*. It cannot verify the reference model, hidden external
forces, or actual physical attachment. No simulator/world row may enter.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from soma.f008 import LocalObservation, validate as validate_a
from soma.f014 import PeerPacket, validate_packet

SCHEMA = "f015.comparison.v1"
SCHEDULE_N = (2.0, 1.0, 0.0)
H = 0.25
TOL = 1e-12
SAME = "observation_signature_same"
CHANGED = "observation_signature_changed"
UNKNOWN = "inconclusive"


@dataclass(frozen=True, slots=True)
class ProbeTrial:
    a_local: tuple[LocalObservation, ...]
    b_packets: tuple[PeerPacket | None, ...]


def analyze_probe(trials: tuple[ProbeTrial, ...]) -> dict:
    """Fixed 2/1/0 N protocol, each full-reset 1s trial.

    The reference a_A = u/2, moved_B = (u != 0) is an investigator-frozen
    hypothesis, NOT a measured/verified link. Differences can have many causes.
    """
    if type(trials) is not tuple or len(trials) != 3:
        raise ValueError("three ordered full-reset probe trials required")
    a_different = False
    peer_different = False
    peer_missing = False
    rejected = False
    max_a_residual = 0.0
    peer_mismatch_count = 0
    for trial_index, (u, trial) in enumerate(zip(SCHEDULE_N, trials)):
        if type(trial) is not ProbeTrial or type(trial.a_local) is not tuple or (
                type(trial.b_packets) is not tuple) or (
                len(trial.a_local) != 4 or len(trial.b_packets) != 4):
            raise ValueError("invalid trial, local stream or peer packet stream")
        previous_velocity = 0.0
        previous_balance = None
        for step_index, (obs, packet) in enumerate(
                zip(trial.a_local, trial.b_packets), 1):
            if type(obs) is not LocalObservation:
                raise ValueError("world truth / extra A fields forbidden")
            validate_a(obs)
            if (obs.step_index != step_index or
                    abs(obs.time_s - step_index*H) > TOL or
                    abs(obs.dt_s - H) > TOL or
                    abs(obs.v_prev_m_s - previous_velocity) > TOL or
                    abs(obs.motor_command_n - u) > TOL):
                raise ValueError("wrong intervention, clock or trial reset")
            if previous_balance is not None and obs.balance_a_uj > previous_balance:
                raise ValueError("unexpected A battery refill mid-trial")
            previous_balance = obs.balance_a_uj
            previous_velocity = obs.v_a_m_s
            if packet is None:
                peer_missing = True
            else:
                validate_packet(packet, obs)
                expected_bit = (u != 0)
                if packet.moved != expected_bit:
                    peer_different = True
                    peer_mismatch_count += 1
            if u > 0 and abs(obs.motor_applied_n - u) > TOL:
                rejected = True
            if u == 0 and abs(obs.motor_applied_n) > TOL:
                raise ValueError("motor unexpectedly active in intentional OFF")
            acceleration = (obs.v_a_m_s - obs.v_prev_m_s) / obs.dt_s
            if not math.isfinite(acceleration):
                raise ValueError("nonfinite measured acceleration")
            diff = abs(acceleration - u/2.0)
            max_a_residual = max(max_a_residual, diff)
            if diff > TOL:
                a_different = True
        if trial_index and abs(trial.a_local[0].v_prev_m_s) > TOL:
            raise ValueError("failed reset between episodes")
    a_status = UNKNOWN if rejected else CHANGED if a_different else SAME
    augmented = (UNKNOWN if rejected or peer_missing else
                 CHANGED if a_different or peer_different else SAME)
    return {
        "schema_version": SCHEMA,
        "a_only_status": a_status,
        "a_plus_peer_status": augmented,
        "a_max_abs_residual_m_s2": max_a_residual,
        "peer_mismatch_steps": peer_mismatch_count,
        "peer_incremental_discrimination": (
            a_status == SAME and augmented == CHANGED),
        "interpretation": "relative_to_frozen_reference_not_topology",
    }
