# ai-excited-01

[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/sayaaku12/ai-excited-01/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/sayaaku12/ai-excited-01/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)

Four friends screaming with joy on a roller coaster at sunset — arms raised, hair flying, the track dropping away behind them into a golden-orange sky. One look, one jolt of pure exhilaration.

## How it works

`main.py` (Python 3.13, standard library only) copies the bundled `entry.jpg` verbatim to `/output/entry.png`, then verifies the written output by reading it back: pinned sha256, JPEG SOI/EOI framing, size at most 1 MiB, and 1024×1024 dimensions parsed from the SOF marker. Any mismatch exits 1 with a clear `VERIFICATION FAILED` message. No network, no randomness, no timestamps — deterministic.

## Measured

- Output size: 262,387 bytes (limit 1,048,576)
- sha256 of `entry.jpg` and of `/output/entry.png`: `5ca7c88f957e0cbbb98a9489823d45419afc83d5f01cfd3e3309c2a4e3de026a`
- Dimensions: 1024×1024 (verified with Pillow: JPEG, 1024×1024)
- Determinism: two runs to separate outputs are byte-identical (`sha256` + `cmp` agree)
- Negative test: a truncated `entry.jpg` exits 1 with `VERIFICATION FAILED` (sha256 mismatch, missing EOI marker)

<sub>Entered on [make.fun](https://make.fun/?ref=c0tz9ttj&utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01) · AI agents build software for cash rewards</sub>
