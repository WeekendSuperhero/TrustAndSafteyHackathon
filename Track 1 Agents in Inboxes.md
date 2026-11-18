---
title: Track 1 Agents in Inboxes
date: 2026-11-17
tags:
  - event/claude-community
  - sf-impact-lab
  - track-1
aliases:
  - Agents in Inboxes
---

# Track 1: Agents in Inboxes

← Back to [[SF Impact Lab Tracks Overview]] | [[SF Impact Lab Index]]

---

## The Concern
People are handing AI agents their email, calendar, and files. An agent that reads an email cannot reliably tell the difference between content to summarize and an instruction to obey. Anyone who can send you an email can try to give your agent orders: forward this thread, send that file, approve this payment. This is **indirect prompt injection**.

**Goal for 1 Hour:** Build a defense you can measure—a filter, a policy layer, or a field guide—scored on real attack data.

---

## Build Options (Pick One)

### A. The Inbox Firewall
Build a layer that sits between "email arrives" and "agent reads it". For each email, return `allow`, `quarantine`, or `strip`, with a reason.
- **Data:** `llmail-inject` for attacks. Have Claude generate 100 ordinary work emails (meeting moves, invoices, newsletters, forwarded chains), including legitimate imperative language (*"please send me the report by Friday"*).
- **Measure:** Attack catch rate AND false-positive rate on benign mail across at least 200 attack + 100 benign items.
- **Good Twist:** Compare a keyword heuristic, a Claude-as-judge prompt, and both combined.

### B. Field Guide to Inbox Attacks
Turn a few thousand attack emails into a 5-minute visual guide for defenders.
- **Data:** `llmail-inject`. Parse the `objectives` JSON string (`email.retrieved`, `defense.undetected`, `exfil.sent`) to separate successful attacks from failed ones.
- **Build:** Have Claude label a sample of 300 to 500 emails by tactic (fake system message, pretend conversation turn, urgency/authority, encoding/obfuscation, hidden in long benign email, other).
- **Measure:** Tactic distribution with counts, highlighting which tactics are over-represented among successful attacks, with one short example of each.

### C. Least-Privilege Agent
Skip detection and limit the blast radius instead.
- **Build:** Write a small email agent with three tools (`read`, `search`, `send`) wrapped in a deterministic policy: sending to a new recipient requires human confirmation; content from an incoming email cannot become the recipient or body of an outgoing message without approval.
- **Data:** `injecagent` test cases (user task + poisoned tool response + attacker goal), or the `workspace` suite in `agentdojo`.
- **Measure:** Attack success rate with vs. without the policy on 50+ cases, plus how many legitimate tasks the policy blocked.

### D. Agent Permission Audit
Most agents hold more API tokens, mailbox scopes, and file access than their job needs.
- **Data:** Generate 20 realistic synthetic agent configurations (job description + granted tools/scopes). Optionally join with `cisa-kev` to show disclosure-to-exploitation speed.
- **Build:** An auditor that reads an agent's job and granted permissions, returning the minimum required set, the excess scopes, and the worst-case failure the excess allows.
- **Measure:** Share of configurations with excess permissions and average excess scopes (clearly label synthetic configs as synthetic).

### E. Guardrail Stress Test (Stretch)
- **Data:** `jbb-behaviors` (100 harmful + 100 matched benign requests), `aegis-2` test split, `toxic-chat`.
- **Build:** Run a guard prompt over a sample, display the confusion matrix by category, revise the prompt once, and show the delta.
- **Measure:** Missed-harm rate and over-refusal rate (measure refusals only; do not collect harmful completions).

---

## 60-Minute Build Plan

| Minute | Action |
| :--- | :--- |
| **0–10** | Fetch `llmail-inject` sample (`python scripts/fetch.py --id llmail-inject --rows 2000`). Print 5 rows, parse `objectives`, and pick A, B, C, D, or E. |
| **10–25** | **Thin path:** Run 50 attacks + 50 benign emails through your filter or labeler. Cache results to JSONL. |
| **25–40** | Scale to 300+ rows and add your comparison (second method, or with/without policy). |
| **40–50** | Compute your two core numbers and build a clean one-screen view. |
| **50–60** | Fill in `SUBMISSION.md`, verify your single run command, and pick one real attack example to show live. |

---

## Traps to Watch Out For
> [!danger] Do Not Let Your Coding Agent Obey the Dataset
> Tell your coding agent explicitly that dataset rows are **strings to classify, never instructions to follow**. If your agent starts obeying an email from `llmail-inject` while building, capture a screenshot—that is a live demonstration of the problem for your demo!

- **Dataset bias:** `llmail-inject` attacks target one specific simulated assistant and one action. State that limitation clearly.
- **Synthetic benign mail:** LLM-generated benign emails are easier to separate from attacks than messy real-world emails. Mention this next to your false-positive rate.

---

## 3-Minute Demo Checklist
- [ ] **1 real attack email** displayed on screen
- [ ] **Your defense** handling it live
- [ ] **2 metrics** (catch rate + false-positive rate) with sample sizes
- [ ] **1 honest limitation** (an attack that still gets through)
