# Installing and running inside ONA (GIC tenant)

This document walks through getting the pre-fill pipeline running inside GIC's
ONA (Claude Opus) environment, end-to-end, for a single application.

> **Audience.** App Health Check workstream operator. Assumes shell access to a
> Linux workstation or jumpbox that can (a) reach ONA's API endpoint, and (b)
> reach GitHub Enterprise (if GitHub extraction is required).

## 1. Prerequisites

| Requirement                                         | Why                                            |
|----------------------------------------------------|------------------------------------------------|
| Python ≥ 3.10                                       | Pipeline language                              |
| Network reachability to ONA's messages endpoint     | Stage 1 + Stage 2 LLM calls                    |
| Network reachability to GitHub (Enterprise) API     | Optional — only if you want GitHub extraction  |
| ONA service account API key (or bearer token)       | Authenticates to ONA                           |
| GitHub PAT with `repo` + `metadata` read scopes     | Optional — for branch protection / workflows   |

## 2. Get the repo onto the workstation

The pipeline source lives under `06-PreFill-System/` in the App Health Check
working folder. Copy that folder onto the workstation (e.g. via SFTP, a
shared drive, or `git clone` if it's been pushed to a GIC-internal repo).

```
/opt/gic-app-health/
├── skills/
│   ├── gic-app-health-check/
│   └── gic-source-extractors/
└── pipeline/
    └── ...
```

## 3. Install the pipeline

```bash
cd /opt/gic-app-health/pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

(If you want the Anthropic SDK route for any reason: `pip install -e .[anthropic]`.)

## 4. Configure environment

Create `/opt/gic-app-health/.env` (or set in your shell):

```bash
# Provider
export GIC_LLM_PROVIDER=ona
export GIC_LLM_MODEL=claude-opus-4
export GIC_LLM_ENDPOINT=https://ona.internal/v1/messages   # adjust to your real ONA URL
export GIC_LLM_API_KEY=...                                  # ONA bearer token
export GIC_LLM_MAX_TOKENS=4096
export GIC_LLM_TEMPERATURE=0.0

# Skills (auto-detected if your layout matches /opt/gic-app-health)
export GIC_SKILLS_ROOT=/opt/gic-app-health/skills

# GitHub (optional)
export GIC_GITHUB_TOKEN=ghp_...
export GIC_GITHUB_API_URL=https://github.gic.internal/api/v3   # or https://api.github.com

# Policy gates (recommended defaults)
export GIC_REQUIRE_EVIDENCE_FOR_YES=true
export GIC_LOW_CONFIDENCE_TO_NOT_SURE=true
```

### 4a. ONA payload shape

The default `ONAClient` posts an Anthropic-Messages-compatible payload:

```json
{
  "model": "claude-opus-4",
  "max_tokens": 4096,
  "temperature": 0.0,
  "system": "...",
  "messages": [{"role": "user", "content": "..."}]
}
```

with `Authorization: Bearer <key>`.

If your ONA tenancy uses a different shape or header (e.g. `x-api-key` instead
of `Authorization`, or a wrapper around the payload), edit
`pipeline/src/prefill/llm_client.py::ONAClient.call()` accordingly. There's a
commented `x-api-key` line right next to the bearer header, ready to enable.

### 4b. Sanity check the wiring

A dry-run end-to-end test never touches the LLM:

```bash
mkdir -p /tmp/sample_sources /tmp/sample_out
gic-prefill --dry-run \
  --sources-dir /tmp/sample_sources \
  --template /opt/gic-app-health/templates/Ollion_GIC_App_Health_Check_v0.9-Checklist.xlsx \
  --output-dir /tmp/sample_out
```

You should get four files in `/tmp/sample_out/`. The `Checklist_prefilled.xlsx`
will have all 332 responses set to "Not Sure" with a "dry-run stub" note. The
`audit_log.json` should show `llm_calls: 0`.

Then run a real ONA call:

```bash
unset GIC_DRY_RUN   # in case it was set
gic-prefill \
  --sources-dir /tmp/sample_sources \
  --template /opt/gic-app-health/templates/Ollion_GIC_App_Health_Check_v0.9-Checklist.xlsx \
  --output-dir /tmp/sample_out
```

If ONA responds and the workbook still gets written, the wiring is good.

## 5. Run against one application

For a real app, drop its sources into a folder following this layout:

```
/opt/gic-app-health/runs/payments-svc/sources/
  risk_assessment.pdf
  arb_decisions.docx
  arb_diagram.pptx
  confluence_runbook.html
  sharepoint_architecture.docx
  github.json
```

(File classification is by filename — see `pipeline/src/prefill/extractors/classifier.py`.)

Then:

```bash
gic-prefill \
  --sources-dir /opt/gic-app-health/runs/payments-svc/sources \
  --template   /opt/gic-app-health/templates/Ollion_GIC_App_Health_Check_v0.9-Checklist.xlsx \
  --output-dir /opt/gic-app-health/runs/payments-svc/out
```

Outputs land in `/opt/gic-app-health/runs/payments-svc/out/`:

```
app_facts.json            ← Stage 1 merged facts
responses.json            ← Stage 2 element responses (332 entries)
Checklist_prefilled.xlsx  ← Stage 3 populated workbook
audit_log.json            ← Provider/model/prompt-hash/response-hash per LLM call
```

## 6. Hand the workbook to the app team

The pre-filled `Checklist_prefilled.xlsx` is intended as a **starting point**,
not a final answer. The app team should:

1. Review every "Yes" response — pre-fill is conservative but not perfect.
2. Resolve every "Not Sure" — these are explicitly flagged for them to confirm.
3. Add additional evidence links in the "Link or Brief Note" column where
   appropriate.

Anything the pipeline auto-downgraded carries a `[auto-downgrade: ...]` tag in
the Note column so the team can see why it landed on Not Sure.

## 7. Running the test suite

```bash
cd /opt/gic-app-health/pipeline
pip install -e .[dev]
pytest -v
```

You should see `32 passed` if installation is correct.

## 8. Troubleshooting

| Symptom                                              | Likely cause / fix                                                  |
|------------------------------------------------------|---------------------------------------------------------------------|
| `Configuration error: Skills root does not exist`   | Set `GIC_SKILLS_ROOT` to the absolute path of the `skills/` folder  |
| ONA returns 401 / 403                                | Wrong `GIC_LLM_API_KEY`, or auth header should be `x-api-key`      |
| ONA returns 400 with "model" complaint               | `GIC_LLM_MODEL` doesn't match what ONA exposes — ask ONA team       |
| ONA returns response, but JSON parsing fails        | `parse_json_from_llm()` is tolerant; check `audit_log.json` raw text |
| GitHub extraction silently produces empty facts     | Missing `GIC_GITHUB_TOKEN`, or wrong `GIC_GITHUB_API_URL` for GHES  |
| Every response is "Not Sure"                         | Policy gates conservative; consider relaxing `GIC_LOW_CONFIDENCE_TO_NOT_SURE` |
| Some elements unmatched in populator log            | Element-row counting in template drifted from rubric; check `parent_qid` |

## 9. Updating the rubric or schema

The pipeline reads from `skills/` at runtime. To change the rubric without
touching code:

- **Add a question or element:** edit
  `skills/gic-app-health-check/assets/questions.json`
- **Tune level definitions:** edit
  `skills/gic-app-health-check/assets/level-definitions.json`
- **Add a new source type:** create a new extractor under
  `pipeline/src/prefill/extractors/`, register it in `extractors/__init__.py::EXTRACTORS`,
  and add a matching guide under `skills/gic-source-extractors/references/`

Re-run the pipeline. No code change required for rubric edits.
