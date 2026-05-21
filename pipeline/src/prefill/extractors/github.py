"""GitHub extractor.

Unlike the document-style extractors, this one queries the GitHub API directly
to get high-fidelity facts about repos (branch protection, workflows, code
scanning, dependabot, languages, default branch, etc.).

Manifest format (sources_dir/github.json):
    {
      "repos": [
        {"owner": "gic-internal", "repo": "payments-svc"},
        {"owner": "gic-internal", "repo": "payments-web"}
      ]
    }
"""
from __future__ import annotations

import base64
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from ..config import Config
from ..llm_client import LLMClient
from ..skills_loader import SourceExtractorsSkill
from .base import build_extraction_prompt, parse_json_from_llm

logger = logging.getLogger(__name__)


@dataclass
class RepoMetrics:
    owner: str
    repo: str
    default_branch: str | None
    branch_protection: dict[str, Any] | None
    workflows: list[str]
    languages: dict[str, int]
    dependabot_enabled: bool
    code_scanning_enabled: bool
    secret_scanning_enabled: bool
    has_readme: bool
    has_codeowners: bool
    has_dockerfile: bool
    has_iac: bool
    raw_errors: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "owner": self.owner,
            "repo": self.repo,
            "default_branch": self.default_branch,
            "branch_protection": self.branch_protection,
            "workflows": self.workflows,
            "languages": self.languages,
            "dependabot_enabled": self.dependabot_enabled,
            "code_scanning_enabled": self.code_scanning_enabled,
            "secret_scanning_enabled": self.secret_scanning_enabled,
            "has_readme": self.has_readme,
            "has_codeowners": self.has_codeowners,
            "has_dockerfile": self.has_dockerfile,
            "has_iac": self.has_iac,
            "raw_errors": self.raw_errors,
        }


def _gh_get(url: str, token: str | None, allow_404: bool = False) -> tuple[int, Any]:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.get(url, headers=headers, timeout=30)
    if r.status_code == 404 and allow_404:
        return 404, None
    if r.status_code >= 400:
        return r.status_code, {"_error": r.text[:200]}
    try:
        return r.status_code, r.json()
    except ValueError:
        return r.status_code, r.text


def gather_repo_metrics(owner: str, repo: str, config: Config) -> RepoMetrics:
    """Collect repo facts via the GitHub REST API. Tolerant of missing perms."""
    api = config.github_api_url.rstrip("/")
    token = config.github_token
    errors: list[str] = []

    # Repo info
    code, repo_info = _gh_get(f"{api}/repos/{owner}/{repo}", token)
    if code >= 400:
        errors.append(f"GET /repos/{owner}/{repo}: {code}")
        repo_info = {}
    default_branch = repo_info.get("default_branch") if isinstance(repo_info, dict) else None

    # Branch protection
    branch_protection = None
    if default_branch:
        code, bp = _gh_get(
            f"{api}/repos/{owner}/{repo}/branches/{default_branch}/protection",
            token,
            allow_404=True,
        )
        if code == 200 and isinstance(bp, dict):
            branch_protection = {
                "required_pull_request_reviews": bp.get("required_pull_request_reviews"),
                "required_status_checks": bp.get("required_status_checks"),
                "enforce_admins": bp.get("enforce_admins"),
                "restrictions": bp.get("restrictions"),
                "required_signatures": bp.get("required_signatures"),
            }
        elif code == 404:
            branch_protection = {"_status": "no_protection_set"}
        else:
            errors.append(f"GET branch_protection: {code}")

    # Workflows
    workflows: list[str] = []
    code, wf = _gh_get(f"{api}/repos/{owner}/{repo}/actions/workflows", token, allow_404=True)
    if code == 200 and isinstance(wf, dict):
        workflows = [w.get("name", "?") for w in wf.get("workflows", [])]
    elif code != 404:
        errors.append(f"GET workflows: {code}")

    # Languages
    languages: dict[str, int] = {}
    code, langs = _gh_get(f"{api}/repos/{owner}/{repo}/languages", token, allow_404=True)
    if code == 200 and isinstance(langs, dict):
        languages = {k: int(v) for k, v in langs.items()}
    elif code != 404:
        errors.append(f"GET languages: {code}")

    # Dependabot / code scanning / secret scanning
    dependabot_enabled = False
    code, dep = _gh_get(f"{api}/repos/{owner}/{repo}/vulnerability-alerts", token, allow_404=True)
    if code == 204:
        dependabot_enabled = True
    elif code != 404:
        errors.append(f"GET vulnerability-alerts: {code}")

    code_scanning_enabled = False
    code, cs = _gh_get(f"{api}/repos/{owner}/{repo}/code-scanning/alerts", token, allow_404=True)
    if code == 200:
        code_scanning_enabled = True

    secret_scanning_enabled = False
    code, ss = _gh_get(f"{api}/repos/{owner}/{repo}/secret-scanning/alerts", token, allow_404=True)
    if code == 200:
        secret_scanning_enabled = True

    # Surface-level file checks
    def _has(path_in_repo: str) -> bool:
        code, _body = _gh_get(
            f"{api}/repos/{owner}/{repo}/contents/{path_in_repo}",
            token,
            allow_404=True,
        )
        return code == 200

    has_readme = _has("README.md") or _has("readme.md") or _has("README")
    has_codeowners = _has(".github/CODEOWNERS") or _has("CODEOWNERS")
    has_dockerfile = _has("Dockerfile")
    has_iac = (
        _has("terraform")
        or _has("infra")
        or _has("cdk.json")
        or _has("template.yaml")
    )

    return RepoMetrics(
        owner=owner,
        repo=repo,
        default_branch=default_branch,
        branch_protection=branch_protection,
        workflows=workflows,
        languages=languages,
        dependabot_enabled=dependabot_enabled,
        code_scanning_enabled=code_scanning_enabled,
        secret_scanning_enabled=secret_scanning_enabled,
        has_readme=has_readme,
        has_codeowners=has_codeowners,
        has_dockerfile=has_dockerfile,
        has_iac=has_iac,
        raw_errors=errors,
    )


def extract_github(
    manifest_path: Path,
    source_skill: SourceExtractorsSkill,
    llm: LLMClient,
    config: Config,
) -> dict[str, Any]:
    """Read repo list from manifest_path, gather API metrics, and ask the LLM
    to map them into the AppFacts schema with provenance.
    """
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    repo_list = manifest.get("repos", [])
    if not repo_list:
        logger.warning("github.json contained no repos")
        return {"_meta": {"source_type": "github", "source_path": str(manifest_path), "empty": True}}

    all_metrics = []
    for r in repo_list:
        try:
            m = gather_repo_metrics(r["owner"], r["repo"], config)
            all_metrics.append(m.as_dict())
        except Exception as exc:  # noqa: BLE001
            logger.error(f"GitHub metrics gather failed for {r}: {exc}")

    # Hand the metrics to the LLM as structured "source content"
    content = json.dumps({"repos": all_metrics}, indent=2)
    system, user = build_extraction_prompt(
        source_skill=source_skill,
        source_type="github",
        source_path=manifest_path,
        source_content=content,
    )
    resp = llm.call(
        system=system,
        user=user,
        max_tokens=config.llm_max_tokens,
        temperature=config.llm_temperature,
    )
    facts = parse_json_from_llm(resp.text)
    facts.setdefault("_meta", {})
    facts["_meta"].update({
        "source_type": "github",
        "source_path": str(manifest_path),
        "prompt_hash": resp.prompt_hash,
        "response_hash": resp.response_hash,
        "repo_count": len(all_metrics),
    })
    # Also stash raw metrics so we have an authoritative trail
    facts["_meta"]["raw_repo_metrics"] = all_metrics
    return facts
