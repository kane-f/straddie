# AI/Agent skills

This directory defines the focused skills/agents that maintain this guide.
They're specs for now — role, inputs, outputs, and constraints — not yet
wired up to an ingestion pipeline. That comes later, once real source
documents are ingested (see the root `ingest/` folder and its future
workflow).

The intended pipeline, once built:

```
ingest/<new file>
    → Content Ingestion
    → Content Classification
    → Content Merger  ──┐
    → Manual Summariser ┤ (as needed, per document type)
    → Image Processor  ─┘
    → Navigation Manager
    → Content Reviewer  → git diff for human review → merge → publish
```

`Quality Checker` runs independently, on demand and in CI
(`scripts/check_content.py` is its first, minimal implementation).

## Skills

| Skill | Job |
| --- | --- |
| [Content Ingestion](content-ingestion.md) | Reads a dropped file, figures out what it contains |
| [Content Classification](content-classification.md) | Decides where each piece of content belongs |
| [Content Merger](content-merger.md) | Updates Markdown without duplicating or losing information |
| [Manual Summariser](manual-summariser.md) | Turns manufacturer manuals into guest-facing instructions |
| [Image Processor](image-processor.md) | Names, compresses, and places images |
| [Navigation Manager](navigation-manager.md) | Keeps `mkdocs.yml` nav in sync with `docs/` |
| [Quality Checker](quality-checker.md) | Catches broken links, missing metadata, duplication, drift |
| [Content Reviewer](content-reviewer.md) | Summarises a proposed change for human approval |

## Shared rules

Every skill in this directory follows the same constraints as the rest of
this repo (see `CLAUDE.md`):

- Never invent house information, appliance capabilities, contact details,
  or island recommendations. Unknown information is flagged, not filled in.
- Never write secrets (passwords, keys, credentials) into `docs/`.
- Never publish AI-generated content directly to `main`. Propose changes on
  a branch as a reviewable diff/PR.
- Prefer merging into existing pages over creating near-duplicate ones.
