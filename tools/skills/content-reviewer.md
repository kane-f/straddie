# Skill: Content Reviewer

## Job

Produce a concise, human-readable summary of a proposed change before it's
merged — the last step before a person approves a PR.

## Inputs

- The Git diff produced by [Content Merger](content-merger.md) and
  [Navigation Manager](navigation-manager.md) for one ingestion run.

## Outputs

A short report (suitable as a PR description) covering:

- **New content** — pages or sections added.
- **Changed content** — what was updated on existing pages, and why.
- **Conflicting information** — anywhere two sources disagreed and a
  decision is needed.
- **Questions requiring human confirmation** — anything ingested content
  implied but didn't confirm outright.
- **Suggested improvements** — optional, clearly separated from the
  required review items above.

## Constraints

- This report gates publishing. Nothing from an ingestion run reaches
  `main` without a human reading this and approving the PR (see the
  branch/PR workflow rule in `CLAUDE.md`).
- Keep it scannable — this is read by a busy human, not another agent.
