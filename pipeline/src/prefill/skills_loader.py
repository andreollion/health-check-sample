"""Skills loader — reads content from the gic-app-health-check and
gic-source-extractors skill bundles.

The pipeline references skill content (rubric data, schema, extraction guides)
rather than duplicating it. This loader provides a clean Python API for that.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class HealthCheckSkill:
    skill_dir: Path
    questions: dict        # parsed assets/questions.json
    level_definitions: dict  # parsed assets/level-definitions.json
    element_source_routing: dict  # parsed assets/element-source-routing.json

    def reference(self, name: str) -> str:
        """Read and return the text of one of the reference docs.

        Example: skill.reference("scoring") returns the contents of
        references/scoring.md.
        """
        path = self.skill_dir / "references" / f"{name}.md"
        if not path.exists():
            raise FileNotFoundError(f"No reference '{name}' in {self.skill_dir}")
        return path.read_text(encoding="utf-8")

    @property
    def all_questions(self) -> list[dict]:
        return self.questions["questions"]

    def question_by_id(self, qid: str) -> dict:
        for q in self.questions["questions"]:
            if q["qid"] == qid:
                return q
        raise KeyError(f"Unknown QID: {qid}")

    def elements_for(self, qid: str) -> list[dict]:
        return self.question_by_id(qid)["elements"]

    def level_def(self, dimension: str, level: str) -> str:
        return self.level_definitions["definitions"][dimension][level]


@dataclass(frozen=True)
class SourceExtractorsSkill:
    skill_dir: Path
    schema: dict  # parsed assets/schema.json

    def reference(self, name: str) -> str:
        path = self.skill_dir / "references" / f"{name}.md"
        if not path.exists():
            raise FileNotFoundError(f"No reference '{name}' in {self.skill_dir}")
        return path.read_text(encoding="utf-8")


def load_health_check_skill(skill_dir: Path) -> HealthCheckSkill:
    """Load the gic-app-health-check skill from disk."""
    skill_dir = Path(skill_dir)
    assets = skill_dir / "assets"

    questions = _read_json(assets / "questions.json")
    level_definitions = _read_json(assets / "level-definitions.json")
    routing = _read_json(assets / "element-source-routing.json")

    return HealthCheckSkill(
        skill_dir=skill_dir,
        questions=questions,
        level_definitions=level_definitions,
        element_source_routing=routing,
    )


def load_source_extractors_skill(skill_dir: Path) -> SourceExtractorsSkill:
    """Load the gic-source-extractors skill from disk."""
    skill_dir = Path(skill_dir)
    assets = skill_dir / "assets"
    schema = _read_json(assets / "schema.json")
    return SourceExtractorsSkill(skill_dir=skill_dir, schema=schema)


def _read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing skill asset: {path}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)
