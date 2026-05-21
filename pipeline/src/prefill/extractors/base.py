"""Common helpers used by per-source-type extractors.

Each extractor follows the same pattern:
  1. Read raw source content (text/PDF/HTML/JSON)
  2. Build a system + user prompt instructing the LLM to extract structured
     facts matching the schema (per the gic-source-extractors skill)
  3. Call the LLM
  4. Parse JSON out of the response (with tolerant fallback)
  5. Return AppFacts dict

This module provides the shared prompt-building and JSON-extraction logic.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import date
from pathlib import Path
from typing import Any

from ..skills_loader import SourceExtractorsSkill

logger = logging.getLogger(__name__)


# Maximum chars of source content to put into the prompt. Tunable per source.
DEFAULT_MAX_CHARS = 60_000


def build_extraction_prompt(
    source_skill: SourceExtractorsSkill,
    source_type: str,
    source_path: Path,
    source_content: str,
) -> tuple[str, str]:
    """Build (system, user) prompts for one source extraction call.

    The system prompt loads the schema and the source-type-specific guide from
    the skill. The user prompt presents the actual source content.
    """
    schema_json = json.dumps(source_skill.schema, indent=2)
    schema_guide = source_skill.reference("schema")
    source_guide = source_skill.reference(source_type.replace("_", "-"))
    provenance_guide = source_skill.reference("provenance")

    system = (
        "You are a structured-data extraction agent for the GIC Application "
        "Health Check pre-fill pipeline.\n\n"
        "Your job: extract facts from ONE source artefact and return them as JSON "
        "that conforms to the schema below.\n\n"
        f"=== SCHEMA (authoritative) ===\n{schema_json}\n\n"
        f"=== SCHEMA GUIDE ===\n{schema_guide}\n\n"
        f"=== SOURCE GUIDE: {source_type} ===\n{source_guide}\n\n"
        f"=== PROVENANCE RULES ===\n{provenance_guide}\n\n"
        "OUTPUT RULES:\n"
        "1. Return ONE JSON object only — no commentary, no markdown fences, no prose.\n"
        "2. Only include fields you found evidence for. Omit anything you didn't see.\n"
        "3. Every populated leaf field MUST have a matching evidence entry under "
        "   `evidence`, keyed by the dotted path to the field (e.g. "
        "   \"appsec.sast.enabled\").\n"
        "4. Each evidence entry: {source, ref, excerpt (<=200 chars), timestamp}.\n"
        "5. Use the values: \"yes\", \"no\", \"n/a\", \"not_sure\" for tri-state booleans "
        "   (the schema documents which fields are tri-state).\n"
        "6. If a field is genuinely unknown from this source, omit it. Do NOT guess.\n"
    )

    today = date.today().isoformat()
    user = (
        f"Source type: {source_type}\n"
        f"Source path: {source_path.name}\n"
        f"Extraction date: {today}\n\n"
        "=== SOURCE CONTENT ===\n"
        f"{source_content}\n"
        "=== END SOURCE CONTENT ===\n\n"
        "Return the JSON now."
    )
    return system, user


# ---------------------------------------------------------------------------
# JSON extraction from LLM text
# ---------------------------------------------------------------------------

_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def parse_json_from_llm(text: str) -> dict[str, Any]:
    """Tolerantly extract a JSON object from an LLM response."""
    text = text.strip()

    # 1. Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Fenced code block
    m = _JSON_FENCE.search(text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # 3. First-brace-to-last-brace (yolo but works often)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = text[start:end + 1]
        try:
            return json.loads(snippet)
        except json.JSONDecodeError as exc:
            logger.error(f"could not parse JSON from LLM response: {exc}\nsnippet[:300]={snippet[:300]}")
            raise

    raise ValueError(f"No JSON object found in LLM response: {text[:200]!r}")


# ---------------------------------------------------------------------------
# Text reading helpers
# ---------------------------------------------------------------------------

def read_pdf_text(path: Path, max_pages: int = 100) -> str:
    """Extract text from a PDF using PyPDF2."""
    try:
        from PyPDF2 import PdfReader  # type: ignore
    except ImportError as exc:
        raise ImportError("PyPDF2 is required for PDF extraction. pip install PyPDF2") from exc

    reader = PdfReader(str(path))
    chunks = []
    for i, page in enumerate(reader.pages[:max_pages]):
        try:
            chunks.append(page.extract_text() or "")
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"PDF page {i} extraction failed: {exc}")
    return "\n\n".join(chunks)


def read_text_file(path: Path) -> str:
    """Read a plain text / HTML / Markdown file."""
    return path.read_text(encoding="utf-8", errors="replace")


def read_docx_text(path: Path) -> str:
    """Extract text from a .docx by unzipping and reading word/document.xml.
    Avoids the python-docx dependency for a minimal install footprint.
    """
    import xml.etree.ElementTree as ET
    import zipfile

    with zipfile.ZipFile(str(path)) as zf:
        try:
            xml = zf.read("word/document.xml").decode("utf-8", errors="replace")
        except KeyError as exc:
            raise ValueError(f"{path} is not a valid .docx (no word/document.xml)") from exc

    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    root = ET.fromstring(xml)
    paragraphs = []
    for p in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
        text = "".join(t.text or "" for t in p.iter(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
        ))
        if text.strip():
            paragraphs.append(text)
    return "\n".join(paragraphs)


def read_pptx_text(path: Path) -> str:
    """Extract text from a .pptx by unzipping and reading slide XML."""
    import xml.etree.ElementTree as ET
    import zipfile

    a_ns = "http://schemas.openxmlformats.org/drawingml/2006/main"

    out = []
    with zipfile.ZipFile(str(path)) as zf:
        slide_names = sorted([n for n in zf.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")])
        for name in slide_names:
            xml = zf.read(name).decode("utf-8", errors="replace")
            try:
                root = ET.fromstring(xml)
            except ET.ParseError:
                continue
            texts = [t.text or "" for t in root.iter(f"{{{a_ns}}}t")]
            slide_text = "\n".join(t for t in texts if t.strip())
            if slide_text:
                out.append(f"--- {name} ---\n{slide_text}")
    return "\n\n".join(out)


def read_source_text(path: Path, max_chars: int = DEFAULT_MAX_CHARS) -> str:
    """Read any supported source format and truncate to max_chars."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text = read_pdf_text(path)
    elif suffix == ".docx":
        text = read_docx_text(path)
    elif suffix == ".pptx":
        text = read_pptx_text(path)
    elif suffix in (".html", ".htm", ".md", ".txt", ".json"):
        text = read_text_file(path)
    else:
        # Best-effort: try as text
        text = read_text_file(path)

    if len(text) > max_chars:
        logger.warning(f"truncating {path.name} from {len(text)} to {max_chars} chars")
        text = text[:max_chars] + "\n\n[...truncated...]"
    return text
