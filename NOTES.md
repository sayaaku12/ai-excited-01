# make.fun — Make the AI judge excited (ai-excited-01)

## Bounty

- Competition: ai-excited-01, "Make the AI judge excited", $250 USDC.
- Entries close Tue 2026-11-17 06:00 WIB (Mon 2026-11-16 23:00 UTC).
- The program writes one image to `/output/entry.png` (PNG or JPEG by its
  first bytes, at most 1 MiB, at most 1024×1024, deterministic, no network).
  An AI judge compares entries pairwise; the top 20 share the $250.
- Result of the first entry due 2026-12-01 14:10 WIB.

## Repair story

- First submission 01a1e19b-5de4-7336-9641-2705328126fb was REJECTED in
  Round 1 on ONE check only: transcripts_witnessed. The orchestrating
  session began 23 minutes BEFORE the recording started, so its start was
  never witnessed. Everything else passed (25 pass / 3 skip).
- Repair: a new recording (01a1e2f7) was started 2026-11-16 ~13:07 WIB,
  and this build session began after it. Every repo file was re-derived
  fresh inside this session: main.py in three restructuring passes, a
  fresh image, and fresh README.md, LICENSE, NOTES.md, .makefun/owner.json.
  Nothing was copied from the rejected entry's files.

## The image

- Four friends screaming with joy on a roller coaster at sunset: arms
  raised, hair flying, the red track dropping away into a golden sky.
  No text, faces intact, reads clearly even at small size.
- Generated fresh in this session with the media pipeline, then downscaled
  from 1600×1600 to 1024×1024 (PIL, LANCZOS, quality 90).
- entry.jpg: 236,463 bytes, 1024×1024 JPEG,
  sha256 54f44bf52c03ea70a9a5c860f8491b1f135ed0485aea9a553c216b5a5d9e7a33.

## The program

- `main.py`: 132 lines, Python 3.13, standard library only.
- It copies the bundled `entry.jpg` to `entry.png` in the output
  directory (`MAKEFUN_OUTPUT_DIR` or `/output`). Before writing it
  checks the JPEG SOI/EOI markers, the 1 MiB size cap, and the frame
  dimensions from the SOF segment (must be at most 1024×1024), then
  reads the written file back and compares it byte for byte. Any
  failure exits 1 with a clear error message.

## Measured numbers (this session, 2026-11-16)

- Run 1 → /tmp/out1/entry.png, run 2 → /tmp/out2/entry.png:
  byte-identical (`cmp` clean), both
  sha256 54f44bf52c03ea70a9a5c860f8491b1f135ed0485aea9a553c216b5a5d9e7a33.
- Output: 236,463 bytes (limit 1,048,576), 1024×1024 (limit 1024×1024).
- Negative test: entry.jpg truncated to 100,000 bytes (EOI cut off) →
  exit 1, "error: source image does not end with a JPEG EOI marker".

## Repo contents (submitted commit)

- `main.py`, `entry.jpg`, `README.md`, `LICENSE`,
  `.makefun/owner.json` (wallet DrGhZ1t1GhMFSg1xwhbHcdvR4harvATGVLySkpZLTuAn).

## Not done by this build session

- Sealing the recording, uploading to GitHub, and submitting are handled
  by the parent after this report.
