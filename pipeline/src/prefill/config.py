"""Pipeline configuration.

All knobs are configurable via environment variables; sensible defaults included.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.environ.get(name, "")
    if not val:
        return default
    return val.lower() in ("true", "1", "yes", "y")


@dataclass(frozen=True)
class Config:
    # Paths
    skills_root: Path             # path to the parent folder containing the gic-* skills
    template_xlsx: Path           # path to the v0.9 Checklist template
    output_dir: Path              # where to write pre-filled outputs

    # Source artefacts for one app
    sources_dir: Path             # folder containing the app's source bundle

    # LLM
    llm_provider: str             # "ona" | "anthropic" | "mock"
    llm_model: str                # "claude-opus-4" or whatever ONA exposes
    llm_endpoint: str             # base URL for ONA's API
    llm_api_key: str | None       # bearer token / API key
    llm_max_tokens: int
    llm_temperature: float

    # GitHub
    github_token: str | None      # PAT for repo access; None disables GitHub extraction
    github_api_url: str           # default https://api.github.com; override for GHES

    # Pipeline behaviour
    require_evidence_for_yes: bool      # auto-downgrade evidence-less Yes to Not Sure
    low_confidence_to_not_sure: bool    # auto-downgrade Low confidence to Not Sure
    dry_run: bool                       # write outputs but don't call the LLM

    @classmethod
    def from_env(
        cls,
        sources_dir: str | None = None,
        template_xlsx: str | None = None,
        output_dir: str | None = None,
    ) -> "Config":
        # Skills root — default to ../skills relative to this file
        skills_root = Path(_env("GIC_SKILLS_ROOT") or "")
        if not skills_root:
            here = Path(__file__).resolve()
            # src/prefill/config.py -> src -> pipeline -> repo root -> skills
            skills_root = here.parents[3] / "skills"

        return cls(
            skills_root=Path(skills_root).resolve(),
            template_xlsx=Path(template_xlsx or _env("GIC_TEMPLATE_XLSX") or "").resolve(),
            output_dir=Path(output_dir or _env("GIC_OUTPUT_DIR") or "./output").resolve(),
            sources_dir=Path(sources_dir or _env("GIC_SOURCES_DIR") or "").resolve(),
            llm_provider=_env("GIC_LLM_PROVIDER") or "mock",
            llm_model=_env("GIC_LLM_MODEL") or "claude-opus-4",
            llm_endpoint=_env("GIC_LLM_ENDPOINT") or "https://ona.internal/v1/messages",
            llm_api_key=_env("GIC_LLM_API_KEY"),
            llm_max_tokens=int(_env("GIC_LLM_MAX_TOKENS") or "4096"),
            llm_temperature=float(_env("GIC_LLM_TEMPERATURE") or "0.0"),
            github_token=_env("GIC_GITHUB_TOKEN"),
            github_api_url=_env("GIC_GITHUB_API_URL") or "https://api.github.com",
            require_evidence_for_yes=_env_bool("GIC_REQUIRE_EVIDENCE_FOR_YES", True),
            low_confidence_to_not_sure=_env_bool("GIC_LOW_CONFIDENCE_TO_NOT_SURE", True),
            dry_run=_env_bool("GIC_DRY_RUN", False),
        )

    @property
    def health_check_skill_dir(self) -> Path:
        return self.skills_root / "gic-app-health-check"

    @property
    def source_extractors_skill_dir(self) -> Path:
        return self.skills_root / "gic-source-extractors"

    def validate(self) -> None:
        """Verify the config is workable; raise ValueError on fatal issues."""
        problems = []
        if not self.skills_root.exists():
            problems.append(f"Skills root does not exist: {self.skills_root}")
        if not self.health_check_skill_dir.exists():
            problems.append(f"Health Check skill missing: {self.health_check_skill_dir}")
        if not self.source_extractors_skill_dir.exists():
            problems.append(f"Source Extractors skill missing: {self.source_extractors_skill_dir}")
        if self.llm_provider not in ("ona", "anthropic", "mock"):
            problems.append(f"Invalid llm_provider '{self.llm_provider}'; must be ona/anthropic/mock")
        if problems:
            raise ValueError("Configuration problems:\n  - " + "\n  - ".join(problems))
