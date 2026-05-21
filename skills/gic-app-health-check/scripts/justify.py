"""Generate the Justification string for a question's level.

Format:
  L1 gaps: N · L2: y/z (Y%) · L3: y/z (Y%) · L4: y/z (Y%)
  [optionally appended:] · Not Sure: N (follow-up needed)
"""
from __future__ import annotations

from collections import Counter
from typing import Iterable

# Local import — works when run as a script or imported as a module
try:
    from .score import ElementResponse  # type: ignore
except (ImportError, ValueError):
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from score import ElementResponse  # type: ignore


def justification(elements: Iterable[ElementResponse]) -> str:
    """Generate the Justification string for a question's element responses."""
    elements = list(elements)

    # Counts per level (excluding N/A from denominator)
    def lvl_counts(level: str) -> tuple[int, int]:
        at_level = [e for e in elements if e.level == level]
        non_na = [e for e in at_level if e.response != "N/A"]
        n_yes = sum(1 for e in non_na if e.response == "Yes")
        return n_yes, len(non_na)

    # L1 — count of "Yes" (gaps acknowledged)
    n_l1_yes = sum(1 for e in elements if e.level == "L1" and e.response == "Yes")

    l2_y, l2_t = lvl_counts("L2")
    l3_y, l3_t = lvl_counts("L3")
    l4_y, l4_t = lvl_counts("L4")

    def pct(y: int, t: int) -> str:
        if t == 0:
            return "—"
        return f"{int(round(100 * y / t))}%"

    parts = [
        f"L1 gaps: {n_l1_yes}",
        f"L2: {l2_y}/{l2_t} ({pct(l2_y, l2_t)})",
        f"L3: {l3_y}/{l3_t} ({pct(l3_y, l3_t)})",
        f"L4: {l4_y}/{l4_t} ({pct(l4_y, l4_t)})",
    ]

    # Append Not Sure count if any
    n_not_sure = sum(1 for e in elements if e.response == "Not Sure")
    if n_not_sure > 0:
        parts.append(f"Not Sure: {n_not_sure} (follow-up needed)")

    return " · ".join(parts)


# Example self-test
if __name__ == "__main__":
    # Q01 with all L2 elements Yes, 1 Not Sure
    elements = [
        ElementResponse("Q01-E01", "L1", "No"),
        ElementResponse("Q01-E02", "L1", "No"),
        ElementResponse("Q01-E03", "L1", "No"),
        ElementResponse("Q01-E04", "L2", "Yes"),
        ElementResponse("Q01-E05", "L2", "Not Sure"),
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
    j = justification(elements)
    print(j)
    assert "L1 gaps: 0" in j
    assert "L2: 5/6" in j
    assert "Not Sure: 1" in j
    print("\nself-test passed")
