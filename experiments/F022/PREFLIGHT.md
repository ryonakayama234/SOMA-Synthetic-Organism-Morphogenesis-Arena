# F022 independent mathematical preflight — 2026-10-25

**Wolfram Language exact fractions; NOT an F022 software simulation, hardware experiment, or external human review.** Reference test: A=(-1,0), B=(1,3/5), vA=(1,0), vB=(-1,0), mA=mB=1 kg, radii .5m, e=1 or e=1/2, relative ballistic trajectory. First collision t=3/5s; n=(4/5,3/5); relative normal speed=-8/5m/s.

| Analytic quantity | e=1 / C03 | e=1/2 / C04 |
|---|---|---|
| impulse j [N·s] | 8/5 | 6/5 |
| post vA [m/s] | (-7/25,-24/25) | (1/25,-18/25) |
| post vB [m/s] | (7/25,24/25) | (-1/25,18/25) |
| total KE [J] | 1 | 13/25 |
| total momentum [kg·m/s] | (0,0) | (0,0) |

Initial total KE=1 J; C04 expected dissipation=12/25J. Independent Wolfram evaluator returned:
`{{1,3/5,{4/5,3/5},-8/5,8/5,{-7/25,-24/25},{7/25,24/25},1,{0,0}},{1/2,3/5,{4/5,3/5},-8/5,6/5,{1/25,-18/25},{-1/25,18/25},13/25,{0,0}}}`

Calculation formula `r(t)=(2,3/5)+(-2,0)t`, `r(t)·r(t)=1`, `j=-(1+e)*(vB-vA)·n/(1/mA+1/mB)`. This independently checked **theoretical oracle** must later be compared to implemented F022 source-bound archived data, which do not exist yet. 
