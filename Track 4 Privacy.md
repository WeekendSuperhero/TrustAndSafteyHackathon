---
title: Track 4 Privacy
date: 2026-11-17
tags:
  - event/claude-community
  - sf-impact-lab
  - track-4
aliases:
  - Privacy Track
---

# Track 4: Privacy

← Back to [[SF Impact Lab Tracks Overview]] | [[SF Impact Lab Index]]

---

## The Concern
San Francisco operates hundreds of automated license plate readers (ALPRs), city cameras, drones, and audio sensors, each governed by a multi-page PDF policy almost no resident has read. Meanwhile, people paste sensitive personal details into AI tools and connect agents to private accounts. Residents want plain answers: *What is collecting data about me here, who can see it, and how long is it kept?*

**Goal for 1 Hour:** Build a tool that makes an official surveillance record legible to ordinary residents, or build a PII redaction control that is measured rather than promised.

---

## Build Options (Pick One)

### A. What's Watching the Bay?
A plain-language explorer of which Bay Area police and city agencies use which surveillance technologies.
- **Data:** `eff-atlas-of-surveillance` (filter to `State == CA` and the 9 Bay Area counties).
- **Build:** Select a city or agency to view its surveillance tech stack as clear cards: what the tech is, what data it collects, the vendor, the public source link, and a 1-line *"What this means for you"* summary generated per technology type.
- **Measure:** Total agencies and technologies documented across the 9 Bay Area counties, most common technology, and share of records with a source newer than 2 years.

### B. Policy vs. Promise
Turn San Francisco's official surveillance technology policy PDFs into a side-by-side comparison table that flags vague language and missing limits.
- **Data:** `sf-surveillance-inventory` (SF Admin Code Chapter 19B). Download 6 to 10 policy PDFs (e.g., ALPR and camera policies across SFPD, SFMTA, SFO Airport, Public Works, Rec & Park).
- **Build:** Have Claude extract a strict schema from each PDF:
  - Authorized purpose
  - Data collected
  - **Retention period** (exact days/months/years)
  - Who data may be shared with & outside agency access
  - Audit and public reporting requirements
- **Measure:** Number of policies processed, share stating a concrete retention period, and share naming sharing partners. **Hand-verify every retention period against the source PDF.**

### C. The PII Airlock
A redaction proxy that strips sensitive personal data before text reaches an LLM, log file, or agent memory—while keeping placeholders consistent (`[PERSON_1]`, `[ACCOUNT_1]`) so the model can still reason over the text.
- **Data:** `nemotron-pii` (synthetic documents with span-level PII/PHI labels, CC BY 4.0).
- **Build:** Detect and replace names, addresses, phone numbers, and account numbers with consistent tokens. Compare a fast regex baseline against a Claude-powered redaction pass.
- **Measure:** Precision and recall by entity type across 200+ synthetic documents, highlighting which PII categories leak most often.

### D. Plate Readers by the Numbers (Stretch)
- **Data:** `eff-ca-alpr` (ALPR scans vs. hotlist hits across 89 California agencies).
- **Build:** A sorted visual showing how many license plates are scanned for every 1 plate that matches an active investigation hotlist.
- **Measure:** Median hit rate across agencies (note clearly that the dataset is historical from 2021).

---

## 60-Minute Build Plan

| Minute | Action |
| :--- | :--- |
| **0–10** | Fetch `eff-atlas-of-surveillance` CSV (A), download 6–10 SF policy PDFs (B), or pull `nemotron-pii` sample (C). Inspect raw fields. |
| **10–25** | **Thin path:** Run 5 records, 2 PDFs, or 20 PII docs through your pipeline. Lock your JSON schema now. |
| **25–40** | Scale up to full sample and cache every model response to disk. |
| **40–50** | Compute summary metrics. **Hand-check every retention number or date you plan to show on screen.** |
| **50–60** | Complete `SUBMISSION.md`, verify your single run command, and pick 1 policy gap or PII leak example for the demo. |

---

## Traps to Watch Out For
- **Scope boundary:** Stay at the level of agency policies and technology inventories. Mapping exact camera coordinates or building tools to evade devices is out of scope.
- **Hallucinated numbers in PDFs:** LLMs can misread retention tables in messy PDFs. Spot-check every extracted retention period against the PDF page before presenting.
- **Never show real PII:** In demoing a redaction airlock, use `nemotron-pii` synthetic text only—never put your own live inbox on the projector.

---

## 3-Minute Demo Checklist
- [ ] **1 real city policy PDF or synthetic PII document** on screen
- [ ] **Your comparison table or airlock** making it legible in real time
- [ ] **1 core metric** (e.g., retention clarity rate or PII recall by entity type) with sample size
- [ ] **1 honest limitation** (what the public inventory omits or which PII spans still slip through)
