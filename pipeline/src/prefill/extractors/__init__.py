"""Stage 1: Source extraction.

For each source artefact in `sources_dir`, classify its type (risk_assessment,
arb, confluence, github, sharepoint), call the matching extractor, then merge
all per-source AppFacts into a single consolidated dict.

Public entry point: `extract_all_sources()`.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from ..config import Config
from ..llm_client import LLMClient
from ..skills_loader import SourceExtractorsSkill
from .arb import extract_arb
from .classifier import classify_source
from .confluence import extract_confluence
from .github import extract_github
from .merger import merge_facts
from .risk_assessment import extract_risk_assessment
from .sharepoint import extract_sharepoint

logger = logging.getLogger(__name__)


EXTRACTORS = {
    "risk_assessment": extract_risk_assessment,
    "arb": extract_arb,
    "confluence": extract_confluence,
    "github": extract_github,
    "sharepoint": extract_sharepoint,
}


def extract_all_sources(
    sources_dir: Path,
    source_skill: SourceExtractorsSkill,
    llm: LLMClient,
    config: Config,
) -> dict[str, Any]:
    """Walk sources_dir, dispatch each file to the right extractor, merge results."""
    sources_dir = Path(sources_dir)
    if not sources_dir.exists():
        raise FileNotFoundError(f"sources_dir does not exist: {sources_dir}")

    per_source_facts: list[dict[str, Any]] = []

    # Special case: GitHub repos are described by a manifest file `github.json`
    # listing repo slugs rather than discovered by file walking.
    gh_manifest = sources_dir / "github.json"
    if gh_manifest.exists():
        try:
            gh_meta = json.loads(gh_manifest.read_text(encoding="utf-8"))
            logger.info(f"GitHub manifest detected: {len(gh_meta.get('repos', []))} repo(s)")
            gh_facts = extract_github(
                gh_manifest, source_skill=source_skill, llm=llm, config=config
            )
            per_source_facts.append(gh_facts)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"GitHub extraction failed: {exc}")

    # Walk other source artefacts
    for path in sorted(sources_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name == "github.json":
            continue  # already handled
        # Skip hidden / temp files
        if path.name.startswith(".") or path.name.startswith("~$"):
            continue

        source_type = classify_source(path)
        if not source_type:
            logger.debug(f"skipping (no classifier match): {path.name}")
            continue

        extractor = EXTRACTORS.get(source_type)
        if not extractor:
            logger.warning(f"no extractor for source_type={source_type}: {path}")
            continue

        if config.dry_run:
            logger.info(f"DRY RUN: would extract {source_type} from {path.name}")
            per_source_facts.append({
                "_meta": {"source_type": source_type, "source_path": str(path), "dry_run": True},
            })
            continue

        try:
            logger.info(f"extracting {source_type} from {path.name}")
            llm.set_context(stage="stage1_extract", item=f"{source_type}:{path.name}")
            facts = extractor(path, source_skill=source_skill, llm=llm, config=config)
            per_source_facts.append(facts)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"extraction failed for {path}: {exc}", exc_info=True)
            # Keep going — don't let one bad source break the whole run

    logger.info(f"extracted {len(per_source_facts)} source artefact(s); merging…")
    merged = merge_facts(per_source_facts)
    return merged


__all__ = ["extract_all_sources"]
