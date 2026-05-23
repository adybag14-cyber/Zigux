#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZIG_TOOL = ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_exact_cursor_test.zig"

EXPECTED_MARKERS = {
    "fd_exact_cursor_empty": 'test "fd-backed exact empty input leaves the cursor at zero" {',
    "fd_exact_cursor_truncated": 'test "fd-backed exact truncated input leaves the cursor at the truncated byte count" {',
    "fd_exact_cursor_near_full": 'test "fd-backed one-byte-short input leaves the cursor at fifteen bytes" {',
    "fd_exact_cursor_elf32": 'test "fd-backed exact 32-bit ELF input leaves the cursor at the full header" {',
    "fd_exact_cursor_elf32_trailing": 'test "fd-backed exact 32-bit ELF input with trailing bytes still leaves the cursor at the full header" {',
    "fd_exact_cursor_elf64": 'test "fd-backed exact 64-bit ELF input leaves the cursor at the full header" {',
    "fd_exact_cursor_elf64_trailing": 'test "fd-backed exact 64-bit ELF input with trailing bytes still leaves the cursor at the full header" {',
    "fd_exact_cursor_invalid_class": 'test "fd-backed exact invalid-class input leaves the cursor at the full header" {',
    "fd_exact_cursor_invalid_class_trailing": 'test "fd-backed exact invalid-class input with trailing bytes still leaves the cursor at the full header" {',
    "fd_exact_cursor_not_elf": 'test "fd-backed exact non-ELF input leaves the cursor at the full header" {',
    "fd_exact_cursor_not_elf_trailing": 'test "fd-backed exact non-ELF input with trailing bytes still leaves the cursor at the full header" {',
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
    with tempfile.TemporaryDirectory(prefix="lane14-fd-exact-cursor-") as tmp_dir:
        tmp_root = Path(tmp_dir)

        ok_path = tmp_root / "ok.zig"
        ok_path.write_text("\n".join(EXPECTED_MARKERS.values()) + "\n", encoding="utf-8")
        validate_markers(ok_path)

        missing_path = tmp_root / "missing.zig"
        missing_path.write_text(
            "\n".join(list(EXPECTED_MARKERS.values())[:-1]) + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(missing_path)
        except ValueError as exc:
            if "missing_marker:fd_exact_cursor_not_elf_trailing" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing-marker self-test failure")

        duplicate_path = tmp_root / "duplicate.zig"
        duplicate_path.write_text(
            "\n".join(
                list(EXPECTED_MARKERS.values())
                + [EXPECTED_MARKERS["fd_exact_cursor_elf32"]]
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(duplicate_path)
        except ValueError as exc:
            if "duplicate_marker:fd_exact_cursor_elf32" not in str(exc):
                raise
        else:
            raise AssertionError("expected duplicate-marker self-test failure")

        reordered_path = tmp_root / "reordered.zig"
        reordered_path.write_text(
            "\n".join(
                [
                    EXPECTED_MARKERS["fd_exact_cursor_empty"],
                    EXPECTED_MARKERS["fd_exact_cursor_truncated"],
                    EXPECTED_MARKERS["fd_exact_cursor_elf32"],
                    EXPECTED_MARKERS["fd_exact_cursor_near_full"],
                    EXPECTED_MARKERS["fd_exact_cursor_elf32_trailing"],
                    EXPECTED_MARKERS["fd_exact_cursor_elf64"],
                    EXPECTED_MARKERS["fd_exact_cursor_elf64_trailing"],
                    EXPECTED_MARKERS["fd_exact_cursor_invalid_class"],
                    EXPECTED_MARKERS["fd_exact_cursor_invalid_class_trailing"],
                    EXPECTED_MARKERS["fd_exact_cursor_not_elf"],
                    EXPECTED_MARKERS["fd_exact_cursor_not_elf_trailing"],
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(reordered_path)
        except ValueError as exc:
            if "marker_order:" not in str(exc):
                raise
        else:
            raise AssertionError("expected marker-order self-test failure")

    print("MK_ELFCONFIG_FD_EXACT_CURSOR_MARKERS_SELF_TEST=pass")
    print("MK_ELFCONFIG_FD_EXACT_CURSOR_MARKERS_SELF_TEST_CASE_COUNT=4")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that mk_elfconfig keeps the fd exact-cursor packet visible."
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
    print("MK_ELFCONFIG_FD_EXACT_CURSOR_MARKERS=pass")
    print(f"MK_ELFCONFIG_FD_EXACT_CURSOR_MARKERS_COUNT={len(EXPECTED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
