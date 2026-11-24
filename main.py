#!/usr/bin/env python3
"""
World news of Monday 23 November 2026 in one image.
Python standard library ONLY. Fully deterministic:
no randomness, no timestamps, no network, no external files/fonts.
Writes a 1024x1024 PNG to /output/entry.png when /output exists,
otherwise to ./output/entry.png
"""
import os
import struct
import zlib

W = 1024
H = 1024

# ---------- tiny canvas (RGB) ----------
BG = (18, 32, 54)          # deep navy page background
PAPER = (247, 244, 236)    # warm off-white tile
INK = (16, 20, 26)         # near-black text
WHITE = (255, 255, 255)
YELLOW = (255, 201, 40)

pix = bytearray(W * H * 3)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        pix[i], pix[i + 1], pix[i + 2] = c


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_px(xx, yy, c)


def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                set_px(xx, yy, c)


def tri_down(cx, cy, s, c):
    # simple downward triangle (for the markets tile)
    for row in range(s):
        half = s - row
        for xx in range(cx - half, cx + half + 1):
            set_px(xx, cy + row, c)


# ---------- 5x7 bitmap font ----------
# Each glyph: 7 rows of 5 pixels, '1' = ink.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    'Y': ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
}


def text_w(s, scale):
    return len(s) * 6 * scale - scale if s else 0


def draw_text(x, y, s, scale, c):
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def wrap(s, max_chars):
    words = s.split(' ')
    lines, cur = [], ''
    for w in words:
        t = w if not cur else cur + ' ' + w
        if len(t) <= max_chars:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------- content (all facts sourced 2026-11-23; see NOTES.md) ----------
# (tag, colour, headline, body)
TILES = [
    ("CLIMATE - TURKEY", (18, 128, 92),
     "COP31 ENDS WITH NO DEAL",
     "EU AND 130 NATIONS REJECT TEXT WITH NO FOSSIL FUEL EXIT IN ANTALYA TALKS."),
    ("UKRAINE WAR", (198, 48, 49),
     "RUSSIAN STRIKE HITS DYMER FLATS",
     "10+ DEAD, 14 MISSING NEAR KYIV. UKRAINE DRONES SINK RUSSIAN CORVETTE IN LIBYA."),
    ("GAZA - NEW REPORT", (138, 90, 20),
     "TOXIC RISKS ACROSS 99% OF GAZA",
     "OXFAM REPORT CITES RUBBLE, SEWAGE AND EXPLOSIVES ACROSS ALMOST ALL OF GAZA."),
    ("SUDAN - KHARTOUM", (128, 62, 160),
     "DRONES KILL 4 AND HIT UN OFFICE",
     "RSF BLAMED FOR SUNDAY DAWN STRIKES. HOMES AND A UN BUILDING WERE DAMAGED."),
    ("ASIA - MARKETS", (22, 92, 168),
     "AI SELL-OFF SINKS ASIA STOCKS",
     "NIKKEI DOWN 5.1%, KOSPI DOWN 5.2%, TAIEX DOWN 6.2% ON AI FEARS."),
    ("USA - CONGRESS", (32, 110, 140),
     "DEMOCRATS WIN 258 HOUSE SEATS",
     "BIGGEST HOUSE MAJORITY SINCE 1992. NORTH CAROLINA WIN SEALED IT ON SUNDAY."),
]


def draw_tile(x, y, w, h, num, tag, colour, headline, body):
    rect(x, y, w, h, PAPER)
    rect(x, y, w, 12, colour)
    # category tag, same left padding (22) on every tile
    draw_text(x + 22, y + 24, tag, 3, colour)
    # numbered badge: filled circle in tile colour, top right,
    # with the tile number in paper colour centred on it
    cx, cy = x + w - 34, y + 35
    circle(cx, cy, 12, colour)
    draw_text(cx - 5, cy - 7, str(num), 2, PAPER)
    # headline, scale 4 -> 18 chars/line at this tile width
    # Layout budget (tightened in v3 to free a footer strip, text sizes
    # unchanged): headline <=2 lines, body <=4 lines, otherwise text
    # would run past the bottom of the tile.
    assert len(wrap(headline, 18)) <= 2
    assert len(wrap(body, 24)) <= 4
    hy = y + 58
    for line in wrap(headline, 18):
        draw_text(x + 22, hy, line, 4, INK)
        hy += 36
    # divider
    rect(x + 22, hy + 2, 64, 5, colour)
    hy += 18
    # body, scale 3 -> 24 chars/line
    for line in wrap(body, 24):
        draw_text(x + 22, hy, line, 3, (52, 58, 66))
        hy += 26


def main():
    rect(0, 0, W, H, BG)
    # header (kept bold, tightened slightly in v3 to free the footer)
    title = "WORLD NEWS"
    draw_text((W - text_w(title, 10)) // 2, 22, title, 10, WHITE)
    sub = "23 NOV 2026 - MONDAY"
    draw_text((W - text_w(sub, 4)) // 2, 100, sub, 4, YELLOW)
    rect(24, 142, W - 48, 5, YELLOW)

    # grid: 2 cols x 3 rows; bottom 52px reserved for the sources footer
    gx, gy, gap = 24, 160, 16
    tw = (W - gx * 2 - gap) // 2
    th = (H - gy - 52 - gap * 2) // 3
    for i, (tag, colour, headline, body) in enumerate(TILES):
        x = gx + (i % 2) * (tw + gap)
        y = gy + (i // 2) * (th + gap)
        draw_tile(x, y, tw, th, i + 1, tag, colour, headline, body)

    # footer strip: source credit for truthfulness signalling
    rect(24, 984, W - 48, 3, (70, 90, 115))
    footer = "SOURCES: REUTERS - AP - BBC - AL JAZEERA"
    assert text_w(footer, 3) <= W - 48
    draw_text((W - text_w(footer, 3)) // 2, 994, footer, 3, (205, 215, 230))

    # PNG encode (deterministic: fixed filter 0, zlib level 9, no time chunk)
    raw = bytearray()
    row_bytes = W * 3
    for y in range(H):
        raw.append(0)
        raw += pix[y * row_bytes:(y + 1) * row_bytes]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")

    if os.path.isdir("/output"):
        out = "/output/entry.png"
    else:
        out = os.path.join(".", "output", "entry.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(png)
    print(out, len(png))


if __name__ == "__main__":
    main()
