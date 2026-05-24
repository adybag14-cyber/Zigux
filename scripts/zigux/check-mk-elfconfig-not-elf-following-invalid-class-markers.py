#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZIG_TOOL = ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_not_elf_following_invalid_class_test.zig"

EXPECTED_MARKERS = {
    "not_elf_following_invalid_class": 'test "fd-backed exact non-ELF header leaves a following invalid-class header for the next call" {',
}
EXPECTED_ORDER = list(EXPECTED_MARKERS)


def validate_markers(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    positions: list[int] = []
    for label in EXPECTED_ORDER:
        marker = EXPECTED_MARKERS[label]
        count = text.count(marker)
        if count == 0:
            raise ValueError(f"{path}:missing_marker:{label}")
        if count > 1:
            raise ValueError(f"{path}:duplicate_marker:{label}")
        positions.append(text.index(marker))
    if positions != sorted(positions):
        raise ValueError(f"{path}:marker_order:{positions!r}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="lane14-not-elf-following-invalid-class-") as tmp_dir:
        tmp_root = Path(tmp_dir)

        ok_path = tmp_root / "ok.zig"
        ok_path.write_text("\n".join(EXPECTED_MARKERS.values()) + "\n", encoding="utf-8")
        validate_markers(ok_path)

        missing_path = tmp_root / "missing.zig"
        missing_path.write_text("", encoding="utf-8")
        try:
            validate_markers(missing_path)
        except ValueError as exc:
            if "missing_marker:not_elf_following_invalid_class" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing-marker self-test failure")

        duplicate_path = tmp_root / "duplicate.zig"
        duplicate_path.write_text(
            "\n".join(
                [
                    EXPECTED_MARKERS["not_elf_following_invalid_class"],
                    EXPECTED_MARKERS["not_elf_following_invalid_class"],
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(duplicate_path)
        except ValueError as exc:
            if "duplicate_marker:not_elf_following_invalid_class" not in str(exc):
                raise
        else:
            raise AssertionError("expected duplicate-marker self-test failure")

    print("MK_ELFCONFIG_NOT_ELF_FOLLOWING_INVALID_CLASS_MARKERS_SELF_TEST=pass")
    print("MK_ELFCONFIG_NOT_ELF_FOLLOWING_INVALID_CLASS_MARKERS_SELF_TEST_CASE_COUNT=3")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the mk_elfconfig non-ELF to invalid-class handoff replay marker stays present."
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

    validate_markers(ZIG_TOOL)
    print("MK_ELFCONFIG_NOT_ELF_FOLLOWING_INVALID_CLASS_MARKERS=pass")
    print(f"MK_ELFCONFIG_NOT_ELF_FOLLOWING_INVALID_CLASS_MARKERS_COUNT={len(EXPECTED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
