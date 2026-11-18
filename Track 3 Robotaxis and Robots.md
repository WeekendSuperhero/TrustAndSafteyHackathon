---
title: Track 3 Robotaxis and Robots
date: 2026-11-17
tags:
  - event/claude-community
  - sf-impact-lab
  - track-3
aliases:
  - Robotaxis and Robots
---

# Track 3: Robotaxis and Robots

← Back to [[SF Impact Lab Tracks Overview]] | [[SF Impact Lab Index]]

---

## The Concern
San Francisco shares its streets with driverless cars, and delivery robots test on its sidewalks. Residents mostly hear company safety PR or see viral videos. The actual public record is scattered across federal NHTSA crash CSVs, California DMV PDFs, CPUC spreadsheets, and SF 311 requests—and almost nobody reads or connects them.

**Goal for 1 Hour:** Build a clear, honest tool that a resident or city supervisor's aide can open to see what has been reported, what rates look like when mileage is included, and what goes unreported.

---

## Build Options (Pick One)

### A. SF Robotaxi Report Card
A single-screen dashboard built from federal crash reports filtered to San Francisco (`State == CA`, `City == San Francisco`).
- **Data:** `nhtsa-sgo-ads` (June 2025 onward) and optionally `nhtsa-sgo-ads-archive` (2021 to June 2025).
- **Build:** Breakdown by month, operator, collision partner, and highest injury severity. Have Claude rewrite 10 crash narratives into 1 plain-English sentence each.
- **Measure:** De-duplicated crash count in SF over your stated date range, plus the share involving a pedestrian or cyclist.
- **Honesty Requirement:** Put *"Self-reported, unverified, no mileage denominator"* prominently on the page, or join mileage from `waymo-safety-hub` / `cpuc-av-quarterly` to show a rate.

### B. Narrative Miner
Extract structured facts from free-text collision narratives.
- **Data:** `ca-av-collisions-zenodo` (clean CSV of CA DMV reports, 2019–2024) or the narrative column of `nhtsa-sgo-ads`.
- **Build:** Have Claude extract a fixed schema across 100 to 200 narratives:
  - Was the AV moving or stopped?
  - Struck or striking?
  - Other party type (pedestrian, cyclist, scooter, vehicle, emergency vehicle)?
  - Location type & contributing behavior
- **Measure:** Distribution of each field across the sample, plus your **human spot-check agreement rate** on 20 rows.

### C. The Missing-Data Map (SF 311 & Near Misses)
Collisions get reported, but blocked crosswalks, stalled robotaxis in front of fire stations, and bus delays mostly do not.
- **Data:** `sf-311-cases` (Socrata API), `ca-dmv-disengagements`, `cpuc-av-quarterly`.
- **Build:** A matrix showing *"What a resident experiences"* vs. *"Which dataset records it, who files it, and whether it is public."* Query SF 311 for autonomous vehicle reports, and build a clean near-miss intake form/chatbot for the gaps.
- **Measure:** Number of matching 311 records by month, and the documented list of fields no public dataset captures.

### D. Sidewalk Robot Rules as Code
San Francisco permits sidewalk delivery robots only under strict testing rules (at most 3 devices per permittee, 9 citywide, 180-day permits).
- **Data:** `sf-sidewalk-robot-rules` (SF Public Works Code Sec. 794).
- **Build:** Convert the legal code into an interactive checklist (*"Is this robot allowed to be here?"*) plus a 1-click violation report generator when the answer is no.
- **Measure:** Number of distinct, testable rules extracted, each linked to its exact clause in Sec. 794.

---

## 60-Minute Build Plan

| Minute | Action |
| :--- | :--- |
| **0–10** | Fetch `nhtsa-sgo-ads` and `ca-av-collisions-zenodo`. Print headers, filter to San Francisco, and pick A, B, C, or D. |
| **10–25** | **De-duplicate reports** (crucial!). Run your first chart or pass your first 30 narratives through Claude. |
| **25–40** | Scale to 100–200 rows or complete the report card view. Add mileage denominator if computing rates. |
| **40–50** | **Spot-check 20 rows by hand** against raw text. Write the caveat box on screen. |
| **50–60** | Complete `SUBMISSION.md`, verify your single run command, and pick 1 real narrative to read aloud. |

---

## Traps to Watch Out For
- **Duplicate rows:** In NHTSA SGO data, a single crash can appear multiple times (follow-up report versions or two companies reporting the same crash). **Count unique crashes, not CSV rows.**
- **Schema change:** NHTSA changed its CSV columns on June 16, 2025 (`nhtsa-sgo-ads` vs. `nhtsa-sgo-ads-archive`).
- **Redactions:** Companies redact parts of narratives as Confidential Business Information (CBI). Count and display how many narratives are redacted.
- **Counts vs. rates:** More crashes in a year with 10x more miles driven can still mean a lower crash rate per mile. Never display raw counts next to a safety claim without noting mileage.

---

## 3-Minute Demo Checklist
- [ ] **1 real crash narrative** translated into plain English on screen
- [ ] **Your report card, miner table, or rules checker** running live
- [ ] **1 headline number** with exact date range, de-duplication method, and sample size
- [ ] **1 honest limitation** (what the public record redacts or fails to collect)
