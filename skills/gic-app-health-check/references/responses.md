# Response Model — Yes / No / N/A / Not Sure

Each of the 332 criteria elements is answered with one of four states.

## The four states

### Yes
The criteria element is true for the application today. The team has direct knowledge that this is the case. A Yes claim must be backed by an evidence quote, link, or file reference in the Link / Brief Note column.

**Scoring:** counts as met for the element's level.

### No
The criteria element is not currently met. The team knows the gap exists.

**Scoring:** counts in the denominator, does not count as met. For L1 (gap) elements: a Yes here forces the question to L1 Developing. For L2/L3/L4 elements: a No prevents the question from reaching that level.

### N/A
The criteria element does not apply to this application. Justification must be provided in Notes (e.g. "No mobile component; Mobile Application Security checklist not applicable").

**Scoring:** excluded from the denominator. A question with all-N/A elements at a level is treated as having no requirement at that level.

### Not Sure
The team does not know the answer and needs to verify before submitting. This is explicitly NOT a "soft No" — it's a flag for follow-up.

**Scoring:** treated like No in the level calculation (counts in denominator, does not count as met). But surfaced separately in the Justification text on the Scorecard as "Not Sure: N (follow-up needed)" so the App Health Check team can flag uncertainty.

**Important:** "Not Sure" prevents an honest team from being penalised for declaring uncertainty. A team that marks all gaps as Not Sure rather than No still gets the same scoring outcome — they can't game the score by being vague.

## Why "Not Sure" is a distinct state

In v0.8 the rubric had three states (Yes / No / N/A). Andre's v0.9 feedback added Not Sure because teams in early field use repeatedly asked "what do I do if I genuinely don't know?" — and were defaulting to No (penalising themselves) or skipping (leaving blanks). Not Sure gives them a clean way to flag uncertainty without hiding it as a No, and gives the App Health Check team visibility into what needs follow-up.

## How to evaluate a response

When pre-filling responses or verifying them:

1. **Read the element text.** What is it asking? Is the question a positive ("does X exist?") or a gap statement ("is X missing?")?
2. **Check the supplied evidence.** Is there a direct quote, file path, or system reference?
3. **Decide:**
   - Direct affirming evidence → Yes
   - Direct contradicting evidence → No
   - The element clearly doesn't apply → N/A (with justification)
   - Evidence is ambiguous, missing, or you'd have to guess → Not Sure

4. **For Yes responses:** the evidence MUST be cited in the Link / Brief Note column. AI-generated Yes responses without evidence should be auto-downgraded to Not Sure.

## L1 elements vs L2/L3/L4 elements

L1 elements are **gap statements** — they describe what's wrong. For these, a Yes acknowledges the gap. Example: "Are there bypass paths to SSO still in place?" — Yes here means the app has bypass paths (a gap).

L2/L3/L4 elements are **positive practice statements** — they describe what's right. For these, a Yes confirms the practice is in place. Example: "Has the application been fully onboarded to Ping SSO with no alternate login paths?" — Yes here means the app meets the baseline.

Any L1 element ticked Yes forces the question to L1 Developing regardless of L2/L3/L4 responses. This rewards honest acknowledgement of gaps — a team that admits a gap can't be incorrectly scored as Healthy.

## Default response

Blank (unanswered) is **not** the same as Not Sure. A blank cell means the team hasn't engaged with the element yet. The scoring treats unanswered as incomplete:

- If any element in a question is unanswered → the question's level is "Awaiting completion"
- A question with all elements answered (Yes/No/N/A/Not Sure) produces a definitive level

Pre-fill workflows MUST produce one of the four states for every element. If the AI cannot determine an answer, it should return Not Sure with a Note explaining why ("source documents do not address this element").
