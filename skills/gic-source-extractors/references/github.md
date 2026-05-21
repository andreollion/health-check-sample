# Extracting from a GitHub Repository

## What this source provides

GitHub is the highest-fidelity source in the bundle because much of it can be read via API rather than inference. Branch protection settings, workflow YAMLs, code-scanning alert states, secret-scanning state, IaC presence, dependency manifests — all directly queryable.

This makes GitHub the **ground truth** for SDLC + AppSec + IaC properties. Treat its outputs as authoritative.

## Extraction approach: API first, LLM as fallback

For most GitHub-derived properties, use the GitHub REST API directly:

| Property | GitHub API endpoint |
|---|---|
| `sdlc.main_protected` | `GET /repos/{owner}/{repo}/branches/main/protection` |
| `sdlc.required_pr_reviews_count` | Same endpoint — `required_pull_request_reviews.required_approving_review_count` |
| `sdlc.required_status_checks` | Same — `required_status_checks.contexts` |
| `sdlc.required_signatures` | Same — `required_signatures.enabled` |
| `sdlc.fully_automated_via_actions` | List workflows: `GET /repos/{owner}/{repo}/actions/workflows`, check for deployment workflow |
| `sdlc.iac_present` | Search for `.tf`, `.cdk.ts`, `template.yml`/`cloudformation` files via `GET /repos/{owner}/{repo}/contents/` |
| `sdlc.iac_tool` | Derived from file types present |
| `appsec.codeql_in_ci` | Check workflows for `github/codeql-action/init`; alternatively check code-scanning alerts |
| `appsec.snyk_in_ci` | Check workflows for `snyk/actions` |
| `appsec.github_secret_scanning_active` | `GET /repos/{owner}/{repo}/secret-scanning/alerts` (presence implies active) |
| `appsec.critical_high_blocks_promotion` | Inferred from workflow YAML — does the SAST/SCA job have `severity-threshold` that blocks? |

Where the API directly gives the answer, the property's value is **highly trustworthy** — far more than LLM inference from documentation.

## When to use LLM extraction for GitHub content

For some properties, the API doesn't give a clean answer and an LLM needs to read the workflow YAML or source code:

- `governance.stateless_processes` — read sample handler code; look for local-state writes
- `governance.config_externalised` — read for `os.environ`, `Parameter Store`, `Secrets Manager` references vs hardcoded strings
- `governance.architecture_pattern` — derived from repo structure + READMEs
- `sdlc.rollback_mechanism` — read deploy workflow for canary / blue-green steps

For these, supply the LLM with the specific files (not the entire repo) and ask focused questions.

## Extraction prompt pattern (LLM portion)

```
You are extracting structured data from a GitHub repository for the GIC
Application Health Check.

The repository has been pre-processed:
- Branch protection settings: <JSON from GitHub API>
- Workflow files: <list + contents>
- IaC files present: <list>
- Sample handler code: <file contents>

For the schema fields listed below, return values based on the API data
and source code provided. Do NOT speculate beyond what's shown.

Add evidence entries with file paths and line ranges.

Schema fields to focus on: <list of relevant fields>

Return JSON.
```

## Provenance examples

```json
{
  "property_path": "sdlc.main_protected",
  "source": "github",
  "ref": "GitHub API: GET /repos/gic/apollo/branches/main/protection",
  "excerpt": "required_pull_request_reviews.required_approving_review_count = 2; required_signatures.enabled = true; required_status_checks.contexts = ['build', 'test', 'codeql', 'snyk']",
  "extracted_at": "2026-05-05T14:23:00Z"
},
{
  "property_path": "appsec.codeql_in_ci",
  "source": "github",
  "ref": ".github/workflows/ci.yml — lines 18-25",
  "excerpt": "uses: github/codeql-action/init@v3 with severity-threshold: error",
  "extracted_at": "2026-05-05T14:23:00Z"
}
```

## Important: GitHub API access constraints

The pipeline must have a read-only token with these scopes:
- `repo` (read code, read PRs, read branch settings)
- `security_events` (read code-scanning + secret-scanning alerts)
- `read:org` (if needed to scope to a specific repo's org)

If access is missing, extractor functions should fail loudly (not silently leave properties null). A null value should mean "the document didn't address this", not "we couldn't access the source."

## Caveats

- **Workflow files describe intent, not execution.** A workflow with `codeql-action` *configured* doesn't prove CodeQL is actually running and finding issues. Cross-check by querying recent code-scanning alerts; if alerts exist, the scanner is active. If no alerts exist over many months, check whether the workflow is actually running.
- **Branch protection can be bypassed.** A protected main branch with admin override means the protection is theatre. Check `enforce_admins.enabled` in the API response.
- **A monorepo may host multiple apps.** Be specific about which path / subdirectory belongs to this application. The extractor function should take the repo path as a parameter, not assume the whole repo is one app.
