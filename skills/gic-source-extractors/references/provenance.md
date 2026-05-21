# Provenance Discipline

Provenance is the chain that ties every extracted value back to its source. Without it, the downstream verification step is blind — the App Health Check team can't check whether a property is correct because they can't find the source statement.

This is non-negotiable. Provenance is the difference between AI extraction that holds up under audit and AI extraction that doesn't.

---

## The rule

**For every property in the per-app JSON that is set to a non-null value, there MUST be at least one corresponding entry in the top-level `evidence` array.**

The evidence entry shape:

```json
{
  "property_path": "<JSONPath to the property, e.g. 'identity.mfa.users'>",
  "source": "<one of: risk_assessment | arb | confluence | github | sharepoint>",
  "ref": "<page number, file path, URL, ticket ID, or other locator>",
  "excerpt": "<direct quote or summary of the supporting evidence>",
  "extracted_at": "<ISO 8601 timestamp>"
}
```

## What good provenance looks like

**Good:**
- `ref: "Risk Assessment p.4 — section 3.2 Identity"` with `excerpt: "Application is onboarded to Ping SSO with no alternate login paths."`
- `ref: "GitHub API: GET /repos/gic/apollo/branches/main/protection"` with `excerpt: "required_pull_request_reviews.required_approving_review_count = 2"`
- `ref: ".github/workflows/ci.yml — lines 18-25"` with `excerpt: "uses: github/codeql-action/init@v3"`

**Bad:**
- `ref: "Risk Assessment"` with no page or section — too vague
- `excerpt: "yes"` — not a quote, not informative
- `ref: ""` with no excerpt — empty provenance is no provenance
- `excerpt: "Inferred from context"` — provenance is for stated facts, not inferences

## When inference is unavoidable

Sometimes you have to infer — e.g. "the document doesn't explicitly say multi-AZ but the architecture diagram shows two AZs." If you infer:

1. Set the property value as you would normally.
2. Add provenance with `excerpt` clearly marked as an inference: `"INFERRED: Architecture diagram shows two AZs (ap-southeast-1a, ap-southeast-1b); explicit 'Multi-AZ' label is absent."`
3. Lower the confidence (this connects to the confidence model in `gic-app-health-check`).

Inferences are valid evidence but should be flagged so the verifier knows to check more carefully.

## When you cannot find evidence

Two cases:

**Case 1: The source is silent on the property.**
Leave the property `null`. Do not add provenance. Stage 2 will treat null as "Not Sure" when generating responses.

**Case 2: You found a statement but it's ambiguous or contradicts other sources.**
Set the property to your best read. Add provenance with the excerpt verbatim. Add a second evidence entry pointing to the conflicting source. Let Stage 2 see the conflict and decide how to handle it.

## Multiple sources for one property

A property can have multiple evidence entries — that's actively useful for cross-verification:

```json
{
  "property_path": "identity.mfa.aws_console",
  "source": "risk_assessment",
  "ref": "p.4 section 3.2",
  "excerpt": "MFA enforced for all AWS console access",
  "extracted_at": "..."
},
{
  "property_path": "identity.mfa.aws_console",
  "source": "github",
  "ref": "GitHub API: AWS IAM policy 'force-mfa'",
  "excerpt": "All users have policy enforcing aws:MultiFactorAuthPresent for console actions",
  "extracted_at": "..."
}
```

Two sources independently confirming a property is much stronger than one.

## Provenance for derived properties

Some properties are computed from other extractions. For example, `data_protection.data_stores[0].kms_managed = true` might be derived from "the architecture says we use AWS RDS" + "the Risk Assessment says we use AWS KMS." In this case:

- Add provenance entries for each underlying source statement
- The combination is the justification

Don't fabricate a single provenance entry for a derived value. Show the components.

## Timestamps

Always include `extracted_at`. This timestamp is what allows the verification step to detect when extractions are stale. If a property was extracted from a document that has since been updated, the timestamp helps flag that the property may be out of date.

## Auditability

The `evidence` array is the audit trail. A compliance reviewer can take any property, find its evidence entries, navigate to the cited sources, and confirm the extraction was justified. Without this trail, the AI's outputs are unverifiable.

If your extractor function ever finds itself setting a property without provenance — stop. That's a bug in the extractor. Either:
- The property shouldn't be set (leave it null)
- Or the provenance is being lost somewhere in the flow

Fix the bug; don't suppress the requirement.

## Pre-Stage 2 validation

Before passing per-app JSON to Stage 2 (question answering), the pipeline should validate:

1. Every non-null property has at least one evidence entry pointing to it.
2. Every evidence entry's `property_path` resolves to a property in the JSON.
3. Every `source` value is one of the five allowed source types.
4. Every `ref` is non-empty.
5. Every `excerpt` is non-empty and at least 10 characters long.

Validation failures should abort the pipeline (not just log a warning). Bad provenance flows downstream as misleading evidence in the pre-filled checklist.
