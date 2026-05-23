#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZIG_TOOL = ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_invalid_class_following_elf64_test.zig"

EXPECTED_MARKER = 'test "fd-backed exact invalid-class header leaves a following 64-bit ELF header for the next call" {'


def validate_marker(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(EXPECTED_MARKER)
    if count == 0:
        raise ValueError(f"{path}:missing_marker:invalid_class_then_elf64")
    if count > 1:
        raise ValueError(f"{path}:duplicate_marker:invalid_class_then_elf64")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="lane14-invalid-class-following-elf64-") as tmp_dir:
        tmp_root = Path(tmp_dir)

        ok_path = tmp_root / "ok.zig"
        ok_path.write_text(EXPECTED_MARKER + "\n", encoding="utf-8")
        validate_marker(ok_path)

        missing_path = tmp_root / "missing.zig"
        missing_path.write_text("", encoding="utf-8")
        try:
            validate_marker(missing_path)
        except ValueError as exc:
            if "missing_marker:invalid_class_then_elf64" not in str(exc):
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
            if "duplicate_marker:invalid_class_then_elf64" not in str(exc):
                raise
        else:
            raise AssertionError("expected duplicate-marker self-test failure")

    print("MK_ELFCONFIG_INVALID_CLASS_FOLLOWING_ELF64_MARKERS_SELF_TEST=pass")
    print("MK_ELFCONFIG_INVALID_CLASS_FOLLOWING_ELF64_MARKERS_SELF_TEST_CASE_COUNT=3")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the mk_elfconfig invalid-class to 64-bit ELF handoff replay marker stays present."
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
    print("MK_ELFCONFIG_INVALID_CLASS_FOLLOWING_ELF64_MARKERS=pass")
    print("MK_ELFCONFIG_INVALID_CLASS_FOLLOWING_ELF64_MARKERS_COUNT=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
