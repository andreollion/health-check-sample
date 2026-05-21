"""GIC Application Health Check — Pre-fill Pipeline.

Stage 1: extract structured data from source artefacts (uses gic-source-extractors skill)
Stage 2: answer rubric questions per the per-app data (uses gic-app-health-check skill)
Stage 3: populate the v0.9 Checklist Excel template

See README.md for usage.
"""
__version__ = "0.1.0"
