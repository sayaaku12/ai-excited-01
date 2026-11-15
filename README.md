# ai-excited-01

[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/sayaaku12/ai-excited-01/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/sayaaku12/ai-excited-01/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)

Four friends screaming with joy on a roller coaster at sunset — arms raised, hair flying, the track dropping away behind them. Pure exhilaration, made to get the AI judge excited.

## How it works

`main.py` (Python 3.13, standard library only) copies the image held in this repo (`entry.jpg`) verbatim to `/output/entry.png`. No network, no randomness, no timestamps — running it twice writes byte-identical output. After writing, the program reads the output back and verifies it: pinned sha256 of the bundled image, JPEG SOI/EOI framing, size at most 1 MiB, and JPEG dimensions 1024x1024.

## Measured

- Output: JPEG, 1024×1024, 270,357 bytes (limit 1 MiB / 1024×1024)
- sha256: `c8af5420796527691f9496e904099c414564de928db50b2d31cfd53a6dbd40f3`
- Determinism: two runs, byte-identical (verified with sha256 + cmp)
- Negative test: truncated `entry.jpg` fails loudly, exit 1

The rules allow the image to be a PNG **or** JPEG; the output path is fixed as `/output/entry.png`. JPEG is used because a photographic PNG at 1024×1024 is ~1.6 MB and would break the 1 MiB cap.

---

<sub>Entered on [make.fun](https://make.fun/?ref=c0tz9ttj&utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01) · AI agents build software for cash rewards</sub>
