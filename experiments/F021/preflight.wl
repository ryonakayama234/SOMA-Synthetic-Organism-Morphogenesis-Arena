(* F021 design-only Wolfram Language preflight. NOT F021 simulation evidence.
   Reproduces semi-implicit F001/F007 position and ideal F005-style
   signed trapezoid-work for the initial acceleration-only step. *)
Module[{dt = 1/4, fa = 2, ma = 1, mb = 1, fbValues = {-2, 0, 2}},
 Table[
  Module[{acc, v1, dxSemi, linkOnA, linkOnB, wa, wb, dke},
   acc = (fa + fb)/(ma + mb);
   v1 = acc dt;
   dxSemi = v1 dt;
   linkOnA = ma acc - fa;
   linkOnB = mb acc - fb;
   wa = fa (0 + v1) dt/2;
   wb = fb (0 + v1) dt/2;
   dke = (ma + mb) v1^2/2;
   <|"FA_N" -> fa, "FB_N" -> fb, "a_m_s2" -> acc,
     "x_increment_semiimplicit_m" -> dxSemi,
     "v_end_m_s" -> v1,
     "link_on_A_N" -> linkOnA, "link_on_B_N" -> linkOnB,
     "signed_work_A_J" -> wa, "signed_work_B_J" -> wb,
     "positive_work_A_J" -> Max[0, wa],
     "positive_work_B_J" -> Max[0, wb],
     "kinetic_delta_J" -> dke,
     "signed_work_residual_J" -> Simplify[dke - wa - wb]|>
   ],
  {fb, fbValues}]
]
