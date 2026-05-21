# Verification + Spot-Audit Workflow

This file describes how a pre-filled checklist is verified by the application team and spot-audited by the App Health Check team.

---

## Why verification exists

AI pre-fills are the **starting point**, not the answer. Every element in a pre-filled checklist must be reviewed by the application team before it counts. The verification step:

- Catches AI hallucination (claims that aren't supported by the sources)
- Catches stale data (sources older than the current state of the app)
- Catches AI optimism (a confident Yes that's actually Partial or No on closer inspection)
- Preserves human accountability (compliance audits trace back to a named person, not "the AI")

## What the app team sees

A pre-filled v0.9 Checklist Excel arrives in the team's SharePoint folder. The team opens it. They see:

- Every Response cell already populated (Yes / No / N/A / Not Sure)
- Every Link / Brief Note cell populated with the AI's evidence (a quote, a file path, a system reference)
- A hidden Confidence column carrying High / Medium / Low (rendered as green / amber / coral via conditional formatting)
- The Scorecard live-calculating their per-question and overall levels

The Confidence colour-coding tells the team where to spend their attention:

- **Green** (High confidence) → visual sanity check; rare amendments needed
- **Amber** (Medium confidence) → re-check the evidence; confirm or amend
- **Coral** (Low confidence) → already auto-downgraded to Not Sure by the pipeline; team must answer definitively

## The verification rules

Three non-negotiable rules govern the verification step:

### Rule 1: Every Yes must have evidence

A Yes claim without a citation in the Link / Brief Note column is invalid. The pipeline pre-checks this and auto-downgrades evidence-less Yes responses to Not Sure. The app team must add a real citation before re-asserting Yes.

Acceptable evidence: a SharePoint document link + section, a Confluence page link, a GitHub file path + line range, a ServiceNow ticket reference, a system screenshot uploaded to the team's evidence folder.

Not acceptable: "yes, we do this" with no source.

### Rule 2: Not Sure is a real answer

A team can legitimately mark an element Not Sure. This isn't a failure — it's a flag for follow-up. The Scorecard surfaces all Not Sure responses in the Justification column with "follow-up needed" so the App Health Check team knows what's outstanding.

Teams should not default-fill Not Sure as a way to avoid answering. The App Health Check team will look for patterns (one team marking >30% Not Sure is a red flag for engagement, not honesty).

### Rule 3: N/A requires justification

Marking an element N/A requires a one-line reason in the Notes column. Acceptable: "No mobile component; Mobile Application Security checklist does not apply." Not acceptable: blank or "doesn't apply."

## What the App Health Check team does (spot-audit)

After the app team submits their verified workbook, the App Health Check team conducts a randomised 10% spot-audit:

- Sample 3 elements per app (random across questions)
- For each sampled element, open the cited evidence
- Verify the evidence actually supports the claim
- Score: pass (evidence supports the claim) / fail (evidence missing, contradicts, or doesn't say what was claimed)

If a fail rate is found above ~10%, the team's submission is rejected and a re-review is triggered.

## How to challenge a pre-fill

If a team disagrees with a pre-fill (e.g. AI says No but team knows it's Yes):

1. **Amend the Response cell** to the correct value.
2. **Replace the Note** with the team's evidence supporting the new value.
3. **Leave the original AI evidence as a comment** if useful for context.

If a team thinks a pre-fill is correct but the evidence is wrong:

1. **Keep the Response value.**
2. **Replace the Note** with stronger evidence.

If a team thinks the rubric question itself is mis-applied to their app (e.g. their app is mobile-only and Q11 OS/Container is N/A):

1. **Mark all elements at that level N/A** with a one-line reason in each Note.
2. The Scorecard will compute the dimension correctly with the N/A handling.

## Confidence calibration check (App Health Check team)

After every 10 apps, the App Health Check team reviews the confidence-vs-accuracy calibration:

- For elements where the AI claimed High confidence + Yes — what % were actually correct after team review?
- For Medium confidence — what %?
- For Low confidence — what % did the team change to a different answer?

Expected calibration:
- High confidence Yes → ≥85% accurate
- Medium confidence Yes → 60-85% accurate
- Low confidence (already downgraded to Not Sure) → app team answers ≥80% of the time (i.e. the Not Sure flag was correctly placed)

If High-confidence accuracy drops below 70%, the AI's prompt or the source data quality has degraded. Pause the pipeline and investigate.

## Compliance audit trail

Every AI call that produced a pre-fill is logged with: timestamp, model + version, prompt hash, response hash, confidence, evidence references. Stored alongside the pre-filled workbook in the SharePoint folder.

If compliance asks "why did the AI say Q01-E07 was Yes?" — the audit log shows the exact prompt, the exact response, and the evidence quote. The chain of reasoning is reproducible.

## When NOT to use the verification workflow

If an application team uses the v0.9 Checklist *without* AI pre-fill (full manual workflow), the spot-audit rule still applies — the App Health Check team samples 3 elements per app and confirms the evidence. But there's no confidence-calibration check because there's no AI to calibrate.
