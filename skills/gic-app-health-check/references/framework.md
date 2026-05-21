# Framework — 10 Dimensions × 4 Levels

The GIC Application Health Check evaluates each application across **10 dimensions**. Each dimension is rated against **4 levels** of maturity. The combination of per-dimension levels produces the per-app Health Check level + justification.

## The 10 dimensions

The dimensions are stable across the programme. They cover the technical surface area that determines whether an application is healthy and migration-ready.

| # | Dimension | What it measures |
|---|---|---|
| 1 | **Identity & Access Management** | How users and machines authenticate, are authorised, and have their access lifecycle managed |
| 2 | **Data Protection & Cryptography** | How sensitive data is classified, encrypted at rest and in transit, and protected from exfiltration |
| 3 | **Application Security** | How vulnerabilities, secrets, and attack surface are detected and remediated across SDLC and runtime |
| 4 | **Secure SDLC & Release** | How code is reviewed, built, tested, and deployed safely with rollback and change control |
| 5 | **Resilience & Recovery** | How the application stays available under failure and recovers within declared RTO / RPO targets |
| 6 | **Observability & Monitoring** | How telemetry — logs, metrics, traces, alerts — produces actionable signals for the team and the SOC |
| 7 | **Operations & Documentation** | How the application is run day-to-day: SOPs, runbooks, asset inventory, vendor support, handover |
| 8 | **Performance & Scalability** | How the application handles load today and scales for projected demand |
| 9 | **Cost & Sustainability** | How cloud spend is visible, attributable, and optimised against business value |
| 10 | **Governance & Architecture** | How ownership, classification, and architecture pattern compliance are maintained |

## The 4 levels

Each dimension is rated on the same 4-level scale.

| Level | Name | What it means |
|---|---|---|
| **L1** | **Developing** | Foundational gaps from the GIC baseline; remediation work is needed |
| **L2** | **Healthy** | Meets the GIC baseline as described in the dimension definition |
| **L3** | **Managed** | Operates above baseline with automation and measurement in this dimension |
| **L4** | **Optimised** | Has adopted advanced cloud-native practices in this dimension |

The levels are nested — to reach L3 the team must also meet everything required at L2, and to reach L4 they must also meet L3. This means an app cannot skip levels; you can't be L4 in IAM unless you also have all L2 and L3 IAM practices in place.

The per-dimension level descriptions (what L1, L2, L3, L4 look like *in each specific dimension*) are in `level-definitions.md`. That 10 × 4 matrix is the canonical reference for what each level means in context.

## How dimensions and questions relate

Each dimension contains 1–5 **questions**. Each question contains 7–17 **criteria elements**. Each element is a short Yes/No-style check tagged (in the background) with the level it tests for.

- 10 dimensions
- 32 questions
- 332 criteria elements

A question's level is computed from its element responses (see `scoring.md`). A dimension's level is the **lowest question level** in that dimension. The overall app level is the **lowest dimension level**.

This "lowest wins" rule reflects the principle that an app is only as healthy as its weakest area.

## Anchoring

The rubric is anchored on two layers:

- **GIC Control Library** — most questions (23 of 32) reference specific GIC controls. The questions encode what GIC's own internal controls require.
- **Industry sources** — questions cite CIS Controls v8.1, NIST 800-53 / SSDF, ISO 27001:2022 / 25010 / 22301, OWASP Top 10, Google SRE, DORA Four Keys, 12-factor, and the AWS Well-Architected Framework. See `industry-sources.md` for the full mapping.

The GIC tooling layer (Ping, Sailpoint IGA, CyberArk PAM, Wiz CSPM, Tenable, Splunk, DataDog, GitHub Enterprise, AWS Config, ServiceNow, Zscaler, etc.) is referenced extensively in the element wording. See `gic-tooling.md` for the tool catalogue and which questions reference each tool.

## Scope

This rubric covers application health for the cloud migration programme. It explicitly does **not** cover:

- Migration-readiness verdict (removed in v0.8; an app at any level can in principle be migrated)
- Application Profile (separate phase + artefact)
- Migration Analysis (separate phase + artefact)
- Runbook + LLD (separate phase + artefact)
- Re-assessment Rubric (a different, later assessment)

The Health Check produces a level + justification. That output feeds the downstream phases but doesn't determine them.

## Rubric version history

| Version | Date | Change |
|---|---|---|
| 0.5 | 2026-05-01 | Five-level rubric (L1-L5); migration verdict; three editions |
| 0.6 | 2026-05-02 | Source mapping merged; graded 5-level responses; rich-text instructions |
| 0.7 | 2026-05-02 | Question-level migration gating (Strict / Conditional / Optional) |
| 0.8 | 2026-05-05 | Element-based checklist (332 elements); L5 dropped; migration verdict removed |
| **0.9** | **2026-05-05** | Column reorder, "Not Sure" response, free row heights |

This skill encodes v0.9. Future rubric changes bump this skill's version accordingly.
