"""Tests for the per-question answerer, including policy gates."""
from __future__ import annotations

import json

import pytest
from prefill.answering.answerer import answer_one_question
from prefill.config import Config
from prefill.llm_client import MockLLMClient
from prefill.skills_loader import load_health_check_skill


def _config(require_evidence_for_yes: bool = True, low_confidence_to_not_sure: bool = True) -> Config:
    return Config(
        skills_root=__import__("pathlib").Path("."),
        template_xlsx=__import__("pathlib").Path("."),
        output_dir=__import__("pathlib").Path("."),
        sources_dir=__import__("pathlib").Path("."),
        llm_provider="mock",
        llm_model="x",
        llm_endpoint="",
        llm_api_key=None,
        llm_max_tokens=4096,
        llm_temperature=0.0,
        github_token=None,
        github_api_url="",
        require_evidence_for_yes=require_evidence_for_yes,
        low_confidence_to_not_sure=low_confidence_to_not_sure,
        dry_run=False,
    )


def test_answer_one_question_happy(health_skill_dir):
    skill = load_health_check_skill(health_skill_dir)
    q = skill.question_by_id("Q01")
    elements = q["elements"][:3]
    q_small = {**q, "elements": elements}

    # Mock LLM returns Yes with evidence + High confidence for all 3 elements
    mock_payload = {
        "responses": [
            {
                "element_id": el["element_id"],
                "response": "yes",
                "confidence": "high",
                "justification": "Found in facts",
                "evidence_refs": ["identity.sso.enabled"],
            }
            for el in elements
        ]
    }
    client = MockLLMClient(default=json.dumps(mock_payload))
    out = answer_one_question(
        question=q_small,
        sliced_facts={"identity": {"sso": {"enabled": "yes"}}},
        health_skill=skill,
        llm=client,
        config=_config(),
    )
    assert len(out) == 3
    assert all(r["response"] == "yes" for r in out)
    assert all(r["confidence"] == "high" for r in out)


def test_answer_one_question_evidenceless_yes_downgraded(health_skill_dir):
    skill = load_health_check_skill(health_skill_dir)
    q = skill.question_by_id("Q01")
    elements = q["elements"][:1]
    q_small = {**q, "elements": elements}

    mock_payload = {
        "responses": [
            {
                "element_id": elements[0]["element_id"],
                "response": "yes",
                "confidence": "high",
                "justification": "Vague.",
                "evidence_refs": [],
            }
        ]
    }
    client = MockLLMClient(default=json.dumps(mock_payload))
    out = answer_one_question(
        question=q_small,
        sliced_facts={},
        health_skill=skill,
        llm=client,
        config=_config(require_evidence_for_yes=True),
    )
    assert out[0]["response"] == "not_sure"
    assert "auto-downgrade" in out[0]["justification"]


def test_answer_one_question_low_confidence_downgraded(health_skill_dir):
    skill = load_health_check_skill(health_skill_dir)
    q = skill.question_by_id("Q01")
    elements = q["elements"][:1]
    q_small = {**q, "elements": elements}

    mock_payload = {
        "responses": [
            {
                "element_id": elements[0]["element_id"],
                "response": "no",
                "confidence": "low",
                "justification": "Couldn't tell.",
                "evidence_refs": ["x.y"],
            }
        ]
    }
    client = MockLLMClient(default=json.dumps(mock_payload))
    out = answer_one_question(
        question=q_small,
        sliced_facts={},
        health_skill=skill,
        llm=client,
        config=_config(low_confidence_to_not_sure=True),
    )
    assert out[0]["response"] == "not_sure"


def test_answer_backfills_missing_elements(health_skill_dir):
    skill = load_health_check_skill(health_skill_dir)
    q = skill.question_by_id("Q01")
    elements = q["elements"][:3]
    q_small = {**q, "elements": elements}

    # Only one of three elements answered
    mock_payload = {
        "responses": [
            {
                "element_id": elements[0]["element_id"],
                "response": "yes",
                "confidence": "high",
                "justification": "ok",
                "evidence_refs": ["x"],
            }
        ]
    }
    client = MockLLMClient(default=json.dumps(mock_payload))
    out = answer_one_question(
        question=q_small,
        sliced_facts={},
        health_skill=skill,
        llm=client,
        config=_config(),
    )
    assert len(out) == 3
    # First is yes, others are not_sure backfill
    yes_count = sum(1 for r in out if r["response"] == "yes")
    not_sure_count = sum(1 for r in out if r["response"] == "not_sure")
    assert yes_count == 1
    assert not_sure_count == 2
