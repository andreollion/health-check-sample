"""Smoke tests for skill loading — confirm the skills on disk are usable."""
from __future__ import annotations

from prefill.skills_loader import (
    load_health_check_skill,
    load_source_extractors_skill,
)


def test_health_skill_loads(health_skill_dir):
    skill = load_health_check_skill(health_skill_dir)
    assert len(skill.all_questions) == 32, "expected exactly 32 questions"

    q01 = skill.question_by_id("Q01")
    assert q01["dimension"] == "Identity & Access Management"

    el_count = sum(len(q["elements"]) for q in skill.all_questions)
    assert el_count == 332, f"expected 332 elements, got {el_count}"


def test_health_skill_level_defs(health_skill_dir):
    skill = load_health_check_skill(health_skill_dir)
    defn = skill.level_def("Identity & Access Management", "L1")
    assert isinstance(defn, str) and len(defn) > 10


def test_health_skill_references(health_skill_dir):
    skill = load_health_check_skill(health_skill_dir)
    for ref in ("scoring", "responses", "framework", "level-definitions"):
        body = skill.reference(ref)
        assert len(body) > 100, f"reference {ref!r} too short"


def test_source_extractors_skill_loads(source_skill_dir):
    skill = load_source_extractors_skill(source_skill_dir)
    assert "app" in skill.schema or "properties" in skill.schema
    for ref in ("schema", "risk-assessment", "arb", "confluence", "github", "sharepoint", "provenance"):
        body = skill.reference(ref)
        assert len(body) > 50
