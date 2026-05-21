"""Reference implementation of the GIC App Health Check scoring algorithm.

Pure functions. No external dependencies beyond the Python stdlib.

The same algorithm is encoded in the v0.9 Checklist Excel scoring formulas.
This module is the authoritative implementation for any other consumer
(pre-fill pipeline, custom analytics, validators).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Optional

Response = Literal["Yes", "No", "N/A", "Not Sure"]
Level = Literal["L1", "L2", "L3", "L4"]
LevelOrUnassessed = Literal[
    "L1 Developing", "L2 Healthy", "L3 Managed", "L4 Optimised",
    "Awaiting completion", "Excluded (all N/A)",
]

LEVEL_NAMES = {
    "L1": "L1 Developing",
    "L2": "L2 Healthy",
    "L3": "L3 Managed",
    "L4": "L4 Optimised",
}


@dataclass(frozen=True)
class ElementResponse:
    element_id: str
    level: Level                  # "L1" | "L2" | "L3" | "L4"
    response: Optional[Response]  # None means blank/unanswered


@dataclass(frozen=True)
class Thresholds:
    """Configurable thresholds per level. Default 100% (1.0)."""
    l2: float = 1.0
    l3: float = 1.0
    l4: float = 1.0


def question_level(
    elements: Iterable[ElementResponse],
    thresholds: Thresholds = Thresholds(),
) -> LevelOrUnassessed:
    """Compute the level for a single question given its element responses.

    Algorithm:
    1. If any element is blank → "Awaiting completion"
    2. If any L1 element has response "Yes" → L1 Developing (gap acknowledged)
    3. If all elements are N/A → "Excluded (all N/A)"
    4. Otherwise compute per-level ratios (Yes / effective-total, excluding N/A)
       and find highest level where ratio meets threshold.
    """
    elements = list(elements)
    if any(e.response is None for e in elements):
        return "Awaiting completion"

    # Step 2: L1 gap acknowledgement
    if any(e.level == "L1" and e.response == "Yes" for e in elements):
        return "L1 Developing"

    # Step 3: all N/A → excluded
    if all(e.response == "N/A" for e in elements):
        return "Excluded (all N/A)"

    # Step 4: per-level ratios (only for L2/L3/L4; L1 is gap-only)
    def ratio(level: Level) -> Optional[float]:
        at_level = [e for e in elements if e.level == level]
        if not at_level:
            return None  # no elements at this level → treat as passed
        non_na = [e for e in at_level if e.response != "N/A"]
        if not non_na:
            return None  # all N/A at this level
        n_yes = sum(1 for e in non_na if e.response == "Yes")
        return n_yes / len(non_na)

    # Note: None ratio is treated as "passed" (no requirement at this level)
    l2 = ratio("L2")
    l3 = ratio("L3")
    l4 = ratio("L4")

    if l2 is not None and l2 < thresholds.l2:
        return "L1 Developing"
    if l3 is not None and l3 < thresholds.l3:
        return "L2 Healthy"
    if l4 is not None and l4 < thresholds.l4:
        return "L3 Managed"
    return "L4 Optimised"


_LEVEL_RANK = {
    "L1 Developing": 1,
    "L2 Healthy": 2,
    "L3 Managed": 3,
    "L4 Optimised": 4,
}


def lowest_level(levels: Iterable[LevelOrUnassessed]) -> LevelOrUnassessed:
    """Return the lowest level from a set, ignoring 'Excluded' but propagating 'Awaiting'."""
    levels = list(levels)
    if any(l == "Awaiting completion" for l in levels):
        return "Awaiting completion"
    rated = [l for l in levels if l in _LEVEL_RANK]
    if not rated:
        return "Excluded (all N/A)"
    return min(rated, key=lambda l: _LEVEL_RANK[l])


def dimension_level(
    question_levels: Iterable[LevelOrUnassessed],
) -> LevelOrUnassessed:
    """Dimension level is the lowest question level."""
    return lowest_level(question_levels)


def app_level(
    dimension_levels: Iterable[LevelOrUnassessed],
) -> LevelOrUnassessed:
    """App level is the lowest dimension level."""
    return lowest_level(dimension_levels)


def secondary_pct_score(
    elements: Iterable[ElementResponse],
    multipliers: Optional[dict[str, float]] = None,
) -> Optional[float]:
    """Compute a percentage score for trend tracking.

    Uses per-level multipliers. Default: L1=0, L2=1.0, L3=1.25, L4=1.5.
    Returns None if there are no answerable elements.
    """
    if multipliers is None:
        multipliers = {"L1": 0.0, "L2": 1.0, "L3": 1.25, "L4": 1.5}

    elements = list(elements)
    answered = [e for e in elements if e.response in ("Yes", "No", "Not Sure")]
    if not answered:
        return None

    earned = sum(
        multipliers[e.level] for e in answered if e.response == "Yes"
    )
    # Denominator: all answered elements assumed to be at the highest possible level
    max_possible = len(answered) * multipliers["L4"]
    if max_possible == 0:
        return None
    return earned / max_possible


# Example self-test when run as a script
if __name__ == "__main__":
    # Q01 with all L2 elements Yes, no L1 gaps, no L3/L4 → L2 Healthy
    elements = [
        ElementResponse("Q01-E01", "L1", "No"),
        ElementResponse("Q01-E02", "L1", "No"),
        ElementResponse("Q01-E03", "L1", "No"),
        ElementResponse("Q01-E04", "L2", "Yes"),
        ElementResponse("Q01-E05", "L2", "Yes"),
        ElementResponse("Q01-E06", "L2", "Yes"),
        ElementResponse("Q01-E07", "L2", "Yes"),
        ElementResponse("Q01-E08", "L2", "Yes"),
        ElementResponse("Q01-E09", "L2", "Yes"),
        ElementResponse("Q01-E10", "L3", "No"),
        ElementResponse("Q01-E11", "L3", "No"),
        ElementResponse("Q01-E12", "L3", "No"),
        ElementResponse("Q01-E13", "L3", "No"),
        ElementResponse("Q01-E14", "L4", "No"),
        ElementResponse("Q01-E15", "L4", "No"),
        ElementResponse("Q01-E16", "L4", "No"),
        ElementResponse("Q01-E17", "L4", "No"),
    ]
    print("Q01 (all L2 Yes):", question_level(elements))
    assert question_level(elements) == "L2 Healthy"

    # Q01 with one L1 gap acknowledged
    elements_with_gap = list(elements)
    elements_with_gap[0] = ElementResponse("Q01-E01", "L1", "Yes")
    print("Q01 (L1 gap acknowledged):", question_level(elements_with_gap))
    assert question_level(elements_with_gap) == "L1 Developing"

    # Awaiting
    elements_partial = list(elements)
    elements_partial[5] = ElementResponse("Q01-E06", "L2", None)
    print("Q01 (one blank):", question_level(elements_partial))
    assert question_level(elements_partial) == "Awaiting completion"

    print("\nself-test passed")
