#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MULTI_HEADER_ZIG_TOOL = ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_multi_header_cursor_test.zig"
NOT_ELF_FOLLOWING_ELF64_ZIG_TOOL = (
    ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_not_elf_following_elf64_test.zig"
)
ELF64_FOLLOWING_ELF32_ZIG_TOOL = (
    ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_elf64_following_elf32_test.zig"
)
DOUBLE_INVALID_CLASS_ZIG_TOOL = (
    ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_double_invalid_class_test.zig"
)

EXPECTED_MULTI_HEADER_MARKERS = {
    "fd_multi_exact_headers": 'test "fd-backed consecutive exact ELF headers advance one header per call" {',
    "fd_multi_elf32_then_not_elf": 'test "fd-backed exact 32-bit ELF header leaves a following non-ELF header for the next call" {',
    "fd_multi_elf32_then_invalid_class": 'test "fd-backed exact 32-bit ELF header leaves a following invalid-class header for the next call" {',
    "fd_multi_elf32_then_truncated": 'test "fd-backed exact 32-bit ELF header leaves a following truncated packet for the next call" {',
    "fd_multi_elf64_then_not_elf": 'test "fd-backed exact 64-bit ELF header leaves a following non-ELF header for the next call" {',
    "fd_multi_elf64_then_invalid_class": 'test "fd-backed exact 64-bit ELF header leaves a following invalid-class header for the next call" {',
    "fd_multi_not_elf_then_elf32": 'test "fd-backed exact non-ELF header leaves a following ELF header for the next call" {',
    "fd_multi_not_elf_then_truncated": 'test "fd-backed exact non-ELF header leaves a following truncated packet for the next call" {',
    "fd_multi_not_elf_then_invalid_class": 'test "fd-backed exact non-ELF header leaves a following invalid-class header for the next call" {',
    "fd_multi_invalid_class_then_elf32": 'test "fd-backed exact invalid-class header leaves a following 32-bit ELF header for the next call" {',
    "fd_multi_invalid_class_then_elf64": 'test "fd-backed exact invalid-class header leaves a following ELF header for the next call" {',
    "fd_multi_invalid_class_then_not_elf": 'test "fd-backed exact invalid-class header leaves a following non-ELF header for the next call" {',
    "fd_multi_invalid_class_then_truncated": 'test "fd-backed exact invalid-class header leaves a following truncated packet for the next call" {',
    "fd_multi_double_not_elf": 'test "fd-backed consecutive exact non-ELF headers advance one header per call" {',
    "fd_multi_truncated_second": 'test "fd-backed truncated second packet keeps the first exact header cursor advance" {',
}
EXPECTED_MULTI_HEADER_ORDER = list(EXPECTED_MULTI_HEADER_MARKERS)

EXPECTED_STANDALONE_MARKERS = {
    NOT_ELF_FOLLOWING_ELF64_ZIG_TOOL: {
        "fd_not_elf_following_elf64": 'test "fd-backed exact non-ELF header leaves a following 64-bit ELF header for the next call" {',
    },
    ELF64_FOLLOWING_ELF32_ZIG_TOOL: {
        "fd_elf64_following_elf32": 'test "fd-backed exact 64-bit ELF header leaves a following 32-bit ELF header for the next call" {',
    },
    DOUBLE_INVALID_CLASS_ZIG_TOOL: {
        "fd_double_invalid_class": 'test "fd-backed consecutive exact invalid-class headers advance one header per call" {',
    },
}


def validate_marker_set(path: Path, expected_markers: dict[str, str], *, enforce_order: bool) -> None:
    text = path.read_text(encoding="utf-8")
    positions: list[int] = []
    for label, marker in expected_markers.items():
        count = text.count(marker)
        if count == 0:
            raise ValueError(f"{path}:missing_marker:{label}")
        if count > 1:
            raise ValueError(f"{path}:duplicate_marker:{label}")
        positions.append(text.index(marker))
    if enforce_order and positions != sorted(positions):
        raise ValueError(f"{path}:marker_order:{positions!r}")


def validate_markers(root: Path) -> None:
    validate_marker_set(
        root / "scripts" / "zigux" / "mk_elfconfig_fd_multi_header_cursor_test.zig",
        EXPECTED_MULTI_HEADER_MARKERS,
        enforce_order=True,
    )
    for path, markers in EXPECTED_STANDALONE_MARKERS.items():
        relative_path = path.relative_to(ROOT)
        validate_marker_set(root / relative_path, markers, enforce_order=False)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_ok_fixture(tmp_root: Path) -> None:
    write_text(
        tmp_root / "scripts" / "zigux" / "mk_elfconfig_fd_multi_header_cursor_test.zig",
        "\n".join(EXPECTED_MULTI_HEADER_MARKERS[label] for label in EXPECTED_MULTI_HEADER_ORDER) + "\n",
    )
    for path, markers in EXPECTED_STANDALONE_MARKERS.items():
        write_text(
            tmp_root / path.relative_to(ROOT),
            "\n".join(markers.values()) + "\n",
        )


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="lane14-fd-handoff-markers-") as tmp_dir:
        tmp_root = Path(tmp_dir)

        build_ok_fixture(tmp_root)
        validate_markers(tmp_root)

        missing_root = tmp_root / "missing"
        build_ok_fixture(missing_root)
        missing_file = missing_root / "scripts" / "zigux" / "mk_elfconfig_fd_multi_header_cursor_test.zig"
        missing_file.write_text(
            "\n".join(
                EXPECTED_MULTI_HEADER_MARKERS[label]
                for label in EXPECTED_MULTI_HEADER_ORDER
                if label != "fd_multi_invalid_class_then_truncated"
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(missing_root)
        except ValueError as exc:
            if "missing_marker:fd_multi_invalid_class_then_truncated" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing-marker self-test failure")

        duplicate_root = tmp_root / "duplicate"
        build_ok_fixture(duplicate_root)
        duplicate_file = duplicate_root / "scripts" / "zigux" / "mk_elfconfig_fd_not_elf_following_elf64_test.zig"
        duplicate_file.write_text(
            "\n".join(
                [
                    EXPECTED_STANDALONE_MARKERS[NOT_ELF_FOLLOWING_ELF64_ZIG_TOOL]["fd_not_elf_following_elf64"],
                    EXPECTED_STANDALONE_MARKERS[NOT_ELF_FOLLOWING_ELF64_ZIG_TOOL]["fd_not_elf_following_elf64"],
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(duplicate_root)
        except ValueError as exc:
            if "duplicate_marker:fd_not_elf_following_elf64" not in str(exc):
                raise
        else:
            raise AssertionError("expected duplicate-marker self-test failure")

        reordered_root = tmp_root / "reordered"
        build_ok_fixture(reordered_root)
        reordered_file = reordered_root / "scripts" / "zigux" / "mk_elfconfig_fd_multi_header_cursor_test.zig"
        reordered_file.write_text(
            "\n".join(
                [EXPECTED_MULTI_HEADER_MARKERS["fd_multi_exact_headers"]]
                + [EXPECTED_MULTI_HEADER_MARKERS["fd_multi_elf32_then_invalid_class"]]
                + [EXPECTED_MULTI_HEADER_MARKERS["fd_multi_elf32_then_not_elf"]]
                + [
                    EXPECTED_MULTI_HEADER_MARKERS[label]
                    for label in EXPECTED_MULTI_HEADER_ORDER
                    if label
                    not in {
                        "fd_multi_exact_headers",
                        "fd_multi_elf32_then_not_elf",
                        "fd_multi_elf32_then_invalid_class",
                    }
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(reordered_root)
        except ValueError as exc:
            if "marker_order:" not in str(exc):
                raise
        else:
            raise AssertionError("expected marker-order self-test failure")

    print("MK_ELFCONFIG_FD_HANDOFF_MARKERS_SELF_TEST=pass")
    print("MK_ELFCONFIG_FD_HANDOFF_MARKERS_SELF_TEST_CASE_COUNT=4")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that mk_elfconfig keeps the fd-backed handoff packet markers visible."
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

    validate_markers(ROOT)
    print("MK_ELFCONFIG_FD_HANDOFF_MARKERS=pass")
    print(
        "MK_ELFCONFIG_FD_HANDOFF_MARKERS_COUNT="
        f"{len(EXPECTED_MULTI_HEADER_MARKERS) + len(EXPECTED_STANDALONE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
