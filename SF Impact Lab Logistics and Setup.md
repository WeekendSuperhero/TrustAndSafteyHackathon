---
title: SF Impact Lab Logistics and Setup
date: 2026-11-17
tags:
  - event/claude-community
  - sf-impact-lab
  - logistics
aliases:
  - Venue and Setup
  - API Credits Setup
---

# SF Impact Lab Logistics and Setup

← Back to [[SF Impact Lab Index]]

---

## Venue & Arrival

- **Location:** Antler SF, **3rd Floor**, 144 Townsend St, San Francisco, CA 94107
- **Map Link:** [Open in Google Maps](https://www.google.com/maps/search/?api=1&query=Antler+144+Townsend+St+San+Francisco)
- **Luma Registration:** [luma.com/claude-sf-impact-lab](https://luma.com/claude-sf-impact-lab)
- **Timing:** Doors open at **5:30 PM** (food and check-in). Kickoff is at **6:00 PM sharp**.

---

## Pre-Flight Checklist (Do This Before 6:00 PM)

- [ ] **Laptop + Charger** plugged in and ready
- [ ] **GitHub Account** signed in (you will push your repo + `SUBMISSION.md` before 8:30 PM)
- [ ] **Claude Account & Anthropic Console** signed in at [console.anthropic.com](https://console.anthropic.com)
- [ ] **Starter Repo Cloned:**
  ```bash
  git clone https://github.com/sergeicu/trust-safety-impact-lab.git
  ```
- [ ] **API Credits Claimed** (follow the exact steps below)

---

## Claiming Your Claude API Credits

> [!warning] Read Before Claiming
> Automated fraud checks run on every claim. Claiming from multiple profiles will get you blocked, and support **cannot** fix a wrong Org ID. Submit once with the right ID.

1. Open the Anthropic Console at [console.anthropic.com](https://console.anthropic.com).
2. Go to **Settings → Organization** and copy your **Org ID**.
   - *Make sure you copy your Console **Org ID**, NOT your Claude.ai ID (Claude.ai IDs are rejected).*
3. Open the **Claim your credits** link on the [Participant Hub](https://claudesocal.com/sf-impact-lab) (shared at the 6:00 PM kickoff) and paste your Org ID.
4. Credits work with the **Claude API only** (not Claude.ai chat) and usually arrive within a couple of minutes.

---

## Rules for Coding Agents Tonight

If you are running Claude Code, HERO, or another coding agent on the starter repository, follow the repo's ground rules:

1. **Read the track file and `datasets.md` first** before writing code.
2. **Build the smallest thing that runs on real data:** one page, one notebook, or one CLI.
3. **Pull small samples first** (e.g., 20 to 50 rows) and cache model responses to JSONL so you do not burn time or API credits re-running calls.
4. **Never collect or commit API keys or personal data** to your repository.
5. **State one honest limitation** of what your tool can and cannot do.

---

## Getting Help in the Room

- **Stuck on the build or data?** Mentors are roaming the room all night. Wave one over.
- **Trouble with team registration, submitting, or the hub page?** Find an organizer in the room.
- **Lost your team number?** Enter any teammate's email under the [Submit section](https://claudesocal.com/sf-impact-lab#submit) on the hub page to recover your team.

---

## Related Notes
- [[SF Impact Lab Index]]
- [[SF Impact Lab Schedule]]
- [[SF Impact Lab Tracks Overview]]
- [[SF Impact Lab Datasets Catalog]]
