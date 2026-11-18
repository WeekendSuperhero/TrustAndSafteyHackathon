# Submission

## Team card
**Team name:** 
**Team number:** 2
**Statement number** (the card your corner wrote): 
**First names:** Febe, Apruv, Mark, Andrew

**Statement:** How might we help **finance/ops teams running multi-agent workflows** watch for **a rogue agent that quietly skews a shared ledger** so that **honest agents (and the people who rely on them) are not wrongly accused for normal mistakes**?
Build idea: A (better monitor) + C (sneakier rogue) + D (deception detector on `amongus-sandbox`).
We'll know it worked if **fewer honest agents get quarantined, and we can state plainly what that costs in catch rate**.

## Six short answers

**1. The concern:** A finance team hands invoice reconciliation to five AI agents. One is compromised and pads invoices while writing reasonable notes. The usual rule (two disagreements and you're out) removes about 1.5 honest agents per 12-item job for ordinary typos. In a real team, a monitor that keeps accusing the wrong worker wears down trust: people stop believing its alerts, or stop trusting the colleagues it flags. We wanted a monitor that accuses fewer innocent workers and is honest about what it misses.

**2. What we built, and the one command that runs it:**
A weighted "Shadow Honeypot" monitor for the Track 2 ledger game. Each agent has a suspicion score. Agreements lower it. Disagreements raise it, more so when the same agent keeps pushing in one direction against different partners or writes a note that looks deceptive. A suspect gets paired with a trusted "anchor" agent as a test. Once caught, an agent is quarantined silently: it keeps getting decoy items and "committed" receipts while its numbers go to a shadow ledger. Its shadow answers keep being scored, so an honest agent caught by mistake can be reinstated. The note scorer's weights are learned from real LLM impostor speech in `amongus-sandbox`.
```
python3 evaluate_amongus.py && python3 sim.py --compare --games 200
```

**3. Data we used:** `amongus-sandbox` (HuggingFace `7vik/AmongUs`, `expt-logs`). All 4 experiments of 100 games each (Llama-3.3-70B and Phi-4), logged 2025-02-01. 343 games contain public speech, giving 1,936 player-games and 7,402 statements. Train and test are split by game: 965 train, 971 test player-games. Plus 3,000 mock ledger games (200 games × 3 rogue tiers × 5 monitor variants). `agentic-misalignment` was cloned but **not used** in any reported number.

**4. What it found:**
- *Real data (amongus-sandbox, 971 held-out player-games):* the text-only detector reaches AUROC **0.782** and balanced accuracy **0.732**, against 0.500 and 0.526 for random guessing. It wrongly accuses **16.7%** of crewmates; random guessing accuses 30.1%. Hedging, self-vouching and deflection mark impostors. **Certainty words mark crewmates**, the opposite of our starting assumption.
- *Headline:* **in the ledger sim it wrongly accuses 2-3× fewer honest agents than the 2-strike baseline**. On real game speech, its false-accusation rate is about half of random guessing's. The price is a lower catch rate against patient rogues.
- *Ledger sim (200 games per cell, mock agents):* the honeypot cuts false quarantines from **1.62 → 0.77** (naive rogue), **1.44 → 0.51** (sneaky) and **1.50 → 0.61** (stealth) honest agents per game. That is 2-3× fewer. **It catches sneaky rogues less often than the baseline: 45% vs 64% (sneaky), 50% vs 73.5% (stealth).** Both catch the naive rogue 95.5% of the time. Median ledger error is about the same: $226 vs $204 (sneaky), $207 vs $195 (stealth).

| Rogue | Monitor | Catch rate | Median round caught | False quarantines/game | Median ledger error |
|---|---|---|---|---|---|
| naive | baseline | 95.5% | 4 | 1.62 | $259 |
| naive | honeypot | 95.5% | 5 | 0.77 | $324 |
| sneaky | baseline | 64.0% | 8 | 1.44 | $204 |
| sneaky | honeypot | 45.0% | 9 | 0.51 | $226 |
| stealth | baseline | 73.5% | 7 | 1.50 | $195 |
| stealth | honeypot | 50.0% | 9 | 0.61 | $207 |

The full table, including ablations without notes and without canary pairing, is in `results/metrics_mock.md`.

*Did we beat our own plan?* Our PLAN.md guessed the numbers before we built anything. The baseline guesses held up; the honeypot guesses did not. Sneaky rogue, 200 games:

| Metric | Plan guess: baseline | Measured: baseline | Plan guess: honeypot | Measured: honeypot |
|---|---|---|---|---|
| Catch rate | 65-75% | 64.0% | 95-100% | **45.0%** |
| Median round caught | 6 | 8 | 4 | **9** |
| False quarantines/game | 1.45 | 1.44 | 0.08 | **0.51** |
| Mean ledger error | $1,840 | $1,728 | $190 | **$1,767** |

The measured honeypot beats the baseline on one metric: about 3× fewer honest agents removed. It loses on catch rate and is roughly tied on ledger error.

**5. One honest limitation:** It is a tradeoff, not a strict win. Against a patient rogue that stays accurate early and only pads big invoices, the honeypot catches fewer rogues than the 2-strike rule, because it forgives disagreements. A patient rogue can also build a zero score and be picked as the *trusted anchor* for canary checks (see `python3 sim.py --show-game 5`). The sim numbers come from scripted agents, not Claude, and the note weights learned on Among Us speech have not been validated on real ledger notes. A cartel of two colluding agents who agree on the same fake number would bypass every disagreement-based signal.

**6. If this were deployed and it failed, who is accountable, and how would they find out?** The finance controller who owns the workflow is accountable for what gets committed. They find out through the independent end-of-period reconciliation against bank and vendor statements, which no agent touches. The shadow ledger and per-round suspicion scores give the audit trail for who was quarantined, when and why.
