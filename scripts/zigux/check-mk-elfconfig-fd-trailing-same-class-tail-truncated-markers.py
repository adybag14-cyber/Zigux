#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

_SCRIPT_PATH = Path(__file__).resolve()
ROOT = _SCRIPT_PATH.parents[2] if len(_SCRIPT_PATH.parents) > 2 else _SCRIPT_PATH.parent
ZIG_TOOL = (
    ROOT
    / "scripts"
    / "zigux"
    / "mk_elfconfig_fd_trailing_same_class_tail_truncated_test.zig"
)

EXPECTED_MARKERS = {
    "fd_trailing_same_class_elf32_tail_truncated": 'test "fd-backed trailing 32-bit ELF input leaves only a truncated tail after the hidden same-class header is consumed" {',
    "fd_trailing_same_class_elf64_tail_truncated": 'test "fd-backed trailing 64-bit ELF input leaves only a truncated tail after the hidden same-class header is consumed" {',
    "fd_trailing_same_class_not_elf_tail_truncated": 'test "fd-backed trailing not-ELF input leaves only a truncated tail after the hidden same-class header is consumed" {',
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
    with tempfile.TemporaryDirectory(
        prefix="lane14-fd-trailing-same-class-tail-truncated-"
    ) as tmp_dir:
        tmp_root = Path(tmp_dir)

        ok_path = tmp_root / "ok.zig"
        ok_path.write_text("\n".join(EXPECTED_MARKERS.values()) + "\n", encoding="utf-8")
        validate_markers(ok_path)

        missing_path = tmp_root / "missing.zig"
        missing_path.write_text(
            "\n".join(
                [
                    EXPECTED_MARKERS["fd_trailing_same_class_elf32_tail_truncated"],
                    EXPECTED_MARKERS["fd_trailing_same_class_elf64_tail_truncated"],
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(missing_path)
        except ValueError as exc:
            if "missing_marker:fd_trailing_same_class_not_elf_tail_truncated" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing-marker self-test failure")

        duplicate_path = tmp_root / "duplicate.zig"
        duplicate_path.write_text(
            "\n".join(
                [
                    EXPECTED_MARKERS["fd_trailing_same_class_elf32_tail_truncated"],
                    EXPECTED_MARKERS["fd_trailing_same_class_elf64_tail_truncated"],
                    EXPECTED_MARKERS["fd_trailing_same_class_not_elf_tail_truncated"],
                    EXPECTED_MARKERS["fd_trailing_same_class_elf32_tail_truncated"],
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(duplicate_path)
        except ValueError as exc:
            if "duplicate_marker:fd_trailing_same_class_elf32_tail_truncated" not in str(exc):
                raise
        else:
            raise AssertionError("expected duplicate-marker self-test failure")

        reordered_path = tmp_root / "reordered.zig"
        reordered_path.write_text(
            "\n".join(
                [
                    EXPECTED_MARKERS["fd_trailing_same_class_elf64_tail_truncated"],
                    EXPECTED_MARKERS["fd_trailing_same_class_elf32_tail_truncated"],
                    EXPECTED_MARKERS["fd_trailing_same_class_not_elf_tail_truncated"],
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

    print("MK_ELFCONFIG_FD_TRAILING_SAME_CLASS_TAIL_TRUNCATED_MARKERS_SELF_TEST=pass")
    print("MK_ELFCONFIG_FD_TRAILING_SAME_CLASS_TAIL_TRUNCATED_MARKERS_SELF_TEST_CASE_COUNT=4")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that mk_elfconfig keeps the same-class trailing hidden-header "
            "tail-truncated replay visible."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root to inspect (defaults to the checker's repository root)",
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

    validate_markers(args.root / "scripts" / "zigux" / ZIG_TOOL.name)
    print("MK_ELFCONFIG_FD_TRAILING_SAME_CLASS_TAIL_TRUNCATED_MARKERS=pass")
    print(
        "MK_ELFCONFIG_FD_TRAILING_SAME_CLASS_TAIL_TRUNCATED_MARKERS_COUNT="
        f"{len(EXPECTED_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())