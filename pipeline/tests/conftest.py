"""Shared pytest fixtures."""
from __future__ import annotations

import os
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]  # 06-PreFill-System/
SKILLS_ROOT = REPO_ROOT / "skills"
TEMPLATE_DIR = REPO_ROOT.parent / "02-Questionnaire" / "v0.9"


@pytest.fixture(scope="session")
def skills_root() -> Path:
    return SKILLS_ROOT


@pytest.fixture(scope="session")
def health_skill_dir(skills_root: Path) -> Path:
    return skills_root / "gic-app-health-check"


@pytest.fixture(scope="session")
def source_skill_dir(skills_root: Path) -> Path:
    return skills_root / "gic-source-extractors"


@pytest.fixture(scope="session")
def template_xlsx() -> Path:
    return TEMPLATE_DIR / "Ollion_GIC_App_Health_Check_v0.9-Checklist.xlsx"


@pytest.fixture(autouse=True)
def _mock_env(monkeypatch, skills_root, template_xlsx):
    """Make config.from_env() resolve to test paths by default."""
    monkeypatch.setenv("GIC_SKILLS_ROOT", str(skills_root))
    monkeypatch.setenv("GIC_LLM_PROVIDER", "mock")
    monkeypatch.delenv("GIC_LLM_API_KEY", raising=False)
