#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZIG_TOOL = ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_elf32_following_invalid_class_test.zig"

EXPECTED_MARKER = 'test "fd-backed exact 32-bit ELF header leaves a following invalid-class header for the next call" {'


def validate_marker(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(EXPECTED_MARKER)
    if count == 0:
        raise ValueError(f"{path}:missing_marker:elf32_then_invalid_class")
    if count > 1:
        raise ValueError(f"{path}:duplicate_marker:elf32_then_invalid_class")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="lane14-elf32-following-invalid-class-") as tmp_dir:
        tmp_root = Path(tmp_dir)

        ok_path = tmp_root / "ok.zig"
        ok_path.write_text(EXPECTED_MARKER + "\n", encoding="utf-8")
        validate_marker(ok_path)

        missing_path = tmp_root / "missing.zig"
        missing_path.write_text("", encoding="utf-8")
        try:
            validate_marker(missing_path)
        except ValueError as exc:
            if "missing_marker:elf32_then_invalid_class" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing-marker self-test failure")

        duplicate_path = tmp_root / "duplicate.zig"
        duplicate_path.write_text(
            "\n".join([EXPECTED_MARKER, EXPECTED_MARKER]) + "\n",
            encoding="utf-8",
        )
        try:
            validate_marker(duplicate_path)
        except ValueError as exc:
            if "duplicate_marker:elf32_then_invalid_class" not in str(exc):
                raise
        else:
            raise AssertionError("expected duplicate-marker self-test failure")

    print("MK_ELFCONFIG_ELF32_FOLLOWING_INVALID_CLASS_MARKERS_SELF_TEST=pass")
    print("MK_ELFCONFIG_ELF32_FOLLOWING_INVALID_CLASS_MARKERS_SELF_TEST_CASE_COUNT=3")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the mk_elfconfig 32-bit ELF to invalid-class handoff replay marker stays present."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="validate the checker logic against synthetic marker fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    validate_marker(ZIG_TOOL)
    print("MK_ELFCONFIG_ELF32_FOLLOWING_INVALID_CLASS_MARKERS=pass")
    print("MK_ELFCONFIG_ELF32_FOLLOWING_INVALID_CLASS_MARKERS_COUNT=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
