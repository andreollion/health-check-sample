"""LLM client abstraction.

Supports three providers:
- "ona"        — GIC's internal Claude Opus deployment (HTTP POST, configurable URL/auth)
- "anthropic"  — Anthropic API direct (for development outside GIC tenant)
- "mock"      — returns canned responses for offline testing

The pipeline never imports a vendor SDK directly; it goes through this abstraction.
This makes it easy to swap providers without touching pipeline code.
"""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import requests

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    text: str
    model: str
    provider: str
    prompt_hash: str
    response_hash: str
    raw: dict[str, Any]  # full provider response for audit


class LLMClient(ABC):
    """Abstract LLM client. Implement call() in subclasses."""

    @abstractmethod
    def call(
        self,
        system: str,
        user: str,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> LLMResponse:
        ...


def _hash(text: str) -> str:
    """Short content hash for audit logging."""
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class ONAClient(LLMClient):
    """Client for GIC's ONA (Claude Opus) deployment.

    Assumes a Messages-API-compatible HTTP endpoint. Configure via Config.llm_endpoint
    and Config.llm_api_key. Adapt request shape if ONA's API differs.
    """

    def __init__(self, endpoint: str, api_key: str | None, model: str):
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model

    def call(self, system: str, user: str, max_tokens: int = 4096, temperature: float = 0.0) -> LLMResponse:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            # ONA may also use x-api-key — uncomment if needed:
            # headers["x-api-key"] = self.api_key

        # Anthropic Messages-API-compatible shape; adjust if ONA differs
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }

        prompt_hash = _hash(system + "|" + user)
        logger.info(f"ONA call: model={self.model} prompt_hash={prompt_hash}")

        resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        body = resp.json()

        # Anthropic-style response: body["content"] is a list of content blocks
        text = ""
        if "content" in body and isinstance(body["content"], list):
            text = "".join(block.get("text", "") for block in body["content"] if block.get("type") == "text")
        elif "completion" in body:
            text = body["completion"]
        else:
            text = json.dumps(body)

        return LLMResponse(
            text=text,
            model=self.model,
            provider="ona",
            prompt_hash=prompt_hash,
            response_hash=_hash(text),
            raw=body,
        )


class AnthropicClient(LLMClient):
    """Client using the Anthropic SDK directly. For dev/test outside GIC."""

    def __init__(self, api_key: str, model: str):
        try:
            import anthropic  # type: ignore
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: pip install gic-prefill[anthropic]"
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def call(self, system: str, user: str, max_tokens: int = 4096, temperature: float = 0.0) -> LLMResponse:
        prompt_hash = _hash(system + "|" + user)
        logger.info(f"Anthropic call: model={self.model} prompt_hash={prompt_hash}")

        msg = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(block.text for block in msg.content if hasattr(block, "text"))

        return LLMResponse(
            text=text,
            model=self.model,
            provider="anthropic",
            prompt_hash=prompt_hash,
            response_hash=_hash(text),
            raw=msg.model_dump() if hasattr(msg, "model_dump") else {"_": str(msg)},
        )


class MockLLMClient(LLMClient):
    """Returns canned responses for offline testing.

    Behaviour: returns a structured JSON-shaped response for any extraction or
    answering prompt. Configurable per-test via the `responses` dict.
    """

    def __init__(self, responses: dict[str, str] | None = None, default: str | None = None):
        self.responses = responses or {}
        self.default = default or json.dumps({
            "mock": True,
            "note": "MockLLMClient default response — supply real responses via the `responses` dict",
        })
        self.call_log: list[dict[str, Any]] = []

    def call(self, system: str, user: str, max_tokens: int = 4096, temperature: float = 0.0) -> LLMResponse:
        prompt_hash = _hash(system + "|" + user)

        # Lookup by prompt content keyword
        text = None
        for keyword, response in self.responses.items():
            if keyword in user or keyword in system:
                text = response
                break
        if text is None:
            text = self.default

        self.call_log.append({
            "system_first_80": system[:80],
            "user_first_80": user[:80],
            "matched": text != self.default,
            "prompt_hash": prompt_hash,
        })

        return LLMResponse(
            text=text,
            model="mock-model",
            provider="mock",
            prompt_hash=prompt_hash,
            response_hash=_hash(text),
            raw={"mock_call_log_index": len(self.call_log) - 1},
        )


def build_client(provider: str, model: str, endpoint: str, api_key: str | None) -> LLMClient:
    """Factory: select the right client based on Config.llm_provider."""
    if provider == "ona":
        return ONAClient(endpoint=endpoint, api_key=api_key, model=model)
    if provider == "anthropic":
        if not api_key:
            raise ValueError("anthropic provider requires GIC_LLM_API_KEY")
        return AnthropicClient(api_key=api_key, model=model)
    if provider == "mock":
        return MockLLMClient()
    raise ValueError(f"Unknown LLM provider: {provider}")
