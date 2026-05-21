"""One-question answerer.

Wraps prompt-building + LLM call + parsing + policy gates for a single
rubric question.
"""
from __future__ import annotations

import logging
from typing import Any

from ..config import Config
from ..extractors.base import parse_json_from_llm
from ..llm_client import LLMClient
from ..skills_loader import HealthCheckSkill
from .prompts import build_question_prompt

logger = logging.getLogger(__name__)


VALID_RESPONSES = {"yes", "no", "n/a", "not_sure"}
VALID_CONFIDENCE = {"high", "medium", "low"}


def answer_one_question(
    question: dict[str, Any],
    sliced_facts: dict[str, Any],
    health_skill: HealthCheckSkill,
    llm: LLMClient,
    config: Config,
) -> list[dict[str, Any]]:
    """Call the LLM for one question; apply policy gates; return ElementResponses."""
    system, user = build_question_prompt(question, sliced_facts, health_skill)

    resp = llm.call(
        system=system,
        user=user,
        max_tokens=config.llm_max_tokens,
        temperature=config.llm_temperature,
    )
    parsed = parse_json_from_llm(resp.text)

    raw_responses = parsed.get("responses", [])
    if not isinstance(raw_responses, list):
        raise ValueError(f"Expected 'responses' list, got {type(raw_responses).__name__}")

    # Normalise + apply policy gates
    expected_ids = {el["element_id"] for el in question.get("elements", [])}
    level_by_id = {el["element_id"]: el["level"] for el in question.get("elements", [])}

    normalised: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for r in raw_responses:
        eid = r.get("element_id")
        if eid not in expected_ids:
            logger.warning(f"LLM returned unknown element_id {eid!r} for {question['qid']}; skipping")
            continue
        seen_ids.add(eid)

        response_val = (r.get("response") or "not_sure").lower().strip()
        if response_val not in VALID_RESPONSES:
            logger.warning(f"{eid}: invalid response {response_val!r} → not_sure")
            response_val = "not_sure"

        confidence = (r.get("confidence") or "low").lower().strip()
        if confidence not in VALID_CONFIDENCE:
            confidence = "low"

        justification = (r.get("justification") or "").strip()
        evidence_refs = r.get("evidence_refs") or []
        if not isinstance(evidence_refs, list):
            evidence_refs = []

        # Policy gate 1: require evidence for Yes
        if (
            config.require_evidence_for_yes
            and response_val == "yes"
            and not evidence_refs
        ):
            logger.info(f"{eid}: downgrading Yes → Not Sure (no evidence_refs)")
            response_val = "not_sure"
            justification = (
                "[auto-downgrade: no evidence cited] " + justification
            ).strip()

        # Policy gate 2: Low confidence → Not Sure
        if (
            config.low_confidence_to_not_sure
            and confidence == "low"
            and response_val in ("yes", "no")
        ):
            logger.info(f"{eid}: downgrading Low confidence {response_val} → Not Sure")
            response_val = "not_sure"
            justification = (
                "[auto-downgrade: low confidence] " + justification
            ).strip()

        normalised.append({
            "element_id": eid,
            "qid": question["qid"],
            "level": level_by_id[eid],
            "response": response_val,
            "confidence": confidence,
            "justification": justification,
            "evidence_refs": evidence_refs,
        })

    # Backfill any missing elements as Not Sure
    for eid in expected_ids - seen_ids:
        logger.warning(f"{eid}: LLM omitted response → Not Sure backfill")
        normalised.append({
            "element_id": eid,
            "qid": question["qid"],
            "level": level_by_id[eid],
            "response": "not_sure",
            "confidence": "low",
            "justification": "[auto-backfill: LLM omitted this element]",
            "evidence_refs": [],
        })

    return normalised
