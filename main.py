#!/usr/bin/env python3
"""Copy the bundled roller-coaster image to the judged output path.

Reads entry.jpg next to this script, verifies it is a real JPEG within
the competition limits, and writes it verbatim to entry.png under the
output directory. The copy is read back and compared byte for byte.
Standard library only; no network; deterministic by construction.
"""

import hashlib
import os
import struct
import sys

SOURCE_NAME = "entry.jpg"
TARGET_NAME = "entry.png"
MAX_BYTES = 1048576
MAX_SIDE = 1024


def die(message):
    """Print an error and exit nonzero."""
    print("error: " + message, file=sys.stderr)
    raise SystemExit(1)


def script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def output_dir():
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def load_source(directory):
    """Read entry.jpg from directory and return it as a JpegInfo."""
    path = os.path.join(directory, SOURCE_NAME)
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        die("cannot read %s: %s" % (path, exc))
    if not data:
        die("source image is empty")
    if len(data) > MAX_BYTES:
        die("source image is %d bytes, over the %d limit"
            % (len(data), MAX_BYTES))
    if data[:2] != b"\xff\xd8":
        die("source image does not start with a JPEG SOI marker")
    if data[-2:] != b"\xff\xd9":
        die("source image does not end with a JPEG EOI marker")
    return JpegInfo.from_bytes(data)


class JpegInfo:
    """A validated JPEG: its bytes plus the size from its SOF frame."""

    def __init__(self, data, width, height):
        self.data = data
        self.width = width
        self.height = height

    @classmethod
    def from_bytes(cls, data):
        width, height = cls._frame_size(data)
        return cls(data, width, height)

    @staticmethod
    def _frame_size(data):
        """Scan JPEG markers for the first SOF frame, return (width, height)."""
        pos = 2
        while pos + 1 < len(data):
            if data[pos] != 0xFF:
                pos += 1
                continue
            marker = data[pos + 1]
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                pos += 2
                continue
            if pos + 4 > len(data):
                break
            length = struct.unpack(">H", data[pos + 2:pos + 4])[0]
            if marker in (0xC0, 0xC1, 0xC2):
                height, width = struct.unpack(">HH", data[pos + 5:pos + 9])
                return width, height
            pos += 2 + length
        die("no JPEG start-of-frame segment found")

    def validate(self):
        if self.width > MAX_SIDE or self.height > MAX_SIDE:
            die("image is %dx%d, over the %dx%d limit"
                % (self.width, self.height, MAX_SIDE, MAX_SIDE))
        if self.width <= 0 or self.height <= 0:
            die("image has a non-positive dimension")


def read_back(dest):
    try:
        with open(dest, "rb") as handle:
            return handle.read()
    except OSError as exc:
        die("cannot read back %s: %s" % (dest, exc))


def publish_copy(data, dest):
    """Write data to dest, read it back, and return its sha256 hex digest."""
    parent = os.path.dirname(dest)
    if parent:
        os.makedirs(parent, exist_ok=True)
    try:
        with open(dest, "wb") as handle:
            handle.write(data)
    except OSError as exc:
        die("cannot write %s: %s" % (dest, exc))
    written = read_back(dest)
    if written != data:
        die("read-back of %s differs from the source bytes" % dest)
    return hashlib.sha256(written).hexdigest()


def main():
    image = load_source(script_dir())
    image.validate()
    print("source ok: %s (%d bytes, %dx%d)"
          % (SOURCE_NAME, len(image.data), image.width, image.height))
    dest = os.path.join(output_dir(), TARGET_NAME)
    digest = publish_copy(image.data, dest)
    print("wrote %s sha256 %s" % (dest, digest))


if __name__ == "__main__":
    main()
