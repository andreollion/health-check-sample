# Scoring — Level Algorithm, Confidence Model, Justification Format

## The level algorithm

Each question's level is computed from its element responses. The algorithm is deterministic — same input always produces same output.

### Per-question level

For a given question Q with elements at levels L1 / L2 / L3 / L4:

```
1. Compute counts per level (excluding N/A):
   - n_L1_yes = count of L1 (gap) elements with response "Yes"
   - n_L1_total = count of L1 elements
   - n_L1_na = count of L1 elements with response "N/A"
   - n_L1_eff = n_L1_total - n_L1_na

   Same for L2, L3, L4.

2. Check for L1 gap acknowledgement:
   IF n_L1_yes > 0:
       question_level = "L1 Developing"
       RETURN

3. Check L2 baseline threshold:
   l2_ratio = n_L2_yes / n_L2_eff (default threshold: 100%)
   IF l2_ratio < threshold_L2:
       question_level = "L1 Developing"
       RETURN

4. Check L3 threshold:
   l3_ratio = n_L3_yes / n_L3_eff (default threshold: 100%)
   IF l3_ratio < threshold_L3:
       question_level = "L2 Healthy"
       RETURN

5. Check L4 threshold:
   l4_ratio = n_L4_yes / n_L4_eff (default threshold: 100%)
   IF l4_ratio < threshold_L4:
       question_level = "L3 Managed"
       RETURN

6. Otherwise:
   question_level = "L4 Optimised"
```

### Per-dimension level

```
dimension_level = min(question_level for question in dimension)
```

The lowest question level in a dimension is the dimension's level.

### Overall app level

```
app_level = min(dimension_level for dimension in all_dimensions)
```

The lowest dimension level is the app's overall level.

### "Lowest wins" rationale

The rule "lowest dimension → overall" reflects the principle that an app is only as healthy as its weakest dimension. A team can't earn a Healthy score by averaging strengths against weaknesses; specific weaknesses must be acknowledged.

### N/A handling

Elements marked N/A are excluded from the denominator. If a question has all-N/A elements at a given level, that level is treated as having no requirement.

If a question has all-N/A elements across L2/L3/L4, the question is excluded from level placement (treated as "Not assessed in this dimension").

### Not Sure handling

Not Sure responses are treated like No in scoring (counted in denominator, not as met). They do not exclude an element from the count. This prevents teams from gaming the score by marking uncertain elements as N/A.

Not Sure is surfaced separately in the Justification (see below) for App Health Check team follow-up.

### Awaiting completion

If any element of a question has a blank response (not Yes / No / N/A / Not Sure), the question's level is reported as "Awaiting completion" rather than computing a partial level. This forces completion before the score is meaningful.

## Configurable thresholds

The default thresholds are 100% per level (all elements at L2 must be Yes to be L2 Healthy, etc.). These thresholds are configurable in the v0.9 Checklist's `04_Rubric_Config` sheet at section 1 ("Element Threshold per Level"). Lower thresholds (e.g. 80%) make levels easier to reach — useful for early cycles when teams are still ramping up. Higher thresholds make grading stricter.

The scoring engine reads thresholds at runtime; the algorithm itself doesn't change.

## Confidence model (for pre-fill workflows)

When AI pre-fills responses, each response carries a confidence rating:

- **High** — directly stated in the source documents; quote is present in the Note column
- **Medium** — inferred from context; not directly stated but reasonable to conclude
- **Low** — ambiguous; should consider returning Not Sure instead

**Auto-downgrade rule:** any Low-confidence Yes/No response should be auto-downgraded to "Not Sure" by the pipeline before writing to the checklist. This prevents the AI from carrying through guesses as confident answers.

A High-confidence response without an evidence quote should also be auto-downgraded. The rule is: every Yes/No claim must have evidence; otherwise it becomes Not Sure.

## Justification format

The Justification text on the Scorecard summarises why each question landed at its level. Format:

```
L1 gaps: N · L2: y/z (Y%) · L3: y/z (Y%) · L4: y/z (Y%)
```

Where:
- `L1 gaps: N` — count of L1 elements ticked Yes (the gap-acknowledgement count)
- `L2: y/z` — number Yes / total effective (excluding N/A) at L2, with % in parentheses
- Same for L3, L4

If there are Not Sure responses, append:

```
· Not Sure: N (follow-up needed)
```

The N is the count across all levels for the question.

### Example justifications

- **Q01 at L2 Healthy:** `L1 gaps: 0 · L2: 6/6 (100%) · L3: 2/4 (50%) · L4: 0/4 (0%)` — all L2 met, partial L3 progress, no L4 work yet.
- **Q01 at L1 Developing (L1 gap acknowledged):** `L1 gaps: 1 · L2: 6/6 (100%) · L3: 4/4 (100%) · L4: 4/4 (100%)` — team has full L4 maturity but acknowledged a baseline gap, so question is L1.
- **Q01 with uncertainty:** `L1 gaps: 0 · L2: 5/6 (83%) · L3: 0/4 (0%) · L4: 0/4 (0%) · Not Sure: 1 (follow-up needed)` — L2 incomplete; one element flagged Not Sure for follow-up.

## Secondary % score (informational)

A weighted percentage is also computed per question, per dimension, and overall:

```
Per-question score = (n_L1*0 + n_L2*1.0 + n_L3*1.25 + n_L4*1.5) / (total_answered * 1.5)
```

This is a trend-tracking metric, not the headline. The headline is the level (L1/L2/L3/L4). The percentage adds nuance — two L2 Healthy apps might score 70% vs 90% depending on how much L3/L4 progress they have.

Multipliers are configurable in the Rubric Config sheet (section 2).
