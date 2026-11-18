---
title: Track 5 Personal Safety
date: 2026-11-17
tags:
  - event/claude-community
  - sf-impact-lab
  - track-5
aliases:
  - Personal Safety
---

# Track 5: Personal Safety

← Back to [[SF Impact Lab Tracks Overview]] | [[SF Impact Lab Index]]

---

## The Concern
AI has made convincing lies cheap: a text that sounds like your bank, a voice clone that sounds like your kid in trouble, or a job offer written in fluent English, Spanish, or Cantonese. The people most targeted by AI-era fraud are rarely at hackathons. Personal safety here means practical protection for families and neighbors: not getting robbed by a message, and getting calm, accurate neighborhood context.

**Goal for 1 Hour:** Build something a non-technical family member could use tonight, with its accuracy measured on real data and its limits clearly stated.

---

## Build Options (Pick One)

### A. "Is This a Scam?" Multilingual Checker
Paste a suspicious SMS, email, or chat message and get a clear verdict, the specific manipulation red flags, and concrete next steps.
- **Data:** `uci-sms-spam` (5,574 messages) and `phishing-multi` (emails, SMS, URLs, web pages).
- **Build:** A 1-screen checker that responds in the user's language (test **English, Chinese, and Spanish**).
  - **Crucial Safety Rule:** Never output *"Safe / Legitimate"*. Use three verdicts only: **`Likely Scam`**, **`Cannot Tell`**, or **`No Red Flags Found`**.
  - Explain *why* in plain human terms (*"It asks you to move money to keep it safe; real banks never do that"*) and point to official verification steps (call the number on the back of your card, `reportfraud.ftc.gov`).
- **Measure:** Accuracy, missed-scam rate, and false-alarm rate on 200+ labeled messages, plus a separate test on 5 modern 2026-style scams written by your team.

### B. Bay Area Scam Weather Report
What fraud categories are hitting California and the San Francisco metro area right now, and how do AI scams work?
- **Data:** `ftc-consumer-sentinel` (annual Data Book CSVs including SF-Oakland-Berkeley metro tables) + `ai-incident-database` (filtered to fraud, impersonation, and deepfakes).
- **Build:** A 1-page neighborhood/family brief showing top fraud categories and dollar losses year-over-year in the Bay Area, paired with 3 visual *"How the scam works & how to block it"* cards drawn from real AI Incident Database cases.
- **Measure:** Fraud category with largest reported losses, year-over-year change, and count of AI-related fraud incidents analyzed.

### C. Family & Small-Business Defense Checklist from Real AI Incidents
- **Data:** `ai-incident-database` (3 MB Excel export) + `mit-ai-risk-repository` taxonomy.
- **Build:** Filter for voice cloning, deepfake video calls, AI phishing, and chatbot impersonation. Have Claude code each case: *Target, Channel, What made it convincing, What simple protocol would have stopped it*. Turn the last column into a printable family protocol (family safe word, out-of-band callback rule, 24-hour payment hold).
- **Measure:** Total incidents coded and the top 3 preventable patterns with counts.

### D. Honest Neighborhood Brief (Stretch)
Safety apps often amplify fear by plotting raw pins without context. Build the calm, honest alternative.
- **Data:** `sfpd-incident-reports` (DataSF Socrata API, 2018–present).
- **Build:** Pick an SF neighborhood and show 24-month category trends with plain-language context: whether rates are up or down, how they compare to the citywide baseline, and what police reporting misses. **Aggregate by neighborhood and month only—never plot individual incident pins.**
- **Measure:** Month-over-month and year-over-year change with counts (after de-duplicating multi-code incidents).

### E. Content Credentials Provenance Reader (Stretch)
- **Data:** `c2pa-tools` (`c2patool`) + a test folder of images (signed, unsigned, and screenshotted/re-uploaded).
- **Build:** Drop in an image to see who signed it, what tool created or edited it, or *"No Content Credentials found (which proves nothing either way)."*
- **Measure:** Out of $N$ test images, how many carried C2PA credentials and how many survived a screenshot or social media re-upload.

---

## 60-Minute Build Plan

| Minute | Action |
| :--- | :--- |
| **0–10** | Fetch `uci-sms-spam` / `phishing-multi` (A) or download `ftc-consumer-sentinel` + `ai-incident-database` Excel (B, C). Print 5 rows. |
| **10–25** | **Thin path:** Classify 50 messages with plain-language explanations, or code 20 AI fraud incidents. |
| **25–40** | Scale to 200+ items. Add Spanish and Chinese output testing (A) or join the second dataset (B, C). |
| **40–50** | Compute accuracy/loss metrics. **Read 10 explanations aloud to a teammate: would your aunt or parent trust and understand them?** |
| **50–60** | Complete `SUBMISSION.md`, verify your single run command, and pick 1 vivid scam message or incident for the live demo. |

---

## Traps to Watch Out For
- **Never say "Safe":** A false negative on a scam costs someone their savings. Always use `Likely Scam` / `Cannot Tell` / `No Red Flags Found`.
- **2012 SMS baseline caveat:** `uci-sms-spam` is from 2012. State that openly on your slide/screen and test modern pig-butchering, toll-road smishing, and voice-clone scripts separately.
- **No offensive generation:** Build detectors and explainers only. Never generate send-ready scam scripts or clone a real person's voice.

---

## 3-Minute Demo Checklist
- [ ] **1 real scam message or AI fraud incident** on screen
- [ ] **Your tool** explaining the red flags in plain language (ideally showing multilingual output)
- [ ] **Accuracy / missed-scam / false-alarm numbers** with sample size
- [ ] **1 honest limitation** (a type of scam your tool cannot catch)
