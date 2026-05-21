"""SharePoint extractor.

SharePoint hosts secondary architecture / governance documents.
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


def extract_sharepoint(
    path: Path,
    source_skill: SourceExtractorsSkill,
    llm: LLMClient,
    config: Config,
) -> dict[str, Any]:
    content = read_source_text(path)
    system, user = build_extraction_prompt(
        source_skill=source_skill,
        source_type="sharepoint",
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
        "source_type": "sharepoint",
        "source_path": str(path),
        "prompt_hash": resp.prompt_hash,
        "response_hash": resp.response_hash,
    })
    return facts
