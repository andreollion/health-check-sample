"""Pipeline orchestrator — main entry point.

Wires together config, LLM client, skill loading, and the three stages:
  Stage 1: Source extraction       → AppFacts JSON
  Stage 2: Per-question answering  → list[ElementResponse]
  Stage 3: Excel population        → populated v0.9 Checklist .xlsx

Run as a module: `python -m prefill.orchestrator --sources-dir ... --template ... --output-dir ...`
Or via the console script: `gic-prefill --sources-dir ...`
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .config import Config
from .llm_client import LLMClient, LLMResponse, build_client
from .skills_loader import (
    HealthCheckSkill,
    SourceExtractorsSkill,
    load_health_check_skill,
    load_source_extractors_skill,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Audit trail
# ---------------------------------------------------------------------------

@dataclass
class AuditEntry:
    stage: str
    item: str            # source file, qid, etc.
    provider: str
    model: str
    prompt_hash: str
    response_hash: str
    duration_ms: int
    error: str | None = None


@dataclass
class AuditLog:
    entries: list[AuditEntry] = field(default_factory=list)

    def add(self, entry: AuditEntry) -> None:
        self.entries.append(entry)

    def write(self, path: Path) -> None:
        path.write_text(
            json.dumps([asdict(e) for e in self.entries], indent=2),
            encoding="utf-8",
        )


# ---------------------------------------------------------------------------
# Audit-wrapped LLM client
# ---------------------------------------------------------------------------

class AuditedLLMClient:
    """Wraps an LLMClient and records every call to an AuditLog."""

    def __init__(self, inner: LLMClient, audit: AuditLog, stage: str = "?"):
        self.inner = inner
        self.audit = audit
        self.stage = stage
        self.current_item = "?"

    def set_context(self, stage: str, item: str) -> None:
        self.stage = stage
        self.current_item = item

    def call(self, system: str, user: str, **kwargs: Any) -> LLMResponse:
        t0 = time.time()
        err: str | None = None
        try:
            resp = self.inner.call(system, user, **kwargs)
            return resp
        except Exception as exc:  # noqa: BLE001
            err = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            dur_ms = int((time.time() - t0) * 1000)
            # Build entry even on error; prompt_hash/response_hash may be missing
            try:
                resp_obj = resp  # type: ignore[name-defined]
                self.audit.add(AuditEntry(
                    stage=self.stage,
                    item=self.current_item,
                    provider=resp_obj.provider,
                    model=resp_obj.model,
                    prompt_hash=resp_obj.prompt_hash,
                    response_hash=resp_obj.response_hash,
                    duration_ms=dur_ms,
                    error=err,
                ))
            except NameError:
                self.audit.add(AuditEntry(
                    stage=self.stage,
                    item=self.current_item,
                    provider="?",
                    model="?",
                    prompt_hash="?",
                    response_hash="?",
                    duration_ms=dur_ms,
                    error=err or "no response object",
                ))


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------

class PipelineOrchestrator:
    """End-to-end pipeline runner.

    Usage:
        orch = PipelineOrchestrator.from_env(sources_dir=..., template=..., output_dir=...)
        orch.run()
    """

    def __init__(
        self,
        config: Config,
        health_skill: HealthCheckSkill,
        source_skill: SourceExtractorsSkill,
        llm: AuditedLLMClient,
        audit: AuditLog,
    ):
        self.config = config
        self.health_skill = health_skill
        self.source_skill = source_skill
        self.llm = llm
        self.audit = audit

    # ---- factory ---------------------------------------------------------

    @classmethod
    def from_env(
        cls,
        sources_dir: str | None = None,
        template_xlsx: str | None = None,
        output_dir: str | None = None,
    ) -> "PipelineOrchestrator":
        config = Config.from_env(
            sources_dir=sources_dir,
            template_xlsx=template_xlsx,
            output_dir=output_dir,
        )
        config.validate()

        health_skill = load_health_check_skill(config.health_check_skill_dir)
        source_skill = load_source_extractors_skill(config.source_extractors_skill_dir)

        inner = build_client(
            provider=config.llm_provider,
            model=config.llm_model,
            endpoint=config.llm_endpoint,
            api_key=config.llm_api_key,
        )
        audit = AuditLog()
        llm = AuditedLLMClient(inner=inner, audit=audit)

        return cls(
            config=config,
            health_skill=health_skill,
            source_skill=source_skill,
            llm=llm,
            audit=audit,
        )

    # ---- the three stages ------------------------------------------------

    def run(self) -> dict[str, Any]:
        """Run all three stages and return a summary dict."""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Stage 1: extracting source artefacts → AppFacts")
        app_facts = self.stage1_extract()
        facts_path = self.config.output_dir / "app_facts.json"
        facts_path.write_text(json.dumps(app_facts, indent=2), encoding="utf-8")
        logger.info(f"  wrote {facts_path}")

        logger.info("Stage 2: answering rubric questions")
        responses = self.stage2_answer(app_facts)
        responses_path = self.config.output_dir / "responses.json"
        responses_path.write_text(json.dumps(responses, indent=2), encoding="utf-8")
        logger.info(f"  wrote {responses_path}")

        logger.info("Stage 3: populating the Checklist xlsx")
        out_xlsx = self.stage3_populate(responses, app_facts)
        logger.info(f"  wrote {out_xlsx}")

        # Audit trail
        audit_path = self.config.output_dir / "audit_log.json"
        self.audit.write(audit_path)
        logger.info(f"  wrote {audit_path}")

        return {
            "app_facts": str(facts_path),
            "responses": str(responses_path),
            "output_xlsx": str(out_xlsx),
            "audit_log": str(audit_path),
            "llm_calls": len(self.audit.entries),
        }

    def stage1_extract(self) -> dict[str, Any]:
        """Walk sources_dir, classify, dispatch to per-source-type extractors."""
        # Imported here to avoid circular imports during package init.
        from .extractors import extract_all_sources
        return extract_all_sources(
            sources_dir=self.config.sources_dir,
            source_skill=self.source_skill,
            llm=self.llm,
            config=self.config,
        )

    def stage2_answer(self, app_facts: dict[str, Any]) -> list[dict[str, Any]]:
        from .answering import answer_all_questions
        return answer_all_questions(
            app_facts=app_facts,
            health_skill=self.health_skill,
            llm=self.llm,
            config=self.config,
        )

    def stage3_populate(
        self,
        responses: list[dict[str, Any]],
        app_facts: dict[str, Any] | None = None,
    ) -> Path:
        from .populator import populate_checklist
        out_xlsx = self.config.output_dir / "Checklist_prefilled.xlsx"
        populate_checklist(
            template_xlsx=self.config.template_xlsx,
            output_xlsx=out_xlsx,
            responses=responses,
            health_skill=self.health_skill,
            app_facts=app_facts,
        )
        return out_xlsx


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gic-prefill",
        description="GIC Application Health Check — pre-fill the v0.9 Checklist from source artefacts.",
    )
    parser.add_argument("--sources-dir", required=True, help="Folder containing one app's source bundle")
    parser.add_argument("--template", required=True, help="Path to the v0.9 Checklist template .xlsx")
    parser.add_argument("--output-dir", required=True, help="Where to write outputs")
    parser.add_argument("--dry-run", action="store_true", help="Skip LLM calls; produce stubs only")
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging")
    args = parser.parse_args(argv)

    _setup_logging(args.verbose)

    # Honour --dry-run via env so Config picks it up too
    import os
    if args.dry_run:
        os.environ["GIC_DRY_RUN"] = "true"

    try:
        orch = PipelineOrchestrator.from_env(
            sources_dir=args.sources_dir,
            template_xlsx=args.template,
            output_dir=args.output_dir,
        )
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    summary = orch.run()
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
