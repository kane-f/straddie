#!/usr/bin/env python3
"""Render a contact sheet of every room's plaque background colour, using
the same fonts/type treatment as the real plaques, for reviewing the
palette before locking it in.

Usage:
    python3 plaques/swatches.py

Writes plaques/output/swatches.png (gitignored, like everything else in
plaques/output/ — this is a review artifact, not something to commit).
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate as g  # noqa: E402 — needs sys.path set up first

COLS, ROWS = 3, 4
CELL_W, CELL_H = 460, 340
GAP = 20
MARGIN = 40
HEADER_H = 110

SHEET_W = MARGIN * 2 + CELL_W * COLS + GAP * (COLS - 1)
SHEET_H = HEADER_H + MARGIN * 2 + CELL_H * ROWS + GAP * (ROWS - 1)


def draw_swatch(sheet: Image.Image, x: int, y: int, *, color, kicker, name, color_name, hex_code):
    ink, accent = g.ink_and_accent(color)

    draw = ImageDraw.Draw(sheet)
    cell = Image.new("RGB", (CELL_W, CELL_H), color)
    sheet.paste(cell, (x, y))

    cx = x + CELL_W // 2
    cy = y + CELL_H // 2

    if kicker:
        kicker_font = g.load_font(g.FONT_SANS, 22, index=2)
        g.draw_tracked_text(draw, cx, cy - 62, kicker.upper(), kicker_font, accent, tracking=5)

    name_font = g.fit_font(draw, name, g.FONT_SERIF, 0, start_size=64, max_width=CELL_W - 60, min_size=32)
    g.draw_tracked_text(draw, cx, cy - 20, name, name_font, ink)

    draw.line([(cx - 40, cy + 14), (cx + 40, cy + 14)], fill=accent, width=2)

    label_font = g.load_font(g.FONT_SANS, 18, index=0)
    g.draw_tracked_text(draw, cx, cy + 42, color_name.upper(), label_font, ink, tracking=3)

    hex_font = g.load_font(g.FONT_SANS, 16, index=0)
    g.draw_tracked_text(draw, cx, cy + 70, hex_code.upper(), hex_font, accent, tracking=2)

    draw.rectangle([(x, y), (x + CELL_W - 1, y + CELL_H - 1)], outline=(0, 0, 0, 40), width=1)


def main():
    rooms = g.load_rooms()
    entries = [
        {
            "kicker": r.get("kicker"),
            "name": r["name"],
            "color_name": r["color_name"],
            "hex": r["color"],
            "color": g.hex_to_rgb(r["color"]),
        }
        for r in rooms
    ]
    entries.append(
        {
            "kicker": None,
            "name": "Wi-Fi",
            "color_name": g.WIFI_COLOR_NAME,
            "hex": "#%02x%02x%02x" % g.WIFI_COLOR,
            "color": g.WIFI_COLOR,
        }
    )

    sheet = Image.new("RGB", (SHEET_W, SHEET_H), (245, 242, 235))
    draw = ImageDraw.Draw(sheet)

    title_font = g.load_font(g.FONT_SANS, 30, index=2)
    g.draw_tracked_text(
        draw, SHEET_W // 2, HEADER_H // 2, "PLAQUE COLOUR PALETTE — REVIEW", title_font, g.TEAL, tracking=3
    )

    for i, entry in enumerate(entries):
        col, row = i % COLS, i // COLS
        x = MARGIN + col * (CELL_W + GAP)
        y = HEADER_H + MARGIN + row * (CELL_H + GAP)
        draw_swatch(
            sheet,
            x,
            y,
            color=entry["color"],
            kicker=entry["kicker"],
            name=entry["name"],
            color_name=entry["color_name"],
            hex_code=entry["hex"],
        )

    output_path = g.OUTPUT_DIR / "swatches.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)
    print(f"Wrote {output_path.relative_to(g.REPO_ROOT)}")


if __name__ == "__main__":
    main()
