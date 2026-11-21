#!/usr/bin/env python3
"""Entry program: copy entry.png to the output directory.

Runs with no network and only the standard library. The output is
byte-identical on every run because it is a plain file copy; after
copying, the program checks the output's hash against the source, so a
truncated or failed write is caught instead of being graded silently.
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ["MAKEFUN_OUTPUT_DIR"]
SRC = os.path.join(HERE, "entry.png")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


os.makedirs(OUT_DIR, exist_ok=True)
dst = os.path.join(OUT_DIR, "entry.png")
shutil.copyfile(SRC, dst)
if sha256(dst) != sha256(SRC):
    raise SystemExit("entry.png copy failed its integrity check")
