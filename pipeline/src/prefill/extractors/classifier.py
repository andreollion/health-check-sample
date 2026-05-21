"""Source classifier — decides which source-type extractor to use.

Classification is filename-based. The sources_dir for one app is expected to
look something like:

    sources_dir/
      risk_assessment.pdf            → risk_assessment
      arb_decisions.docx             → arb
      arb_diagram.pptx               → arb
      confluence_runbook.html        → confluence
      sharepoint_architecture.docx   → sharepoint
      github.json                    → github (manifest, handled separately)

If a file's type can't be guessed from filename, we return None and the file
is skipped with a log message.
"""
from __future__ import annotations

from pathlib import Path


_CLASSIFIERS: list[tuple[str, list[str]]] = [
    # (source_type, keyword list to match in lowercased filename)
    ("risk_assessment", ["risk_assessment", "risk-assessment", "riskassessment", "rsa", "risk_a"]),
    ("arb", ["arb_", "_arb", "archboard", "architecture_review", "design_review"]),
    ("confluence", ["confluence", "wiki", "runbook"]),
    ("sharepoint", ["sharepoint", "spo_", "_spo"]),
]


def classify_source(path: Path) -> str | None:
    """Return one of the source_type strings, or None if unknown."""
    name = path.name.lower()

    for source_type, keywords in _CLASSIFIERS:
        if any(kw in name for kw in keywords):
            return source_type

    # Fallback by extension if name didn't match a keyword:
    # - .pdf → assume Risk Assessment unless the name hints otherwise
    # - .html/.htm → assume Confluence
    if path.suffix.lower() == ".pdf":
        return "risk_assessment"
    if path.suffix.lower() in (".html", ".htm"):
        return "confluence"

    return None
