"""Per-question prompt templates.

For one question, the prompt bundles:
  - the question text + dimension + sub-domain
  - the question's elements (each with element_id + level + criterion text)
  - the 4 level definitions for this dimension (from level-definitions.json)
  - the canonical responses semantics (Yes/No/N/A/Not Sure)
  - the sliced AppFacts JSON
  - explicit output schema

The LLM must return JSON: one entry per element with response + confidence +
justification + evidence references.
"""
from __future__ import annotations

import json
from typing import Any

from ..skills_loader import HealthCheckSkill


_OUTPUT_FORMAT = {
    "responses": [
        {
            "element_id": "Q01-E03",
            "response": "yes | no | n/a | not_sure",
            "confidence": "high | medium | low",
            "justification": "1–2 sentences citing specific facts",
            "evidence_refs": ["fact_path_1", "fact_path_2"],
        }
    ]
}


def build_question_prompt(
    question: dict[str, Any],
    sliced_facts: dict[str, Any],
    health_skill: HealthCheckSkill,
) -> tuple[str, str]:
    """Build (system, user) for one question's answering call."""
    qid = question["qid"]
    dimension = question["dimension"]
    sub_domain = question.get("sub_domain", "")
    text = question.get("question") or question.get("text", "")

    # 4 level definitions for this dimension
    level_block_lines = []
    for lvl in ("L1", "L2", "L3", "L4"):
        try:
            defn = health_skill.level_def(dimension, lvl)
            level_block_lines.append(f"  {lvl}: {defn}")
        except (KeyError, TypeError):
            pass
    level_block = "\n".join(level_block_lines)

    # Elements list (id, level, text)
    el_lines = []
    for el in question.get("elements", []):
        el_lines.append(
            f"  - {el['element_id']} [Level {el['level']}]: {el['text']}"
        )
    elements_block = "\n".join(el_lines)

    # Load responses + scoring guidance from the skill
    responses_guide = health_skill.reference("responses")
    scoring_guide = health_skill.reference("scoring")

    system = (
        "You are answering one question from the GIC Application Health Check rubric.\n"
        "Your job: for each element of the question, decide Yes / No / N/A / Not Sure\n"
        "based STRICTLY on the AppFacts provided. Do not invent facts.\n\n"
        "=== RESPONSE SEMANTICS ===\n"
        f"{responses_guide}\n\n"
        "=== SCORING CONTEXT ===\n"
        f"{scoring_guide}\n\n"
        "OUTPUT RULES:\n"
        "1. Return ONE JSON object with key 'responses' — a list of element responses.\n"
        "2. response: one of 'yes', 'no', 'n/a', 'not_sure'\n"
        "3. confidence: 'high' (multiple corroborating facts), 'medium' (one direct\n"
        "   fact), 'low' (weak inference). Use 'low' liberally — better to flag than\n"
        "   to assume.\n"
        "4. justification: 1–2 sentences. Cite specific values from the facts.\n"
        "5. evidence_refs: dotted fact paths (e.g. 'appsec.sast.enabled') that justify\n"
        "   the response.\n"
        "6. If a fact is absent or ambiguous, prefer 'not_sure' over guessing 'no'.\n"
        "7. If the element is genuinely not applicable to this app, use 'n/a' and\n"
        "   explain why.\n\n"
        f"Expected output format example:\n{json.dumps(_OUTPUT_FORMAT, indent=2)}\n"
    )

    user = (
        f"=== QUESTION {qid} ===\n"
        f"Dimension: {dimension}\n"
        f"Sub-domain: {sub_domain}\n"
        f"Question text: {text}\n\n"
        f"=== LEVEL DEFINITIONS FOR {dimension} ===\n{level_block}\n\n"
        f"=== ELEMENTS TO EVALUATE ===\n{elements_block}\n\n"
        f"=== APP FACTS (sliced for this question) ===\n"
        f"{json.dumps(sliced_facts, indent=2)}\n\n"
        "Now produce the JSON response."
    )

    return system, user
