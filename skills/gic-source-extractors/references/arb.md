# Extracting from an ARB Output PDF

## What this source provides

The Architecture Review Board (AWG) output is a Confluence-exported document recording GIC's architecture review for an application. It captures the approved system architecture, network topology, data flows, integration points, and the AWG's sign-off on the design.

It is the **architecture authority** for the app. When the question is "what is the architecture", the ARB output is the answer.

## Typical fields present

A standard ARB output will include:

- AWG approval record (date, approver, scope of approval)
- System architecture diagram or description
- Network architecture (VPC, subnet layout, firewall rules, proxy rules)
- Data flow descriptions
- External integrations / dependencies
- Cloud account / environment list
- Multi-AZ vs single-AZ deployment topology
- High-availability design notes
- Component decomposition

## What to extract per schema area

### app
- `app.classification` — sometimes restated; cross-check against Risk Assessment

### data_protection (architecture-level)
- `data_protection.data_stores[]` — list of databases / storage systems from the architecture
- `data_protection.tls_version_min` — if architecture specifies TLS configuration
- `data_protection.internal_unencrypted_hops` — derived from data flow diagrams (look for unencrypted intra-VPC links)

### resilience
- `resilience.multi_az_deployed` — explicit from architecture description
- `resilience.az_count` — count from architecture diagram
- `resilience.data_stores_multi_az_or_xregion` — derived from architecture
- `resilience.automatic_failover_tested` — sometimes referenced in HA notes

### operations
- `operations.system_arch_awg_approved` — usually True if the document exists at all
- `operations.awg_approval_date` — date stamp from AWG sign-off section
- `operations.network_diagram_current` — derived from document timestamp and content
- `operations.firewall_rules_documented` — True if firewall section present
- `operations.proxy_rules_documented` — True if proxy section present

### governance
- `governance.architecture_pattern` — derived from architecture description (12-factor / layered / microservices)
- `governance.stateless_processes` — if architecture explicitly states statelessness
- `governance.dependencies_inventoried` — True if a dependencies list is present

## Extraction prompt pattern

```
You are extracting structured data from a GIC Architecture Review Board (AWG)
output PDF.

The schema is provided below. Focus on architecture-related fields:
multi-AZ deployment, data flow encryption, AWG approval status, network
documentation completeness, architecture pattern compliance.

Do NOT infer values. If the document does not state something, leave it null.

For every property you set, add a corresponding entry to the evidence array
with the page number, section, and a direct quote or summary.

Schema: <embed relevant slice>

ARB Output content:
<PDF text>

Return JSON matching the schema.
```

## Provenance examples

```json
{
  "property_path": "resilience.multi_az_deployed",
  "source": "arb",
  "ref": "ARB output p.6 — Architecture Diagram",
  "excerpt": "Application is deployed across 2 AZs in ap-southeast-1; data stores use Multi-AZ RDS",
  "extracted_at": "2026-05-05T14:23:00Z"
},
{
  "property_path": "operations.awg_approval_date",
  "source": "arb",
  "ref": "ARB output p.1 — Sign-off Block",
  "excerpt": "AWG Approval Date: 2026-03-14 — Approver: M. Chen (Cloud Architecture Lead)",
  "extracted_at": "2026-05-05T14:23:00Z"
}
```

## Reading architecture diagrams in PDFs

Claude Opus can read diagrams in PDFs directly. When extracting from a diagram:

- Identify components by their labels in the diagram
- Use the legend to interpret connection lines (encrypted vs unencrypted, internal vs external)
- Note any annotations about multi-AZ / multi-region
- Capture the count of components and their types

If a diagram is unclear or low-resolution, prefer the surrounding prose. If both are unclear, leave the relevant properties null.

## Caveats

- ARB outputs can be old. If the document is >12 months old, the architecture may have drifted. Flag in `metadata.stale_sources`.
- An ARB output proves the architecture *was* approved at the time of sign-off. It doesn't prove the implementation matches today. Stage 2 will cross-reference against GitHub (IaC) where possible.
- If no ARB output is provided for an app, leave `operations.system_arch_awg_approved = false` (since the absence of an approval record is itself a finding).
