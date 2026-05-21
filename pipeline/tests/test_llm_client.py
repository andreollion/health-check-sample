"""LLM client unit tests — focus on MockLLMClient + factory routing."""
from __future__ import annotations

import json

import pytest
from prefill.llm_client import MockLLMClient, build_client


def test_mock_client_returns_default():
    client = MockLLMClient()
    resp = client.call(system="sys", user="user")
    assert resp.provider == "mock"
    assert resp.model == "mock-model"
    body = json.loads(resp.text)
    assert body.get("mock") is True


def test_mock_client_keyword_match():
    client = MockLLMClient(responses={"foo": '{"matched": "foo"}'})
    resp = client.call(system="sys", user="please return foo data")
    assert json.loads(resp.text) == {"matched": "foo"}


def test_mock_client_call_log():
    client = MockLLMClient()
    client.call(system="s1", user="u1")
    client.call(system="s2", user="u2")
    assert len(client.call_log) == 2


def test_build_client_mock():
    client = build_client(provider="mock", model="x", endpoint="", api_key=None)
    assert isinstance(client, MockLLMClient)


def test_build_client_unknown():
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        build_client(provider="bogus", model="x", endpoint="", api_key=None)


def test_build_client_anthropic_requires_key():
    with pytest.raises(ValueError, match="GIC_LLM_API_KEY"):
        build_client(provider="anthropic", model="claude-opus-4", endpoint="", api_key=None)
