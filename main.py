#!/usr/bin/env python3
"""ai-excited-01: copy the bundled roller-coaster image to /output/entry.png.

Standard library only. Deterministic: no network, no randomness, no
timestamps. The bundled image is checked, copied verbatim, then the
written output is read back and checked again before success is
reported.
"""

import hashlib
import os
import sys

# sha256 of the bundled entry.jpg, computed from the file itself.
EXPECTED_SHA256 = "5ca7c88f957e0cbbb98a9489823d45419afc83d5f01cfd3e3309c2a4e3de026a"
MAX_BYTES = 1048576
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024

# SOF markers that carry frame dimensions (baseline + progressive).
SOF_MARKERS = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
               0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}


class EntryImage:
    """One image's bytes plus the facts derived from them."""

    def __init__(self, data: bytes):
        self.data = data
        self.sha256 = hashlib.sha256(data).hexdigest()
        self.size = len(data)
        self.width = None
        self.height = None
        self.dimensions_error = None
        try:
            self.width, self.height = parse_jpeg_dimensions(data)
        except ValueError as exc:
            self.dimensions_error = str(exc)

    def problems(self, label: str) -> list:
        """Verification failures for this image, prefixed with its label."""
        found = []
        if self.sha256 != EXPECTED_SHA256:
            found.append("%s: sha256 mismatch" % label)
        if self.size > MAX_BYTES:
            found.append("%s: image over 1 MiB (%d bytes)" % (label, self.size))
        if not self.data.startswith(b"\xff\xd8"):
            found.append("%s: missing JPEG SOI marker" % label)
        if not self.data.endswith(b"\xff\xd9"):
            found.append("%s: missing JPEG EOI marker" % label)
        if self.dimensions_error is not None:
            found.append("%s: dimension parse failed: %s"
                         % (label, self.dimensions_error))
        elif (self.width, self.height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
            found.append("%s: dimensions %dx%d, expected %dx%d"
                         % (label, self.width, self.height,
                            EXPECTED_WIDTH, EXPECTED_HEIGHT))
        return found


def parse_jpeg_dimensions(data: bytes) -> tuple:
    """Return (width, height) from the first SOF segment of a JPEG stream."""
    if len(data) < 4 or data[0] != 0xFF or data[1] != 0xD8:
        raise ValueError("not a JPEG (missing SOI)")
    pos = 2
    while pos + 4 <= len(data):
        if data[pos] != 0xFF:
            raise ValueError("bad marker at offset %d" % pos)
        marker = data[pos + 1]
        # Standalone markers carry no length field.
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7 or marker == 0x01:
            pos += 2
            continue
        seg_len = (data[pos + 2] << 8) | data[pos + 3]
        if seg_len < 2 or pos + 2 + seg_len > len(data):
            raise ValueError("truncated segment at offset %d" % pos)
        if marker in SOF_MARKERS:
            if seg_len < 7:
                raise ValueError("SOF segment too short")
            height = (data[pos + 5] << 8) | data[pos + 6]
            width = (data[pos + 7] << 8) | data[pos + 8]
            return width, height
        if marker == 0xDA:  # SOS: entropy data follows, no more headers.
            raise ValueError("no SOF segment before scan data")
        pos += 2 + seg_len
    raise ValueError("no SOF segment found")


def read_file(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


def write_file(path: str, data: bytes) -> None:
    with open(path, "wb") as fh:
        fh.write(data)


def fail(problems: list) -> int:
    for problem in problems:
        print("VERIFICATION FAILED:", problem, file=sys.stderr)
    return 1


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.jpg")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    dest = os.path.join(out_dir, "entry.png")

    bundled = EntryImage(read_file(source))
    problems = bundled.problems("bundled image")
    if problems:
        return fail(problems)

    os.makedirs(out_dir, exist_ok=True)
    write_file(dest, bundled.data)

    # Read the output back and verify it is byte-identical to the source.
    written = EntryImage(read_file(dest))
    problems = written.problems("written output")
    if problems:
        return fail(problems)
    if written.data != bundled.data:
        return fail(["written output: bytes differ from bundled image"])

    print("sha256:", written.sha256)
    print("size:", written.size, "bytes")
    print("dimensions: %dx%d" % (written.width, written.height))
    print("wrote:", dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
