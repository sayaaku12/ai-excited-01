#!/usr/bin/env python3
"""Make the AI judge excited (make.fun bounty ai-excited-01).

Writes one image to /output/entry.png: four friends screaming with
joy on a roller coaster at sunset, arms raised, hair flying — pure
exhilaration. The image is held in this repository as entry.jpg and
is copied verbatim.

The bundled image is JPEG bytes (1024x1024). The bounty rules allow
the image to be a PNG *or* a JPEG, and the output path is fixed as
/output/entry.png, so JPEG bytes are written to that path. A
photographic PNG at 1024x1024 would be ~1.6 MB and break the 1 MiB
cap, which is why the entry ships as JPEG.

Deterministic: no network, no randomness, no timestamps. Running the
program twice writes byte-identical output.

After writing, the program reads the output back and verifies it
(pass 2): the output must be at most 1 MiB, must hash to exactly the
bundled image's sha256, and must parse as a JPEG whose SOF frame is
1024x1024. Any mismatch fails loudly (non-zero exit, message on
stderr) instead of silently shipping a wrong image.

Pass 3 adds a pinned hash of the bundled image itself: the source
bytes are checked against EXPECTED_SHA256 before anything is
written, and the JPEG SOI/EOI framing markers are checked, so a
swapped or truncated entry.jpg in the repo fails loudly instead of
passing verification (output == corrupted source would otherwise
still hash-match).
"""

import hashlib
import os
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLED = HERE / "entry.jpg"

MAX_BYTES = 1_048_576        # 1 MiB cap from the bounty rules
WANT_WIDTH = 1024
WANT_HEIGHT = 1024
# Pinned hash of the chosen bundled image (roller-coaster sunset),
# measured 2026-11-16. Checking the source against it means a swapped
# or corrupted entry.jpg fails loudly instead of silently passing.
EXPECTED_SHA256 = (
    "c8af5420796527691f9496e904099c414564de928db50b2d31cfd53a6dbd40f3"
)


def jpeg_size(data: bytes) -> tuple[int, int]:
    """Return (width, height) from a JPEG's SOF0/SOF1/SOF2 frame."""
    if len(data) < 4 or data[0:2] != b"\xff\xd8":
        raise ValueError("not a JPEG (missing SOI marker 0xFFD8)")
    pos = 2
    while pos + 9 < len(data):
        if data[pos] != 0xFF:
            raise ValueError(f"bad JPEG marker at offset {pos}")
        marker = data[pos + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        seg_len = struct.unpack(">H", data[pos + 2:pos + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[pos + 5:pos + 9])
            return width, height
        pos += 2 + seg_len
    raise ValueError("no SOF frame found in JPEG")


def check_output(written: bytes, source: bytes) -> list[str]:
    """Return a list of problems with the written output (empty = OK)."""
    problems: list[str] = []
    if len(written) != len(source):
        problems.append(
            f"output size {len(written)} != bundled size {len(source)}"
        )
    if len(written) > MAX_BYTES:
        problems.append(
            f"output size {len(written)} exceeds 1 MiB cap {MAX_BYTES}"
        )
    if hashlib.sha256(written).hexdigest() != hashlib.sha256(source).hexdigest():
        problems.append("output sha256 != bundled image sha256")
    try:
        width, height = jpeg_size(written)
    except ValueError as exc:
        problems.append(f"output is not a readable JPEG: {exc}")
    else:
        if (width, height) != (WANT_WIDTH, WANT_HEIGHT):
            problems.append(
                f"output dimensions {width}x{height} != "
                f"{WANT_WIDTH}x{WANT_HEIGHT}"
            )
    return problems


def main() -> int:
    data = BUNDLED.read_bytes()

    # Pinned-hash check on the bundled image itself (pass 3): a swapped
    # or corrupted entry.jpg must fail here, before anything is written.
    source_digest = hashlib.sha256(data).hexdigest()
    if source_digest != EXPECTED_SHA256:
        print(
            f"VERIFICATION FAILED: bundled image sha256 {source_digest} "
            f"!= expected {EXPECTED_SHA256} (entry.jpg may be swapped "
            f"or corrupted)",
            file=sys.stderr,
        )
        return 1
    # JPEG framing: SOI at the start, EOI at the end (catches truncation).
    if data[:2] != b"\xff\xd8" or data[-2:] != b"\xff\xd9":
        print(
            "VERIFICATION FAILED: bundled image lacks JPEG SOI/EOI "
            "framing markers",
            file=sys.stderr,
        )
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "entry.png"
    out.write_bytes(data)

    written = out.read_bytes()
    problems = check_output(written, data)
    if problems:
        for problem in problems:
            print(f"VERIFICATION FAILED: {problem}", file=sys.stderr)
        return 1

    digest = hashlib.sha256(written).hexdigest()
    print(f"wrote {out} ({len(written)} bytes, sha256 {digest})")
    print(
        f"verified: JPEG {WANT_WIDTH}x{WANT_HEIGHT}, {len(written)} bytes "
        f"(<= 1 MiB), sha256 matches bundled image"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
