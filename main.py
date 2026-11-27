#!/usr/bin/env python3
"""World news in one image — Friday 27 November 2026.

Pure standard library. Draws a 1024x1024 PNG summary of the five most
consequential world stories of Friday 27 November 2026 and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

Deterministic: no randomness, no timestamps, no network access.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
NAVY = (13, 27, 46)        # page background
PANEL = (24, 43, 66)       # story panel
PANEL_EDGE = (48, 76, 104)
GOLD = (232, 184, 74)      # accent / date
WHITE = (244, 246, 248)
MUTED = (168, 186, 204)
RED = (214, 74, 74)
BLUE = (86, 156, 214)
GREEN = (88, 178, 120)
ORANGE = (232, 138, 60)
PURPLE = (158, 124, 206)

# ------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, '#' = on.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
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
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
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
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def wrap_text(s, scale, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = s.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            base = (yy * self.w + max(0, x)) * 3
            for xx in range(max(0, x), min(self.w, x + w)):
                i = (yy * self.w + xx) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, t, c):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d <= (r + t) ** 2:
                    self.set(xx, yy, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps + 1):
            x = round(x0 + dx * i / steps)
            y = round(y0 + dy * i / steps)
            for tx in range(thick):
                for ty in range(thick):
                    self.set(x + tx, y + ty, c)

    def poly(self, pts, c):
        # scanline fill for a simple polygon
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.set(x, y, c)

    def rrect(self, x, y, w, h, r, c, edge=None):
        self.rect(x + r, y, w - 2 * r, h, c)
        self.rect(x, y + r, w, h - 2 * r, c)
        for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r),
                       (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
            self.disc(cx, cy, r, c)
        if edge:
            self.line(x + r, y, x + w - r, y, edge)
            self.line(x + r, y + h - 1, x + w - r, y + h - 1, edge)
            self.line(x, y + r, x, y + h - r, edge)
            self.line(x + w - 1, y + r, x + w - 1, y + h - r, edge)

    def text(self, x, y, s, scale, c, bold=False):
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
                        if bold:
                            self.rect(cx + col * scale + 1, y + row * scale,
                                      scale, scale, c)
            cx += 6 * scale
        return cx


# ---------------------------------------------------------------- icons
def icon_drone(cv, x, y, s, c):
    # quadcopter: body + 4 arms + 4 rotors, small blast star below
    cv.rect(x + 34, y + 38, 28, 20, c)
    cv.rect(x + 42, y + 30, 12, 8, c)
    for ax, ay in ((x + 8, y + 12), (x + 76, y + 12),
                   (x + 8, y + 76), (x + 76, y + 76)):
        cv.line(x + 48, y + 48, ax, ay, c, 4)
        cv.disc(ax, ay, 9, c)
        cv.line(ax - 14, ay, ax + 14, ay, c, 3)
    cv.disc(x + 48, y + 48, 5, GOLD)
    cv.poly([(x + 48, y + 88), (x + 54, y + 76), (x + 60, y + 88),
             (x + 48, y + 84), (x + 36, y + 88), (x + 42, y + 76)],
            ORANGE)


def icon_storm(cv, x, y, s, c):
    # cloud + lightning bolt + rain
    cv.disc(x + 34, y + 34, 18, c)
    cv.disc(x + 56, y + 28, 22, c)
    cv.disc(x + 72, y + 40, 15, c)
    cv.rect(x + 18, y + 34, 66, 18, c)
    cv.poly([(x + 52, y + 50), (x + 40, y + 78), (x + 50, y + 78),
             (x + 44, y + 94), (x + 62, y + 62), (x + 52, y + 62)], GOLD)
    for rx in (x + 22, x + 76):
        cv.line(rx, y + 62, rx - 4, y + 76, BLUE, 3)


def icon_gaza(cv, x, y, s, c):
    # broken building silhouette + flame
    cv.rect(x + 14, y + 30, 26, 66, c)
    cv.rect(x + 46, y + 48, 26, 48, c)
    cv.poly([(x + 14, y + 30), (x + 26, y + 14), (x + 34, y + 30)], c)
    cv.rect(x + 20, y + 40, 8, 8, NAVY)
    cv.rect(x + 20, y + 56, 8, 8, NAVY)
    cv.rect(x + 52, y + 58, 8, 8, NAVY)
    cv.poly([(x + 82, y + 96), (x + 74, y + 74), (x + 82, y + 62),
             (x + 88, y + 76), (x + 96, y + 60), (x + 94, y + 96)], ORANGE)


def icon_tariff(cv, x, y, s, c):
    # big % sign + rising arrow
    cv.disc(x + 26, y + 26, 11, c)
    cv.disc(x + 70, y + 70, 11, c)
    cv.line(x + 74, y + 18, x + 22, y + 78, c, 6)
    cv.line(x + 30, y + 88, x + 62, y + 88, GOLD, 5)
    cv.line(x + 62, y + 88, x + 62, y + 60, GOLD, 5)
    cv.poly([(x + 62, y + 52), (x + 74, y + 68), (x + 50, y + 68)], GOLD)


def icon_chess(cv, x, y, s, c):
    # 4x4 board + pawn
    sq = 20
    for r in range(4):
        for col in range(4):
            if (r + col) % 2 == 0:
                cv.rect(x + 8 + col * sq, y + 8 + r * sq, sq, sq, WHITE)
            else:
                cv.rect(x + 8 + col * sq, y + 8 + r * sq, sq, sq, c)
    cv.disc(x + 48, y + 34, 10, GOLD)
    cv.poly([(x + 38, y + 44), (x + 58, y + 44), (x + 64, y + 76),
             (x + 32, y + 76)], GOLD)
    cv.rect(x + 30, y + 76, 36, 8, GOLD)


ICONS = (icon_drone, icon_storm, icon_gaza, icon_tariff, icon_chess)

# ---------------------------------------------------------------- stories
STORIES = [
    dict(num="1", color=RED, tag="MIDDLE EAST",
         head="DRONE STRIKE KILLS 2 IN KUWAIT",
         fact="Iran blamed for attack on air-defence site",
         detail="Two Italian technicians dead; Tehran denies role."),
    dict(num="2", color=BLUE, tag="UNITED STATES",
         head="THANKSGIVING STORM HITS U.S.",
         fact="Macy's 100th parade postponed in New York",
         detail="500,000+ without power; hundreds of flights axed."),
    dict(num="3", color=ORANGE, tag="GAZA",
         head="GAZA STRIKES KILL 10",
         fact="Hamas weighs its response as truce frays",
         detail="Fighting grinds on; 16 schoolchildren killed in Nov."),
    dict(num="4", color=GREEN, tag="TRADE WAR",
         head="U.S. TARIFFS HIT 14 PARTNERS",
         fact="New duties of up to 40% on trading partners",
         detail="Markets brace as the trade war widens again."),
    dict(num="5", color=PURPLE, tag="SPORT",
         head="CHESS: GUKESH-SINDAROV DRAW",
         fact="Game 3 marathon ends level",
         detail="World Championship still deadlocked at 1.5-1.5."),
]


def build():
    cv = Canvas(W, H, NAVY)
    # top gold rule
    cv.rect(0, 0, W, 10, GOLD)
    # header
    cv.text(48, 44, "WORLD NEWS", 8, WHITE, bold=True)
    cv.text(48, 116, "FRIDAY 27 NOVEMBER 2026", 4, GOLD, bold=True)
    cv.text(648, 116, "5 STORIES THAT SHAPED THE DAY", 2, MUTED)
    cv.rect(48, 152, 928, 3, PANEL_EDGE)

    y = 172
    row_h, gap = 152, 10
    for st in STORIES:
        cv.rrect(24, y, 976, row_h, 14, PANEL, edge=PANEL_EDGE)
        cv.rect(24, y + 14, 8, row_h - 28, st["color"])
        # number badge
        cy = y + row_h // 2
        cv.ring(76, cy, 26, 3, st["color"])
        cv.text(76 - 9, cy - 14, st["num"], 4, WHITE, bold=True)
        # icon
        ICONS[int(st["num"]) - 1](cv, 116, cy - 48, 96, st["color"])
        # text block
        tx = 236
        cv.text(tx, y + 22, st["tag"], 2, st["color"], bold=True)
        cv.text(tx, y + 48, st["head"], 4, WHITE, bold=True)
        cv.text(tx, y + 92, st["fact"], 3, GOLD)
        cv.text(tx, y + 122, st["detail"], 2, MUTED)
        y += row_h + gap

    # footer
    cv.text(48, 986, "SOURCES: REUTERS - BBC - NYT - MINT - INDIA TODAY", 2, MUTED)
    return cv


# ---------------------------------------------------------------- PNG out
def chunk(kind, data):
    c = struct.pack(">I", len(data)) + kind + data
    return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(cv, path):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    cv = build()
    write_png(cv, os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
