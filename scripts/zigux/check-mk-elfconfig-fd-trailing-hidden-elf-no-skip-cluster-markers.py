#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

_SCRIPT_PATH = Path(__file__).resolve()
ROOT = _SCRIPT_PATH.parents[2] if len(_SCRIPT_PATH.parents) > 2 else _SCRIPT_PATH.parent

EXPECTED_MARKERS = {
    Path("scripts/zigux/mk_elfconfig_fd_invalid_class_trailing_hidden_elf_no_skip_test.zig"): [
        (
            "fd_invalid_class_trailing_hidden_elf32_no_skip",
            'test "fd-backed trailing invalid-class input does not silently skip forward to the hidden 32-bit ELF header" {',
        ),
        (
            "fd_invalid_class_trailing_hidden_elf64_no_skip",
            'test "fd-backed trailing invalid-class input does not silently skip forward to the hidden 64-bit ELF header" {',
        ),
    ],
    Path("scripts/zigux/mk_elfconfig_fd_not_elf_trailing_hidden_elf_no_skip_test.zig"): [
        (
            "fd_not_elf_trailing_hidden_elf32_no_skip",
            'test "fd-backed trailing not-ELF input does not silently skip forward to the hidden 32-bit ELF header" {',
        ),
        (
            "fd_not_elf_trailing_hidden_elf64_no_skip",
            'test "fd-backed trailing not-ELF input does not silently skip forward to the hidden 64-bit ELF header" {',
        ),
    ],
}


def validate_file(path: Path, expected_markers: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    positions: list[int] = []
    for label, marker in expected_markers:
        count = text.count(marker)
        if count == 0:
            raise ValueError(f"{path}:missing_marker:{label}")
        if count > 1:
            raise ValueError(f"{path}:duplicate_marker:{label}")
        positions.append(text.index(marker))
    if positions != sorted(positions):
        raise ValueError(f"{path}:marker_order:{positions!r}")


def validate_markers(root: Path) -> None:
    for relative_path, expected_markers in EXPECTED_MARKERS.items():
        validate_file(root / relative_path, expected_markers)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_ok_fixture(tmp_root: Path) -> None:
    for relative_path, expected_markers in EXPECTED_MARKERS.items():
        write_text(tmp_root / relative_path, "\n".join(marker for _, marker in expected_markers) + "\n")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="lane14-fd-trailing-hidden-elf-no-skip-cluster-") as tmp_dir:
        tmp_root = Path(tmp_dir)

        build_ok_fixture(tmp_root)
        validate_markers(tmp_root)

        missing_root = tmp_root / "missing"
        build_ok_fixture(missing_root)
        missing_path = missing_root / "scripts/zigux/mk_elfconfig_fd_not_elf_trailing_hidden_elf_no_skip_test.zig"
        missing_path.write_text(
            EXPECTED_MARKERS[Path("scripts/zigux/mk_elfconfig_fd_not_elf_trailing_hidden_elf_no_skip_test.zig")][0][1]
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(missing_root)
        except ValueError as exc:
            if "missing_marker:fd_not_elf_trailing_hidden_elf64_no_skip" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing-marker self-test failure")

        duplicate_root = tmp_root / "duplicate"
        build_ok_fixture(duplicate_root)
        duplicate_path = (
            duplicate_root / "scripts/zigux/mk_elfconfig_fd_invalid_class_trailing_hidden_elf_no_skip_test.zig"
        )
        duplicate_marker = EXPECTED_MARKERS[
            Path("scripts/zigux/mk_elfconfig_fd_invalid_class_trailing_hidden_elf_no_skip_test.zig")
        ][0][1]
        duplicate_path.write_text(
            "\n".join(
                [
                    duplicate_marker,
                    EXPECTED_MARKERS[
                        Path("scripts/zigux/mk_elfconfig_fd_invalid_class_trailing_hidden_elf_no_skip_test.zig")
                    ][1][1],
                    duplicate_marker,
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(duplicate_root)
        except ValueError as exc:
            if "duplicate_marker:fd_invalid_class_trailing_hidden_elf32_no_skip" not in str(exc):
                raise
        else:
            raise AssertionError("expected duplicate-marker self-test failure")

        reordered_root = tmp_root / "reordered"
        build_ok_fixture(reordered_root)
        reordered_path = reordered_root / "scripts/zigux/mk_elfconfig_fd_not_elf_trailing_hidden_elf_no_skip_test.zig"
        reordered_markers = EXPECTED_MARKERS[
            Path("scripts/zigux/mk_elfconfig_fd_not_elf_trailing_hidden_elf_no_skip_test.zig")
        ]
        reordered_path.write_text(
            "\n".join(
                [
                    reordered_markers[1][1],
                    reordered_markers[0][1],
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

    print("MK_ELFCONFIG_FD_TRAILING_HIDDEN_ELF_NO_SKIP_CLUSTER_MARKERS_SELF_TEST=pass")
    print("MK_ELFCONFIG_FD_TRAILING_HIDDEN_ELF_NO_SKIP_CLUSTER_MARKERS_SELF_TEST_CASE_COUNT=4")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the mk_elfconfig trailing-input hidden-ELF no-skip replay cluster stays present."
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

    validate_markers(args.root)
    print("MK_ELFCONFIG_FD_TRAILING_HIDDEN_ELF_NO_SKIP_CLUSTER_MARKERS=pass")
    print(f"MK_ELFCONFIG_FD_TRAILING_HIDDEN_ELF_NO_SKIP_CLUSTER_MARKERS_COUNT={len(EXPECTED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
