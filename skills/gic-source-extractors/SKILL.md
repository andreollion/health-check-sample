---
name: gic-source-extractors
description: |
  Use this skill when extracting structured per-application data from raw source artefacts — Risk Assessment PDFs, Architecture Review Board (ARB) outputs, Confluence support documents, GitHub repositories, or SharePoint documents. The skill defines the canonical per-app JSON schema (matching the GIC App Health Check rubric) and provides per-source-type extraction instructions describing what fields to look for, where to find them, and how to record provenance. Used by Stage 1 of the pre-fill pipeline. Do NOT use for answering rubric questions (that's gic-app-health-check) or for generic document reading.
metadata:
  schema_version: "0.9"
  programme: "GIC Cloud Migration"
---

# GIC Source Extractors — Schema + Per-Source Instructions

This skill turns raw source artefacts into a structured per-application JSON record. It is Stage 1 of the pre-fill pipeline. The resulting JSON is then consumed by Stage 2 (question answering, which uses `gic-app-health-check`).

The skill is the canonical reference for: what the per-app data structure looks like (the schema), how to extract it from each source type, and how to preserve provenance so every property is traceable.

---

## When to use

- Extracting structured data from a Risk Assessment PDF
- Extracting structured data from an ARB / Architecture output PDF
- Extracting structured data from Confluence support documentation
- Extracting structured data from a GitHub repository (code, IaC, workflows)
- Extracting structured data from SharePoint documents
- Designing or validating the per-app JSON schema

## When NOT to use

- Answering rubric questions (use `gic-app-health-check` instead)
- Generic document parsing (this skill is scoped to GIC source artefacts)
- Producing checklists, reports, or executive artefacts

## What's in this skill

| Topic | Reference file | Load when |
|---|---|---|
| Per-app JSON schema | `references/schema.md` | Designing or validating extraction output |
| How to extract from Risk Assessment PDFs | `references/risk-assessment.md` | Working with Risk Assessment submission documents |
| How to extract from ARB PDFs | `references/arb.md` | Working with Architecture Review Board outputs |
| How to extract from Confluence support docs | `references/confluence.md` | Working with Confluence-exported documentation |
| How to extract from GitHub repos | `references/github.md` | Working with GitHub repository content |
| How to extract from SharePoint docs | `references/sharepoint.md` | Working with SharePoint document exports |
| Provenance discipline | `references/provenance.md` | Always — every property MUST carry provenance |

Structured assets:

- `assets/schema.json` — the canonical per-app JSON schema (also embedded in `references/schema.md`)

## Common operations

### Extract from a Risk Assessment PDF

Read `references/risk-assessment.md`. The instructions describe the typical layout of a GIC Risk Assessment submission, the fields to look for (classification, RTO, RPO, declared vendors, criticality tier, SCR rating, etc.), and how to map them into the schema.

### Extract from a GitHub repository

Read `references/github.md`. GitHub extraction is highest-fidelity because it can use the REST API directly (branch protection settings, workflow YAMLs, code-scanning alerts) — no LLM needed for most fields.

### Validate extraction output

Compare the produced JSON against `assets/schema.json`. Every property in the schema is optional in the output (sources may be silent on a field), but every present property must conform to the schema's type + format.

### Preserve provenance

Read `references/provenance.md`. The rule: every property that is set MUST carry a provenance reference — a source type, a document or file ref, and an excerpt or quote. This is non-negotiable; provenance is what makes the downstream verification step possible.

## How this skill composes with others

- **`gic-source-extractors` (this skill)** → defines what to extract and how → output is per-app JSON
- **`gic-app-health-check`** → defines what to ask of the per-app JSON → output is element responses
- **The pre-fill pipeline (code)** → orchestrates both stages

Each stage references the corresponding skill but the orchestration logic lives in code.

## Schema version

This skill encodes **v0.9** of the schema. Aligned with the v0.9 rubric. Major schema changes bump the skill's major version.
