# `gic-prefill` — Pipeline package

Python package that implements the three-stage pre-fill pipeline. See the parent
folder's `README.md` for system-level docs, and `INSTALL_ONA.md` for the
GIC-tenant install/run guide.

## Install

```bash
pip install -e .                  # core
pip install -e .[dev]             # adds pytest, pytest-cov
pip install -e .[anthropic]       # adds the Anthropic SDK (for non-ONA development)
```

## Run

```bash
gic-prefill --sources-dir ./sources --template path/to/Checklist.xlsx --output-dir ./out
gic-prefill --dry-run ...         # smoke test — no LLM calls
gic-prefill -v ...                # verbose / debug logging
```

## Test

```bash
pytest -v
```

32 tests covering: skill loading, LLM client routing, JSON parsing, source
classifier, AppFacts merger, per-question answerer (incl. policy gates),
Excel populator (against the real v0.9 template), and an end-to-end dry-run.

## Module map

```
src/prefill/
├── config.py              # env-driven Config
├── llm_client.py          # ONAClient / AnthropicClient / MockLLMClient
├── skills_loader.py       # reads skills/ contents
├── orchestrator.py        # main entry point — wires everything
├── extractors/
│   ├── classifier.py      # filename → source_type
│   ├── base.py            # shared prompt builder + JSON parser + file readers
│   ├── risk_assessment.py # PDF Risk Assessment extractor
│   ├── arb.py             # docx/pptx ARB extractor
│   ├── confluence.py      # HTML Confluence extractor
│   ├── github.py          # GitHub REST API extractor
│   ├── sharepoint.py      # SharePoint document extractor
│   └── merger.py          # priority-ordered multi-source merge
├── answering/
│   ├── slicer.py          # AppFacts → per-question fact subset
│   ├── prompts.py         # per-question prompt builder
│   └── answerer.py        # LLM call + policy gates + backfill
└── populator/
    └── excel_writer.py    # writes to v0.9 Checklist template
```
