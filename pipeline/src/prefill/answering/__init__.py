"""Stage 2: Per-question answering.

For each of the 32 questions in the gic-app-health-check skill:
  1. Slice the merged AppFacts down to just the parts relevant to this question
  2. Build a per-question prompt (using the question text + its elements +
     the relevant level definitions + the responses semantics)
  3. Ask the LLM to return Yes/No/N/A/Not Sure per element with justification
  4. Apply policy gates (require_evidence_for_yes, low_confidence_to_not_sure)
  5. Return a flat list of ElementResponse dicts

Public entry point: `answer_all_questions()`.
"""
from __future__ import annotations

import logging
from typing import Any

from ..config import Config
from ..llm_client import LLMClient
from ..skills_loader import HealthCheckSkill
from .answerer import answer_one_question
from .slicer import slice_facts_for_question

logger = logging.getLogger(__name__)


def answer_all_questions(
    app_facts: dict[str, Any],
    health_skill: HealthCheckSkill,
    llm: LLMClient,
    config: Config,
) -> list[dict[str, Any]]:
    """Iterate all 32 questions, return a list of element responses."""
    all_responses: list[dict[str, Any]] = []
    questions = health_skill.all_questions

    logger.info(f"answering {len(questions)} questions")

    for q in questions:
        qid = q["qid"]
        llm.set_context(stage="stage2_answer", item=qid)

        if config.dry_run:
            logger.info(f"DRY RUN: {qid}")
            for el in q.get("elements", []):
                all_responses.append({
                    "element_id": el["element_id"],
                    "qid": qid,
                    "level": el["level"],
                    "response": "not_sure",
                    "confidence": "low",
                    "justification": "dry-run stub — no LLM call performed",
                    "evidence": [],
                })
            continue

        try:
            sliced_facts = slice_facts_for_question(app_facts, q, health_skill)
            element_responses = answer_one_question(
                question=q,
                sliced_facts=sliced_facts,
                health_skill=health_skill,
                llm=llm,
                config=config,
            )
            all_responses.extend(element_responses)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"answering {qid} failed: {exc}", exc_info=True)
            # Fall back to Not Sure for every element of this question
            for el in q.get("elements", []):
                all_responses.append({
                    "element_id": el["element_id"],
                    "qid": qid,
                    "level": el["level"],
                    "response": "not_sure",
                    "confidence": "low",
                    "justification": f"answering failed: {exc}",
                    "evidence": [],
                })

    logger.info(f"produced {len(all_responses)} element responses")
    return all_responses


__all__ = ["answer_all_questions"]
