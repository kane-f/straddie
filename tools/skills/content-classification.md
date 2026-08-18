# Skill: Content Classification

## Job

Decide where each unit of extracted content belongs in the information
architecture.

## Inputs

- Structured extraction from [Content Ingestion](content-ingestion.md).

## Outputs

- Each unit tagged with a category and target location, for example:

  | Category | Example target |
  | --- | --- |
  | House / room | `docs/house/kitchen/index.md` |
  | Appliance | `docs/appliances/<appliance>.md` |
  | Technology | `docs/technology/index.md` |
  | Before you come | `docs/before-you-come/index.md` |
  | Before you leave / checkout | `docs/before-you-leave/checkout.md` |
  | Island | `docs/island/<subsection>/index.md` |
  | Help / emergency | `docs/help/index.md` |
  | Other | flagged for human placement |

## Constraints

- When a unit could plausibly belong in more than one place (e.g. a
  dishwasher tip that's both a kitchen quirk and an appliance instruction),
  classify it to the canonical appliance/technology page and note where it
  should be cross-linked from — don't duplicate it.
- Don't invent a room or category that doesn't already exist in `docs/`
  just to have somewhere to put content. If nothing fits, flag it as
  "Other" for a human to decide.

## Hands off to

[Content Merger](content-merger.md) (text), [Manual Summariser](manual-summariser.md)
(manuals), or [Image Processor](image-processor.md) (photos).
