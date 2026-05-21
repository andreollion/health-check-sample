# The 32 Questions — Metadata and Context

Each question is identified by `QID` (Q01–Q32), lives in one dimension, and is anchored to either the GIC Control Library (Y) or industry sources only (N). Priority is Must or Should (the rubric distinguishes baseline-required from above-baseline-recommended).

The full element list per question is in `elements.md` and `assets/questions.json`.

---

## Identity & Access Management (Q01–Q05)

- **Q01** · SSO + MFA + Identity Lifecycle · Must · GIC · *CIS 6.3 / 6.7, NIST 800-63*
  How does the application authenticate users and manage their identity lifecycle? Tests Ping SSO onboarding, MFA enforcement across all access paths, Sailpoint IGA / MyAccess lifecycle management, session timeouts, breakglass procedures.

- **Q02** · Privileged Access (PAM) · Must · GIC · *CIS 5.3 / 5.4, NIST 800-53 AC-6*
  How are privileged accounts (human admins, service accounts, breakglass) managed? Tests CyberArk PAM coverage, credential rotation, just-in-time elevation.

- **Q03** · Authorisation & Least Privilege · Must · GIC · *CIS 6.8, NIST 800-53 AC-3*
  How is least-privilege enforced for IAM roles and policies? Tests Wiz CSPM / IAM Access Analyzer findings, AD/PARIS integration, permission boundaries.

- **Q04** · Secrets & Session Hygiene · Must · GIC · *CIS 3.11, OWASP A07, NIST 800-53 IA-5*
  How are application secrets stored and how are user sessions hardened? Tests vault usage (CyberArk / AWS Secrets Manager), absence of plaintext secrets, session timeout configuration.

- **Q05** · Access Reviews & Account Hygiene · Must · GIC · *CIS 5.5 / 6.2, ISO 27001 A.5.16, A.5.18*
  How are access reviews and account hygiene maintained over time? Tests quarterly access reviews, orphaned account detection, default-account removal.

## Data Protection & Cryptography (Q06–Q09)

- **Q06** · Encryption + Vendor Assurance · Must · GIC · *NIST 800-57, CIS 3.10 / 3.11, OWASP A02, ISO 27001 A.5.20*
  How is sensitive data encrypted at rest and in transit, and what cryptographic assurance do you have for third-party vendors?

- **Q07** · Data Classification & Residency · Must · GIC · *CIS 3.7, ISO 27001 A.5.12 / A.5.13*
  How is data classified and where is Secret-classified data stored?

- **Q08** · Data Masking & Non-Prod Hygiene · Must · GIC · *CIS 3.7, OWASP A04, NIST 800-53 SC-28*
  How is non-production data handled and segregated from production?

- **Q09** · DLP & Egress Control · Should · GIC · *CIS 13.3, OWASP A04, AWS WAF Security*
  How are data exfiltration risks controlled?

## Application Security (Q10–Q13)

- **Q10** · SAST / SCA / Secrets in Pipeline · Must · GIC · *CIS 16.11, OWASP A06, NIST SSDF PW.6 / PW.7*
  How are vulnerabilities and secrets detected in your CI/CD pipeline? Tests CodeQL / Snyk / GitHub Secret Scanning integration.

- **Q11** · OS / Container Vulnerability & Patch Mgmt · Must · GIC · *CIS 7, NIST 800-53 SI-2, OWASP A06*
  How are OS and container vulnerabilities detected and patched? Tests Tenable agent coverage, monthly VAR, patch SLA.

- **Q12** · Penetration Testing & Cloud Posture · Must · GIC · *CIS 18, OWASP ASVS, NIST 800-53 RA-5*
  How are penetration testing and cloud security posture managed? Tests TICRP pen-test, Wiz CSPM continuous, ITRM AI/Mobile checklists where applicable.

- **Q13** · Input Validation & File Upload · Must · GIC · *OWASP A03 / A04 / A05, CIS 16.10*
  How are input validation and file uploads protected against attack?

## Secure SDLC & Release (Q14–Q16)

- **Q14** · Branch Protection & Code Review · Must · GIC · *NIST SSDF PO.3 / PW.4, CIS 16.1*
  How are code changes reviewed and protected before merge?

- **Q15** · Deployment Pipeline & Rollback · Must · Industry · *DORA 4 keys, AWS WAF Op-Excellence, NIST SSDF PO.5*
  How is deployment automated and how do you roll back failed releases?

- **Q16** · Infrastructure as Code & Environment Consistency · Should · Industry · *12-factor.net, NIST SSDF PO.5, AWS CAF*
  How is infrastructure defined, versioned, and deployed consistently across environments?

## Resilience & Recovery (Q17–Q21)

- **Q17** · Multi-AZ & Redundancy · Must · GIC · *AWS WAF Reliability, CIS 11*
  How is the application architected for availability under failure?

- **Q18** · SLO / SLI & Error Budget · Should · Industry · *Google SRE, AWS WAF Reliability*
  How are reliability targets defined and monitored?

- **Q19** · Graceful Degradation · Should · Industry · *Google SRE, AWS WAF Reliability, ISO 25010*
  How does the application handle dependency failures gracefully?

- **Q20** · Automated Backup & Restore Test · Must · GIC · *CIS 11.5, NIST 800-53 CP-9, AWS WAF Reliability*
  How are backups configured and how often is restore tested?

- **Q21** · DR Plan & Tested Recovery · Must · GIC · *CIS 11, NIST 800-53 CP-2 / CP-4, ISO 22301*
  Is the disaster recovery plan documented, signed off, and tested?

## Observability & Monitoring (Q22–Q24)

- **Q22** · Telemetry to Datadog + Splunk · Must · GIC · *Google SRE, OpenTelemetry, CIS 8*
  How are application metrics, logs, and security signals captured?

- **Q23** · Security Monitoring & Audit Logs · Must · GIC · *CIS 8.11, NIST 800-53 AU-12, OWASP A09*
  How are security events monitored, and how are audit logs sanitised?

- **Q24** · Expiry & Agent Health Alerting · Must · GIC · *CIS 1.5 / 2.4, ITIL 4 Service Level Mgmt*
  How are certificate, licence, and agent-coverage gaps detected?

## Operations & Documentation (Q25–Q27)

- **Q25** · Asset & Account Inventory · Must · GIC · *CIS Control 1, CIS Control 5, ISO 27001 A.5.9*
  How accurate and complete is your asset and account inventory?

- **Q26** · System & Network Documentation · Must · GIC · *ISO 25010 Maintainability, TOGAF, CIS 12*
  How current and AWG-approved is your system + network documentation?

- **Q27** · Operational Readiness · Must · GIC · *ITIL 4 Service Transition, CIS 16*
  How operationally ready is the application — SOPs, vendor support, certificates, UAT?

## Performance & Scalability (Q28–Q29)

- **Q28** · Capacity & Auto-Scale · Must · Industry · *AWS WAF Performance, Google SRE*
  How is capacity planned and auto-scale configured?

- **Q29** · Performance SLOs & Regression Detection · Should · Industry · *AWS WAF Performance, Google SRE, OpenTelemetry*
  How are performance regressions detected and rolled back?

## Cost & Sustainability (Q30)

- **Q30** · Cost Visibility & Optimisation · Should · Industry · *AWS WAF Cost Optimisation + Sustainability*
  How is cloud spend visible, attributable, and optimised?

## Governance & Architecture (Q31–Q32)

- **Q31** · 12-Factor & Architecture Pattern · Must · GIC · *12-factor.net (III, IV, VI), CIS 4, ISO 25010 Maintainability*
  How cloud-portable is the application's architecture?

- **Q32** · CMDB Metadata & Ownership · Must · GIC · *CIS 1 / 2, ISO 27001 A.5.9, GIC Control Library*
  Is application ownership and third-party dependency information current and complete?

---

## Distribution

- **By dimension:** IAM 5, Data Protection 4, AppSec 4, SDLC 3, Resilience 5, Observability 3, Operations 3, Performance 2, Cost 1, Governance 2 = 32
- **By priority:** Must 26, Should 6
- **By anchor:** GIC Control Library 25, Industry-only 7
- **Total elements across 32 questions:** 332

Full element text per question is in `elements.md`. Programmatic access via `assets/questions.json`.
