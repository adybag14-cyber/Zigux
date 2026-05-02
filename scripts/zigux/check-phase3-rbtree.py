#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _find_cc() -> str:
    for candidate in ("gcc", "cc", "clang"):
        path = shutil.which(candidate)
        if path:
            return path
    raise SystemExit("no C compiler found")


def _find_zig() -> str:
    explicit = os.environ.get("ZIG")
    if explicit:
        return explicit
    path = shutil.which("zig")
    if path:
        return path
    raise SystemExit("zig not found")


def _run_json(cmd: list[str], *, cwd: Path) -> dict[str, object]:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def main() -> int:
    fixture = ROOT / "zigux" / "tests" / "fixtures" / "phase3_rbtree" / "expected.json"
    build_file = ROOT / "zigux" / "tests" / "phase3_rbtree_build.zig"
    harness = ROOT / "zigux" / "tests" / "fixtures" / "phase3_rbtree" / "phase3_rbtree_c_harness.c"

    expected = json.loads(fixture.read_text(encoding="utf-8"))
    cc = _find_cc()
    zig = _find_zig()

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_rbtree_") as tmp_dir:
        tmp = Path(tmp_dir)
        harness_bin = tmp / "phase3_rbtree_c_harness"
        subprocess.run(
            [cc, "-std=gnu11", "-Wall", "-Wextra", "-I", str(ROOT / "include"), "-o", str(harness_bin), str(harness)],
            cwd=ROOT,
            check=True,
        )
        c_actual = _run_json([str(harness_bin)], cwd=ROOT)
        zig_actual = _run_json(
            [zig, "build", "phase3-rbtree-dump", "--build-file", str(build_file)],
            cwd=ROOT,
        )

    if c_actual != expected:
        print("PHASE3_RBTREE_DIFF=fail")
        print("c-harness output drifted from expected.json")
        return 1
    if zig_actual != expected:
        print("PHASE3_RBTREE_DIFF=fail")
        print("zig dump output drifted from expected.json")
        return 1

    print("PHASE3_RBTREE_DIFF=pass")
    print(f"FIXTURE={fixture}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
