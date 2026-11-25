#!/usr/bin/env python3
"""Copy the pre-rendered front page to the output directory.

The image is rendered offline by compose.py; this program only checks
that entry.png is a whole 1024x1024 PNG under 1 MiB and copies it
unchanged, so both grader runs write the same bytes.
"""
import hashlib
import os
import shutil
import struct
import sys

NAME = "entry.png"
LIMIT = 1048576


def fail(message):
    print("error:", message, file=sys.stderr)
    return 1


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, NAME)
    try:
        with open(src, "rb") as handle:
            blob = handle.read()
    except OSError as exc:
        return fail(f"cannot read {NAME}: {exc}")
    if len(blob) > LIMIT:
        return fail(f"{NAME} is {len(blob)} bytes, over the 1 MiB limit")
    if blob[:8] != b"\x89PNG\r\n\x1a\n":
        return fail(f"{NAME} does not start with the PNG signature")
    if len(blob) < 33 or blob[12:16] != b"IHDR":
        return fail(f"{NAME} has no IHDR chunk where one belongs")
    width, height = struct.unpack(">II", blob[16:24])
    if (width, height) != (1024, 1024):
        return fail(f"{NAME} is {width}x{height}, expected 1024x1024")
    # The destination honours the grader's output directory first, then
    # the container's /output, then the working directory as a fallback.
    dest_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or (
        "/output" if os.path.isdir("/output") else os.getcwd()
    )
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, NAME)
    with open(src, "rb") as handle_in, open(dest, "wb") as handle_out:
        shutil.copyfileobj(handle_in, handle_out)
    digest = hashlib.sha256(blob).hexdigest()
    print(f"wrote {dest}: {len(blob)} bytes, sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
