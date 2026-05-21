# Per-Application Schema (Prose Version)

The full machine-readable schema is in `assets/schema.json`. This document is the human-readable summary.

## Top-level structure

```
{
  "metadata":         { schema_version, extracted_at, sources_present, ... },
  "app":              { name, asset_id, classification, owner, tech_lead, ... },
  "identity":         { sso, mfa, lifecycle, pam, secrets, sessions, advanced },
  "data_protection":  { encryption, vendors, classification, masking, dlp },
  "appsec":           { codeql/snyk/secret-scanning, tenable, pen-test, wiz, ... },
  "sdlc":             { branch_protection, deployment, iac },
  "resilience":       { multi_az, slo, backup, dr },
  "observability":    { datadog, splunk, monitoring, audit_logs, alerts },
  "operations":       { cmdb, account_inventory, awg, sops, vendor_support, uat },
  "performance":      { autoscale, slo, regression_detection },
  "cost":             { tagging, trend_review, right_sizing, anomaly_alerting },
  "governance":       { stateless, config_externalised, architecture_pattern, cmdb },
  "evidence":         [ { property_path, source, ref, excerpt, extracted_at }, ... ]
}
```

## Three rules to follow when extracting

### Rule 1: Three-state values, not boolean

Every property uses **True / False / null**, not True/False alone. A missing value is **null**, not False. This is critical — the rubric distinguishes "Not Sure" from "No", and the extracted data must preserve that distinction.

If a source document says nothing about a property, set the property to `null`. Do not infer False.

### Rule 2: Every set property carries provenance

For every property you set to a non-null value, you MUST add an entry to the top-level `evidence` array. The entry maps the property path back to the source document + excerpt that justified the value.

Example:
```json
"identity": {
  "sso_provider": "Ping",
  ...
},
"evidence": [
  {
    "property_path": "identity.sso_provider",
    "source": "risk_assessment",
    "ref": "Risk Assessment p.4 — section 3.2 Identity",
    "excerpt": "Application is onboarded to Ping SSO; no alternate login paths exist.",
    "extracted_at": "2026-05-05T14:23:00Z"
  }
]
```

If you cannot find evidence for a property, leave the property null. Do not fabricate provenance.

### Rule 3: Numeric values use the units declared in the schema

The schema declares units in property names: `rto_hours`, `rpo_minutes`, `session_timeout_idle_min`, `session_timeout_absolute_hr`, `kms_rotation_days`. If the source uses different units, convert.

## Common pitfalls

**Don't conflate "declared" with "verified."** The Risk Assessment is the team's *declaration* of controls. Setting `identity.sso_app_onboarded = true` based on the Risk Assessment is fine — the property says "the team declares this is true." Stage 2 (question answering) will combine this with other sources and apply judgment.

**Don't make up structured values from unstructured prose.** If the source describes the architecture as "we use containers" but doesn't say multi-AZ vs single-AZ, leave `resilience.multi_az_deployed = null`. Don't guess.

**Don't average across sources.** If the Risk Assessment says MFA is required but ARB suggests there are some bypass paths, set both properties truthfully and let the contradiction surface in the evidence trail. Don't paper over inconsistencies.

**Don't extract from source artefacts older than 12 months without flagging.** Add a note in `metadata` if any source is stale: `metadata.stale_sources: ["risk_assessment dated 2024-09-12 is older than 12 months"]`.
