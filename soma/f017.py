"""F017 candidate: learn the action value of an opaque peer symbol.

No sender policy, world state, or topology truth is passed to this receiver.
This is receiver-side experience learning, not emergent communication or body formation.
DESIGN UNFROZEN: code candidate only, no F017 experiment/adoption claims.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import random


@dataclass(frozen=True)
class RawPeerSymbol:
    """Envelope metadata is NOT counted as one physical communication bit."""
    source_id: str
    step_index: int
    time_s: float
    symbol: int


def context_of(packet: RawPeerSymbol | None) -> int | None:
    """Validate B's framed opaque bit. None is absence, never bit zero."""
    if packet is None:
        return None
    if (
        type(packet) is not RawPeerSymbol
        or packet.source_id != "B"
        or type(packet.step_index) is not int
        or packet.step_index != 0
        or type(packet.time_s) is not float
        or packet.time_s != 0.0
        or type(packet.symbol) is not int
        or packet.symbol not in (0, 1)
    ):
        raise ValueError("invalid F017 B packet")
    return packet.symbol


class Receiver:
    """Two-actions/three-context epsilon-greedy recency-value learner.

    Learner input has no hidden target, mapping label, episode index, ground-truth
    'reached' or B battery. The independent experiment runner controls whether
    post-episode learn() is called; it must never communicate a phase flag.
    """

    def __init__(self, *, exploration_seed: int, alpha: float = 0.25,
                 epsilon: float = 0.125) -> None:
        if type(exploration_seed) is not int:
            raise ValueError("exploration seed must be integer")
        if (type(alpha) is not float or not math.isfinite(alpha)
                or not 0.0 < alpha <= 1.0):
            raise ValueError("alpha outside (0,1]")
        if (type(epsilon) is not float or not math.isfinite(epsilon)
                or not 0.0 <= epsilon <= 1.0):
            raise ValueError("epsilon outside [0,1]")
        self._rng = random.Random(exploration_seed)
        self.alpha = alpha
        self.epsilon = epsilon
        self._q = {(ctx, force): 0.0 for ctx in (None, 0, 1)
                   for force in (-2.0, 2.0)}
        self._pending: tuple[int | None, float] | None = None
        self._updates = 0

    def observe(self, packet: RawPeerSymbol | None) -> float:
        if self._pending is not None:
            raise RuntimeError("previous action must be closed before next observation")
        ctx = context_of(packet)
        scores = (self._q[(ctx, -2.0)], self._q[(ctx, 2.0)])
        if self._rng.random() < self.epsilon or scores[0] == scores[1]:
            force = (-2.0, 2.0)[self._rng.randrange(2)]
        else:
            force = -2.0 if scores[0] > scores[1] else 2.0
        self._pending = (ctx, force)
        return force

    def learn(self, *, own_action_n: float, own_acquired_uj: int,
              own_motor_spent_uj: int) -> None:
        """Accept only settled, own-cell ledger figures; no world score."""
        if self._pending is None:
            raise RuntimeError("no pending action to learn from")
        ctx, force = self._pending
        if (type(own_action_n) is not float or own_action_n != force
                or type(own_acquired_uj) is not int or own_acquired_uj < 0
                or type(own_motor_spent_uj) is not int or own_motor_spent_uj < 0):
            raise ValueError("invalid A-local feedback")
        reward_j = (own_acquired_uj - own_motor_spent_uj) / 1_000_000.0
        old = self._q[(ctx, force)]
        self._q[(ctx, force)] = old + self.alpha * (reward_j - old)
        self._updates += 1
        self._pending = None

    def end_without_learning(self) -> None:
        """Holdout/ablation: close a trial with no Q update or phase hint to A."""
        if self._pending is None:
            raise RuntimeError("no pending action")
        self._pending = None

    def snapshot(self) -> dict:
        """Research-only: never feed this snapshot into the A policy inputs."""
        if self._pending is not None:
            raise RuntimeError("snapshot only between episodes")
        return {
            "schema": "f017.receiver.snapshot.v1",
            "updates": self._updates,
            "q": {
                "none": [self._q[(None, -2.0)], self._q[(None, 2.0)]],
                "0": [self._q[(0, -2.0)], self._q[(0, 2.0)]],
                "1": [self._q[(1, -2.0)], self._q[(1, 2.0)]],
            },
        }
