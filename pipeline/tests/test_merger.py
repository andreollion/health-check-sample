"""Tests for the multi-source AppFacts merger."""
from __future__ import annotations

from prefill.extractors.merger import merge_facts


def test_merge_single_source():
    facts = [{
        "appsec": {"sast": {"enabled": "yes"}},
        "evidence": {"appsec.sast.enabled": {"source": "arb", "excerpt": "SAST in pipeline"}},
        "_meta": {"source_type": "arb"},
    }]
    merged = merge_facts(facts)
    assert merged["appsec"]["sast"]["enabled"] == "yes"
    assert "appsec.sast.enabled" in merged["evidence"]


def test_merge_github_overrides_arb():
    facts = [
        {
            "appsec": {"sast": {"enabled": "no"}},
            "evidence": {"appsec.sast.enabled": {"source": "arb", "excerpt": "ARB said no"}},
            "_meta": {"source_type": "arb"},
        },
        {
            "appsec": {"sast": {"enabled": "yes"}},
            "evidence": {"appsec.sast.enabled": {"source": "github", "excerpt": "code-scanning enabled"}},
            "_meta": {"source_type": "github"},
        },
    ]
    merged = merge_facts(facts)
    # GitHub has higher priority
    assert merged["appsec"]["sast"]["enabled"] == "yes"
    ev = merged["evidence"]["appsec.sast.enabled"]
    assert ev["source"] == "github"
    # Old evidence preserved as alternative
    assert any(a.get("source") == "arb" for a in ev.get("alternatives", []))


def test_merge_disjoint_keys():
    facts = [
        {"a": 1, "_meta": {"source_type": "arb"}},
        {"b": 2, "_meta": {"source_type": "confluence"}},
    ]
    merged = merge_facts(facts)
    assert merged["a"] == 1
    assert merged["b"] == 2


def test_merge_empty():
    merged = merge_facts([])
    assert merged["_meta"]["merged"] is True
