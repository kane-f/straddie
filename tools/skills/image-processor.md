# Skill: Image Processor

## Job

Take a dropped photo and get it into a state where it's useful on the site:
sensibly named, compressed, described, and placed.

## Inputs

- An image file from `ingest/`, with whatever classification context is
  available (which room/appliance/island topic it relates to).

## Outputs

- The image saved under `docs/assets/images/<section>/<slug>/`, with a
  clear, descriptive filename (`kitchen-oven-dial.jpg`, not `IMG_4213.jpg`).
- The image compressed/optimised for web delivery.
- Descriptive alt text.
- A note on where it should be embedded (a specific room/appliance page)
  and, where relevant, that it should also appear in
  [Photo Gallery](../../docs/gallery/index.md).

## Constraints

- Don't duplicate the same image under multiple filenames — reuse one file
  and reference it from multiple pages where needed.
- Don't upscale or otherwise fabricate image content.
- Strip location/device metadata (EXIF) that guests don't need exposed in
  a public repository.

## Hands off to

[Content Merger](content-merger.md), to embed the reference on the target page(s).
