# Criteria Elements — 332 elements grouped by question

Each element is a short Yes/No-style check. Elements are tagged by level (L1/L2/L3/L4) — the level is hidden from form-fillers but used by the scoring engine.

Element IDs follow the pattern `Q##-E##`. Element IDs are stable across rubric versions — when the rubric changes, IDs of removed elements are deprecated, never reused.

Full structured data: `assets/questions.json`.

---

## Q01 — SSO + MFA + Identity Lifecycle (Identity & Access Management)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS 6.3 (MFA), 6.7 (SSO); NIST 800-63

**Question:** How does the application authenticate users and manage their identity lifecycle? (SSO + MFA + IGA)

**L1 elements:**
- `Q01-E01` — Are there bypass paths to SSO still in place (e.g. direct URLs or local accounts permitted)?
- `Q01-E02` — Is MFA only enforced on some access paths but not all?
- `Q01-E03` — Is identity lifecycle management manual, ad-hoc, or lacking a quarterly review process?

**L2 elements:**
- `Q01-E04` — Has the application been fully onboarded to Ping SSO with no alternate login paths permitted?
- `Q01-E05` — Is MFA enforced for all interactive access, including users, admins, and AWS console / CLI / API?
- `Q01-E06` — Is identity lifecycle managed centrally via MyAccess (SailPoint IGA) with quarterly access reviews?
- `Q01-E07` — Is the session inactivity timeout set to 15 minutes or less?
- `Q01-E08` — Is Zscaler device restriction active and enforced?
- `Q01-E09` — Are breakglass procedures documented with a defined activation process?

**L3 elements:**
- `Q01-E10` — Is automated provisioning and deprovisioning in place via IGA workflows, with no manual ticket-driven onboarding?
- `Q01-E11` — Is access anomaly detection actively running and generating alerts?
- `Q01-E12` — Is a service account inventory maintained with credential rotation tracking?
- `Q01-E13` — Is RBAC fully defined and mapped to business roles?

**L4 elements:**
- `Q01-E14` — Do all service accounts use short-lived credentials (STS / OIDC tokens) with no static keys in use?
- `Q01-E15` — Are zero standing privileges enforced, with admin access granted on a JIT basis only?
- `Q01-E16` — Is access certification performed on a continuous basis, not limited to quarterly reviews?
- `Q01-E17` — Is Identity Threat Detection and Response (ITDR) deployed and operational?

---

## Q02 — Privileged Access (PAM) (Identity & Access Management)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS 5.3, 5.4; NIST 800-53 AC-6

**Question:** Are privileged + service accounts in CyberArk with automated rotation, and breakglass accounts properly stored?

**L1 elements:**
- `Q02-E01` — Are any privileged accounts existing outside of CyberArk?
- `Q02-E02` — Is credential rotation manual or infrequent?
- `Q02-E03` — Is the breakglass procedure undocumented or shared too broadly?

**L2 elements:**
- `Q02-E04` — Are all privileged and service accounts integrated with CyberArk PAM with automated credential rotation?
- `Q02-E05` — Is JIT access enforced for all human admins?
- `Q02-E06` — Are breakglass accounts stored in CyberArk or a physical safe with a documented activation procedure?

**L3 elements:**
- `Q02-E07` — Is PAM coverage reconciled daily against the ServiceNow privileged-account inventory with drift alerts active?
- `Q02-E08` — Is session recording enabled on all privileged sessions?
- `Q02-E09` — Is just-in-time elevation in place for routine admin tasks, with no long-running admin shells permitted?

**L4 elements:**
- `Q02-E10` — Do all privileged sessions route through Privileged Access Workstations (PAWs)?
- `Q02-E11` — Are privileged credentials never exposed outside the vault, with all access via proxy-based methods?
- `Q02-E12` — Is behavioural analytics active and monitoring privileged activity?

---

## Q03 — Authorisation & Least Privilege (Identity & Access Management)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS 6.8; NIST 800-53 AC-3

**Question:** Is least-privilege enforced (verified by Wiz / IAM Access Analyzer) and AD/PARIS integration in place?

**L1 elements:**
- `Q03-E01` — Are IAM policies coarse-grained (e.g. broad admin or power-user roles) with no automated check for over-permissive policies?
- `Q03-E02` — Is AD/PARIS integration ad-hoc or incomplete?

**L2 elements:**
- `Q03-E03` — Are IAM roles and policies verified as least-privilege via Wiz CSPM or IAM Access Analyzer with no over-permissive policies?
- `Q03-E04` — Is the application integrated with enterprise AD for authorisation, with PARIS registration for infrastructure access?

**L3 elements:**
- `Q03-E05` — Are IAM findings tracked to SLA-based remediation with no overdue critical or high findings?
- `Q03-E06` — Are permission boundaries enforced on all IAM roles?
- `Q03-E07` — Is cross-account access reviewed on a regular basis?

**L4 elements:**
- `Q03-E08` — Are just-in-time policy adjustments made based on usage telemetry?
- `Q03-E09` — Is policy-as-code in place with automated policy linting integrated in the CI pipeline?
- `Q03-E10` — Is policy drift detected and auto-remediated?

---

## Q04 — Secrets & Session Hygiene (Identity & Access Management)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS 3.11; OWASP A07; NIST 800-53 IA-5

**Question:** Are secrets vaulted and sessions hardened? (no plaintext creds; 15-min idle / 24-hr absolute timeout)

**L1 elements:**
- `Q04-E01` — Are any secrets stored as plaintext in source code, config files, or environment variables?
- `Q04-E02` — Are session timeouts inconsistent, absent, or not server-side enforced?
- `Q04-E03` — Is automated secret scanning absent?

**L2 elements:**
- `Q04-E04` — Are all application secrets (API keys, DB credentials, tokens) stored in an approved vault (CyberArk / AWS Secrets Manager) with no plaintext credentials in source or config?
- `Q04-E05` — Are user sessions configured with a 15-minute inactivity timeout and a 24-hour absolute timeout, enforced server-side?

**L3 elements:**
- `Q04-E06` — Is GitHub Enterprise Secret Scanning and Wiz secret detection running across all repos and config?
- `Q04-E07` — Are secret scanning findings tracked to a remediation SLA?
- `Q04-E08` — Are secret rotation policies enforced across all secrets?

**L4 elements:**
- `Q04-E09` — Are secrets injected at runtime via short-lived dynamic credentials, with no secrets resident in application config?
- `Q04-E10` — Are sessions cryptographically signed and bound to the device?

---

## Q05 — Access Reviews & Account Hygiene (Identity & Access Management)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS 5.5, 6.2; ISO 27001 A.5.16, A.5.18

**Question:** Are quarterly access reviews completed and default/temp accounts removed?

**L1 elements:**
- `Q05-E01` — Are access reviews ad-hoc or only triggered by audit findings rather than on a scheduled basis?
- `Q05-E02` — Are default or temporary accounts from implementation still active or not actively pruned?

**L2 elements:**
- `Q05-E03` — Are quarterly access reviews performed covering least-privilege validation, orphaned accounts, and role appropriateness, with action items closed within 30 days?
- `Q05-E04` — Have all temporary and default native accounts created during implementation been removed or disabled?

**L3 elements:**
- `Q05-E05` — Does review tooling automatically pre-populate reviewers with usage telemetry such as time-since-last-use and sensitive-resource access patterns?
- `Q05-E06` — Is orphaned account detection running on a daily basis?

**L4 elements:**
- `Q05-E07` — Are ML-assisted reviewer recommendations in place to flag anomalous entitlements compared to peers?
- `Q05-E08` — Are micro-attestations triggered automatically on role changes, not just on a calendar cadence?

---

## Q06 — Encryption + Vendor Assurance (Data Protection & Cryptography)

*Priority:* Must · *GIC Control:* Y · *Industry:* NIST 800-57; CIS 3.10, 3.11; OWASP A02; ISO 27001 A.5.20

**Question:** Is data encrypted at rest (KMS, rotated), in transit (TLS 1.2+), aligned to GIC crypto standards, and SOC2/OSPAR vendor assurance current?

**L1 elements:**
- `Q06-E01` — Is encryption at rest only partially enabled, with some services or data stores unprotected?
- `Q06-E02` — Are there any internal hops where TLS 1.2+ is not enforced?
- `Q06-E03` — Are SOC2/OSPAR vendor attestations outdated or missing for third-party vendors handling sensitive data?

**L2 elements:**
- `Q06-E04` — Is all sensitive data encrypted at rest using KMS-managed keys with automated rotation within policy limits?
- `Q06-E05` — Is TLS 1.2+ enforced for all data in transit with no unencrypted internal hops?
- `Q06-E06` — Are GIC mandatory cryptography controls adhered to for algorithms and protocols?
- `Q06-E07` — Have SOC2 Type 2 / OSPAR / ISO 27001 attestations been obtained and reviewed within the last 12 months for all third-party vendors handling sensitive data?

**L3 elements:**
- `Q06-E08` — Is automated data discovery and classification running continuously?
- `Q06-E09` — Is key rotation performed within 90 days?
- `Q06-E10` — Is data lineage tracked across the estate?
- `Q06-E11` — Is tokenisation applied to sensitive data fields?
- `Q06-E12` — Is production data prohibited from non-production environments without explicit approval and masking?

**L4 elements:**
- `Q06-E13` — Is envelope encryption with per-tenant keys implemented?
- `Q06-E14` — Is automated DLP with ML-based data classification in place?
- `Q06-E15` — Is crypto agility in place, allowing algorithm rotation without downtime?
- `Q06-E16` — Is hardware-backed key storage implemented?

---

## Q07 — Data Classification & Residency (Data Protection & Cryptography)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS 3.7; ISO 27001 A.5.12, A.5.13

**Question:** Is data classified per GIC scheme and Secret data restricted to dedicated Singapore infrastructure?

**L1 elements:**
- `Q07-E01` — Is data classification only partially applied or existing only on paper?
- `Q07-E02` — Is any Secret-classified data hosted on shared infrastructure or outside Singapore?

**L2 elements:**
- `Q07-E03` — Is all data classified per the GIC scheme (Public / Internal / Restricted / Secret)?
- `Q07-E04` — Is Secret-classified information stored exclusively on dedicated infrastructure in GIC-managed Singapore data centres with restricted access?

**L3 elements:**
- `Q07-E05` — Are automated data discovery and classification scans running continuously?
- `Q07-E06` — Do classification labels propagate through data lineage tracking?
- `Q07-E07` — Is production data prohibited from landing in non-production environments without approval and masking?

**L4 elements:**
- `Q07-E08` — Is per-tenant isolation implemented for Secret data using envelope encryption?
- `Q07-E09` — Is automated re-classification triggered on data drift?
- `Q07-E10` — Is data residency enforced via policy-as-code, preventing workloads from deploying outside approved regions?

---

## Q08 — Data Masking & Non-Prod Hygiene (Data Protection & Cryptography)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS 3.7; OWASP A04; NIST 800-53 SC-28

**Question:** Is non-prod data masked, and are dev/UAT segregated from prod?

**L1 elements:**
- `Q08-E01` — Is production data being refreshed unmasked into non-production environments?
- `Q08-E02` — Are dev and UAT environments insufficiently segregated from production?
- `Q08-E03` — Are debug tools or compilers present in the production environment?

**L2 elements:**
- `Q08-E04` — Is PII and sensitive data masked or anonymised when refreshed to non-production environments?
- `Q08-E05` — Is production data retained in non-production environments for no more than 30 days?
- `Q08-E06` — Are dev and UAT environments segregated from production, with no compilers, dev tools, or debug utilities in prod?

**L3 elements:**
- `Q08-E07` — Are synthetic data generation pipelines in place for non-production testing?
- `Q08-E08` — Is automated detection of unmasked production data in lower environments active?
- `Q08-E09` — Does data lineage tracking confirm masking is applied at every refresh?

**L4 elements:**
- `Q08-E10` — Is per-tenant tokenisation applied in non-production environments?
- `Q08-E11` — Is automated lifecycle management of test data in place, including auto-purge after each sprint?
- `Q08-E12` — Is referential integrity preserved across all masked datasets?

---

## Q09 — DLP & Egress Control (Data Protection & Cryptography)

*Priority:* Should · *GIC Control:* Y · *Industry:* CIS 13.3; OWASP A04; AWS WAF Security

**Question:** Are DLP / egress controls in place (Zscaler, S3 policies, monitored)?

**L1 elements:**
- `Q09-E01` — Is egress traffic largely unrestricted with no effective DLP policies enforced?
- `Q09-E02` — Are any S3 buckets publicly accessible?
- `Q09-E03` — Is Zscaler SSL inspection only partially applied?

**L2 elements:**
- `Q09-E04` — Are data exfiltration controls enforced, including egress filtering, DLP policies, and S3 bucket policies?
- `Q09-E05` — Is all internet traffic routed through Zscaler SSL inspection?
- `Q09-E06` — Is monitoring in place for anomalous egress activity?

**L3 elements:**
- `Q09-E07` — Is DLP alert volume baselined and reviewed monthly?
- `Q09-E08` — Are S3 bucket policies reviewed on a quarterly basis?
- `Q09-E09` — Is egress anomaly detection (by volume and destination) wired to the SOC?

**L4 elements:**
- `Q09-E10` — Is ML-based DLP classification in place, going beyond keyword matching?
- `Q09-E11` — Is zero-trust egress enforced with a deny-by-default policy and explicit allow-lists?
- `Q09-E12` — Is CASB integrated for visibility and control over SaaS data flows?

---

## Q10 — SAST / SCA / Secrets in Pipeline (Application Security)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS 16.11; OWASP A06; NIST SSDF PW.6, PW.7

**Question:** Are CodeQL + Snyk + Secret Scanning integrated in CI/CD with critical/high blocking promotion?

**L1 elements:**
- `Q10-E01` — Are security scanning findings failing to block promotion to production?
- `Q10-E02` — Is secret scanning only partial with no SLA on remediation?

**L2 elements:**
- `Q10-E03` — Are CodeQL (SAST), Snyk (SCA), and GitHub Enterprise Secret Scanning integrated in CI/CD with critical and high findings blocking promotion to production?
- `Q10-E04` — Are all vulnerability findings tracked to SLA-based remediation?

**L3 elements:**
- `Q10-E05` — Are vulnerability SLA metrics tracked and reported?
- `Q10-E06` — Is DAST integrated in the staging environment?
- `Q10-E07` — Is container image scanning performed before every deployment?
- `Q10-E08` — Is a WAF deployed for all internet-exposed endpoints?
- `Q10-E09` — Is auto-remediation in place for known vulnerability patterns?

**L4 elements:**
- `Q10-E10` — Is Runtime Application Self-Protection (RASP) deployed?
- `Q10-E11` — Is a Software Bill of Materials (SBOM) generated per release?
- `Q10-E12` — Is autonomous patching in place for non-breaking updates?
- `Q10-E13` — Is threat-intelligence-driven prioritisation used for vulnerability remediation?

---

## Q11 — OS / Container Vulnerability & Patch Mgmt (Application Security)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS 7; NIST 800-53 SI-2; OWASP A06

**Question:** Is Tenable installed everywhere with monthly VAR, and is patch mgmt documented and on-SLA?

**L1 elements:**
- `Q11-E01` — Is the Tenable Agent missing from any server assets?
- `Q11-E02` — Is monthly VAR coverage incomplete?
- `Q11-E03` — Is the patch management process manual or untested?

**L2 elements:**
- `Q11-E04` — Is the Tenable Agent installed on all server assets with monthly Vulnerability Assessment Report (VAR) coverage?
- `Q11-E05` — Is a documented patch management process in place covering automated deployment via GIC tools, lower-environment testing, and SLA-based remediation?

**L3 elements:**
- `Q11-E06` — Are patch compliance metrics tracked and reported monthly?
- `Q11-E07` — Are container base images automatically rebuilt when new CVEs are published?
- `Q11-E08` — Are overdue vulnerability findings dashboarded and visible to the team?

**L4 elements:**
- `Q11-E09` — Is autonomous patching in place for non-breaking updates?
- `Q11-E10` — Is CVE-to-deploy time under 7 days?
- `Q11-E11` — Is ephemeral or immutable infrastructure used, eliminating the need for in-place patching?

---

## Q12 — Penetration Testing & Cloud Posture (Application Security)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS 18; OWASP ASVS; NIST 800-53 RA-5

**Question:** Pen-test completed with crit/high closed, Wiz CSPM clean, and conditional AI/Mobile checklists done?

**L1 elements:**
- `Q12-E01` — Is the last penetration test more than 12 months old or has one never been conducted?
- `Q12-E02` — Are there outstanding critical findings in Wiz CSPM?
- `Q12-E03` — Have the AI and Mobile security checklists been skipped where applicable?

**L2 elements:**
- `Q12-E04` — Has penetration testing been completed prior to go-live per TICRP criteria with all critical and high findings remediated?
- `Q12-E05` — Is Wiz CSPM running continuously with no outstanding critical misconfigurations?
- `Q12-E06` — Have the AI Security checklist (via ITRM) and Mobile Application Security checklist been completed where applicable?

**L3 elements:**
- `Q12-E07` — Is penetration testing conducted quarterly for Tier-1 applications?
- `Q12-E08` — Are Wiz CSPM findings tracked to SLA-based remediation?
- `Q12-E09` — Is a threat model in place that is updated on architecture changes?

**L4 elements:**
- `Q12-E10` — Is an active bug bounty or red-team programme in place?
- `Q12-E11` — Is chaos and abuse-case testing automated in the CI/CD pipeline?
- `Q12-E12` — Is a security-champion model actively practised within the team?

---

## Q13 — Input Validation & File Upload (Application Security)

*Priority:* Must · *GIC Control:* Y · *Industry:* OWASP A03, A04, A05; CIS 16.10

**Question:** Is input validation enforced and file upload hardened (size/type/content/AV-scanned/outside web root)?

**L1 elements:**
- `Q13-E01` — Is input validation only performed client-side with no server-side enforcement?
- `Q13-E02` — Do file uploads accept any size or type without restriction?
- `Q13-E03` — Are uploaded files stored within the web root or not scanned for malware?

**L2 elements:**
- `Q13-E04` — Is input validation enforced server-side, including parameterised queries, output encoding, and anti-CSRF controls?
- `Q13-E05` — Are file uploads validated for size, file type, and content, with files stored outside the web root and scanned for malware?

**L3 elements:**
- `Q13-E06` — Are WAF rules tuned to application-specific traffic patterns?
- `Q13-E07` — Are security headers (CSP, HSTS, etc.) applied on all responses?
- `Q13-E08` — Is file upload sandboxing in place for content inspection?

**L4 elements:**
- `Q13-E09` — Is a positive security (allow-list) model enforced at the WAF?
- `Q13-E10` — Is inline file detonation in a sandbox performed before file delivery?
- `Q13-E11` — Is CSP report-uri integrated with the SOC for visibility on policy violations?

---

## Q14 — Branch Protection & Code Review (Secure SDLC & Release)

*Priority:* Must · *GIC Control:* Y · *Industry:* NIST SSDF PO.3, PW.4; CIS 16.1

**Question:** Is main branch protected with required reviews + required CI checks + signed commits?

**L1 elements:**
- `Q14-E01` — Is direct push to the main branch permitted in any repository?
- `Q14-E02` — Are PR reviews optional or limited to a single reviewer for production code?
- `Q14-E03` — Are CI checks not required before merging to the main branch?

**L2 elements:**
- `Q14-E04` — Are main and release branches protected with required PR reviews (at least 1 reviewer, at least 2 for production code)?
- `Q14-E05` — Are required status checks enforced, including build, tests, SAST, and SCA passing before merge?
- `Q14-E06` — Are signed commits and verified contributors enforced on protected branches?

**L3 elements:**
- `Q14-E07` — Is code-owner-based review routing in place?
- `Q14-E08` — Are required reviewer expertise tags enforced?
- `Q14-E09` — Are merges blocked on stale reviews?

**L4 elements:**
- `Q14-E10` — Is trunk-based development with feature flags in place?
- `Q14-E11` — Is AI-assisted code review covering security and style active?
- `Q14-E12` — Is deployment lead-time under 1 day?

---

## Q15 — Deployment Pipeline & Rollback (Secure SDLC & Release)

*Priority:* Must · *GIC Control:* N · *Industry:* DORA 4 keys; AWS WAF Operational Excellence; NIST SSDF PO.5

**Question:** Is deployment fully automated with rollback/blue-green/canary tested and approvals in place?

**L1 elements:**
- `Q15-E01` — Are there any manual steps required on production servers during deployment?
- `Q15-E02` — Has the rollback mechanism never been tested?
- `Q15-E03` — Are deployment change approvals ad-hoc rather than formally enforced?

**L2 elements:**
- `Q15-E04` — Is deployment fully automated via GitHub Actions with no manual production-server steps?
- `Q15-E05` — Is a tested rollback, blue-green, or canary deployment mechanism in place?
- `Q15-E06` — Are deployment approvals enforced via the change control process?

**L3 elements:**
- `Q15-E07` — Are DORA Four Keys (Deployment Frequency, Lead Time, Change Failure Rate, MTTR) tracked?
- `Q15-E08` — Are feature flags in place for progressive rollout of changes?
- `Q15-E09` — Is automated rollback triggered on deployment failure?
- `Q15-E10` — Is infrastructure drift detection active?

**L4 elements:**
- `Q15-E11` — Is trunk-based development with continuous deployment in place?
- `Q15-E12` — Are commits and deployment artefacts cryptographically signed?
- `Q15-E13` — Is supply-chain security implemented at SLSA Level 2 or above?

---

## Q16 — Infrastructure as Code & Environment Consistency (Secure SDLC & Release)

*Priority:* Should · *GIC Control:* N · *Industry:* 12-factor.net; NIST SSDF PO.5; AWS CAF

**Question:** Is infrastructure defined as code, version-controlled, and deployed consistently across environments?

**L1 elements:**
- `Q16-E01` — Is any infrastructure hand-built or deployed via click-ops rather than code?
- `Q16-E02` — Do environments drift from each other due to inconsistent deployment practices?

**L2 elements:**
- `Q16-E03` — Is all infrastructure defined as code (Terraform / CDK) with the same artefact deployed across dev, UAT, and production?
- `Q16-E04` — Is environment-specific configuration kept out of the IaC code itself?
- `Q16-E05` — Is IaC stored in version control with required peer review?

**L3 elements:**
- `Q16-E06` — Is drift detection running daily and alerting on environment divergence?
- `Q16-E07` — Is IaC modularised and reused across applications?

**L4 elements:**
- `Q16-E08` — Is policy-as-code (e.g. OPA / Sentinel) blocking non-compliant infrastructure at the PR stage?
- `Q16-E09` — Are ephemeral environments provisioned per pull request?

---

## Q17 — Multi-AZ & Redundancy (Resilience & Recovery)

*Priority:* Must · *GIC Control:* Y · *Industry:* AWS WAF Reliability; CIS 11

**Question:** Is the app multi-AZ with tested failover, including data stores?

**L1 elements:**
- `Q17-E01` — Is the application running in a single Availability Zone with no automatic failover?
- `Q17-E02` — Do data stores lack redundancy or have untested redundancy?

**L2 elements:**
- `Q17-E03` — Is the application deployed across 2 or more Availability Zones with tested automatic failover?
- `Q17-E04` — Are critical data stores configured for multi-AZ or cross-region redundancy (e.g. RDS Multi-AZ, S3 cross-region)?

**L3 elements:**
- `Q17-E05` — Is an availability SLO defined, measured, and alerted on?
- `Q17-E06` — Is graceful degradation under partial failure tested and validated?
- `Q17-E07` — Has the HA architecture been validated against documented scenario tests?

**L4 elements:**
- `Q17-E08` — Is chaos testing conducted on a schedule with documented results?
- `Q17-E09` — Is self-healing infrastructure in place?
- `Q17-E10` — Is multi-region active-active or warm standby deployed with automated failover under 5 minutes?

---

## Q18 — SLO / SLI & Error Budget (Resilience & Recovery)

*Priority:* Should · *GIC Control:* N · *Industry:* Google SRE; AWS WAF Reliability

**Question:** Are SLOs defined for your Application?

**L1 elements:**
- `Q18-E01` — Are there no formal SLOs defined, with reliability measured ad-hoc or only by incident count?

**L2 elements:**
- `Q18-E02` — Are SLIs and SLOs defined for user-facing endpoints, covering availability and latency?
- `Q18-E03` — Are Datadog SLO monitors alerting when thresholds approaching unhealthy?

**L3 elements:**
- `Q18-E04` — Does error-budget exhaustion trigger a feature-freeze decision?
- `Q18-E05` — Is SLO posture reviewed quarterly with stakeholders?

**L4 elements:**
- `Q18-E06` — Are composite SLOs defined across all dependencies?
- `Q18-E07` — Is predictive burn-rate alerting in place, alerting on trajectory rather than just current state?
- `Q18-E08` — Is SLO-driven autoscaling configured?

---

## Q19 — Graceful Degradation (Resilience & Recovery)

*Priority:* Should · *GIC Control:* N · *Industry:* Google SRE; AWS WAF Reliability; ISO 25010

**Question:** Does the app degrade gracefully on dependency failure? (circuit breakers, fallbacks, tested)

**L1 elements:**
- `Q19-E01` — Do dependency failures cascade and bring down the entire application?
- `Q19-E02` — Are circuit breakers and fallback mechanisms absent?

**L2 elements:**
- `Q19-E03` — Does the application implement graceful degradation for non-critical dependency failures, including circuit breakers, fallbacks, and timeouts?

**L3 elements:**
- `Q19-E04` — Has graceful degradation been verified via chaos or dependency-failure testing in non-production?
- `Q19-E05` — Are chaos and dependency failure tests run on a schedule with documented results?

**L4 elements:**
- `Q19-E06` — Is graceful degradation validated for every external integration?
- `Q19-E07` — Is chaos engineering practised in production behind feature flags?

---

## Q20 — Automated Backup & Restore Test (Resilience & Recovery)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS 11.5; NIST 800-53 CP-9; AWS WAF Reliability

**Question:** Are backups automated to required RPO, with annual restore test and measured RTO?

**L1 elements:**
- `Q20-E01` — Is backup coverage incomplete, or has a restore test not been performed in the last 24 months?

**L2 elements:**
- `Q20-E02` — Are automated backups configured for all critical data stores, meeting the required RPO?
- `Q20-E03` — Has backup restore been tested at least annually with documented results and a measured RTO?

**L3 elements:**
- `Q20-E04` — Are restore tests conducted semi-annually?
- `Q20-E05` — Are cross-region backup copies maintained for Tier-1 data?
- `Q20-E06` — Are immutable backups in place (e.g. using Vault Lock)?

**L4 elements:**
- `Q20-E07` — Are restore tests automated and run on a continuous rolling basis?
- `Q20-E08` — Is RTO measured statistically at P50 and P95?

---

## Q21 — DR Plan & Tested Recovery (Resilience & Recovery)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS 11; NIST 800-53 CP-2, CP-4; ISO 22301

**Question:** Is the DR plan signed off, aligned to RTO/RPO, and tested within 12 months?

**L1 elements:**
- `Q21-E01` — Is the DR plan unsigned, untested, or more than 12 months out of date?

**L2 elements:**
- `Q21-E02` — Is a documented DR plan in place, signed off, aligned to the declared RTO and RPO, and including a recovery runbook?
- `Q21-E03` — Has DR testing been completed within the last 12 months with results formally signed off?

**L3 elements:**
- `Q21-E04` — Is DR tested semi-annually with documented results?
- `Q21-E05` — Are RTO and RPO targets validated against current business requirements?
- `Q21-E06` — Is the recovery runbook updated after every DR test?

**L4 elements:**
- `Q21-E07` — Are chaos game days conducted to exercise DR scenarios?
- `Q21-E08` — Is multi-region active-active or warm standby deployed with automated failover under 5 minutes, eliminating manual runbook execution

---

## Q22 — Telemetry to Datadog + Splunk (Observability & Monitoring)

*Priority:* Must · *GIC Control:* Y · *Industry:* Google SRE; OpenTelemetry; CIS 8

**Question:** Is Datadog (metrics/synthetics) + Splunk (logs) integrated and active?

**L1 elements:**
- `Q22-E01` — Are logs incomplete or inconsistently shipping to Splunk or Datadog?
- `Q22-E02` — Is monitoring limited to basic uptime checks with no structured observability in place?

**L2 elements:**
- `Q22-E03` — Is Datadog integrated for service monitoring, including URLs, endpoints, APIs, certificates, and synthetics?
- `Q22-E04` — Are all application and infrastructure logs onboarded to Splunk with at least hourly shipping and log sources documented?
- `Q22-E05` — Are the Four Golden Signals (latency, traffic, errors, saturation) dashboarded?

**L3 elements:**
- `Q22-E06` — Is distributed tracing with correlation IDs implemented?
- `Q22-E07` — Is SLO-based alerting with burn-rate monitoring in place?
- `Q22-E08` — Is log-based anomaly detection active?
- `Q22-E09` — Is a daily agent reconciliation report running?
- `Q22-E10` — Is synthetic monitoring in place for all critical user paths?

**L4 elements:**
- `Q22-E11` — Is AIOps in place for anomaly detection and alert noise reduction?
- `Q22-E12` — Is automated runbook execution triggered on alerts?
- `Q22-E13` — Is predictive alerting in place to detect degradation before user impact occurs?

---

## Q23 — Security Monitoring & Audit Logs (Observability & Monitoring)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS 8.11; NIST 800-53 AU-12; OWASP A09

**Question:** Is privileged-activity security monitoring + log sanitisation in place?

**L1 elements:**
- `Q23-E01` — Is security monitoring only partially implemented for privileged activities?
- `Q23-E02` — Do audit logs contain credentials, PII, tokens, or session IDs?

**L2 elements:**
- `Q23-E03` — Is security monitoring enabled for all privileged activities (admin logins, privilege escalation, config changes, data access) with alerting wired to the SOC?
- `Q23-E04` — Are audit logs sanitised to ensure no credentials, PII, tokens, or session IDs are written to log stores?

**L3 elements:**
- `Q23-E05` — Is SOC alert routing tested on a quarterly basis?
- `Q23-E06` — Are correlation rules tuned to application-specific patterns?
- `Q23-E07` — Are insider-threat detection rules active and wired to the SOC?

**L4 elements:**
- `Q23-E08` — Is UEBA (User and Entity Behaviour Analytics) baselining active per application?
- `Q23-E09` — Is ML-based anomaly correlation active across multiple data sources?

---

## Q24 — Expiry & Agent Health Alerting (Observability & Monitoring)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS 1.5, 2.4; ITIL 4 Service Level Mgmt

**Question:** Are expiry alerts (>3mo lead) and daily agent-coverage reconciliation operating?

**L1 elements:**
- `Q24-E01` — Are SSL certificate or licence expiries only caught reactively after they cause failures?
- `Q24-E02` — Is there no daily agent reconciliation process in place?

**L2 elements:**
- `Q24-E03` — Are automated alerts configured for SSL certificate, licence, and support contract expiry with at least 3 months lead time?
- `Q24-E04` — Is daily agent reconciliation in place for Datadog, Tenable, Splunk, and endpoint agents, with missing-agent escalation?

**L3 elements:**
- `Q24-E05` — Are certificate and licence renewal tickets auto-generated 90 or more days before expiry?
- `Q24-E06` — Are agent coverage gaps remediated within 24 hours?

**L4 elements:**
- `Q24-E07` — Is predictive expiry detection in place, factoring in ticket queue length and vendor lead time?
- `Q24-E08` — Is agent health scored per asset?

---

## Q25 — Asset & Account Inventory (Operations & Documentation)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS Control 1, CIS Control 5; ISO 27001 A.5.9

**Question:** Are your assets and accounts fully inventoried — ServiceNow/Helix matches reality, all account types listed with owners?

**L1 elements:**
- `Q25-E01` — Does the ServiceNow / Helix CMDB show more than 5% drift from the actual deployed infrastructure?
- `Q25-E02` — Is the account list incomplete, out of date, or missing ACM approval traces?

**L2 elements:**
- `Q25-E03` — Does the asset inventory in ServiceNow / Helix accurately reflect all deployed infrastructure, including servers, databases, load balancers, and network components?
- `Q25-E04` — Does the account list cover all breakglass, service, privileged, and application accounts with named owners and ACM approval traces?

**L3 elements:**
- `Q25-E05` — Is the inventory reconciled daily against AWS Config and Wiz, with drift above 5% triggering a ticket?
- `Q25-E06` — Is the account list version-controlled?

**L4 elements:**
- `Q25-E07` — Is the inventory auto-populated from cloud APIs with no manual CMDB entry required?
- `Q25-E08` — Is orphaned account auto-detection in place?

---

## Q26 — System & Network Documentation (Operations & Documentation)

*Priority:* Must · *GIC Control:* Y · *Industry:* ISO 25010 Maintainability; TOGAF; CIS 12

**Question:** Is your architecture documentation AWG-approved and current? (system arch + network diagrams + firewall + proxy rules)

**L1 elements:**
- `Q26-E01` — Is the architecture diagram stale (more than 12 months old), unapproved, or are firewall and proxy rules undocumented?

**L2 elements:**
- `Q26-E02` — Is there an AWG-approved system architecture document covering components, data flows, integration points, and network connectivity?
- `Q26-E03` — Are network architecture diagrams, firewall rules, and proxy rules documented and kept current?

**L3 elements:**
- `Q26-E04` — Is architecture documentation version-controlled and reviewed annually?
- `Q26-E05` — Are all documentation changes tracked through a PR process?

**L4 elements:**
- `Q26-E06` — Is documentation generated directly from code and config to prevent drift?
- `Q26-E07` — Are Architecture Decision Records (ADRs) maintained?

---

## Q27 — Operational Readiness (Operations & Documentation)

*Priority:* Must · *GIC Control:* Y · *Industry:* ITIL 4 Service Transition; CIS 16

**Question:** Is the app operationally ready? (SOPs + vendor support + certificate management + UAT sign-off complete)

**L1 elements:**
- `Q27-E01` — Are any operational SOPs incomplete or missing coverage for the relevant ops teams?
- `Q27-E02` — Are vendor support contacts missing or out of date?
- `Q27-E03` — Is UAT sign-off from the business owner absent?

**L2 elements:**
- `Q27-E04` — Are SOPs completed for all applicable ops teams (ServiceDesk, End User Infra, Compute, Cloud, IAM Ops)?
- `Q27-E05` — Are vendor support contacts documented, including 24x7 support and escalation paths?
- `Q27-E06` — Are certificate SOPs in place covering a maximum validity of 398 days and automated expiry monitoring?
- `Q27-E07` — Has UAT been formally signed off by the business owner?

**L3 elements:**
- `Q27-E08` — Are operational metrics tracked, including MTTR, ticket volume, and change success rate?
- `Q27-E09` — Are post-incident reviews conducted with tracked action items?
- `Q27-E10` — Is a knowledge base actively maintained?

**L4 elements:**
- `Q27-E11` — Are self-service operations in place, including ChatOps and automated remediation?
- `Q27-E12` — Is documentation generated from code and config rather than maintained manually?
- `Q27-E13` — Are operational excellence reviews conducted quarterly?

---

## Q28 — Capacity & Auto-Scale (Performance & Scalability)

*Priority:* Must · *GIC Control:* N · *Industry:* AWS WAF Performance; Google SRE

**Question:** Is auto-scale configured against measured baselines and tested at 1.5× peak?

**L1 elements:**
- `Q28-E01` — Is auto-scaling absent or untested, with no load test conducted in the last 12 months?

**L2 elements:**
- `Q28-E02` — Are auto-scaling policies configured against measured baselines (CPU, memory, request rate, queue depth)?
- `Q28-E03` — Has capacity been tested at 1.5 times peak load via Datadog load tests or synthetic monitors?

**L3 elements:**
- `Q28-E04` — Are P95 and P99 latency tracked and within SLO at production load?
- `Q28-E05` — Is a capacity model in place with growth projections?
- `Q28-E06` — Is performance regression testing integrated in CI?

**L4 elements:**
- `Q28-E07` — Is predictive autoscaling in place to scale before demand arrives?
- `Q28-E08` — Are performance budgets enforced per release?
- `Q28-E09` — Is real-time performance profiling active in production?

---

## Q29 — Performance SLOs & Regression Detection (Performance & Scalability)

*Priority:* Should · *GIC Control:* N · *Industry:* AWS WAF Performance; Google SRE; OpenTelemetry

**Question:** Are perf SLOs defined with APM regression detection on releases?

**L1 elements:**
- `Q29-E01` — Is performance only monitored reactively after user complaints, with no APM regression detection in place?

**L2 elements:**
- `Q29-E02` — Are performance SLOs defined covering p50, p95, and p99 latency?
- `Q29-E03` — Is Datadog APM regression detection active on each release, with rollback triggered on regression?

**L3 elements:**
- `Q29-E04` — Is a performance regression test run in CI before merge?
- `Q29-E05` — Is regression history tracked and visible across releases?

**L4 elements:**
- `Q29-E06` — Is real-time performance profiling active in production?
- `Q29-E07` — Are performance budgets enforced per release?
- `Q29-E08` — Is predictive degradation alerting in place?

---

## Q30 — Cost Visibility & Optimisation (Cost & Sustainability)

*Priority:* Should · *GIC Control:* N · *Industry:* AWS WAF Cost Optimisation + Sustainability

**Question:** Is cloud spend tagged + monthly-reviewed with right-sizing acted on?

**L1 elements:**
- `Q30-E01` — Is cloud spend tagging incomplete, or are right-sizing recommendations not consistently acted on?

**L2 elements:**
- `Q30-E02` — Is application cloud spend tagged and reviewed monthly, with right-sizing recommendations acted on?
- `Q30-E03` — Is a documented sustainability posture in place, covering workload placement and instance generation choices?

**L3 elements:**
- `Q30-E04` — Is cost-per-unit tracked at the transaction or per-user level?
- `Q30-E05` — Is cost anomaly alerting configured?
- `Q30-E06` — Is reserved instance or savings-plan coverage optimised?
- `Q30-E07` — Are FinOps reviews conducted monthly?

**L4 elements:**
- `Q30-E08` — Is automated cost anomaly detection and response in place?
- `Q30-E09` — Is real-time cost attribution available?
- `Q30-E10` — Do architecture decisions include cost modelling?

---

## Q31 — 12-Factor & Architecture Pattern (Governance & Architecture)

*Priority:* Must · *GIC Control:* Y · *Industry:* 12-factor.net (III, IV, VI); CIS 4; ISO 25010 Maintainability

**Question:** Is the app stateless, with externalised config and a documented architecture pattern?

**L1 elements:**
- `Q31-E01` — Are there stateful processes with local files or sessions, or is configuration partly hardcoded?
- `Q31-E02` — Are backing services treated as anything other than attached resources?

**L2 elements:**
- `Q31-E03` — Is the application built to 12-factor principles, with stateless processes, externalised configuration via environment variables or Parameter Store or Secrets Manager, and backing services as attached resources?
- `Q31-E04` — Is the architecture pattern documented (e.g. 12-factor, layered, microservices) with dependencies inventoried?

**L3 elements:**
- `Q31-E05` — Has the architecture been reviewed within the last 12 months and is a threat model in place?
- `Q31-E06` — Are managed services preferred over self-operated components?
- `Q31-E07` — Is technical debt inventoried?
- `Q31-E08` — Are components isolated with a minimal blast radius?

**L4 elements:**
- `Q31-E09` — Is the architecture continuously validated against principles using fitness functions?
- `Q31-E10` — Are automated compliance checks running against the architecture?
- `Q31-E11` — Are Architecture Decision Records (ADRs) maintained?

---

## Q32 — CMDB Metadata & Ownership (Governance & Architecture)

*Priority:* Must · *GIC Control:* Y · *Industry:* CIS 1, 2; ISO 27001 A.5.9; (GIC Control Library)

**Question:** Is CMDB metadata current with named owner/lead and are vendor dependencies registered?

**L1 elements:**
- `Q32-E01` — Is CMDB metadata partial, stale, or are third-party dependencies tracked only informally?

**L2 elements:**
- `Q32-E02` — Is the application registered in the CMDB with current metadata, including owner, technical lead, classification, tier, and environment list?
- `Q32-E03` — Is a third-party and vendor dependency register maintained with named owners and contractual SLA details?

**L3 elements:**
- `Q32-E04` — Is CMDB metadata reviewed quarterly?
- `Q32-E05` — Is the third-party register tracked against contractual SLAs and renewal dates?

**L4 elements:**
- `Q32-E06` — Is CMDB metadata auto-populated from authoritative sources?
- `Q32-E07` — Is vendor health monitored continuously?

---
