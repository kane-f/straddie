#!/usr/bin/env python3
"""Generate 5x7" room-door plaques: a background photo, the room name, and
a QR code linking to that room's page in the guest guide.

Usage:
    python3 plaques/generate.py --all
    python3 plaques/generate.py kitchen bedroom-main
    python3 plaques/generate.py --wifi

Run `python3 plaques/generate.py --list` to see available room slugs.
See plaques/README.md for the design system and print instructions.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import qrcode
import yaml
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAQUES_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PLAQUES_DIR / "output"

# 5x7" at 300 DPI — print resolution for a photo-lab 5x7 print.
PAGE_W, PAGE_H = 1500, 2100

# Brand palette — matches docs/stylesheets/extra.css / mkdocs.yml theme.
TEAL = (11, 61, 63)
AMBER = (244, 199, 107)
WHITE = (255, 255, 255)
AMBER_DEEP = (121, 71, 21)   # accent on pale (sand/foam) cards — AMBER is too washed out there

# The Wi-Fi plaque isn't a room, so it gets its own colour rather than one
# from rooms.yml — see plaques/DESIGN-SYSTEM.md.
WIFI_COLOR = (29, 22, 49)     # Night Sky
WIFI_COLOR_NAME = "Night Sky"

HOUSE_NAME = "THE LOOKOUT BEACH HOUSE"

FONT_DIR = Path("/System/Library/Fonts/Supplemental")
FONT_SERIF = FONT_DIR / "Didot.ttc"          # room name — index 0 = Regular
FONT_SANS = FONT_DIR / "Futura.ttc"          # labels — index 0 = Medium, 2 = Bold

# --- Layout ---------------------------------------------------------------
# The whole card sits on a solid teal ground, inside one amber frame line
# that everything else — photo, name, QR — is drawn inside of, so nothing
# can ever cross it. Content stacks top to bottom: house label, then a
# rounded-corner photo, then a footer (kicker / name / rule / subtitle /
# QR) using fixed-height "slots" so the layout is the same shape whether
# or not a given room has a kicker.

FRAME_MARGIN = 60   # frame line inset from the page edge
FRAME_PAD = 30       # gap between the frame line and all content
CONTENT_LEFT = FRAME_MARGIN + FRAME_PAD
CONTENT_RIGHT = PAGE_W - FRAME_MARGIN - FRAME_PAD
CONTENT_TOP = FRAME_MARGIN + FRAME_PAD
CONTENT_BOTTOM = PAGE_H - FRAME_MARGIN - FRAME_PAD
CONTENT_WIDTH = CONTENT_RIGHT - CONTENT_LEFT

HEADER_H = 100        # house label + its rule
PHOTO_RADIUS = 26
PHOTO_FOOTER_GAP = 44

KICKER_SLOT = 64
NAME_SLOT = 190
RULE_GAP_BEFORE = 22
RULE_W = 3
RULE_GAP_AFTER = 26
INFO_CARD_H = 220     # Wi-Fi plaque's SSID/password card
INFO_GAP_AFTER = 30
SUBTITLE_SLOT = 50
GAP_BEFORE_QR = 30
QR_SIZE = 300
QR_PAD = 30
QR_CARD = QR_SIZE + QR_PAD * 2


def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _relative_luminance(rgb: tuple) -> float:
    def channel(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(rgb_a: tuple, rgb_b: tuple) -> float:
    la, lb = _relative_luminance(rgb_a) + 0.05, _relative_luminance(rgb_b) + 0.05
    return max(la, lb) / min(la, lb)


def ink_and_accent(card_color: tuple) -> tuple:
    """Pick legible ink (name/subtitle) and accent (rule/kicker/frame)
    colours for a given card background: white ink + bright amber on a
    dark card, or dark-teal ink + deep amber on a pale one — whichever
    pairing contrasts better against this particular colour."""
    if contrast_ratio(card_color, WHITE) >= contrast_ratio(card_color, TEAL):
        return WHITE, AMBER
    return TEAL, AMBER_DEEP


def load_font(path: Path, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    if not path.exists():
        sys.exit(
            f"Font not found: {path}\n"
            "This generator uses macOS system fonts (Didot, Futura). "
            "Edit FONT_SERIF/FONT_SANS in plaques/generate.py to point at "
            "substitutes if you're not running this on a Mac."
        )
    return ImageFont.truetype(str(path), size, index=index)


def site_url() -> str:
    # mkdocs.yml uses custom !!python/name: tags (for markdown extensions)
    # that yaml.safe_load can't parse, so pull this one value out with a
    # regex instead of loading the whole file.
    text = (REPO_ROOT / "mkdocs.yml").read_text()
    match = re.search(r'^site_url:\s*(\S+)\s*$', text, re.MULTILINE)
    if not match:
        sys.exit("Couldn't find site_url in mkdocs.yml")
    return match.group(1).strip().strip('"\'').rstrip("/")


def fit_cover(im: Image.Image, w: int, h: int) -> Image.Image:
    """Resize+crop im to exactly w x h, cropping the longer dimension."""
    im = im.convert("RGB")
    src_ratio = im.width / im.height
    dst_ratio = w / h
    if src_ratio > dst_ratio:
        new_h = h
        new_w = round(h * src_ratio)
    else:
        new_w = w
        new_h = round(w / src_ratio)
    im = im.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    return im.crop((left, top, left + w, top + h))


def rounded_mask(size: tuple, radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [(0, 0), (size[0] - 1, size[1] - 1)], radius=radius, fill=255
    )
    return mask


def tracked_text_width(draw, text, font, tracking):
    if not text:
        return 0
    widths = [draw.textlength(ch, font=font) for ch in text]
    return sum(widths) + tracking * (len(text) - 1)


def draw_tracked_text(draw, center_x, y, text, font, fill, tracking=0):
    """Draw text horizontally centered on center_x, vertically centered on y,
    with `tracking` extra pixels between letters (Pillow has no letter-spacing)."""
    total_w = tracked_text_width(draw, text, font, tracking)
    x = center_x - total_w / 2
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill, anchor="lm")
        x += draw.textlength(ch, font=font) + tracking


def fit_font(draw, text, font_path, index, start_size, max_width, min_size=60):
    size = start_size
    font = load_font(font_path, size, index=index)
    while tracked_text_width(draw, text, font, 0) > max_width and size > min_size:
        size -= 6
        font = load_font(font_path, size, index=index)
    return font


def make_qr_image(data: str, module_color=TEAL) -> Image.Image:
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2, box_size=10)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color=module_color, back_color=WHITE).convert("RGB")


def paste_qr_card(canvas: Image.Image, qr_data: str, center_x: int, top_y: int):
    card_size = QR_CARD
    card = Image.new("RGBA", (card_size, card_size), WHITE + (255,))
    card.putalpha(rounded_mask((card_size, card_size), radius=22))

    qr_img = make_qr_image(qr_data).resize((QR_SIZE, QR_SIZE), Image.NEAREST)
    card.paste(qr_img, (QR_PAD, QR_PAD))

    canvas.alpha_composite(card, (center_x - card_size // 2, top_y))


def footer_height(*, has_kicker: bool, has_info: bool) -> int:
    h = (KICKER_SLOT if has_kicker else 0) + NAME_SLOT
    h += RULE_GAP_BEFORE + RULE_W + RULE_GAP_AFTER
    if has_info:
        h += INFO_CARD_H + INFO_GAP_AFTER
    h += SUBTITLE_SLOT + GAP_BEFORE_QR + QR_CARD
    return h


def draw_header(canvas, draw, ink, accent):
    house_font = load_font(FONT_SANS, 34, index=0)
    label_y = CONTENT_TOP + 34
    draw_tracked_text(draw, PAGE_W // 2, label_y, HOUSE_NAME, house_font, ink, tracking=5)
    rule_y = CONTENT_TOP + 68
    draw.line([(PAGE_W // 2 - 44, rule_y), (PAGE_W // 2 + 44, rule_y)], fill=accent, width=3)


def draw_photo(canvas, background_path: Path, top: int, bottom: int, accent):
    photo = fit_cover(Image.open(background_path), CONTENT_WIDTH, bottom - top).convert("RGBA")
    photo.putalpha(rounded_mask(photo.size, radius=PHOTO_RADIUS))
    canvas.alpha_composite(photo, (CONTENT_LEFT, top))
    ImageDraw.Draw(canvas).rounded_rectangle(
        [(CONTENT_LEFT, top), (CONTENT_RIGHT, bottom)], radius=PHOTO_RADIUS, outline=accent, width=2
    )


def draw_footer(canvas, draw, top: int, *, kicker: str | None, name: str, info: dict | None, qr_data: str, subtitle: str, ink, accent):
    cx = PAGE_W // 2
    y = top

    if kicker:
        kicker_font = load_font(FONT_SANS, 30, index=2)
        draw_tracked_text(draw, cx, y + KICKER_SLOT // 2, kicker.upper(), kicker_font, accent, tracking=6)
        y += KICKER_SLOT

    name_font = fit_font(draw, name, FONT_SERIF, 0, start_size=128, max_width=CONTENT_WIDTH - 60)
    draw_tracked_text(draw, cx, y + NAME_SLOT // 2, name, name_font, ink)
    y += NAME_SLOT

    y += RULE_GAP_BEFORE
    draw.line([(cx - 60, y), (cx + 60, y)], fill=accent, width=RULE_W)
    y += RULE_W + RULE_GAP_AFTER

    if info:
        card_w = CONTENT_WIDTH - 60
        card = Image.new("RGBA", (card_w, INFO_CARD_H), WHITE + (235,))
        card.putalpha(rounded_mask((card_w, INFO_CARD_H), radius=20))
        canvas.alpha_composite(card, (cx - card_w // 2, y))

        label_font = load_font(FONT_SANS, 22, index=2)
        value_font = load_font(FONT_SANS, 40, index=0)
        row_h = INFO_CARD_H // len(info)
        for i, (label, value) in enumerate(info.items()):
            row_cy = y + row_h * i + row_h // 2
            draw_tracked_text(draw, cx, row_cy - 22, label.upper(), label_font, TEAL, tracking=4)
            draw_tracked_text(draw, cx, row_cy + 18, value, value_font, TEAL)
        y += INFO_CARD_H + INFO_GAP_AFTER

    subtitle_font = load_font(FONT_SANS, 26, index=0)
    draw_tracked_text(draw, cx, y + SUBTITLE_SLOT // 2, subtitle, subtitle_font, ink, tracking=4)
    y += SUBTITLE_SLOT + GAP_BEFORE_QR

    paste_qr_card(canvas, qr_data, cx, y)
    y += QR_CARD
    return y


def render_card(
    *,
    background_path: Path,
    kicker: str | None,
    name: str,
    qr_data: str,
    output_path: Path,
    card_color: tuple = TEAL,
    info: dict | None = None,
    subtitle: str = "SCAN FOR THE GUEST GUIDE",
):
    ink, accent = ink_and_accent(card_color)

    canvas = Image.new("RGBA", (PAGE_W, PAGE_H), card_color + (255,))
    draw = ImageDraw.Draw(canvas)

    draw_header(canvas, draw, ink, accent)

    f_height = footer_height(has_kicker=bool(kicker), has_info=bool(info))
    photo_top = CONTENT_TOP + HEADER_H
    photo_bottom = CONTENT_BOTTOM - PHOTO_FOOTER_GAP - f_height
    if photo_bottom - photo_top < 300:
        sys.exit(f"Footer content too tall for {output_path.name} — shrink a slot in generate.py")
    draw_photo(canvas, background_path, photo_top, photo_bottom, accent)

    footer_top = photo_bottom + PHOTO_FOOTER_GAP
    bottom_used = draw_footer(
        canvas, draw, footer_top, kicker=kicker, name=name, info=info, qr_data=qr_data, subtitle=subtitle,
        ink=ink, accent=accent,
    )
    assert bottom_used <= CONTENT_BOTTOM + 1, "footer overflowed the frame"

    draw.rounded_rectangle(
        [(FRAME_MARGIN, FRAME_MARGIN), (PAGE_W - FRAME_MARGIN, PAGE_H - FRAME_MARGIN)],
        radius=32,
        outline=accent,
        width=3,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rgb = Image.new("RGB", canvas.size, WHITE)
    rgb.paste(canvas, mask=canvas.split()[3])
    rgb.save(output_path, dpi=(300, 300), quality=95)
    print(f"Wrote {output_path.relative_to(REPO_ROOT)}")


def wifi_qr_payload(ssid: str, password: str, security: str) -> str:
    def esc(s: str) -> str:
        return re.sub(r'([\\;,:"])', r"\\\1", s)

    if security == "nopass":
        return f"WIFI:T:nopass;S:{esc(ssid)};;"
    return f"WIFI:T:{security};S:{esc(ssid)};P:{esc(password)};;"


def render_wifi_plaque():
    local_config = PLAQUES_DIR / "wifi.local.yml"
    if not local_config.exists():
        sys.exit(
            f"{local_config.relative_to(REPO_ROOT)} not found.\n\n"
            "The Wi-Fi plaque needs real credentials, which must never be "
            "committed to this public repo. Copy plaques/wifi.example.yml "
            "to plaques/wifi.local.yml (already gitignored) and fill in "
            "the real SSID/password, then run this again."
        )
    with open(local_config) as f:
        wifi = yaml.safe_load(f)

    background = PLAQUES_DIR / "wifi-background.jpg"
    if not background.exists():
        background = REPO_ROOT / "docs/assets/images/house/balcony/balcony-sunset-view.jpg"

    qr_data = wifi_qr_payload(wifi["ssid"], wifi["password"], wifi.get("security", "WPA"))

    render_card(
        background_path=background,
        kicker=None,
        name="Wi-Fi",
        qr_data=qr_data,
        output_path=OUTPUT_DIR / "wifi.png",
        card_color=WIFI_COLOR,
        info={"Network": wifi["ssid"], "Password": wifi["password"]},
        subtitle="OR SCAN TO CONNECT",
    )
    print("Do not commit plaques/output/wifi.png — it encodes the Wi-Fi password.")


def load_rooms() -> list:
    with open(PLAQUES_DIR / "rooms.yml") as f:
        return yaml.safe_load(f)["rooms"]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("slugs", nargs="*", help="room slug(s) from plaques/rooms.yml")
    parser.add_argument("--all", action="store_true", help="generate every room plaque")
    parser.add_argument("--wifi", action="store_true", help="generate the Wi-Fi plaque")
    parser.add_argument("--list", action="store_true", help="list available room slugs and exit")
    args = parser.parse_args()

    rooms = load_rooms()

    if args.list:
        for room in rooms:
            print(room["slug"])
        return

    if args.wifi:
        render_wifi_plaque()
        return

    if not args.all and not args.slugs:
        parser.error("pass room slug(s), --all, --wifi, or --list")

    by_slug = {room["slug"]: room for room in rooms}
    targets = rooms if args.all else [by_slug[s] for s in args.slugs if s in by_slug]

    missing = [] if args.all else [s for s in args.slugs if s not in by_slug]
    if missing:
        parser.error(f"unknown slug(s): {', '.join(missing)} — see --list")

    base_url = site_url()
    for room in targets:
        render_card(
            background_path=REPO_ROOT / room["background"],
            kicker=room.get("kicker"),
            name=room["name"],
            qr_data=f"{base_url}/{room['url']}",
            output_path=OUTPUT_DIR / f"{room['slug']}.png",
            card_color=hex_to_rgb(room["color"]),
        )


if __name__ == "__main__":
    main()
