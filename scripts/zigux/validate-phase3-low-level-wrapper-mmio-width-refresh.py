#!/usr/bin/env python3
"""Validate the bounded P3-L19 MMIO width refresh note against helper reality."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase3-low-level-wrapper-mmio-width-refresh.md")
MMIO_PATH = Path("zigux/helpers/mmio.zig")

NOTE_MARKERS = (
    "The remaining same-lane survey gap is narrower than helper implementation",
    "`read8InteropPolicyBytes()` and `write8InteropPolicyBytes()`",
    "`read8InteropPolicyByte()` and `write8InteropPolicyByte()`",
    "`read16InteropPolicyBytes()` and `write16InteropPolicyBytes()`",
    "`read16InteropPolicyByte()` and `write16InteropPolicyByte()`",
    "`read32InteropPolicyBytes()` and `write32InteropPolicyBytes()`",
    "`read32InteropPolicyByte()` and `write32InteropPolicyByte()`",
    "`read64InteropPolicyBytes()` and `write64InteropPolicyBytes()`",
    "`read64InteropPolicyByte()` and `write64InteropPolicyByte()`",
    "There is no roadmap-backed implementation gap here for atomic, barrier, or MMIO leaf presence",
)

MMIO_MARKERS = (
    "pub fn read8InteropPolicyBytes(",
    "pub fn write8InteropPolicyBytes(",
    "pub fn read8InteropPolicyByte(",
    "pub fn write8InteropPolicyByte(",
    "pub fn read16InteropPolicyBytes(",
    "pub fn write16InteropPolicyBytes(",
    "pub fn read16InteropPolicyByte(",
    "pub fn write16InteropPolicyByte(",
    "pub fn read32InteropPolicyBytes(",
    "pub fn write32InteropPolicyBytes(",
    "pub fn read32InteropPolicyByte(",
    "pub fn write32InteropPolicyByte(",
    "pub fn read64InteropPolicyBytes(",
    "pub fn write64InteropPolicyBytes(",
    "pub fn read64InteropPolicyByte(",
    "pub fn write64InteropPolicyByte(",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")



def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    try:
        note = _read(repo_root / NOTE_PATH)
    except FileNotFoundError:
        return [f"missing repo file: {NOTE_PATH.as_posix()}"]

    try:
        mmio = _read(repo_root / MMIO_PATH)
    except FileNotFoundError:
        return [f"missing repo file: {MMIO_PATH.as_posix()}"]

    for marker in NOTE_MARKERS:
        if marker not in note:
            issues.append(f"missing {NOTE_PATH.as_posix()} marker: {marker}")

    for marker in MMIO_MARKERS:
        if marker not in mmio:
            issues.append(f"missing {MMIO_PATH.as_posix()} marker: {marker}")

    return issues



def _populate_repo(root: Path) -> None:
    _write(root / NOTE_PATH, "\n".join(NOTE_MARKERS) + "\n")
    _write(root / MMIO_PATH, "\n".join(MMIO_MARKERS) + "\n")



def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_p3l19_mmio_width_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("P3_L19_MMIO_WIDTH_REFRESH_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for marker in NOTE_MARKERS:
            _populate_repo(root)
            note_path = root / NOTE_PATH
            note_path.write_text(_read(note_path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {NOTE_PATH.as_posix()} marker: {marker}"
            if expected not in issues:
                print("P3_L19_MMIO_WIDTH_REFRESH_SELF_TEST=fail")
                print(f"expected missing note marker was not reported: {expected}")
                return 1

        for marker in MMIO_MARKERS:
            _populate_repo(root)
            mmio_path = root / MMIO_PATH
            mmio_path.write_text(_read(mmio_path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {MMIO_PATH.as_posix()} marker: {marker}"
            if expected not in issues:
                print("P3_L19_MMIO_WIDTH_REFRESH_SELF_TEST=fail")
                print(f"expected missing helper marker was not reported: {expected}")
                return 1

    print("P3_L19_MMIO_WIDTH_REFRESH_SELF_TEST=pass")
    print(f"P3_L19_MMIO_WIDTH_REFRESH_SELF_TEST_CASE_COUNT={len(NOTE_MARKERS) + len(MMIO_MARKERS)}")
    return 0



def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded P3-L19 MMIO width refresh note against helper reality."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("P3_L19_MMIO_WIDTH_REFRESH=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {NOTE_PATH.as_posix()}")
    print(f"validated {MMIO_PATH.as_posix()}")
    print("P3_L19_MMIO_WIDTH_REFRESH=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
