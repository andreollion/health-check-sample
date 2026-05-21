"""Validate pre-fill response structures against the rubric.

Pure functions. Verifies that a set of element responses is well-formed:
- Element IDs match the rubric
- Response values are in the allowed set
- Confidence values are in the allowed set
- Yes responses carry evidence (if expected)
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

_VALID_RESPONSES = {"Yes", "No", "N/A", "Not Sure"}
_VALID_CONFIDENCE = {"High", "Medium", "Low"}
_VALID_LEVELS = {"L1", "L2", "L3", "L4"}


@dataclass(frozen=True)
class ValidationError:
    element_id: str
    field: str
    message: str


def load_rubric_questions(skill_assets_dir: str) -> dict:
    """Load the canonical rubric from the skill's assets/questions.json."""
    path = os.path.join(skill_assets_dir, "questions.json")
    with open(path) as f:
        return json.load(f)


def known_element_ids(rubric: dict) -> set[str]:
    """Return all valid element IDs from the rubric."""
    ids = set()
    for q in rubric["questions"]:
        for e in q["elements"]:
            ids.add(e["element_id"])
    return ids


def known_element_levels(rubric: dict) -> dict[str, str]:
    """Return mapping of element_id → level."""
    out: dict[str, str] = {}
    for q in rubric["questions"]:
        for e in q["elements"]:
            out[e["element_id"]] = e["level"]
    return out


def validate_response(
    response: dict[str, Any],
    rubric: dict,
    require_evidence_for_yes: bool = True,
) -> list[ValidationError]:
    """Validate a single element response dict.

    Expected shape:
    {
        "element_id": "Q01-E07",
        "response": "Yes" | "No" | "N/A" | "Not Sure",
        "confidence": "High" | "Medium" | "Low",   # optional but recommended
        "evidence": "..."                           # required for Yes if flag set
    }
    """
    errors: list[ValidationError] = []
    eid = response.get("element_id", "<missing>")

    # element_id must be in rubric
    if eid not in known_element_ids(rubric):
        errors.append(ValidationError(eid, "element_id",
                                       f"Element ID '{eid}' not found in rubric"))
        return errors  # no point validating further

    # response must be in allowed set
    r = response.get("response")
    if r not in _VALID_RESPONSES:
        errors.append(ValidationError(eid, "response",
                                       f"Response '{r}' must be one of {_VALID_RESPONSES}"))

    # confidence (if present) must be in allowed set
    if "confidence" in response:
        c = response["confidence"]
        if c not in _VALID_CONFIDENCE:
            errors.append(ValidationError(eid, "confidence",
                                           f"Confidence '{c}' must be one of {_VALID_CONFIDENCE}"))

    # Yes responses should carry evidence (configurable)
    if require_evidence_for_yes and r == "Yes":
        evidence = response.get("evidence", "")
        if not evidence or not str(evidence).strip():
            errors.append(ValidationError(eid, "evidence",
                                           "Yes response must include evidence (quote, file ref, or system reference)"))

    return errors


def validate_responses(
    responses: list[dict[str, Any]],
    rubric: dict,
    require_evidence_for_yes: bool = True,
) -> list[ValidationError]:
    """Validate a batch of element responses."""
    all_errors: list[ValidationError] = []
    seen_ids: set[str] = set()
    for r in responses:
        errs = validate_response(r, rubric, require_evidence_for_yes)
        all_errors.extend(errs)
        eid = r.get("element_id")
        if eid:
            if eid in seen_ids:
                all_errors.append(ValidationError(
                    eid, "element_id", "Duplicate element_id in batch"))
            seen_ids.add(eid)
    return all_errors


# Example self-test
if __name__ == "__main__":
    import sys
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(skill_dir, "assets")
    rubric = load_rubric_questions(assets_dir)
    print(f"Loaded rubric with {len(known_element_ids(rubric))} elements")

    # Valid response
    r1 = {"element_id": "Q01-E04", "response": "Yes",
          "confidence": "High",
          "evidence": "Ping admin console: app id 'apollo-prod' active=true"}
    errs = validate_response(r1, rubric)
    assert not errs, f"Expected valid, got {errs}"
    print("Valid response: pass")

    # Invalid: unknown element id
    r2 = {"element_id": "Q99-E99", "response": "Yes"}
    errs = validate_response(r2, rubric)
    assert errs, "Expected error for unknown element_id"
    print(f"Unknown element_id: caught ({errs[0].message})")

    # Invalid: Yes without evidence
    r3 = {"element_id": "Q01-E04", "response": "Yes"}
    errs = validate_response(r3, rubric)
    assert errs, "Expected error for missing evidence"
    print(f"Missing evidence: caught ({errs[0].message})")

    print("\nself-test passed")
