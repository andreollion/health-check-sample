"""Stage 3: Excel populator.

Loads the v0.9 Checklist template, walks 03_Assessment row by row, matches
each criteria-element row to the corresponding ElementResponse, and writes:
  - col E (Response): Yes / No / N/A / Not Sure
  - col F (Link or Brief Note): justification text

Also populates 02_App_Profile from app_facts.app / app_facts.identity.

Public entry point: `populate_checklist()`.
"""
from __future__ import annotations

from .excel_writer import populate_checklist

__all__ = ["populate_checklist"]
