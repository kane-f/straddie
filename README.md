# The Lookout Beach House — Guest Guide

A mobile-first guest guide for The Lookout Beach House, Point Lookout, North
Stradbroke Island — built with [MkDocs](https://www.mkdocs.org/) and
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/), hosted
as a static site on GitHub Pages.

The goal is convenience: a guest standing in a room with a phone should be
able to find what they need in 10–20 seconds, not read a manual.

**Status:** this is the foundation — repository structure, theme, navigation,
and deployment are set up, but the real house/island content hasn't been
imported yet. Every content page currently says so.

## Repository structure

```
.
├── docs/                  # Site content (source of truth)
│   ├── index.md           # Welcome
│   ├── before-you-come/
│   ├── house/              # Room-by-room guides
│   │   ├── kitchen/, living/, dining/, bedrooms/, bathrooms/, outdoor/, laundry/
│   ├── appliances/         # One page per appliance, linked from room pages
│   ├── technology/         # Wi-Fi, smart home, TV, sound
│   ├── island/              # Beaches, food, things to do, practical info
│   ├── before-you-leave/   # Checkout checklist, incl. bins
│   ├── help/                # Contacts, emergencies
│   ├── gallery/             # Photo gallery
│   └── assets/images/       # Images referenced from docs/
├── templates/               # Copy these when adding a new room/appliance page
├── tools/skills/             # Specs for the AI skills that maintain this repo
├── scripts/                 # check_content.py — link/heading validation
├── ingest/                   # Drop source documents here (gitignored — see below)
├── overrides/                # Material theme overrides (currently empty)
├── .github/workflows/        # Build + deploy to GitHub Pages
├── mkdocs.yml
└── requirements.txt
```

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Then open <http://127.0.0.1:8000>. Pages reload as you edit.

To check content quality (broken links, missing headings) the same way CI
does:

```bash
python scripts/check_content.py
```

To build the static site into `site/` (matches what CI publishes):

```bash
mkdocs build --strict
```

## Content workflow

1. **Never commit directly to `main`.** Create a branch, make changes, open
   a PR. See `CLAUDE.md`.
2. Content lives entirely in `docs/` as Markdown with YAML front matter
   (`title`, `description`, `section`, `tags`, `last_reviewed`, `source`,
   `status`). `status` is one of `draft`, `review`, `published`.
3. Room pages (`docs/house/**`) follow `templates/room-page-template.md`.
   Appliance/technology pages follow
   `templates/appliance-page-template.md`. Copy the template, don't start
   from a blank page.
4. Room pages should **link** to the canonical appliance/technology page
   rather than repeating instructions.
5. Merging to `main` triggers `.github/workflows/deploy.yml`, which
   validates the content, builds the site, and deploys it to GitHub Pages.

## Adding real content (the ingestion workflow)

This is designed so that maintaining the guide is eventually as simple as:

> Drop a document into `ingest/` → review the proposed changes → merge →
> the guide updates.

- `ingest/` is **gitignored** — nothing in it is ever committed. It's a
  local working folder for dropping source material (existing guides,
  appliance manuals, photos) before it's turned into reviewed Markdown
  under `docs/`.
- The intended pipeline and the skills that run it (content ingestion,
  classification, merging, manual summarising, image processing,
  navigation updates, quality checks, and a final human-readable review
  report) are specified in [`tools/skills/`](tools/skills/README.md).
- Nothing from `ingest/` is published without a human reviewing the
  resulting PR — see the Content Reviewer skill.

Ingestion isn't wired up yet; the two existing guides that will seed this
site are still sitting locally in `ingest/`, to be processed as a separate
step.

## Rules

See [`CLAUDE.md`](CLAUDE.md) for the working agreements this repo follows
(branch/PR workflow, no secrets committed — this repo is public).
