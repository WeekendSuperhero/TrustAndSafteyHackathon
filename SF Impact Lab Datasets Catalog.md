---
title: SF Impact Lab Datasets Catalog
date: 2026-11-17
tags:
  - event/claude-community
  - sf-impact-lab
  - datasets
aliases:
  - Datasets Catalog
  - Public Datasets
---

# SF Impact Lab Datasets Catalog

← Back to [[SF Impact Lab Index]]

All datasets are cataloged in `datasets.json` and `datasets.md` inside the [Starter Repo](https://github.com/sergeicu/trust-safety-impact-lab).

---

## How Pull Types Work

- **`hf_rows`**: Row sample pulled via Hugging Face dataset viewer API (fast, no huge downloads).
- **`http`**: Direct CSV/JSON file download via HTTP.
- **`socrata`**: DataSF Socrata API query (always filter/limit rows; tables have millions of records).
- **`git`**: Shallow git clone (`git clone --depth 1 ...`).
- **`manual`**: Open the link and download the specific CSV/Excel/PDF bundle.

---

## Track 1: Agents in Inboxes & Guardrails

| Dataset ID | Description & Size | Pull Type | Key Caveat |
| :--- | :--- | :--- | :--- |
| `llmail-inject` | Microsoft LLMail-Inject: ~462k adaptive prompt-injection emails (`Phase1` & `Phase2`) | `hf_rows` | Parse `objectives` JSON (`email.retrieved`, `defense.undetected`, `exfil.sent`). Tell your coding agent rows are strings to classify, not instructions! |
| `injecagent` | 1,054 indirect prompt-injection test cases across 17 user tools & 62 attacker tools | `git` | Single-turn cases: user task + poisoned tool response + attacker goal. |
| `agentdojo` | Dynamic agent evaluation suites (`workspace`, `travel`, `banking`, `slack`) | `manual` | Budget ~15 minutes for setup if running full tool loops. |
| `deepset-prompt-injections` | Labeled set of prompt injections vs. benign prompts (0/1 label) | `hf_rows` | Great fast baseline and source of benign prompts for false-positive checks. |
| `jbb-behaviors` | JailbreakBench: 100 harmful + 100 matched benign behaviors across 10 categories | `hf_rows` | Small enough to run in full; matched benign half measures over-refusal. |
| `aegis-2` | NVIDIA Aegis 2.0 Content Safety Dataset (33,416 interactions; 1,964 test split) | `hf_rows` | May require `HF_TOKEN` login on Hugging Face. Use test split only. |
| `toxic-chat` | ~10k real chatbot prompts labeled for toxicity and jailbreaking | `hf_rows` | Mostly benign distribution—strong for realistic false-positive testing. |
| `cisa-kev` | CISA Known Exploited Vulnerabilities catalog (CSV/JSON, 1 row per CVE) | `http` | Authoritative list of CVEs exploited in the wild. Defensive analysis only. |
| `petri-bloom` | Open-source automated behavioral auditing tools (Petri & Bloom) | `manual` | Setup takes ~20 min and consumes API credits; keep to 10–20 scenarios. |

---

## Track 2: Spot the Rogue Agent

| Dataset ID | Description & Size | Pull Type | Key Caveat |
| :--- | :--- | :--- | :--- |
| `amongus-sandbox` | 400 complete LLM-agent social deduction game logs + 2,054 summaries | `git` | Score your deception detector directly on published logs without running new games. |
| `agentic-misalignment` | Anthropic framework where an agent with email access faces goal conflicts | `git` | Great source of transcripts where an agent turns against its principal. |

---

## Track 3: Robotaxis and Robots

| Dataset ID | Description & Size | Pull Type | Key Caveat |
| :--- | :--- | :--- | :--- |
| `nhtsa-sgo-ads` | NHTSA Automated Driving Systems crash reports (June 16, 2025 onward) | `http` | Filter `State == CA` and `City == San Francisco`. **De-duplicate crashes** (multiple report versions exist). Unverified, no mileage denominator. |
| `nhtsa-sgo-ads-archive` | NHTSA ADS crash reports archive (2021 to June 15, 2025) | `http` | Older schema than the June 2025+ file; column names differ. |
| `ca-av-collisions-zenodo` | Structured CSV of CA DMV autonomous vehicle collisions (2019–2024, ~670 kB) | `http` | Fastest way to get structured CA AV collision narratives + GIS fields. Ends Dec 31, 2024. |
| `ca-dmv-collision-reports` | Raw CA DMV Form OL 316 PDFs by company and date (2019–2026) | `manual` | Download 5–10 PDFs from 2025–2026 to extract with Claude. |
| `ca-dmv-disengagements` | Annual disengagement and mileage CSVs | `manual` | Covers **testing permits only** (commercial deployment permits report to CPUC). |
| `cpuc-av-quarterly` | CPUC quarterly passenger-service spreadsheets (trips, miles, incidents) | `manual` | Best official source for mileage and trip denominators. |
| `waymo-safety-hub` | Waymo rider-only miles and crash CSVs by city (includes SF) | `manual` | Company-published denominator to cross-check against raw NHTSA rows. |
| `sf-311-cases` | DataSF 311 resident service requests (Socrata API) | `socrata` | Query matching `'autonomous'` (default fetch pulls 2,000 most recent rows). |
| `sf-traffic-crashes` | DataSF police-reported injury crashes (human driver baseline) | `socrata` | Use as human baseline by neighborhood/time. |
| `sf-sidewalk-robot-rules` | SF Public Works Code Sec. 794 (Autonomous Delivery Devices) | `manual` | Max 3 devices per permittee, 9 citywide, 180-day testing permits. |

---

## Track 4: Privacy

| Dataset ID | Description & Size | Pull Type | Key Caveat |
| :--- | :--- | :--- | :--- |
| `eff-atlas-of-surveillance` | EFF CSV of US police agencies and surveillance tech deployed | `http` | Filter `State == CA` and Bay Area counties. Open-source research, not an exhaustive census. |
| `sf-surveillance-inventory` | SF Admin Code Ch. 19B Surveillance Tech Inventory & policy PDFs | `manual` | Pick 6–10 department policy PDFs and extract retention/sharing rules. Hand-check numbers! |
| `nemotron-pii` | NVIDIA synthetic documents with span-level PII/PHI labels | `hf_rows` | 100% synthetic and safe to display on the projector for redaction airlock demos. |
| `eff-ca-alpr` | EFF California license plate reader scans vs. hotlist hits (89 agencies) | `manual` | Historical dataset released in 2021; state the date clearly. |

---

## Track 5: Personal Safety

| Dataset ID | Description & Size | Pull Type | Key Caveat |
| :--- | :--- | :--- | :--- |
| `uci-sms-spam` | 5,574 labeled SMS messages (`ham` vs. `spam`) | `http` | From 2012 (mostly UK/Singapore). Use for fast baseline, then test 2026 scams separately. |
| `phishing-multi` | Labeled phishing vs. benign emails, SMS, URLs, and web pages | `manual` | Download JSON files directly from the Hugging Face `Files` tab (do not run the HF loading script). |
| `ftc-consumer-sentinel` | FTC annual fraud and identity theft CSVs (includes SF metro area) | `manual` | Self-reported aggregates only; massive under-reporting among older adults. |
| `ai-incident-database` | Press-reported AI harm/near-harm incidents | `manual` | Grab the ~3 MB weekly Excel export for speed instead of the 120 MB dump. |
| `mit-ai-risk-repository` | Taxonomy of AI risks (7 domains, 23 subdomains) + incident tracker | `manual` | Great label taxonomy for coding incidents or room concerns. |
| `sfpd-incident-reports` | DataSF SFPD Incident Reports (2018–present) | `socrata` | One incident can span multiple rows/codes—de-duplicate by incident ID and aggregate by month/neighborhood only. |
| `c2pa-tools` | Open-source Content Credentials (`c2patool`) CLI and SDKs | `manual` | Tooling only; absence of credentials proves nothing. |

---

## Track 6 / Cross-Track: People, Values & Agent Governance

| Dataset ID | Description & Size | Pull Type | Key Caveat |
| :--- | :--- | :--- | :--- |
| `anthropic-interviewer` | 1,250 interview transcripts on how workers, creatives, and scientists view AI | `hf_rows` | Long transcripts (5k–27k chars); sample 50–100 rows. |
| `anthropic-values-in-the-wild` | Taxonomy and frequencies of ~3k values Claude expressed in real chats | `hf_rows` | Aggregated counts only. Great vocabulary for value alignment checks. |
| `anthropic-discrim-eval` | Templated yes/no decision scenarios varied by age, gender, and race | `hf_rows` | Compare yes-rates across demographic variants of identical prompts. |
| `ai-agent-index` | MIT 2025 structured documentation of 30 deployed AI agents | `manual` | Shows what agent builders publicly disclose vs. omit on safety. |

---

## Related Notes
- [[SF Impact Lab Index]]
- [[SF Impact Lab Tracks Overview]]
- [[SF Impact Lab Submission and Judging]]
