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
its own identity through colour, tied to a real element of the island's
beaches rather than an arbitrary swatch.

## Colour palette

One background colour per room, each named after a literal beach/coastal
element rather than an abstract colour-story name — the point is that
someone looking at "Sunset Clay" or "Driftwood Sand" should be able to
picture the thing, not just the hex code.

| Room | Token | Hex | Card |
|---|---|---|---|
| Kitchen | Lagoon Turquoise | `#35b6ad` | light |
| Dining Room | Sunset Clay | `#964c2c` | dark |
| Living Room — Upstairs | Ocean Blue | `#276b9b` | dark |
| Living Room — Downstairs | Palm Green | `#327b57` | dark |
| Balcony | Dusk Rose | `#9b505c` | dark |
| Bathroom | Sea Foam | `#baded5` | light |
| Laundry | Driftwood Sand | `#c1ac90` | light |
| Bedroom — Main | Deep Tide | `#212f50` | dark |
| Bedroom — Flinders | Flinders Surf | `#25799d` | dark |
| Bedroom — Frenchmans | Frenchmans Lagoon | `#227769` | dark |
| Bedroom — Cylinder | Cylinder Gold | `#e0b152` | light |
| Wi-Fi *(utility, not a room)* | Night Sky | `#1d1631` | dark |

The three beach-named bedrooms (Flinders, Frenchmans, Cylinder) each draw
their colour from that actual beach's character — Flinders' surf, the
calm emerald water at Frenchmans, Cylinder's golden sand and sunrise
headland. Main (not beach-named) gets the moodiest, most premium tone,
fitting the primary suite. Wi-Fi deliberately sits outside the beach hue
range (indigo) so it never gets mistaken for a room.

**On purpose, not every colour is dark.** A real beach spans pale sand
and sea foam as well as deep ocean and night sky — forcing every plaque
to the same dark value read as a generic "moody hotel" palette rather
than a beach. Four colours (Kitchen, Bathroom, Laundry, Cylinder) are
intentionally light.

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
2. Pick a colour that (a) ties to a real beach/coastal element and (b)
   clears the 4.5:1 contrast rule above.
3. Run `python3 plaques/swatches.py` to sanity-check it against the rest
   of the set before generating the full plaque.
4. Run `python3 plaques/generate.py <slug>`.

## Changing the palette

Edit the `color`/`color_name` fields in `rooms.yml`, regenerate
`plaques/swatches.py`, review, then re-run `generate.py --all`. Update
the table at the top of this document to match — it's documentation, not
config, so it won't drift automatically.
