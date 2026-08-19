# Skill: Content Ingestion

## Job

Read a file dropped into `ingest/` and work out what useful information it
contains, before anything is classified, merged, or published.

## Inputs

- A single file from `ingest/` — Markdown, PDF, Word document, plain text,
  image/photo, appliance manual, or an existing house guide.

## Outputs

- A structured extraction of the file's content: distinct facts,
  instructions, contact details, recommendations, and media — each as a
  discrete, taggable unit rather than one large blob.
- A short note on anything that couldn't be extracted cleanly (e.g. a
  scanned page with unclear text, a table that didn't parse) so it can be
  checked by a human.

## Constraints

- Extract, don't editorialise. Don't summarise away specific details
  (model numbers, phone numbers, exact instructions) that a guest or the
  next skill in the pipeline will need.
- Don't discard information just because it looks redundant with existing
  content — that judgement belongs to Content Merger, which can see both
  sides.
- Flag anything that looks like a secret (password, key, credential) and
  exclude it from the extraction rather than passing it downstream.

## Hands off to

[Content Classification](content-classification.md).
