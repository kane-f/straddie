# Skill: Quality Checker

## Job

Catch structural and content problems before they reach guests. Runs on
demand and in CI.

## Checks

- Broken internal links.
- Missing images (a reference with no matching file).
- Missing or incomplete front matter metadata.
- Duplicate content across pages (same instructions copy-pasted instead of
  linked).
- Orphan pages (not reachable from `nav` or any other page).
- Inconsistent terminology (e.g. "wifi" vs "Wi-Fi" vs "WiFi").
- Outdated content (`last_reviewed` far in the past relative to a house
  change, or a `status: draft` page that's been linked from the nav as if
  finished).
- Missing manuals where an appliance page implies one exists.
- Missing contact information on the Help page.
- Incorrect/out-of-sync navigation (see
  [Navigation Manager](navigation-manager.md)).

## Current implementation

`scripts/check_content.py` is the first, minimal version: it checks every
page has a top-level heading and that relative links resolve. It runs in
`.github/workflows/deploy.yml` before every build. The rest of the checks
above are the roadmap for extending that script (or replacing it with a
proper skill) as the site grows.

## Constraints

- Fail the build only on things that would actually break the published
  site (broken links, missing images). Everything else is a warning —
  placeholder content is expected while the site is still being filled in.
