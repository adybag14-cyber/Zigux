#!/usr/bin/env python3
"""Thin wrapper delegating to the Zig artifact_diff implementation."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER_ZIG = ROOT / "scripts" / "zigux" / "artifact_diff.zig"


def find_zig(explicit: str | None = None) -> str:
    if explicit:
        return explicit
    env = os.environ.get("ZIG")
    if env:
        return env
    toolchain_dir = ROOT / ".zig-toolchain"
    if toolchain_dir.is_dir():
        candidates = sorted(toolchain_dir.glob("*/zig"))
        if not candidates:
            candidates = sorted(toolchain_dir.glob("*/zig.exe"))
        if candidates:
            return str(candidates[-1])
    path = shutil.which("zig")
    if path:
        return path
    raise SystemExit("zig not found; set ZIG or install zig")


def main() -> int:
    zig = find_zig()
    result = subprocess.run(
        [zig, "run", str(HELPER_ZIG), "--", *sys.argv[1:]],
        cwd=ROOT,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())