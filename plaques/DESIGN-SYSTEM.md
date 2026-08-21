# Room Plaque Design System

The reference spec for the 5x7" room-door plaques: what the palette
means, how the layout is built, and the rules to follow when adding a
room or changing the look. `plaques/rooms.yml` is the source of truth for
the actual values (colours, names, URLs) — this document explains *why*
they're what they are and how to keep new ones consistent.

For how to run the generator day to day, see [plaques/README.md](README.md).

## Concept

Each plaque is a small, framed piece of house signage: a photo of the
room, its name, and a QR code to the matching page in the guest guide.
The set is meant to read as one family once framed around the house —
same layout, same typography, same brand marks — while each room gets
its own identity through colour, drawn from the house's official
**Coastal Colour Palette** moodboard rather than an invented swatch.

## Colour palette

### Source

The full palette (13 named, hex-specified colours) came in as a
moodboard image via `ingest/` — like all raw ingest material it isn't
committed (see `.gitignore` / `README.md`'s ingest note); this table is
the durable, checked-in record of it:

| Colour | Hex | Tier |
|---|---|---|
| Deep Cornflour Blue | `#26507A` | Primary |
| Light Forest Green | `#7FA17F` | Primary |
| Sandy Taupe | `#C8BCA6` | Primary |
| Ocean Depth | `#1F3D4D` | Secondary |
| Sea Glass | `#6DB7B5` | Secondary |
| Tide Pool | `#A6D3D6` | Secondary |
| Soft Sand | `#E7DFC9` | Secondary |
| Driftwood | `#D8C7A6` | Secondary |
| Dune Grass | `#A8B89A` | Secondary |
| Coastal Green | `#6E8B6F` | Secondary |
| Sea Foam | `#BFD8C6` | Secondary |
| Coastal Sky | `#B7CCE1` | Secondary |
| Sunlit Glow | `#F1D9A6` | Secondary |

### Room mapping

| Room | Colour | Hex | Card |
|---|---|---|---|
| Kitchen | Sea Glass | `#6DB7B5` | light |
| Dining Room | Sandy Taupe | `#C8BCA6` | light |
| Living Room — Upstairs | Coastal Sky | `#B7CCE1` | light |
| Living Room — Downstairs | Light Forest Green | `#7FA17F` | light |
| Balcony | Sunlit Glow | `#F1D9A6` | light |
| Bathroom | Sea Foam | `#BFD8C6` | light |
| Laundry | Driftwood | `#D8C7A6` | light |
| Bedroom — Main | Deep Cornflour Blue | `#26507A` | dark |
| Bedroom — Flinders | Tide Pool | `#A6D3D6` | light |
| Bedroom — Frenchmans | Coastal Green | `#6E8B6F` | dark |
| Bedroom — Cylinder | Soft Sand | `#E7DFC9` | light |
| Wi-Fi *(utility, not a room)* | Ocean Depth | `#1F3D4D` | dark |

`Dune Grass` isn't used by any current room — free to assign if a 12th
area gets a plaque later.

Mapping logic: Flinders (a swimming/surf beach) gets the clear
shallow-water **Tide Pool**; Frenchmans (calm water, bush-backed) gets
the richer **Coastal Green**; Cylinder (its sand and sunrise headland)
gets the palest, warmest neutral, **Soft Sand**. Main — not
beach-named — gets the moodiest, most saturated colour in the whole set,
**Deep Cornflour Blue**, fitting the primary suite. Wi-Fi takes
**Ocean Depth**, the single darkest colour in the palette, so it reads
as clearly apart from every room.

**Most of the palette is pale.** Unlike a hand-picked "one deep jewel
tone per room" approach, the actual Coastal Colour Palette leans light
and muted — closer to painted weatherboard and sun-bleached textiles
than saturated colour blocking. Only two rooms (Main, Wi-Fi) end up
dark-card; light-card is now the norm, not the exception. `Coastal
Green` (Frenchmans) and `Light Forest Green` (Living Room — Downstairs)
sit a little under the 4.5:1 contrast rule below (4.17 and 3.76 against
their better-contrasting ink) — still clearly legible at the room name's
large display size, just not to the same margin as the rest of the set.

### Adaptive ink and accent

Because the palette spans light and dark, plaque text can't be a fixed
colour. `ink_and_accent()` in `generate.py` picks automatically, per
colour:

1. Compute WCAG contrast ratio of the card colour against white and
   against the brand dark teal (`#0b3d3f`).
2. Whichever wins becomes the **ink** (room name, subtitle) — white on a
   dark card, dark teal on a light one.
3. The **accent** (rules, kicker text, photo/frame keylines) follows the
   same choice: bright amber (`#f4c76b`) on dark cards, a deeper bronze
   amber (`#794715`) on light ones — pale amber nearly disappears against
   a pale card.

This is computed at generate-time from the hex in `rooms.yml`, not
hand-picked per room — adding a new room only means adding one colour,
never a text-colour decision. `plaques/swatches.py` renders every card
through the same function, so the review sheet always matches what the
real plaques will do.

**Rule of thumb when adding a colour:** aim for a contrast ratio of at
least 4.5:1 against *either* white or `#0b3d3f` (that's what
`ink_and_accent()` needs to make a clean choice). `generate.py` doesn't
enforce this automatically — check by eye against the swatch sheet, or
compute it (`contrast_ratio()` is already in `generate.py`).

## Layout

5x7" print, 1500x2100px at 300 DPI. One amber (or bronze, on light cards)
frame line inset from the edge; everything else is drawn inside it in
fixed-height "slots" stacked top to bottom, so nothing can ever cross the
frame:

```
┌─────────────────────────────┐
│   THE LOOKOUT BEACH HOUSE    │  ← header: house label + rule
│  ┌─────────────────────────┐ │
│  │                         │ │
│  │     room photo          │ │  ← rounded-corner panel, ~4:3
│  │   (rounded corners)     │ │
│  │                         │ │
│  └─────────────────────────┘ │
│           BEDROOM             │  ← kicker (optional)
│          Flinders             │  ← room name, Didot
│              ──                │  ← rule
│    SCAN FOR THE GUEST GUIDE   │  ← subtitle
│           ┌──────┐            │
│           │  QR  │            │  ← white QR card
│           └──────┘            │
└─────────────────────────────┘
```

The photo is a standalone panel, not a full-bleed background — this was
a deliberate change after an earlier version put text over the photo
with a gradient scrim, which let the QR code overlap the outer frame on
long names. Separating photo from text/QR removes that failure mode
entirely: the footer's height is computed first from fixed slot
constants, the photo gets whatever space is left, and an assertion in
`render_card()` catches it if a future edit ever makes the footer too
tall to fit.

Key constants (all in `generate.py`):

| Constant | Value | What it controls |
|---|---|---|
| `FRAME_MARGIN` / `FRAME_PAD` | 60 / 30px | frame line inset; gap from frame to content |
| `HEADER_H` | 100px | house label + its rule |
| `PHOTO_RADIUS` | 26px | photo corner rounding |
| `KICKER_SLOT` / `NAME_SLOT` | 64 / 190px | reserved even when a room has no kicker, so every plaque's name sits at the same height |
| `QR_SIZE` / `QR_PAD` | 300 / 30px | QR module size / white-card padding |

## Typography

Both are macOS system fonts (see `FONT_SERIF`/`FONT_SANS` in
`generate.py` if generating elsewhere):

- **Didot** (serif) — the room name and "Wi-Fi". Large, editorial, does
  the work of making each plaque feel considered rather than printed
  off a template.
- **Futura** (sans, small-caps style via `tracked_text_width`/
  `draw_tracked_text`) — house label, kicker, subtitle, QR caption. Pillow
  has no native letter-spacing, so `draw_tracked_text()` draws
  character-by-character with manual tracking to fake it.

Room names shrink-to-fit (`fit_font()`) rather than wrapping, so a long
name like "Downstairs Living Room" — split here into kicker
"Downstairs" + name "Living Room" — never breaks the layout.

## QR codes

- **Room plaques:** `site_url` (from `mkdocs.yml`) + the room's `url` in
  `rooms.yml`, e.g. `https://kane-f.github.io/straddie/house/kitchen/`.
  `generate.py` reads `site_url` straight out of `mkdocs.yml` with a
  regex (it can't use a plain YAML parser — `mkdocs.yml` has custom
  `!!python/name:` tags for its Markdown extensions), so the QR targets
  can never drift out of sync with the real site config.
- **Wi-Fi plaque:** a `WIFI:T:<security>;S:<ssid>;P:<password>;;` payload
  (the standard Wi-Fi QR format that auto-connects most phones), built
  from `plaques/wifi.local.yml` — which is gitignored and must never be
  committed. See [plaques/README.md](README.md#the-wi-fi-plaque) for why.
- QR modules render in dark teal on white (`make_qr_image()`), always,
  regardless of card colour — they sit on their own white card
  (`paste_qr_card()`), so contrast is never a per-room concern.

## Adding a room

1. Add an entry to `plaques/rooms.yml`: `slug`, `name`, optional
   `kicker`, `url`, `background`, `color`, `color_name`.
2. Pick a colour — `Dune Grass` (`#A8B89A`) is the one unused colour left
   in the official palette above. If it's already spoken for, either
   reuse a used colour (fine — it just won't be unique to that room) or
   extend the palette with a new named colour that clears the 4.5:1
   contrast rule below.
3. Run `python3 plaques/swatches.py` to sanity-check it against the rest
   of the set before generating the full plaque.
4. Run `python3 plaques/generate.py <slug>`.

## Changing the palette

Edit the `color`/`color_name` fields in `rooms.yml`, regenerate
`plaques/swatches.py`, review, then re-run `generate.py --all`. Update
the table at the top of this document to match — it's documentation, not
config, so it won't drift automatically.
