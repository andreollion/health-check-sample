# Industry Sources — citations per question

The rubric supplements GIC's internal Control Library with industry-recognised frameworks. Each question cites the frameworks that back its elements. This document is the reverse index — which industry sources are cited where.

## The framework set

- **CIS Controls v8.1** — Center for Internet Security baseline controls. Cited across security, identity, vulnerability, and asset-inventory questions.
- **NIST 800-53** — US federal security controls catalogue. Cited for access control, audit, contingency planning, system integrity.
- **NIST SSDF** — NIST Secure Software Development Framework (SP 800-218). Cited for SDLC + supply chain (Q10, Q14, Q15, Q16).
- **NIST 800-63** — Digital Identity Guidelines. Cited for identity authentication (Q01).
- **NIST 800-57** — Key Management. Cited for cryptography (Q06).
- **ISO 27001:2022** — Information security management. Cited across most security questions.
- **ISO 25010** — Software product quality (maintainability, reliability). Cited for architecture quality (Q19, Q26, Q31).
- **ISO 22301** — Business continuity management. Cited for resilience (Q21).
- **OWASP Top 10** — Web application security risks. Cited for AppSec (Q04, Q06, Q08, Q09, Q10, Q11, Q13).
- **OWASP ASVS** — Application Security Verification Standard. Cited for pen-testing (Q12).
- **Google SRE** — Reliability engineering. Cited for SLOs, observability, graceful degradation (Q18, Q19, Q22, Q28, Q29).
- **OpenTelemetry** — Distributed tracing + observability standard. Cited for observability (Q22).
- **DORA Four Keys** — Software delivery performance metrics (Deploy Frequency, Lead Time, Change Failure Rate, MTTR). Cited for delivery (Q15).
- **12-factor.net** — Cloud-native application architecture principles. Cited for architecture (Q31).
- **AWS Well-Architected Framework** — Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimisation, Sustainability pillars. Cited across cloud-architecture questions (Q06, Q09, Q15, Q17, Q19, Q20, Q28, Q29, Q30).
- **AWS Well-Architected FSI Lens** — FSI-specific guidance layered on top of WAF. Cited where FSI considerations apply.
- **AWS CAF** — Cloud Adoption Framework. Cited for IaC + migration patterns (Q16).
- **TOGAF** — Enterprise architecture framework. Cited for architecture documentation (Q26).
- **ITIL 4** — Service management. Cited for operational maturity (Q24, Q27).

## Citation distribution (which questions cite each source)

| Source | Cited in |
|---|---|
| CIS Controls v8.1 | Q01–Q04, Q06–Q14, Q17, Q20, Q23, Q24, Q25, Q26 (most security questions) |
| NIST 800-53 | Q02–Q04, Q06, Q08, Q11, Q13, Q14, Q20–Q23 |
| NIST SSDF | Q10, Q14, Q15, Q16 |
| NIST 800-63 | Q01 |
| NIST 800-57 | Q06 |
| ISO 27001:2022 | Q03–Q07, Q14, Q25, Q32 |
| ISO 25010 | Q19, Q26, Q31 |
| ISO 22301 | Q21 |
| OWASP Top 10 | Q04, Q06, Q08, Q09, Q10, Q11, Q13, Q23 |
| OWASP ASVS | Q12 |
| Google SRE | Q18, Q19, Q22, Q28, Q29 |
| OpenTelemetry | Q22, Q29 |
| DORA Four Keys | Q15 |
| 12-factor.net | Q31 |
| AWS Well-Architected | Q06, Q09, Q15, Q17, Q19, Q20, Q28, Q29, Q30 |
| AWS CAF | Q16 |
| TOGAF | Q26 |
| ITIL 4 | Q24, Q27 |

## Why this matters for pre-fill

When AI pre-fills a response, the industry citations help it ground its reasoning in well-known practices. For example, when answering Q14 (branch protection), the AI should reason in terms of NIST SSDF PO.3 / PW.4 + CIS 16.1. The Note column can reference both the GIC control (where applicable) and the industry source — making the answer defensible to auditors.

When verifying a response, App Health Check team members can challenge by asking "does this match what NIST SSDF actually requires?" — using the industry source as an external reference.

## What this isn't

The industry sources are background grounding, not the rubric itself. The rubric's text + the GIC Control Library determine what's measured. The industry citations explain why a question matters in broader practice. Treat them as supporting context, not as primary authority.
