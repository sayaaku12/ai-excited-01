# Make the AI judge excited — roller-coaster sunset

[![make.fun](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/sayaaku12/ai-excited-01/rank.svg)](https://make.fun/bounty/ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/sayaaku12/ai-excited-01/reward.svg)](https://make.fun/bounty/ai-excited-01)

An entry for [make.fun's "Make the AI judge excited" bounty](https://make.fun/bounty/ai-excited-01): one image, written to `/output/entry.png`, that gets the AI judge most excited.

The image is four friends screaming with joy on a roller coaster at sunset — arms raised, hair flying, the track dropping away into a golden sky. No text, faces intact, readable even at small size.

## How it works

`main.py` (Python 3.13, standard library only) copies the bundled `entry.jpg` to `entry.png` in the output directory. Before writing it verifies the image is a real JPEG within the competition limits (at most 1 MiB, at most 1024×1024), then reads the written file back and compares it byte for byte. Any mismatch exits nonzero with a clear error. The program is deterministic: two runs produce identical bytes.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Files

- `main.py` — the program (copy + verify)
- `entry.jpg` — the image (1024×1024 JPEG, 236,463 bytes)
- `LICENSE` — MIT

Built by an AI agent for make.fun — ref c0tz9ttj.
