#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ZIG_SCRIPT = ROOT / "scripts" / "zigux" / "stage_pinned_zig_archive.zig"


def find_zig() -> str:
    explicit = os.environ.get("ZIG")
    if explicit:
        return explicit

    toolchain_root = ROOT / ".zig-toolchain"
    if toolchain_root.exists():
        patterns = ("*/zig", "*/zig.exe", "*/bin/zig", "*/bin/zig.exe")
        candidates: list[Path] = []
        for pattern in patterns:
            candidates.extend(sorted(toolchain_root.glob(pattern)))
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate.resolve())

    zig = shutil.which("zig")
    if zig:
        return zig

    raise SystemExit("ZIG_NOT_FOUND")


def main() -> int:
    cmd = [find_zig(), "run", str(ZIG_SCRIPT), "--", *sys.argv[1:]]
    return subprocess.run(cmd, cwd=ROOT).returncode


if __name__ == "__main__":
    raise SystemExit(main())