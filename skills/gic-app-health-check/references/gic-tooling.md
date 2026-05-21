# GIC Tooling — Named systems referenced in the rubric

Many element texts reference specific GIC tools by name. This file is the catalogue: one section per tool, with a one-line description, which questions reference it, and where to look for it in a typical application's source artefacts.

The full element-to-source routing is in `assets/element-source-routing.json`. This document is the prose explanation of the tools themselves.

---

## Identity & Access

### Ping (SSO)
GIC's single sign-on provider. All applications onboard to Ping for federated authentication. Element references appear in Q01 (SSO + MFA + Identity Lifecycle).

**Look in:** Risk Assessment "declared controls"; Confluence "identity onboarding" page; Ping admin console (where API access available).

### Sailpoint IGA / MyAccess
GIC's identity governance platform. Manages joiner-mover-leaver lifecycle, quarterly access reviews, certification campaigns. Element references appear in Q01, Q05.

**Look in:** Confluence access-review SOPs; MyAccess admin console; Sailpoint IdentityNow API.

### CyberArk PAM
GIC's privileged access management vault. All privileged + service accounts integrate with CyberArk. Element references appear in Q02 (Privileged Access), Q04 (Secrets).

**Look in:** Confluence privileged-account inventory; CyberArk vault listing; account-management SOPs.

### Active Directory + PARIS
Enterprise AD for authorisation. PARIS is GIC's infra-registration system tracking which roles can access which infrastructure. Element references appear in Q03 (Authorisation).

**Look in:** Risk Assessment infra section; PARIS registration records; AD group memberships.

### Zscaler
Enterprise device-restriction + DLP egress. Element references appear in Q01 (device restriction), Q09 (DLP & Egress).

**Look in:** Risk Assessment network access section; Zscaler admin console.

### ACM (Account Management)
GIC's account-management approval process. Element references appear in Q01, Q02, Q05, Q25 (Asset & Account Inventory).

**Look in:** Confluence account-management approval records; ACM ticket history.

### ITRM (IT Risk Management)
GIC's IT risk management process. Houses the AI Security checklist and Mobile Application Security checklist. Element references appear in Q12 (Pen Testing & Cloud Posture).

**Look in:** ITRM checklist artefacts; Confluence ITRM pages.

## Security tooling

### Wiz CSPM
Cloud Security Posture Management — continuously scans for cloud misconfigurations, IAM issues, container vulnerabilities. Element references appear in Q03, Q04, Q12.

**Look in:** Confluence security-monitoring pages; Wiz console exports; Risk Assessment "cloud posture" section.

### Tenable
OS / endpoint vulnerability scanning agent. Element references appear in Q11 (OS / Container Vulnerability & Patch Mgmt), Q24 (Agent Health).

**Look in:** Confluence VAR (Vulnerability Assessment Report) artefacts; monthly Tenable reports.

### TICRP (Penetration Testing)
GIC's penetration-testing standard. Pen-tests follow TICRP criteria. Element references appear in Q12.

**Look in:** Pen-test reports (typically in SharePoint or Confluence "security artefacts").

### IAM Access Analyzer
AWS IAM Access Analyzer findings. Element references appear in Q03.

**Look in:** AWS console exports; Risk Assessment IAM section.

## Code + delivery

### GitHub Enterprise (CodeQL + Snyk + Secret Scanning)
GIC's enterprise GitHub. Hosts code repos; runs CodeQL (SAST), Snyk (SCA), and GitHub Secret Scanning. Element references appear in Q04 (secrets), Q10 (SAST/SCA pipeline), Q14 (branch protection), Q15 (deployment pipeline), Q16 (IaC).

**Look in:** GitHub REST API endpoints (`/repos/{owner}/{repo}/branches/{branch}/protection`, `/repos/.../code-scanning/alerts`, etc.); workflow YAMLs in `.github/workflows/`.

### AWS Secrets Manager
AWS secrets vaulting service. Alternative or complement to CyberArk for app secrets. Element references appear in Q04.

**Look in:** Risk Assessment secrets section; AWS Secrets Manager listings.

## Observability + operations

### DataDog
Service monitoring (URLs, APIs, certs, jobs, DBs, disk). SLO monitors, APM, synthetics. Element references appear in Q18 (SLOs), Q22 (Telemetry), Q24 (Expiry alerts), Q28 (Capacity), Q29 (Performance).

**Look in:** DataDog dashboard exports; Confluence observability page; runbooks referencing DataDog monitors.

### Splunk
Security log aggregation (SIEM). Receives audit logs, privileged-activity logs. Element references appear in Q22 (Telemetry), Q23 (Security Monitoring).

**Look in:** Splunk index health screenshots; Confluence security-monitoring page; SOC alert routing rules.

### ServiceNow / Helix CMDB
GIC's CMDB / asset inventory. Tracks application metadata: owner, tech lead, classification, tier, environments. Element references appear in Q25 (Asset Inventory), Q26 (Documentation), Q32 (CMDB Metadata).

**Look in:** ServiceNow record extracts; Confluence CMDB-onboarding page.

### AWG (Architecture Working Group)
GIC's architecture review board. Approves system architectures. Element references appear in Q26 (System & Network Documentation).

**Look in:** ARB output PDFs (Confluence exports); AWG sign-off records.

### AWS Config + AWS Backup + AWS ACM + AWS Cost Explorer
AWS-native services used across the rubric. Element references appear in Q06 (encryption), Q09 (S3 bucket policies), Q17 (Multi-AZ), Q20 (Backup), Q24 (cert expiry), Q30 (cost tagging).

**Look in:** AWS console exports; Risk Assessment AWS section; ARB output AWS architecture.

---

## Tool coverage by question

A summary of which tools each question references (most-frequent tools first):

| Question | Primary tools referenced |
|---|---|
| Q01 IAM SSO+MFA+IGA | Ping, Sailpoint IGA, MyAccess, Zscaler |
| Q02 PAM | CyberArk |
| Q03 Authorisation | Wiz CSPM, IAM Access Analyzer, AD, PARIS |
| Q04 Secrets & Sessions | AWS Secrets Manager, CyberArk, GitHub Secret Scanning, Wiz |
| Q05 Access Reviews | Sailpoint, MyAccess |
| Q06 Encryption + Vendor | AWS Config, AWS KMS, manual vendor attestations |
| Q07 Data Classification | (Manual / Risk Assessment) |
| Q08 Data Masking | (Manual) |
| Q09 DLP & Egress | Zscaler, AWS Config |
| Q10 SAST/SCA/Secrets | CodeQL, Snyk, GitHub Secret Scanning, Tenable |
| Q11 OS / Container Vuln | Tenable |
| Q12 Pen Test & CSPM | TICRP, Wiz CSPM, ITRM |
| Q13 Input Validation | (Manual / code review) |
| Q14 Branch Protection | GitHub |
| Q15 Deployment Pipeline | GitHub Actions |
| Q16 IaC | GitHub, Terraform Cloud |
| Q17 Multi-AZ | AWS Config |
| Q18 SLOs | DataDog SLO |
| Q19 Graceful Degradation | (Manual / code review + chaos artefacts) |
| Q20 Backup & Restore | AWS Backup |
| Q21 DR Plan | (Manual / DR test sign-off) |
| Q22 Telemetry | DataDog, Splunk |
| Q23 Security Monitoring | Splunk |
| Q24 Expiry & Agents | AWS ACM, DataDog, Tenable, Splunk |
| Q25 Asset & Account Inventory | ServiceNow / Helix, AWS Config |
| Q26 System & Network Docs | AWG, ServiceNow |
| Q27 Operational Readiness | (Manual / SOPs) |
| Q28 Capacity & Auto-Scale | AWS Auto Scaling, DataDog |
| Q29 Performance SLOs | DataDog APM |
| Q30 Cost Visibility | AWS Cost Explorer |
| Q31 12-Factor & Arch | (Manual + GitHub IaC scan) |
| Q32 CMDB Metadata | ServiceNow |
