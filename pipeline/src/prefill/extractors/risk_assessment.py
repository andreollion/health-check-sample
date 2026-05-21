"""Risk Assessment extractor.

Risk Assessments are typically PDFs produced during the architecture review
process. They contain governance, data classification, and risk-control
findings — strong signal for the data_protection, governance, and parts of
the resilience/observability dimensions.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ..config import Config
from ..llm_client import LLMClient
from ..skills_loader import SourceExtractorsSkill
from .base import build_extraction_prompt, parse_json_from_llm, read_source_text

logger = logging.getLogger(__name__)


def extract_risk_assessment(
    path: Path,
    source_skill: SourceExtractorsSkill,
    llm: LLMClient,
    config: Config,
) -> dict[str, Any]:
    content = read_source_text(path)
    system, user = build_extraction_prompt(
        source_skill=source_skill,
        source_type="risk_assessment",
        source_path=path,
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
        "source_type": "risk_assessment",
        "source_path": str(path),
        "prompt_hash": resp.prompt_hash,
        "response_hash": resp.response_hash,
    })
    return facts
