#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_MARKERS = {
    ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_elf32_second_call_test.zig": {
        "elf32_then_elf64": 'test "fd-backed exact 32-bit ELF header leaves a following 64-bit ELF header for the next call" {',
        "double_elf32": 'test "fd-backed consecutive exact 32-bit ELF headers advance one header per call" {',
        "elf32_then_truncated": 'test "fd-backed exact 32-bit ELF header leaves a following truncated packet for the next call" {',
    },
    ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_elf64_second_call_test.zig": {
        "elf64_then_elf32": 'test "fd-backed exact 64-bit ELF header leaves a following 32-bit ELF header for the next call" {',
        "double_elf64": 'test "fd-backed consecutive exact 64-bit ELF headers advance one header per call" {',
        "elf64_then_truncated": 'test "fd-backed exact 64-bit ELF header leaves a following truncated packet for the next call" {',
    },
    ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_invalid_class_second_call_test.zig": {
        "invalid_class_then_elf32": 'test "fd-backed exact invalid-class header leaves a following 32-bit ELF header for the next call" {',
        "invalid_class_then_not_elf": 'test "fd-backed exact invalid-class header leaves a following non-ELF header for the next call" {',
        "invalid_class_then_truncated": 'test "fd-backed exact invalid-class header leaves a following truncated packet for the next call" {',
    },
    ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_not_elf_second_call_test.zig": {
        "not_elf_then_elf64": 'test "fd-backed exact non-ELF header leaves a following 64-bit ELF header for the next call" {',
        "double_not_elf": 'test "fd-backed consecutive exact non-ELF headers advance one header per call" {',
        "not_elf_then_truncated": 'test "fd-backed exact non-ELF header leaves a following truncated packet for the next call" {',
    },
}


def validate_marker_set(path: Path, expected_markers: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    positions: list[int] = []
    for label, marker in expected_markers.items():
        count = text.count(marker)
        if count == 0:
            raise ValueError(f"{path}:missing_marker:{label}")
        if count > 1:
            raise ValueError(f"{path}:duplicate_marker:{label}")
        positions.append(text.index(marker))
    if positions != sorted(positions):
        raise ValueError(f"{path}:marker_order:{positions!r}")


def validate_markers(root: Path) -> None:
    for path, markers in EXPECTED_MARKERS.items():
        validate_marker_set(root / path.relative_to(ROOT), markers)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_ok_fixture(tmp_root: Path) -> None:
    for path, markers in EXPECTED_MARKERS.items():
        write_text(tmp_root / path.relative_to(ROOT), "\n".join(markers.values()) + "\n")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="lane14-second-call-cluster-") as tmp_dir:
        tmp_root = Path(tmp_dir)

        build_ok_fixture(tmp_root)
        validate_markers(tmp_root)

        invalid_class_path = ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_invalid_class_second_call_test.zig"
        missing_root = tmp_root / "missing"
        build_ok_fixture(missing_root)
        missing_file = missing_root / invalid_class_path.relative_to(ROOT)
        missing_markers = EXPECTED_MARKERS[invalid_class_path]
        missing_file.write_text(
            "\n".join(
                marker
                for label, marker in missing_markers.items()
                if label != "invalid_class_then_truncated"
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(missing_root)
        except ValueError as exc:
            if "missing_marker:invalid_class_then_truncated" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing-marker self-test failure")

        not_elf_path = ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_not_elf_second_call_test.zig"
        duplicate_root = tmp_root / "duplicate"
        build_ok_fixture(duplicate_root)
        duplicate_file = duplicate_root / not_elf_path.relative_to(ROOT)
        duplicate_markers = EXPECTED_MARKERS[not_elf_path]
        duplicate_file.write_text(
            "\n".join(
                [duplicate_markers["not_elf_then_elf64"], duplicate_markers["not_elf_then_elf64"]]
                + [duplicate_markers["double_not_elf"], duplicate_markers["not_elf_then_truncated"]]
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(duplicate_root)
        except ValueError as exc:
            if "duplicate_marker:not_elf_then_elf64" not in str(exc):
                raise
        else:
            raise AssertionError("expected duplicate-marker self-test failure")

        elf64_path = ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_elf64_second_call_test.zig"
        reordered_root = tmp_root / "reordered"
        build_ok_fixture(reordered_root)
        reordered_file = reordered_root / elf64_path.relative_to(ROOT)
        reordered_markers = EXPECTED_MARKERS[elf64_path]
        reordered_file.write_text(
            "\n".join(
                [
                    reordered_markers["double_elf64"],
                    reordered_markers["elf64_then_elf32"],
                    reordered_markers["elf64_then_truncated"],
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

    print("MK_ELFCONFIG_SECOND_CALL_CLUSTER_MARKERS_SELF_TEST=pass")
    print("MK_ELFCONFIG_SECOND_CALL_CLUSTER_MARKERS_SELF_TEST_CASE_COUNT=4")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the mk_elfconfig exact second-call replay cluster stays present and ordered."
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
    print("MK_ELFCONFIG_SECOND_CALL_CLUSTER_MARKERS=pass")
    print(
        "MK_ELFCONFIG_SECOND_CALL_CLUSTER_MARKERS_COUNT="
        f"{sum(len(markers) for markers in EXPECTED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
