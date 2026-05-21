"""Confluence extractor.

Confluence pages (exported as HTML) describe operational runbooks, incident
playbooks, on-call rotations, and team practices. Strong signal for
operations, observability, and SDLC.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from ..config import Config
from ..llm_client import LLMClient
from ..skills_loader import SourceExtractorsSkill
from .base import build_extraction_prompt, parse_json_from_llm, read_source_text

logger = logging.getLogger(__name__)


_TAG_STRIP = re.compile(r"<[^>]+>")
_WS_COLLAPSE = re.compile(r"\s+")


def _strip_html(html: str) -> str:
    """Crude HTML-to-text. Confluence exports are noisy but largely safe."""
    text = _TAG_STRIP.sub(" ", html)
    text = _WS_COLLAPSE.sub(" ", text)
    return text.strip()


def extract_confluence(
    path: Path,
    source_skill: SourceExtractorsSkill,
    llm: LLMClient,
    config: Config,
) -> dict[str, Any]:
    raw = read_source_text(path)
    # If HTML, strip tags so the LLM sees text rather than markup noise.
    if path.suffix.lower() in (".html", ".htm"):
        content = _strip_html(raw)
    else:
        content = raw

    system, user = build_extraction_prompt(
        source_skill=source_skill,
        source_type="confluence",
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
        "source_type": "confluence",
        "source_path": str(path),
        "prompt_hash": resp.prompt_hash,
        "response_hash": resp.response_hash,
    })
    return facts
