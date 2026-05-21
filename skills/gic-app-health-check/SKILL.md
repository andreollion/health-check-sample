---
name: gic-app-health-check
description: |
  Use this skill any time work touches the GIC Application Health Check rubric — the 10 dimensions, 4 levels (Developing / Healthy / Managed / Optimised), 32 questions, or 332 criteria elements. Triggers include filling out the v0.9 Checklist, verifying pre-filled responses, computing per-question or per-app health levels, generating Justification text, spot-auditing AI-pre-filled answers, or any reference to "L1 Developing", "L2 Healthy", "L3 Managed", "L4 Optimised", "GIC Control Library mapping", or the App Health Check rubric. Do NOT use for unrelated GIC work (cost reporting, generic AWS guidance, ITSM tickets) — this skill is specifically scoped to the App Health Check rubric.
metadata:
  rubric_version: "0.9"
  programme: "GIC Cloud Migration"
---

# GIC Application Health Check — Rubric Skill

This skill encodes the canonical rubric for the GIC Application Health Check programme. It defines the framework (10 dimensions × 4 levels), the question set (32 questions, 332 criteria elements), the scoring algorithm, the confidence model, and the verification workflow.

The skill is the single source of truth for what the rubric is. Other components — the pre-fill pipeline, the verification UI, the spot-audit workflow, executive reporting — load this skill and reference its content.

---

## When to use

- Filling out or pre-filling the v0.9 Checklist Excel
- Verifying or spot-auditing a pre-filled response
- Computing per-question, per-dimension, or per-app levels
- Generating Justification strings for the Scorecard
- Producing internal documentation about the rubric
- Answering questions like "what does L3 Managed mean for IAM?" or "what elements roll up to Q10?"

## When NOT to use

- Generic GIC documentation (use a different skill or no skill)
- Other migration-phase artefacts (Application Profile, Migration Analysis, Runbook) — those have their own skills when ready
- Source data extraction — use `gic-source-extractors` for that

## What's in this skill

| Topic | Reference file | Load when |
|---|---|---|
| Framework (10 dimensions, 4 levels, scope) | `references/framework.md` | Explaining the rubric structure |
| The 32 questions with metadata | `references/questions.md` | Working at the question level |
| The 332 criteria elements | `references/elements.md` | Working at the element level |
| Per-dimension × per-level matrix | `references/level-definitions.md` | Describing what a level means |
| Response model (Yes / No / N/A / Not Sure) | `references/responses.md` | Answering or evaluating responses |
| Scoring algorithm + confidence model + justification | `references/scoring.md` | Computing levels or generating justifications |
| GIC tooling (Ping, CyberArk, Wiz, ...) | `references/gic-tooling.md` | Mapping elements to source systems |
| Industry source citations (CIS, NIST, ISO, ...) | `references/industry-sources.md` | Citing why an element is asked |
| Verification + spot-audit workflow | `references/verification.md` | Reviewing or challenging an answer |

The structured-data version lives in `assets/`:

- `assets/questions.json` — 32 questions + 332 elements with metadata
- `assets/level-definitions.json` — 10 × 4 level matrix
- `assets/element-source-routing.json` — element → recommended source types

Helper scripts in `scripts/`:

- `scripts/score.py` — reference implementation of the level algorithm
- `scripts/validate.py` — validate a response shape against the rubric
- `scripts/justify.py` — generate justification strings

## Common operations

### Computing a question's level

Read `references/scoring.md`. Algorithm summary: any L1 (gap) element ticked Yes → forces L1 Developing. Otherwise the highest level where every positive element at that level has a Yes (or N/A) response. See `scripts/score.py` for the reference implementation.

### Verifying a pre-filled answer

Read `references/verification.md`. Key rule: any Yes claim must be backed by an evidence quote in the Link / Notes column. Without evidence, auto-downgrade to "Not Sure".

### Identifying which source answers an element

Load `assets/element-source-routing.json` or read `references/gic-tooling.md`. Each of the 332 elements has a recommended source type (risk_assessment / arb / confluence / github / sharepoint).

### Working with the response model

Read `references/responses.md`. Four states: Yes / No / N/A / Not Sure. Not Sure is treated like No in scoring (counted in denominator, not as met) but is surfaced separately in the Justification text to flag follow-up.

## Rubric version

This skill encodes **v0.9** of the rubric. Major rubric changes bump this skill's major version; additions or clarifications bump the minor. Downstream consumers should pin to a specific skill version to avoid breaking on updates.
