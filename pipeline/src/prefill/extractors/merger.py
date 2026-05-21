"""Merge multiple per-source AppFacts dicts into one consolidated AppFacts.

Priority order when two sources disagree on a leaf value (highest wins):
  1. github (API-derived → highest fidelity)
  2. risk_assessment
  3. arb
  4. confluence
  5. sharepoint

Provenance is preserved per-source: when a value is overridden, the previous
evidence is retained in `evidence[<path>].alternatives` so the question-
answering stage can see both.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


SOURCE_PRIORITY = ["github", "risk_assessment", "arb", "confluence", "sharepoint"]


def _priority_index(source_type: str) -> int:
    try:
        return SOURCE_PRIORITY.index(source_type)
    except ValueError:
        return len(SOURCE_PRIORITY)  # unknown sources sort last


def merge_facts(per_source: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge a list of per-source AppFacts into one."""
    if not per_source:
        return {"_meta": {"merged": True, "sources": []}}

    # Sort so highest-priority source is processed last (overrides win)
    ordered = sorted(
        per_source,
        key=lambda f: _priority_index(f.get("_meta", {}).get("source_type", "")),
        reverse=True,  # least-priority first → most-priority last
    )

    merged: dict[str, Any] = {}
    evidence: dict[str, Any] = {}
    sources_meta: list[dict[str, Any]] = []

    for facts in ordered:
        meta = facts.get("_meta", {}) or {}
        source_type = meta.get("source_type", "unknown")
        sources_meta.append(meta)

        # Pull evidence aside first
        this_evidence = facts.pop("evidence", None) or {}
        # Then merge non-meta keys
        _deep_merge(merged, {k: v for k, v in facts.items() if k != "_meta"}, source_type)

        # Merge evidence map
        for path, ev in this_evidence.items():
            if path not in evidence:
                evidence[path] = ev
            else:
                # Different source already claimed this path
                prior = evidence[path]
                # Latest (highest priority due to sort order) wins; demote old
                alts = prior.pop("alternatives", []) if isinstance(prior, dict) else []
                alts.append(prior)
                if isinstance(ev, dict):
                    ev = {**ev, "alternatives": alts}
                evidence[path] = ev

    merged["evidence"] = evidence
    merged["_meta"] = {"merged": True, "sources": sources_meta}
    return merged


def _deep_merge(into: dict[str, Any], update: dict[str, Any], source_type: str) -> None:
    """Recursive dict merge — later values overwrite, dicts merge."""
    for k, v in update.items():
        if isinstance(v, dict) and isinstance(into.get(k), dict):
            _deep_merge(into[k], v, source_type)
        else:
            if k in into and into[k] != v:
                logger.debug(f"merge: {source_type} overrides {k} ({into[k]!r} → {v!r})")
            into[k] = v
