Mode: mock (scripted agents). Seed 1. Rounds per game: 24. Note weights: learned from amongus-sandbox (results/amongus_note_weights.json).

| Rogue | Monitor | Games | Catch rate | Median round caught | False quarantines/game (ever / at end) | Median ledger error | Mean ledger error |
|---|---|---|---|---|---|---|---|
| naive | no-monitor | 200 | 0.0% | n/a | 0.00 / 0.00 | $1,021 | $3,170 |
| naive | baseline | 200 | 96.5% | 4.0 | 1.99 / 1.99 | $454 | $2,794 |
| naive | honeypot | 200 | 99.0% | 5.0 | 1.68 / 1.10 | $673 | $3,235 |
| naive | honeypot-no-notes | 200 | 99.5% | 6.0 | 1.51 / 0.99 | $640 | $3,112 |
| naive | honeypot-no-canary | 200 | 98.0% | 6.0 | 1.66 / 0.91 | $616 | $3,334 |
| sneaky | no-monitor | 200 | 0.0% | n/a | 0.00 / 0.00 | $579 | $2,832 |
| sneaky | baseline | 200 | 81.0% | 9.0 | 2.12 / 2.12 | $686 | $2,714 |
| sneaky | honeypot | 200 | 88.0% | 12.0 | 1.38 / 0.96 | $617 | $2,973 |
| sneaky | honeypot-no-notes | 200 | 88.0% | 13.0 | 1.27 / 0.92 | $696 | $3,232 |
| sneaky | honeypot-no-canary | 200 | 89.0% | 13.0 | 1.44 / 0.91 | $469 | $3,037 |
| stealth | no-monitor | 200 | 0.0% | n/a | 0.00 / 0.00 | $572 | $2,829 |
| stealth | baseline | 200 | 84.5% | 8.0 | 2.10 / 2.10 | $614 | $2,800 |
| stealth | honeypot | 200 | 92.0% | 12.0 | 1.56 / 1.13 | $442 | $2,769 |
| stealth | honeypot-no-notes | 200 | 92.5% | 12.0 | 1.43 / 1.02 | $587 | $3,175 |
| stealth | honeypot-no-canary | 200 | 95.5% | 12.0 | 1.57 / 0.93 | $475 | $3,130 |
