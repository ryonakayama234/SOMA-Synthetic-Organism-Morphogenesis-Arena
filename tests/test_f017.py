"""F017 receiver-only interface tests. Synthetic terminal feedback, NOT F017 world data."""
from __future__ import annotations

import copy
import unittest

from soma.f017 import RawPeerSymbol, Receiver, context_of


def packet(bit: int) -> RawPeerSymbol:
    return RawPeerSymbol("B", 0, 0.0, bit)


class F017ReceiverUnitTests(unittest.TestCase):
    def test_opaque_bits_and_none_are_distinct(self):
        self.assertIsNone(context_of(None))
        self.assertEqual(context_of(packet(0)), 0)
        self.assertEqual(context_of(packet(1)), 1)
        for bad in (
            RawPeerSymbol("world", 0, 0.0, 1),
            RawPeerSymbol("B", 1, 0.0, 1),
            RawPeerSymbol("B", True, 0.0, 1),
            RawPeerSymbol("B", 0, .25, 1),
            RawPeerSymbol("B", 0, 0.0, True),
            RawPeerSymbol("B", 0, 0.0, 2),
            {"symbol": 0, "true_target": -0.625},
            False,
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                context_of(bad)

    def test_strict_local_feedback_and_two_step_lifecycle(self):
        a = Receiver(exploration_seed=0, epsilon=0.0)
        with self.assertRaises(RuntimeError):
            a.learn(own_action_n=2.0, own_acquired_uj=0, own_motor_spent_uj=0)
        force = a.observe(packet(0))
        with self.assertRaises(RuntimeError):
            a.observe(packet(0))
        with self.assertRaises(ValueError):
            a.learn(own_action_n=-force, own_acquired_uj=0, own_motor_spent_uj=1_000_000)
        with self.assertRaises(ValueError):
            a.learn(own_action_n=force, own_acquired_uj=True, own_motor_spent_uj=0)
        with self.assertRaises(TypeError):
            a.learn(own_action_n=force, own_acquired_uj=3_000_000,
                    own_motor_spent_uj=1_000_000, target_x_m=.625)
        a.learn(own_action_n=force, own_acquired_uj=3_000_000,
                own_motor_spent_uj=1_000_000)
        self.assertEqual(a.snapshot()["updates"], 1)

    def test_feedback_withheld_does_not_modify_values(self):
        a = Receiver(exploration_seed=12)
        before = a.snapshot()
        for bit in (0, 1, 0, 1, 0):
            a.observe(packet(bit))
            a.end_without_learning()
        self.assertEqual(a.snapshot(), before)

    def test_reproducible_exploration_without_world_inputs(self):
        a = Receiver(exploration_seed=1729)
        b = Receiver(exploration_seed=1729)
        for bit in (0, 1, None, 0, 1, 1, None) * 4:
            p = None if bit is None else packet(bit)
            fa, fb = a.observe(p), b.observe(p)
            self.assertEqual(fa, fb)
            reward = 3_000_000 if ((bit == 0 and fa == -2.0)
                                   or (bit == 1 and fa == 2.0)) else 0
            a.learn(own_action_n=fa, own_acquired_uj=reward, own_motor_spent_uj=1_000_000)
            b.learn(own_action_n=fb, own_acquired_uj=reward, own_motor_spent_uj=1_000_000)
            self.assertEqual(a.snapshot(), b.snapshot())

    def test_causal_listening_probe_is_cloned_and_no_learning(self):
        a = Receiver(exploration_seed=3, epsilon=0.0)
        # Synthetic controlled teaching events, not simulated F007 evidence:
        for bit, reward_action in ((0, -2.0), (1, 2.0)):
            for _ in range(20):
                # Ensure the desired action is eventually visited by forced exploration.
                a.epsilon = 1.0
                f = a.observe(packet(bit))
                a.learn(own_action_n=f,
                        own_acquired_uj=3_000_000 if f == reward_action else 0,
                        own_motor_spent_uj=1_000_000)
        a.epsilon = 0.0
        before = a.snapshot()
        a0, a1 = copy.deepcopy(a), copy.deepcopy(a)
        self.assertEqual(a0.observe(packet(0)), -2.0)
        self.assertEqual(a1.observe(packet(1)), 2.0)
        a0.end_without_learning()
        a1.end_without_learning()
        self.assertEqual(a.snapshot(), before)

    def test_invalid_hyperparameters(self):
        for kwargs in (
            {"exploration_seed": True},
            {"exploration_seed": 0, "alpha": 0.0},
            {"exploration_seed": 0, "alpha": 2.0},
            {"exploration_seed": 0, "epsilon": -0.1},
            {"exploration_seed": 0, "epsilon": 1.1},
            {"exploration_seed": 0, "epsilon": float("nan")},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Receiver(**kwargs)


if __name__ == "__main__":
    unittest.main()
