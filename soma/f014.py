"""F014: one-bit B-local movement evidence added to strict F008 A observation.

No global state, coupling truth, B numeric velocity, or world force may enter
this estimator. A peer-response signal is NOT evidence of mechanical attachment.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from soma.f008 import LocalObservation, validate as validate_a

PACKET_SCHEMA = "f014.packet.v1"
RESULT_SCHEMA = "f014.comparison.v1"
THRESHOLD_M_S = 1e-10
TOL = 1e-12


@dataclass(frozen=True, slots=True)
class PeerPacket:
    source: str
    step_index: int
    time_s: float
    moved: bool


def validate_packet(packet: PeerPacket, a: LocalObservation) -> None:
    if type(packet) is not PeerPacket:
        raise ValueError("wrong or extra peer observation fields")
    if packet.source != "B" or type(packet.source) is not str:
        raise ValueError("wrong source")
    if type(packet.step_index) is not int or packet.step_index != a.step_index:
        raise ValueError("stale, duplicate or reordered packet index")
    if (type(packet.time_s) not in (int, float) or
            not math.isfinite(packet.time_s) or
            abs(packet.time_s - a.time_s) > TOL):
        raise ValueError("wrong packet time")
    if type(packet.moved) is not bool:
        raise ValueError("peer payload must be exactly a boolean")


def estimate_trial(a_stream: tuple[LocalObservation, ...],
                   packets: tuple[PeerPacket | None, ...]) -> dict:
    """Four synchronized intervals; missing is inconclusive, never False.

    Only the *observed response* is classified. Topology is not identified.
    """
    if (type(a_stream) is not tuple or type(packets) is not tuple or
            len(a_stream) != 4 or len(packets) != 4):
        raise ValueError("four aligned observations/packets required")
    statuses = []
    for k, (a, packet) in enumerate(zip(a_stream, packets), 1):
        if type(a) is not LocalObservation:
            raise ValueError("A world truth/extra fields forbidden")
        validate_a(a)
        if (a.step_index != k or abs(a.time_s - .25*k) > TOL or
                abs(a.dt_s - .25) > TOL):
            raise ValueError("noncanonical local clock")
        if k == 1:
            if abs(a.v_prev_m_s) > TOL:
                raise ValueError("trial must start at rest")
        elif abs(a.v_prev_m_s - a_stream[k-2].v_a_m_s) > TOL:
            raise ValueError("broken A-local continuity")
        if packet is not None:
            validate_packet(packet, a)
        if packet is None:
            statuses.append("inconclusive")
        elif (a.motor_applied_n == 0 or
              abs(a.motor_command_n - a.motor_applied_n) > TOL):
            statuses.append("inconclusive")
        else:
            statuses.append("peer_motion_seen" if packet.moved else "peer_still")
    if all(s == statuses[0] for s in statuses):
        overall = statuses[0]
    else:
        overall = "inconclusive"
    return {"schema_version": RESULT_SCHEMA, "status": overall,
            "step_statuses": statuses,
            "interpretation": "peer_motion_only_not_mechanical_coupling"}


def packet_csv_row(packet: PeerPacket) -> dict:
    """Safe serializer for the fixed one-boolean payload and framing."""
    if type(packet) is not PeerPacket:
        raise ValueError("invalid B packet")
    return {"source": packet.source, "step_index": packet.step_index,
            "time_s": packet.time_s, "moved": packet.moved}
