"""Unit tests for shared extractor helpers (JSON parsing, classifier)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from prefill.extractors.base import parse_json_from_llm
from prefill.extractors.classifier import classify_source


def test_parse_clean_json():
    out = parse_json_from_llm('{"a": 1}')
    assert out == {"a": 1}


def test_parse_fenced_json():
    text = "Here is the answer:\n```json\n{\"a\": 2}\n```\nThanks"
    out = parse_json_from_llm(text)
    assert out == {"a": 2}


def test_parse_braces_in_prose():
    text = "Some prelude text. {\"a\": 3} and trailing chatter."
    out = parse_json_from_llm(text)
    assert out == {"a": 3}


def test_parse_failure():
    with pytest.raises(ValueError):
        parse_json_from_llm("totally not json at all, just text")


def test_classifier_risk_assessment():
    assert classify_source(Path("/x/risk_assessment_v3.pdf")) == "risk_assessment"
    assert classify_source(Path("/x/RSA_payments.pdf")) == "risk_assessment"


def test_classifier_arb():
    assert classify_source(Path("/x/arb_decisions.docx")) == "arb"


def test_classifier_confluence():
    assert classify_source(Path("/x/confluence_runbook.html")) == "confluence"
    assert classify_source(Path("/x/wiki_oncall.html")) == "confluence"


def test_classifier_sharepoint():
    assert classify_source(Path("/x/sharepoint_arch.docx")) == "sharepoint"


def test_classifier_pdf_fallback():
    # No keyword match but .pdf → risk_assessment
    assert classify_source(Path("/x/random_doc.pdf")) == "risk_assessment"


def test_classifier_unknown():
    assert classify_source(Path("/x/some_thing.csv")) is None
