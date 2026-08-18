# Skill: Content Merger

## Job

Write classified content into the target Markdown file — updating existing
pages in place rather than duplicating them.

## Inputs

- Classified content units and their target file, from
  [Content Classification](content-classification.md).
- The current content of the target file.

## Outputs

- An updated version of the target file, as a diff:
  - New sections/facts added under the right heading.
  - Existing correct information preserved untouched.
  - Superseded information replaced, with the change visible in the diff.
  - Front matter (`last_reviewed`, `source`, `status`) updated.

## Constraints

- Preserve existing useful information. Don't overwrite a detailed,
  correct section with a thinner one just because new source material
  covers the same topic.
- When two sources disagree (e.g. two different Wi-Fi setup steps), don't
  silently pick one — merge both as a flagged conflict for
  [Content Reviewer](content-reviewer.md) to raise.
- Follow the existing page template structure (see
  `templates/room-page-template.md` and `templates/appliance-page-template.md`)
  rather than introducing ad hoc structure.
- Never merge directly to `main`. Output changes on a branch.

## Hands off to

[Navigation Manager](navigation-manager.md), then [Content Reviewer](content-reviewer.md).
