# Skill: Navigation Manager

## Job

Keep `mkdocs.yml`'s `nav` in sync with what actually exists under `docs/`,
whenever [Content Merger](content-merger.md) adds a new page.

## Inputs

- The current `mkdocs.yml`.
- The set of pages added or removed by a pending change.

## Outputs

- An updated `nav` section: new pages added in a sensible position within
  their existing section, matching the section's current ordering
  conventions.

## Constraints

- Don't reorganise existing nav structure beyond what's needed to place
  the new page — minimise diff noise.
- Don't leave orphan pages (a page under `docs/` with no nav entry and no
  inbound link) — that's also checked by
  [Quality Checker](quality-checker.md).
- Don't introduce new top-level nav sections without flagging it — the
  information architecture is intentional; growing it is a judgement call
  for [Content Reviewer](content-reviewer.md) to surface.

## Hands off to

[Content Reviewer](content-reviewer.md).
