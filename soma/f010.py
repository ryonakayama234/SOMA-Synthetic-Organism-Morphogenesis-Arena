"""F010: offline A-local force-response signature, not a body/topology classifier.

Only typed adopted F008 LocalObservation fields are permitted here. The caller
organizes three *independent* runs at distinct actually-applied force levels.
The inference code is not passed F007 configs, attachment, partner state, or
unknown external force. Not online autonomous active probing.
"""
from __future__ import annotations

from dataclasses import asdict
import math

from soma.f008 import LocalObservation, validate

SCHEMA = "f010.signature.v1"
TOL = 1e-12  # Only frozen exact-rational F010 A-E cases; no real sensor calibration.
FORCES = (2.0, 1.0, 0.5)


def _finite(x: float) -> bool:
    return type(x) in (int, float) and math.isfinite(x)


def _close(a: float, b: float) -> bool:
    return math.isclose(a, b, abs_tol=TOL, rel_tol=0.0)


def _inconclusive(reason: str) -> dict:
    return {"schema_version": SCHEMA, "status": "inconclusive",
            "reason": reason, "alpha_per_kg": None, "beta_m_s2": None,
            "holdout_residual_m_s2": None, "response_signature": None,
            "topology_verified": False}


def _trial(observations: tuple[LocalObservation, ...]) -> tuple[float, float] | None:
    if type(observations) is not tuple or len(observations) != 4:
        raise ValueError("exactly four A-local observations per independent trial required")
    applied = []
    accelerations = []
    for i, obs in enumerate(observations, start=1):
        if type(obs) is not LocalObservation:
            raise ValueError("world truth or extra observation fields prohibited")
        validate(obs)
        if (obs.step_index != i or not _close(obs.dt_s, .25)
                or not _close(obs.time_s, i*.25)):
            raise ValueError("noncanonical independent F010 trial clock/index")
        if i == 1:
            if not _close(obs.v_prev_m_s, 0):
                raise ValueError("trial must start from rest")
        elif not _close(obs.v_prev_m_s, observations[i-2].v_a_m_s):
            raise ValueError("broken local velocity continuity")
        applied.append(obs.motor_applied_n)
        accel = (obs.v_a_m_s-obs.v_prev_m_s)/obs.dt_s
        if not _finite(accel):
            raise ValueError("nonfinite local acceleration")
        accelerations.append(accel)
    if any(not _close(f, applied[0]) for f in applied):
        return None  # battery rejection or motor modulation; cannot infer a fixed input
    if _close(applied[0], 0):
        return None  # no actually applied input, regardless of command
    if any(not _close(a, accelerations[0]) for a in accelerations):
        return None  # inconsistent response; no constant-acceleration inference
    return applied[0], sum(accelerations)/len(accelerations)


def estimate(trials: tuple[tuple[LocalObservation, ...], ...]) -> dict:
    """Two-point force-slope fit plus reserved 0.5N holdout, without world labels.

    A 0.5 kg^-1 signature does NOT prove another mass or mechanical attachment:
    the unknown input-dependent disturbance -u/2 creates the same measurements.
    """
    if type(trials) is not tuple or len(trials) != 3:
        return _inconclusive("requires_three_independent_force_trials")
    pairs = []
    for trial in trials:
        result = _trial(trial)
        if result is None:
            return _inconclusive("rejected_or_unstable_applied_excitation")
        pairs.append(result)
    by_force = {}
    for force, acceleration in pairs:
        if force in by_force:
            return _inconclusive("insufficient_distinct_applied_forces")
        by_force[force] = acceleration
    if set(by_force) != set(FORCES):
        return _inconclusive("outside_preregistered_force_levels")
    alpha = (by_force[2.] - by_force[1.])/(2.-1.)
    beta = by_force[1.] - alpha*1.
    holdout = by_force[.5] - (alpha*.5 + beta)
    if not all(_finite(v) for v in (alpha, beta, holdout)):
        raise ValueError("nonfinite response fit")
    if not _close(holdout, 0.):
        return {
            "schema_version": SCHEMA, "status": "non_affine_holdout",
            "reason": "third_force_contradicts_affine_model",
            "alpha_per_kg": alpha, "beta_m_s2": beta,
            "holdout_residual_m_s2": holdout,
            "response_signature": "unclassified", "topology_verified": False,
        }
    if _close(alpha, .5) and _close(beta, 0.):
        signature = "inertia_like"  # ALSO d(u)=-u/2, cannot establish attachment
    elif _close(alpha, 1.) and _close(beta, -1.):
        signature = "offset_like"
    elif _close(alpha, 1.) and _close(beta, 0.):
        signature = "nominal_like"
    else:
        signature = "unclassified"
    return {
        "schema_version": SCHEMA, "status": "affine_response_fit",
        "reason": "fixed_ideal_1d_discrete_response_only",
        "alpha_per_kg": alpha, "beta_m_s2": beta,
        "holdout_residual_m_s2": holdout,
        "response_signature": signature, "topology_verified": False,
    }
