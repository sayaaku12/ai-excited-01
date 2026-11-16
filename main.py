#!/usr/bin/env python3
"""TIDAL SURGE — make.fun ai-excited-01 entry.

A lone surfer riding a towering bioluminescent wave at dawn: a curling
turquoise barrel, glowing spray exploding off the lip, an orange sun
breaking over the horizon. Rendered procedurally, pixel by pixel, in
pure Python 3 stdlib. No network, no external assets, deterministic.

Usage:
    python3 main.py            # writes entry.png to $MAKEFUN_OUTPUT_DIR or /output
"""

import math
import os
import struct
import sys
import zlib

# ---------------------------------------------------------------- constants

WIDTH = 1024
HEIGHT = 1024
MAX_BYTES = 1024 * 1024          # 1 MiB cap from the bounty rules
HORIZON = 560                    # y where sky meets sea
SUN_X, SUN_Y = 700, 462          # sun centre
SUN_R = 62                       # sun disc radius
SEED = 20261117                  # fixed seed: every run is identical

# ---------------------------------------------------------------- tiny RNG

def lcg(seed):
    """Deterministic linear congruential generator yielding floats in [0, 1)."""
    state = seed & 0x7FFFFFFF
    while True:
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        yield state / 0x80000000

# ---------------------------------------------------------------- colour helpers

def clamp(v, lo=0, hi=255):
    return lo if v < lo else hi if v > hi else int(v)


def lerp3(c1, c2, t):
    """Linear blend of two RGB triples; t in [0, 1]."""
    return (clamp(c1[0] + (c2[0] - c1[0]) * t),
            clamp(c1[1] + (c2[1] - c1[1]) * t),
            clamp(c1[2] + (c2[2] - c1[2]) * t))


def multi_lerp(stops, t):
    """Piecewise-linear gradient through (position, colour) stops."""
    if t <= stops[0][0]:
        return stops[0][1]
    for i in range(1, len(stops)):
        p0, c0 = stops[i - 1]
        p1, c1 = stops[i]
        if t <= p1:
            return lerp3(c0, c1, (t - p0) / (p1 - p0))
    return stops[-1][1]


SKY_STOPS = [
    (0.00, (18, 26, 66)),     # deep indigo, top of sky
    (0.45, (96, 48, 92)),     # violet dusk
    (0.75, (214, 96, 62)),    # burning rose
    (1.00, (255, 158, 74)),   # dawn orange at the horizon
]

SEA_STOPS = [
    (0.00, (12, 74, 84)),     # sunlit teal at the horizon
    (0.55, (7, 46, 58)),      # mid sea
    (1.00, (3, 22, 38)),      # deep water at the bottom
]

# ---------------------------------------------------------------- framebuffer

class Canvas:
    """A plain RGB framebuffer: one bytearray per row, 3 bytes per pixel."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.rows = [bytearray(w * 3) for _ in range(h)]

    def fill_span(self, y, x0, x1, rgb):
        """Solid horizontal run, clipped to the canvas."""
        if y < 0 or y >= self.h:
            return
        x0 = max(0, x0)
        x1 = min(self.w, x1)
        if x1 <= x0:
            return
        row = self.rows[y]
        row[x0 * 3:x1 * 3] = bytes(rgb) * (x1 - x0)

    def blend_span(self, y, x0, x1, rgb, alpha):
        """Alpha-blended horizontal run (alpha in [0, 1])."""
        if y < 0 or y >= self.h or alpha <= 0.0:
            return
        x0 = max(0, x0)
        x1 = min(self.w, x1)
        if x1 <= x0:
            return
        row = self.rows[y]
        inv = 1.0 - alpha
        for x in range(x0, x1):
            i = x * 3
            row[i] = clamp(rgb[0] * alpha + row[i] * inv)
            row[i + 1] = clamp(rgb[1] * alpha + row[i + 1] * inv)
            row[i + 2] = clamp(rgb[2] * alpha + row[i + 2] * inv)

    def disc(self, cx, cy, r, rgb, alpha=1.0):
        """Filled circle, blended if alpha < 1."""
        if r <= 0:
            return
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            half = int(math.sqrt(max(0, r * r - dy * dy)))
            if alpha >= 1.0:
                self.fill_span(y, cx - half, cx + half + 1, rgb)
            else:
                self.blend_span(y, cx - half, cx + half + 1, rgb, alpha)

    def thick_line(self, x0, y0, x1, y1, width, rgb):
        """A fat line drawn as a chain of small discs (silhouette limbs)."""
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        r = max(1, width // 2)
        for s in range(steps + 1):
            t = s / steps
            self.disc(int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t),
                     r, rgb)

# ---------------------------------------------------------------- scene pieces

def wave_edge(y):
    """Right-hand edge x of the wave body at row y, or None off-wave.

    The crest starts off the top-left, bulges right through the middle
    (the barrel belly) and tapers back toward the base, with the lip
    curling back over itself near the top.
    """
    if y < 190 or y > 780:
        return None
    u = (y - 190) / 590.0
    edge = 150 + 560 * math.sin(u * math.pi * 0.82) ** 1.1
    if y < 330:
        edge -= ((330 - y) / 140.0) ** 2 * 110
    return edge


def paint_sky_and_sea(cv):
    for y in range(HEIGHT):
        if y < HORIZON:
            cv.fill_span(y, 0, WIDTH, multi_lerp(SKY_STOPS, y / HORIZON))
        else:
            cv.fill_span(y, 0, WIDTH,
                         multi_lerp(SEA_STOPS, (y - HORIZON) / (HEIGHT - HORIZON)))


def paint_sun(cv):
    # Wide soft halo, then a hotter inner glow, then the solid disc.
    for r, alpha in ((190, 0.10), (140, 0.16), (100, 0.25)):
        cv.disc(SUN_X, SUN_Y, r, (255, 140, 60), alpha)
    cv.disc(SUN_X, SUN_Y, SUN_R + 6, (255, 190, 90), 0.9)
    cv.disc(SUN_X, SUN_Y, SUN_R, (255, 216, 110), 1.0)
    cv.disc(SUN_X, SUN_Y, SUN_R - 22, (255, 240, 170), 1.0)


def lip_width(y):
    """Wobbling width of the foam lip at row y (deterministic)."""
    return 9 + int(6 * math.sin(y * 0.13) + 3 * math.sin(y * 0.041))


def paint_wave_foam(cv):
    """Bright foam hugging the wave edge, with an aqua under-glow."""
    foam = (234, 252, 255)
    lip = (150, 240, 224)
    for y in range(190, 781):
        edge = wave_edge(y)
        if edge is None or edge <= 0:
            continue
        edge = int(edge)
        wob = lip_width(y)
        cv.fill_span(y, max(0, edge - wob), edge, foam)
        cv.fill_span(y, max(0, edge - wob - 5), edge - wob, lip)


def paint_sun_reflection(cv):
    """Warm vertical column of light on the sea beneath the sun."""
    for y in range(HORIZON + 4, HEIGHT, 2):
        spread = 26 + (y - HORIZON) * 0.28
        x0 = int(SUN_X - spread)
        x1 = int(SUN_X + spread)
        shimmer = 0.10 + 0.08 * math.sin(y * 0.21)
        cv.blend_span(y, x0, x1, (255, 150, 70), shimmer)


def paint_wave(cv):
    lip = (150, 240, 224)      # bright aqua at the crest
    mid = (12, 168, 178)       # mid face
    deep = (4, 92, 110)        # dark base
    bands = 6
    for y in range(190, 781):
        edge = wave_edge(y)
        if edge is None or edge <= 0:
            continue
        edge = int(edge)
        # Vertical shading: brighter near the crest, darker at the base.
        vt = (y - 190) / 590.0
        base = lerp3(lip, deep, vt * 0.85)
        # Six horizontal bands: bright at the lip, deep at the back.
        for b in range(bands):
            x0 = int(edge * b / bands)
            x1 = int(edge * (b + 1) / bands)
            shade = lerp3(deep, base, (b + 0.5) / bands)
            cv.fill_span(y, x0, x1, shade)

    # Dark barrel tube: the hollow shadow inside the curl.
    for y in range(330, 531):
        dy = (y - 430) / 100.0
        if abs(dy) >= 1.0:
            continue
        half = int(175 * math.sqrt(1.0 - dy * dy))
        cv.blend_span(y, 400 - half, 400 + half, (2, 84, 96), 0.55)
    paint_wave_foam(cv)


def paint_spray(cv):
    """Glowing spray bursting off the lip — deterministic LCG positions.

    Two bursts: a fine mist flung far off the crest, and fat glowing
    droplets clustered near the curl tip for sparkle.
    """
    rng = lcg(SEED)
    mist = (210, 250, 255)
    drop = (160, 240, 235)
    for _ in range(300):
        y0 = 200 + int(next(rng) * 240)          # source row along the lip
        edge = wave_edge(y0)
        if edge is None:
            continue
        drift = next(rng) ** 1.6 * 150            # flung right and up
        x = int(edge + drift + next(rng) * 30)
        y = int(y0 - next(rng) * 90 - drift * 0.25)
        r = 1 + int(next(rng) * 3)
        a = 0.35 + next(rng) * 0.55
        cv.disc(x, y, r, mist, a)
    for _ in range(40):
        y0 = 195 + int(next(rng) * 90)
        edge = wave_edge(y0)
        if edge is None:
            continue
        x = int(edge + 20 + next(rng) * 110)
        y = int(y0 - 10 - next(rng) * 70)
        cv.disc(x, y, 2 + int(next(rng) * 3), drop, 0.9)


def paint_surfer(cv):
    """Small dark silhouette riding the face, low on the wave."""
    ink = (7, 22, 36)
    # Board slicing across the face.
    cv.thick_line(428, 672, 514, 652, 6, ink)
    # Legs, torso, head.
    cv.thick_line(468, 652, 462, 620, 7, ink)
    cv.thick_line(478, 650, 470, 622, 7, ink)
    cv.thick_line(464, 622, 460, 592, 8, ink)
    cv.disc(459, 584, 7, ink)
    # Arms reaching for balance.
    cv.thick_line(463, 606, 438, 592, 5, ink)
    cv.thick_line(463, 606, 490, 594, 5, ink)


def paint_sea_glitter(cv):
    """Sun glitter: short bright dashes on the water under the sun."""
    rng = lcg(SEED ^ 0x5EED)
    for _ in range(160):
        y = HORIZON + 12 + int(next(rng) * 300)
        spread = 30 + (y - HORIZON) * 0.55
        x = int(SUN_X - spread + next(rng) * spread * 2)
        w = 6 + int(next(rng) * 26)
        a = 0.25 + next(rng) * 0.5
        cv.blend_span(y, x, x + w, (255, 200, 110), a)


def paint_foam_streaks(cv):
    """White foam streaks washing across the foreground."""
    rng = lcg(SEED ^ 0xF0A)
    for _ in range(90):
        y = 830 + int(next(rng) * 180)
        x = int(next(rng) * WIDTH)
        w = 20 + int(next(rng) * 120)
        a = 0.15 + next(rng) * 0.35
        cv.blend_span(y, x, x + w, (220, 245, 248), a)


def paint_birds(cv):
    """Three distant birds, tiny V strokes high in the dawn sky."""
    ink = (30, 30, 55)
    for bx, by, s in ((210, 150, 9), (260, 128, 7), (300, 168, 8)):
        cv.thick_line(bx - s, by - 3, bx, by, 2, ink)
        cv.thick_line(bx, by, bx + s, by - 3, 2, ink)


def render():
    """Paint the scene back-to-front: sky, sun, sea light, wave, life."""
    cv = Canvas(WIDTH, HEIGHT)
    paint_sky_and_sea(cv)
    paint_sun(cv)
    paint_sun_reflection(cv)
    paint_wave(cv)
    paint_spray(cv)
    paint_surfer(cv)
    paint_sea_glitter(cv)
    paint_foam_streaks(cv)
    paint_birds(cv)
    return cv

# ---------------------------------------------------------------- PNG encoder

def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    """Encode the canvas as a PNG (filter 0, zlib level 9)."""
    if cv.w <= 0 or cv.h <= 0 or cv.w > 1024 or cv.h > 1024:
        raise ValueError("bad dimensions: %dx%d" % (cv.w, cv.h))
    raw = bytearray()
    for row in cv.rows:
        raw.append(0)          # filter type 0 (None) per scanline
        raw.extend(row)
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png

# ---------------------------------------------------------------- validation

def verify_png(path, expect_w, expect_h):
    """Read the file back and check signature, size cap and dimensions."""
    with open(path, "rb") as f:
        data = f.read()
    if len(data) > MAX_BYTES:
        raise ValueError("file too big: %d bytes > %d" % (len(data), MAX_BYTES))
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG (bad signature)")
    w, h = struct.unpack(">II", data[16:24])
    if (w, h) != (expect_w, expect_h):
        raise ValueError("dimension mismatch: %dx%d" % (w, h))
    # IDAT must decompress to exactly h * (1 + 3 * w) bytes.
    # Layout: 8-byte signature, 25-byte IHDR chunk, then the IDAT chunk
    # (4 length + 4 type + payload + 4 CRC), then the 12-byte IEND chunk.
    idat_len = struct.unpack(">I", data[33:37])[0]
    idat = data[41:41 + idat_len]
    raw = zlib.decompress(idat)
    if len(raw) != expect_h * (1 + 3 * expect_w):
        raise ValueError("IDAT payload length mismatch")
    return len(data)


def _selftest():
    """Negative test: the encoder must refuse out-of-cap dimensions."""
    bad = Canvas(0, 10)
    try:
        encode_png(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("encoder accepted width 0")
    bad2 = Canvas(2048, 10)
    try:
        encode_png(bad2)
    except ValueError:
        pass
    else:
        raise AssertionError("encoder accepted width 2048")
    good = Canvas(2, 2)
    good.fill_span(0, 0, 2, (255, 0, 0))
    data = encode_png(good)
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError("encoder produced bad signature")
    print("selftest: negative dimension checks passed", file=sys.stderr)


def main():
    _selftest()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    cv = render()
    png = encode_png(cv)
    if len(png) > MAX_BYTES:
        print("error: encoded PNG %d bytes exceeds 1 MiB" % len(png),
              file=sys.stderr)
        return 1
    with open(path, "wb") as f:
        f.write(png)
    size = verify_png(path, WIDTH, HEIGHT)
    print("wrote %s (%dx%d, %d bytes)" % (path, WIDTH, HEIGHT, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
