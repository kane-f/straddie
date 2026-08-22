# Room plaques

Generates print-ready 5x7" door plaques: a background photo, the room
name, and a QR code linking to that room's page in the guest guide.
Print each as a 5x7" photo, mount in a frame, and stick it on the wall
near the room's door.

This is a print asset pipeline, separate from the website — nothing here
gets deployed by `mkdocs build`. For the full design rationale (palette,
layout, typography, contrast rules), see
[plaques/DESIGN-SYSTEM.md](DESIGN-SYSTEM.md) — this file is the quick
start.

## Quick start

```bash
pip install -r plaques/requirements.txt
python3 plaques/generate.py kitchen          # one room
python3 plaques/generate.py --all            # every room
python3 plaques/generate.py --list           # see available slugs
```

Output lands in `plaques/output/` as 1500x2100px PNGs — 5x7" at 300 DPI,
ready to send to a photo lab. Room plaques are tracked in git (they're
the actual deliverable); `wifi.png` and `swatches.png` are gitignored —
see [Why the Wi-Fi output isn't committed](#why-the-wi-fi-output-isnt-committed).

## The design system

Every plaque shares one template (`render_card()` in `generate.py`) so
they read as a set once framed around the house — a solid colour card
with an amber (or bronze, on pale cards) frame line inset from the edge,
"THE LOOKOUT BEACH HOUSE" up top, the room photo as its own
rounded-corner panel (not a full-bleed background — there's no
legibility fight between photo and text), then the room name in Didot
serif and a white QR card below it. Nothing ever crosses the frame line.

Each room has its own background colour, drawn from the house's official
Coastal Colour Palette (Sea Glass for the Kitchen, Sunset Clay for
Dining, Sunlit Glow for the Cylinder bedroom, and so on) — full palette,
source, and the contrast rules behind it are in
**[plaques/DESIGN-SYSTEM.md](DESIGN-SYSTEM.md)**. Run
`python3 plaques/swatches.py` to render a review sheet of the whole
palette (written to `plaques/output/swatches.png`, gitignored — it's a
working file, not a deliverable) before generating real plaques from a
colour change.

Fonts are constants at the top of `generate.py`
(`FONT_SERIF`/`FONT_SANS`) — currently macOS system fonts (Didot,
Futura), so if you're generating on Linux/Windows you'll need to point
those at substitutes you have installed.

## Adding or changing a room

Edit `plaques/rooms.yml`. Each entry is:

```yaml
- slug: kitchen                # output filename: plaques/output/kitchen.png
  name: Kitchen                # large text on the plaque
  kicker: Bedroom               # optional small-caps text above the name
  url: house/kitchen/           # path relative to site_url in mkdocs.yml —
                                 # the QR links to site_url + this path
  background: docs/assets/images/house/kitchen/kitchen-island-and-cooktop.jpg
  color: "#B3D6CE"              # background colour — see DESIGN-SYSTEM.md
  color_name: Sea Glass
```

Then run `python3 plaques/generate.py <slug>`.

**Backgrounds:** the current entries reuse existing room-gallery photos as
placeholders. The photo panel crops to roughly 4:3 (centred), which suits
most of the existing gallery shots reasonably well — but the crop is
always centred, so keep the room's key feature in the middle of the
frame. When new photos are shot specifically for the plaques, a shot with
some breathing room on all four sides will crop the most predictably.

## The Wi-Fi plaque

```bash
cp plaques/wifi.example.yml plaques/wifi.local.yml
# edit plaques/wifi.local.yml with the real network name/password
python3 plaques/generate.py --wifi
```

Same template, but the body shows the network name and password as text
(for anyone without a camera handy) plus a QR code that auto-connects
compatible phones.

### Why the Wi-Fi output isn't committed

This repo is public, and the Wi-Fi QR code encodes the password
directly — so the *image*, not just `wifi.local.yml`, is a secret. Both
`plaques/wifi.local.yml` and `plaques/output/wifi.png` are gitignored.
Generate locally, print, done — nothing Wi-Fi-related should ever be
committed. Room plaques don't have this problem and are tracked
normally.

## Printing

- Order as a standard 5x7" photo print (matte finish resists glare from
  the QR code better than glossy).
- Any 5x7" frame works — the amber inset line in the design leaves a
  natural mat/border so the print doesn't feel cropped by the frame.
