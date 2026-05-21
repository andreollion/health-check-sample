"""Per-question slicer: given the full AppFacts and one question, produce a
minimal, focused dict of facts relevant to *that question's elements*.

Why slice? Two reasons:
  1. Token economy — the full AppFacts may be huge; one question only needs
     a fraction of it.
  2. Signal — narrowing input to the relevant section sharpens LLM output.

The slicer uses `element-source-routing.json` (in the skill assets) which
maps element_id → list of fact paths (dotted) that are likely relevant.
"""
from __future__ import annotations

import logging
from typing import Any

from ..skills_loader import HealthCheckSkill

logger = logging.getLogger(__name__)


def _get_by_path(d: dict[str, Any], path: str) -> Any:
    """Walk a dotted path through nested dicts; return None if missing."""
    cur: Any = d
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def _set_by_path(d: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    cur = d
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value


def slice_facts_for_question(
    app_facts: dict[str, Any],
    question: dict[str, Any],
    health_skill: HealthCheckSkill,
) -> dict[str, Any]:
    """Return a minimal AppFacts subset relevant to one question's elements."""
    routing = health_skill.element_source_routing or {}

    # Always include identity for context
    sliced: dict[str, Any] = {}
    if "app" in app_facts:
        sliced["app"] = app_facts["app"]
    if "identity" in app_facts:
        sliced["identity"] = app_facts["identity"]

    # Collect all fact paths referenced by this question's elements
    relevant_paths: set[str] = set()
    for el in question.get("elements", []):
        eid = el["element_id"]
        # routing values may be a list of strings or a dict with 'fact_paths'
        ent = routing.get(eid) or routing.get(eid.lower())
        if ent:
            if isinstance(ent, dict):
                for p in ent.get("fact_paths", []) or []:
                    relevant_paths.add(p)
            elif isinstance(ent, list):
                for p in ent:
                    if isinstance(p, str):
                        relevant_paths.add(p)

    # Fall back: if no routing matched, include sub-domain-related top-level keys
    if not relevant_paths:
        sub_domain = (question.get("sub_domain") or "").lower().replace(" ", "_")
        for k in (sub_domain, question.get("dimension", "").lower().replace(" ", "_")):
            if k and k in app_facts:
                sliced[k] = app_facts[k]

    # Copy each relevant fact path
    for p in relevant_paths:
        val = _get_by_path(app_facts, p)
        if val is not None:
            _set_by_path(sliced, p, val)

    # Always include evidence entries for the slices we pulled in
    evidence = app_facts.get("evidence") or {}
    if evidence:
        sliced_ev: dict[str, Any] = {}
        for p in relevant_paths:
            if p in evidence:
                sliced_ev[p] = evidence[p]
        if sliced_ev:
            sliced["evidence"] = sliced_ev

    return sliced
