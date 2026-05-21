# Extracting from Confluence Support Docs

## What this source provides

Confluence support docs are operational artefacts: SOPs per team (ServiceDesk, End User Infra, Compute, Cloud, IAM Ops), runbooks, vendor support details, certificate renewal procedures, UAT sign-off records, operational handover sign-offs, knowledge-base pages, post-incident reviews.

These documents typically arrive as a collection of 5–20 PDFs exported from Confluence. Each PDF is one Confluence page.

## What to extract per schema area

### identity
- `identity.breakglass_procedure_documented` — True if a breakglass SOP exists
- `identity.lifecycle_iga_provider` — confirmed from access-review SOPs
- `identity.quarterly_review_evidence[]` — references to past quarterly review records

### operations (this is the primary source)
- `operations.account_list_complete` — derived from account-list SOP completeness
- `operations.account_list_covers[]` — list of account types covered (breakglass, service, privileged, application)
- `operations.acm_approvals_present` — True if ACM approval records are referenced
- `operations.sops_per_team` — dict keyed by team name with True/False for SOP presence
- `operations.vendor_support_24x7_contacts` — True if vendor support page lists 24x7 contacts
- `operations.cert_398d_max_validity` — True if cert renewal SOP enforces 398-day limit
- `operations.uat_sign_off_present` — True if a UAT sign-off page exists
- `operations.operational_handover_complete` — True if a handover sign-off page exists

### resilience
- `resilience.dr_plan_documented` — True if DR plan page is present
- `resilience.dr_plan_signed_off` — True if DR plan has explicit sign-off block
- `resilience.dr_tested_within_12m` — derived from DR test records
- `resilience.dr_test_sign_off_date` — date from DR test record

### observability
- `observability.log_sources_documented` — True if log-source inventory exists
- `observability.privileged_activity_monitored[]` — list of monitored activities from security-monitoring SOP

### appsec
- `appsec.patch_management_documented` — True if patch SOP exists

## Extraction prompt pattern

Since Confluence support docs come as multiple PDFs, the extractor should iterate:

```
For each PDF in the support-docs bundle:

You are extracting structured data from a GIC Confluence-exported support document.

First, identify what type of document this is:
- SOP (and for which ops team)
- Runbook
- Vendor support contact list
- Certificate renewal procedure
- UAT sign-off record
- Operational handover record
- DR plan
- Post-incident review
- Knowledge base article
- Other

Then extract only the fields relevant to that document type. Set null for
properties not addressed.

For every property you set, add an evidence entry with the page reference
and a direct quote.

Schema: <embed relevant slices based on document type>

Document content:
<PDF text>

Return JSON.
```

After all PDFs are processed, **merge the partial extractions** into one per-app JSON.

## Merging rule for conflicting values

When two Confluence pages disagree (e.g. one says vendor support is 24x7, another doesn't mention it), prefer the more recent document. Record the conflict in `metadata`:

```json
"metadata": {
  ...
  "extraction_conflicts": [
    {
      "property": "operations.vendor_support_24x7_contacts",
      "sources_disagree": ["confluence/vendor-support-2024-03.pdf says yes", "confluence/vendor-support-2023-08.pdf is silent"],
      "resolution": "Used the more recent document"
    }
  ]
}
```

## Provenance examples

```json
{
  "property_path": "operations.uat_sign_off_present",
  "source": "confluence",
  "ref": "confluence/Apollo-UAT-Sign-off.pdf — p.1",
  "excerpt": "UAT testing completed and signed off by business owner J. Wong on 2026-02-18.",
  "extracted_at": "2026-05-05T14:23:00Z"
},
{
  "property_path": "resilience.dr_test_sign_off_date",
  "source": "confluence",
  "ref": "confluence/Apollo-DR-Test-2025.pdf — Final Sign-off Section",
  "excerpt": "DR test executed 2025-11-12; restored within 3h RTO target; signed off by App Owner + DR Coordinator on 2025-11-15.",
  "extracted_at": "2026-05-05T14:23:00Z"
}
```

## Caveats

- Confluence exports can have stale content if pages aren't kept current. Look for "last modified" or sign-off dates on each PDF. Pages older than 12 months should be treated with caution.
- A missing SOP for one ops team doesn't mean ALL SOPs are missing. Set `operations.sops_per_team` as a dict, with each team's SOP presence individually recorded.
- Where Confluence pages are exported as scanned PDFs (rare but possible), OCR may be needed. If extraction quality is low, leave properties null and flag the source as needing OCR.
