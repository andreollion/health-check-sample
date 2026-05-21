# Extracting from a Risk Assessment PDF

## What this source provides

The Risk Assessment is a GIC-internal submission that the application team completes early in the migration workflow. It declares the app's risk profile, classification, declared controls, and high-level posture.

It is the **declaration of intent + claimed posture**. Other sources (GitHub, ARB) verify whether the declarations are real.

## Typical fields present

A standard Risk Assessment will include (sections may vary):

- Application metadata (name, asset ID, classification tier, business owner, tech lead)
- Data classification (Public / Internal / Restricted / Secret) and types of data processed
- Data residency requirements (Singapore-only, multi-region acceptable, etc.)
- Declared identity controls (SSO provider, MFA enforcement, PAM coverage)
- Declared encryption posture
- Vendor / third-party dependencies (with attested standards: SOC2 Type 2, OSPAR, ISO 27001)
- Recovery objectives (RTO, RPO)
- Criticality tier (1-4 typically, where 1 = most critical)
- SCR rating (Security Classification Rating)
- Primary AppsOIC (the assigned operations-in-charge)
- External connectivity (whether the app is internet-facing, internal-only, etc.)
- Product type (web app, batch job, API, etc.)

## What to extract per schema area

### app
- `app.name` — usually on the cover page or section 1
- `app.asset_id` — typically a unique ID near app.name
- `app.classification` — explicit classification field
- `app.criticality_tier` — explicit criticality field (1-4)
- `app.scr_rating` — explicit SCR field
- `app.primary_apps_oic` — explicit field naming the OIC
- `app.product_type` — explicit field
- `app.external_connectivity` — explicit field or derived from "internet-facing" description
- `app.owner`, `app.tech_lead` — explicit fields
- `app.rto_hours`, `app.rpo_minutes` — explicit RTO/RPO declarations (convert units if needed)

### identity (declared)
- `identity.sso_provider` — usually "Ping" if onboarded
- `identity.sso_app_onboarded` — explicit declaration
- `identity.mfa.*` — declared MFA enforcement (users / admins / cloud)
- `identity.lifecycle_system` — usually "MyAccess" or "Sailpoint"
- `identity.pam_vault_system` — usually "CyberArk" if used
- `identity.session_timeout_idle_min`, `session_timeout_absolute_hr`

### data_protection (declared)
- `data_protection.data_classification` — same as `app.classification` typically
- `data_protection.secret_data_present` — if classification is Secret
- `data_protection.secret_data_dedicated_singapore_infra` — declaration
- `data_protection.vendors[]` — third-party vendor declarations with attestation dates

### resilience (declared)
- `resilience.dr_plan_documented` — if the Risk Assessment references a DR plan
- `resilience.rpo_target_min`, `resilience.rto_achieved_hr` — declared targets

## Extraction prompt pattern

When asking an LLM to extract from a Risk Assessment, structure the prompt:

```
You are extracting structured data from a GIC Application Risk Assessment PDF.

The schema is provided below. For each property in the schema, look through
the Risk Assessment and extract the value if present. Set null for any
property the document does not address.

For every property you set, add a corresponding entry to the evidence array
with the page number, section, and a direct quote.

Do NOT infer values. If the document does not state something, leave it null.

Schema: <embed schema.json or relevant slice>

Risk Assessment content:
<PDF text>

Return JSON matching the schema.
```

## Provenance examples

```json
{
  "property_path": "app.classification",
  "source": "risk_assessment",
  "ref": "p.2, section 1.4",
  "excerpt": "Data Classification: Restricted",
  "extracted_at": "2026-05-05T14:23:00Z"
},
{
  "property_path": "data_protection.vendors[0].name",
  "source": "risk_assessment",
  "ref": "p.8, section 5.1",
  "excerpt": "Primary data processor: AcmeVendor Pte Ltd (SOC2 Type 2 attestation dated 2025-09-14)",
  "extracted_at": "2026-05-05T14:23:00Z"
}
```

## Caveats

- The Risk Assessment is **self-declared**. Treat it as declaration, not verification. Setting properties from it is fine; Stage 2 (question answering) will combine with other sources.
- Risk Assessments older than 12 months should be flagged in `metadata.stale_sources`.
- If a Risk Assessment is missing entirely (some apps may not have one), leave the relevant properties null and add an `metadata.sources_present` entry that excludes `risk_assessment`.
