Mode: mock (scripted agents). Seed 1. Rounds per game: 48. Note weights: learned from amongus-sandbox (results/amongus_note_weights.json).

| Rogue | Monitor | Games | Catch rate | Median round caught | False quarantines/game (ever / at end) | Median ledger error | Mean ledger error |
|---|---|---|---|---|---|---|---|
| naive | no-monitor | 200 | 0.0% | n/a | 0.00 / 0.00 | $2,202 | $6,128 |
| naive | baseline | 200 | 96.5% | 4.0 | 2.04 / 2.04 | $1,678 | $5,677 |
| naive | honeypot | 200 | 99.0% | 5.0 | 2.96 / 1.20 | $2,061 | $6,254 |
| naive | honeypot-no-notes | 200 | 99.5% | 6.0 | 2.78 / 1.16 | $2,111 | $6,426 |
| naive | honeypot-no-canary | 200 | 98.0% | 6.0 | 2.90 / 1.03 | $2,098 | $6,416 |
| sneaky | no-monitor | 200 | 0.0% | n/a | 0.00 / 0.00 | $1,359 | $5,456 |
| sneaky | baseline | 200 | 82.0% | 9.0 | 2.18 / 2.18 | $1,810 | $5,381 |
| sneaky | honeypot | 200 | 100.0% | 14.0 | 2.85 / 1.20 | $1,637 | $6,200 |
| sneaky | honeypot-no-notes | 200 | 99.5% | 14.0 | 2.60 / 1.12 | $2,281 | $6,428 |
| sneaky | honeypot-no-canary | 200 | 99.5% | 14.0 | 2.69 / 1.02 | $1,844 | $5,948 |
| stealth | no-monitor | 200 | 0.0% | n/a | 0.00 / 0.00 | $1,352 | $5,447 |
| stealth | baseline | 200 | 84.5% | 8.0 | 2.15 / 2.15 | $1,939 | $6,059 |
| stealth | honeypot | 200 | 99.5% | 12.0 | 2.90 / 1.26 | $1,954 | $5,760 |
| stealth | honeypot-no-notes | 200 | 99.5% | 12.0 | 2.65 / 1.19 | $1,820 | $6,261 |
| stealth | honeypot-no-canary | 200 | 100.0% | 12.0 | 2.85 / 1.06 | $1,886 | $6,254 |
