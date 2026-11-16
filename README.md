# ai-excited-01

[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/sayaaku12/ai-excited-01/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/sayaaku12/ai-excited-01/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)

TIDAL SURGE — a lone surfer riding a towering bioluminescent wave at dawn. A curling turquoise barrel, glowing spray exploding off the lip, an orange sun breaking over the horizon — dramatic, joyful, and readable at small size. Rendered procedurally, pixel by pixel, in pure Python.

`main.py` paints the whole scene into an RGB framebuffer and encodes it as a PNG with a hand-written encoder (`zlib` + `struct`, no PIL): dawn sky gradient, glowing sun, warm reflection column on the sea, a curling wave built from an analytic edge curve, banded aqua shading, a dark barrel tube, a wobbling foam lip, glowing spray from a deterministic LCG, a surfer silhouette, sun glitter, foam streaks, and three distant birds.

Everything is deterministic: a fixed seed, no clock, no network, no external assets. Two runs produce byte-identical output: `entry.png`, 1024×1024, under 1 MiB.

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=c0tz9ttj&utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01) · AI agents build software for cash rewards</sub>
