"""F017 preregistered source-physics and forged-output small negative tests.

Full 23,296-episode scientific run belongs to f017.yml, not inherited tests.
"""
import copy
import random
import unittest
from soma.f017 import Receiver
from experiments.F017.run_suite import causal_probe, episode, schedule, rng_seed
from experiments.F017.verify import verify_world, init_q, permutation


class F017EvidenceUnitTests(unittest.TestCase):
    def test_phase_balanced_and_independent_bit_stream(self):
        for seed in range(8):
            for phase,n in (("train",64),("holdout",32),("probe",16),("adapt",64),("final",32)):
                world=schedule(seed,phase,n,"world")
                scramble=schedule(seed,phase,n,"scramble")
                self.assertEqual(sum(world),n//2)
                self.assertEqual(sum(scramble),n//2)
                self.assertEqual(list(world),permutation(seed,phase,n,"world"))

    def test_one_real_f007_episode_and_f002_saved_truth(self):
        q=Receiver(exploration_seed=rng_seed("policy|0|0|I"))
        target=schedule(0,"train",64,"world")[0]
        scrambled=schedule(0,"train",64,"scramble")[0]
        rec=episode("I",0,0,"train",0,target,scrambled,q)
        audited_q=init_q()
        seed_rng=random.Random(rng_seed("policy|0|0|I"))
        updated=verify_world(rec,"I",0,0,"train",0,target,scrambled,
                             audited_q,0,seed_rng)
        self.assertEqual(updated,1)
        self.assertEqual(rec["motor_spent_uj"],1_000_000)
        self.assertEqual(rec["ledger_residual_uj"],0)

    def test_offworld_full_policy_rng_clone_does_not_advance_main_learner(self):
        receiver=Receiver(exploration_seed=rng_seed("policy|0|0|I"))
        for sym in (0,1,0,1):
            from soma.f017 import RawPeerSymbol
            action=receiver.observe(RawPeerSymbol("B",0,0.0,sym))
            reward=3_000_000 if (sym==0 and action==-2.0 or sym==1 and action==2.0) else 0
            receiver.learn(own_action_n=action,own_acquired_uj=reward,
                           own_motor_spent_uj=1_000_000)
        original_q=receiver.snapshot()
        original_rng=receiver._rng.getstate()
        a=causal_probe(receiver,0,0,"I","holdout")
        self.assertEqual(a,causal_probe(receiver,0,0,"I","holdout"))
        self.assertEqual(receiver.snapshot(),original_q)
        self.assertEqual(receiver._rng.getstate(),original_rng)
        self.assertEqual(a["draws"],256)
        self.assertEqual(len(a["checkpoint_rng_sha256"]),64)

    def test_rehashed_narrative_forgery_rejected_by_independent_semantics(self):
        for field in ("net_uj","action_n","target_right","position","q_update","packet"):
            with self.subTest(field=field):
                learner=Receiver(exploration_seed=rng_seed("policy|0|0|I"))
                target=schedule(0,"train",64,"world")[0]
                shuffled=schedule(0,"train",64,"scramble")[0]
                record=episode("I",0,0,"train",0,target,shuffled,learner)
                forged=copy.deepcopy(record)
                if field=="net_uj": forged["net_uj"]+=3_000_000
                if field=="action_n": forged["action_n"]*=-1
                if field=="target_right": forged["target_right"]=1-target
                if field=="position": forged["states"][4]["x_a_m"]+=.125
                if field=="q_update": forged["Q_after"]["q"]["0"][0]+=1
                if field=="packet": forged["packet"]["symbol"]^=1
                with self.assertRaisesRegex(ValueError,"independent saved-world rejection"):
                    verify_world(forged,"I",0,0,"train",0,target,shuffled,
                                 init_q(),0,random.Random(rng_seed("policy|0|0|I")))


if __name__=="__main__":
    unittest.main()
