# GIC Application Health Check — Pre-Fill System

End-to-end system for automatically pre-filling the v0.9 Checklist Excel from
an application's source artefacts (Risk Assessment, ARB, Confluence, GitHub,
SharePoint).

## What's in this folder

```
06-PreFill-System/
├── skills/
│   ├── gic-app-health-check/         # Rubric skill (32 questions × 332 elements)
│   └── gic-source-extractors/        # Source extraction skill (schema + per-source guides)
└── pipeline/
    ├── pyproject.toml
    ├── src/prefill/
    │   ├── config.py                 # Env-driven configuration
    │   ├── llm_client.py             # ONA / Anthropic / Mock clients
    │   ├── skills_loader.py          # Reads skill content from disk
    │   ├── orchestrator.py           # CLI + 3-stage runner
    │   ├── extractors/               # Stage 1: per-source-type extractors
    │   ├── answering/                # Stage 2: per-question answerer
    │   └── populator/                # Stage 3: Excel writer
    └── tests/                        # 32 tests
```

## Three stages

1. **Stage 1 — Extraction.** Walk `sources_dir`, classify each file, dispatch
   to the matching source extractor (which calls the LLM with the
   `gic-source-extractors` skill content), then merge per-source AppFacts.
2. **Stage 2 — Answering.** For each of the 32 questions in
   `gic-app-health-check`, slice the merged AppFacts down to relevant parts,
   build a per-question prompt, call the LLM, and apply policy gates
   (downgrade evidence-less Yes → Not Sure, downgrade Low confidence → Not Sure).
3. **Stage 3 — Population.** Open the v0.9 Checklist template, walk
   `03_Assessment` row by row, write Response + Note for every criteria element.

## Quick start

See `INSTALL_ONA.md` for the full GIC/ONA install guide.

For local development against the Anthropic API:

```bash
cd pipeline
pip install -e .[anthropic]
export GIC_LLM_PROVIDER=anthropic
export GIC_LLM_API_KEY=sk-ant-...
export GIC_LLM_MODEL=claude-opus-4-6
gic-prefill \
  --sources-dir ./sample_app/sources \
  --template ../02-Questionnaire/v0.9/Ollion_GIC_App_Health_Check_v0.9-Checklist.xlsx \
  --output-dir ./out
```

For a no-LLM smoke test (writes all responses as Not Sure):

```bash
gic-prefill --dry-run \
  --sources-dir ./empty_sources \
  --template ../02-Questionnaire/v0.9/Ollion_GIC_App_Health_Check_v0.9-Checklist.xlsx \
  --output-dir ./out
```

## Running tests

```bash
cd pipeline
pip install -e .[dev]
pytest -v
```

All 32 tests should pass.

## Outputs

The pipeline writes four files into `--output-dir`:

| File                    | Purpose                                                                |
|-------------------------|-------------------------------------------------------------------------|
| `app_facts.json`        | Stage 1 output — merged AppFacts (one app, all sources)                |
| `responses.json`        | Stage 2 output — flat list of 332 element responses + confidence + refs |
| `Checklist_prefilled.xlsx` | Stage 3 output — populated v0.9 Checklist template                  |
| `audit_log.json`        | Per-call audit trail (provider, model, prompt_hash, response_hash)     |

## Source bundle layout

For one application, prepare a folder like:

```
sources/
  risk_assessment.pdf            ← classified as risk_assessment
  arb_decisions.docx             ← classified as arb
  arb_diagram.pptx               ← classified as arb
  confluence_runbook.html        ← classified as confluence
  sharepoint_architecture.docx   ← classified as sharepoint
  github.json                    ← manifest of repos (see below)
```

GitHub manifest (`github.json`):

```json
{
  "repos": [
    {"owner": "gic-internal", "repo": "payments-svc"},
    {"owner": "gic-internal", "repo": "payments-web"}
  ]
}
```

## Configuration (environment variables)

| Variable                          | Default                                | Purpose                                |
|-----------------------------------|----------------------------------------|-----------------------------------------|
| `GIC_LLM_PROVIDER`                | `mock`                                 | `ona` / `anthropic` / `mock`            |
| `GIC_LLM_MODEL`                   | `claude-opus-4`                        | Model name                              |
| `GIC_LLM_ENDPOINT`                | `https://ona.internal/v1/messages`     | ONA endpoint                            |
| `GIC_LLM_API_KEY`                 | _(unset)_                              | Bearer token / API key                  |
| `GIC_LLM_MAX_TOKENS`              | `4096`                                 | Per-call max tokens                     |
| `GIC_LLM_TEMPERATURE`             | `0.0`                                  | Deterministic by default                |
| `GIC_GITHUB_TOKEN`                | _(unset)_                              | GitHub PAT for repo metric collection  |
| `GIC_GITHUB_API_URL`              | `https://api.github.com`               | Override for GHES                       |
| `GIC_REQUIRE_EVIDENCE_FOR_YES`    | `true`                                 | Auto-downgrade evidence-less Yes → Not Sure |
| `GIC_LOW_CONFIDENCE_TO_NOT_SURE`  | `true`                                 | Auto-downgrade Low confidence → Not Sure |
| `GIC_DRY_RUN`                     | `false`                                | Skip all LLM calls; produce stubs       |
| `GIC_SKILLS_ROOT`                 | _(auto-detected)_                      | Override skills folder location         |

## Architecture notes

The pipeline never imports a vendor LLM SDK directly — every LLM call goes
through `llm_client.LLMClient`. Three concrete implementations exist:

- `ONAClient` — HTTP POST against an Anthropic-Messages-API-compatible endpoint
- `AnthropicClient` — uses the `anthropic` SDK
- `MockLLMClient` — returns canned responses for offline testing

Swapping providers is one environment variable change.

Skill content is the canonical source of truth. The pipeline doesn't
hardcode rubric content — it reads it from
`skills/gic-app-health-check/` at runtime via `skills_loader.py`. Update the
skill and the pipeline picks it up next run.

Every LLM call records a `prompt_hash` + `response_hash` into the audit
log so the workstream can reconstruct exactly what was asked and what came
back for any pre-filled answer.
