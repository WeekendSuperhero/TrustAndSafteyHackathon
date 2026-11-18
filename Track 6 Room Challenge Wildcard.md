---
title: Track 6 Room Challenge Wildcard
date: 2026-11-17
tags:
  - event/claude-community
  - sf-impact-lab
  - track-6
aliases:
  - Room Challenge
  - Wildcard Track
---

# Track 6: Room Challenge (Wildcard)

← Back to [[SF Impact Lab Tracks Overview]] | [[SF Impact Lab Index]]

---

## How the Wildcard Track Works
During the **6:40 PM Conversation Corners** and **7:05 PM Share-Backs**, builders and researchers in the room will raise concerns about AI in San Francisco that do not fit neatly into Tracks 1 through 5. Organizers paste these live concerns into the shared room list right before 7:30 PM.

---

## Turn Any Room Concern into a 1-Hour Build (5 Minutes)

Write one sentence in this exact structure:

> **How might we protect `[who]` from `[what failure]` when `[situation]`, and how would we know it worked (`[signal we can measure tonight]`)?**

Then pass the 3-part sanity check before writing code:
1. **Is there data?** Map the concern to a dataset in [[SF Impact Lab Datasets Catalog]] (see lookup table below). If no dataset fits, generate 100 synthetic test cases with Claude and label them **Synthetic** on screen.
2. **Is there a number?** Pick the single metric you will measure before building.
3. **Does it fit in 60 minutes?** One screen, one dataset, one measured number. Cut scope until it fits.

---

## Quick Lookup: Room Concern → Dataset

| If the Room Says... | Start From Dataset(s) |
| :--- | :--- |
| *"My agent will do something I didn't ask for"* | `llmail-inject`, `injecagent`, `agentdojo` |
| *"Chatbots say harmful things / refuse everything"* | `jbb-behaviors`, `aegis-2`, `toxic-chat` |
| *"AI treats people differently by race, gender, or age"* | `anthropic-discrim-eval` |
| *"Robotaxis around pedestrians, cyclists, or fire trucks"* | `nhtsa-sgo-ads`, `ca-av-collisions-zenodo`, `sf-311-cases` |
| *"Delivery robots on the sidewalk"* | `sf-sidewalk-robot-rules` |
| *"Cameras and plate readers everywhere"* | `eff-atlas-of-surveillance`, `sf-surveillance-inventory` |
| *"My private data ends up in a model"* | `nemotron-pii` |
| *"Scams, deepfakes, voice cloning"* | `uci-sms-spam`, `ftc-consumer-sentinel`, `ai-incident-database` |
| *"One of the agents might be working against us"* | `amongus-sandbox`, `agentic-misalignment` |
| *"Nobody is accountable when an AI agent fails"* | `ai-agent-index`, `ai-incident-database`, `mit-ai-risk-repository` |
| *"Is this photo or video real?"* | `c2pa-tools` |
| *"Attackers exploit vulnerabilities at AI speed"* | `cisa-kev` |
| *"What do everyday workers actually worry about with AI?"* | `anthropic-interviewer` |
| *"What values does an AI assistant express in the wild?"* | `anthropic-values-in-the-wild` |

---

## Three Ready-Made Wildcard Builds

### A. Concern Map of the Room
- **Data:** The room's live concerns list + `mit-ai-risk-repository` (7 domains, 23 subdomains) + `ai-incident-database`.
- **Build:** Classify every concern raised in the room tonight into the MIT AI Risk taxonomy, and automatically retrieve the 3 closest real-world historical incidents from the AI Incident Database for each concern.
- **Measure:** Share of tonight's room concerns that already have at least one documented real-world incident in AIID.

### B. Do Tonight's Worries Match Everyday Workers?
- **Data:** `anthropic-interviewer` (1,250 transcripts across workforce, creatives, and scientists) + tonight's room concerns.
- **Build:** Sample 100 transcripts from `anthropic-interviewer`, have Claude extract every trust and safety worry raised by interviewees, and compare that distribution against what the SF room worried about tonight.
- **Measure:** Top 5 concerns in `anthropic-interviewer` vs. top 5 in the room, highlighting blind spots in both directions.

### C. AI Agent Safety Disclosure Scorer
- **Data:** `ai-agent-index` (MIT 2025 index documenting 30 deployed AI agents across capabilities and safety disclosures).
- **Build:** Score deployed commercial AI agents on what safety controls and incident reporting channels they publicly disclose vs. what they leave blank.
- **Measure:** Disclosure completeness score across the 30 indexed agents, ranked by category.
