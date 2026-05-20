#!/usr/bin/env python3
"""Validate the bounded Phase 3 bitmap/cpumask starter packet."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


DOC_PATH = Path("Documentation/zigux/phase3-bitmap-cpumask-slice.md")
BITMAP_PATH = Path("zigux/helpers/bitmap_view.zig")
CPUMASK_PATH = Path("zigux/helpers/cpumask_view.zig")
TEST_PATH = Path("zigux/tests/phase3_bitmap_cpumask_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig")

REQUIRED_MARKERS = {
    DOC_PATH: (
        "bounded shared-subsystems helper packet",
        "zigux/helpers/bitmap_view.zig",
        "zigux/helpers/cpumask_view.zig",
        "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    ),
    BITMAP_PATH: (
        "pub const word_bits: usize = @bitSizeOf(usize);",
        "pub fn activeWordLen(self: BitmapView) usize {",
        "pub fn countSetBits(self: BitmapView) usize {",
        "pub fn firstSetBit(self: BitmapView) ?usize {",
        "pub fn firstClearBit(self: BitmapView) ?usize {",
    ),
    CPUMASK_PATH: (
        'const bitmap_view = @import("bitmap_view");',
        "pub fn hasCpu(self: CpuMaskView, cpu: usize) bool {",
        "pub fn countPresentCpus(self: CpuMaskView) usize {",
        "pub fn isSubsetOf(self: CpuMaskView, other: CpuMaskView) bool {",
        "pub fn intersects(self: CpuMaskView, other: CpuMaskView) bool {",
    ),
    TEST_PATH: (
        "bitmap starter packet keeps set-bit counting bounded to the declared range",
        "bitmap starter packet keeps a sparse shared bitmap reviewable",
        "cpumask starter packet keeps cpu membership and missing-cpu discovery explicit",
        "cpumask starter packet keeps subset and overlap semantics inside the bounded mask",
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../helpers/bitmap_view.zig"),',
        '.root_source_file = b.path("../helpers/cpumask_view.zig"),',
        'cpumask_view.addImport("bitmap_view", bitmap_view);',
        '"phase3-bitmap-cpumask-starter-packet"',
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def validate_repo(repo_root: Path, zig: str, *, skip_exec: bool = False) -> list[str]:
    issues: list[str] = []

    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        if not path.exists():
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        text = _read(path)
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    if issues or skip_exec:
        return issues

    result = _run(
        [
            zig,
            "build",
            "phase3-bitmap-cpumask-starter-packet",
            "--build-file",
            str(repo_root / BUILD_PATH),
        ],
        cwd=repo_root / "zigux/tests",
    )
    if result.returncode != 0:
        issues.append(
            "zig starter packet failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 3 bitmap/cpumask starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the bitmap/cpumask starter packet",
    )
    parser.add_argument("--zig", help="path to zig executable")
    parser.add_argument("--skip-exec", action="store_true")
    args = parser.parse_args()

    zig = args.zig or os.environ.get("ZIG", "zig")
    issues = validate_repo(args.repo_root, zig, skip_exec=args.skip_exec)
    if issues:
        print("PHASE3_BITMAP_CPUMASK_STARTER_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / BITMAP_PATH}")
    print(f"validated {args.repo_root / CPUMASK_PATH}")
    print(f"validated {args.repo_root / TEST_PATH}")
    print(f"validated {args.repo_root / BUILD_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
