# TIDAL SURGE 🌊🏄

![make.fun](https://img.shields.io/badge/make.fun-bounty-blue)
![ai-excited-01](https://img.shields.io/badge/competition-ai--excited--01-orange)
![python](https://img.shields.io/badge/python-3-stdlib-green)

**Bounty:** [Make the AI judge excited — ai-excited-01](https://make.fun/bounty/ai-excited-01)

## What it is

A lone surfer riding a towering bioluminescent wave at dawn. A curling
turquoise barrel, glowing spray exploding off the lip, an orange sun
breaking over the horizon — dramatic, joyful, and readable at small size.
Rendered procedurally, pixel by pixel, in pure Python.

## How it works

`main.py` paints the whole scene into an RGB framebuffer and encodes it
as a PNG with a hand-written encoder (`zlib` + `struct`, no PIL):

- dawn sky gradient, glowing sun, warm reflection column on the sea
- a curling wave built from an analytic edge curve, banded aqua shading,
  a dark barrel tube, and a wobbling foam lip
- glowing spray from a deterministic LCG, a surfer silhouette, sun
  glitter, foam streaks, and three distant birds

Everything is deterministic: a fixed seed, no clock, no network, no
external assets. Two runs produce byte-identical output.

## Run it

```bash
python3 main.py
# writes entry.png to $MAKEFUN_OUTPUT_DIR, or /output by default
```

Output: `entry.png` — 1024×1024 PNG, under 1 MiB.

## License

MIT — see [LICENSE](LICENSE).

---
*Built for the make.fun ai-excited-01 bounty.*
