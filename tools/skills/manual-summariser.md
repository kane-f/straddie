# Skill: Manual Summariser

## Job

Turn a manufacturer manual (appliance or technology) into short,
guest-oriented instructions, while keeping a link to the full manual for
anyone who needs it.

## Inputs

- A manual (PDF, or a link to one) classified as belonging to a specific
  appliance/technology page.

## Outputs

- A short "Quick Start" / "Common Tasks" summary in guest language (see
  the appliance page template's Manual section) — the handful of things a
  guest would actually want to do, not a restatement of the whole manual.
- The manufacturer, model number, and a direct link to the manual PDF.
- A one- or two-line "you probably don't need the manual, but here's the
  relevant bit" note.

## Constraints

- Don't invent capabilities the manual doesn't describe.
- Don't reproduce large verbatim sections of the manual — summarise, and
  link out for detail.
- If the model number or manufacturer can't be identified from the
  document, leave it as a flagged placeholder rather than guessing.

## Hands off to

[Content Merger](content-merger.md), targeting the relevant
`docs/appliances/*.md` or `docs/technology/*.md` page.
