#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_MARKERS = {
    ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_trailing_then_following_header_test.zig": {
        "label": "not_elf_then_trailing_following_header",
        "marker": 'test "fd-backed exact non-ELF header with trailing bytes folds a later ELF header into the next not-ELF packet" {',
    },
    ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_elf32_trailing_then_following_header_test.zig": {
        "label": "elf32_then_trailing_following_header",
        "marker": 'test "fd-backed exact 32-bit ELF header with trailing bytes folds a later 32-bit ELF header into the next not-ELF packet" {',
    },
    ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_invalid_class_trailing_then_following_header_test.zig": {
        "label": "invalid_class_then_trailing_following_header",
        "marker": 'test "fd-backed exact invalid-class header with trailing bytes folds a later ELF header into the next not-ELF packet" {',
    },
}


def validate_marker(path: Path, label: str, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(marker)
    if count == 0:
        raise ValueError(f"{path}:missing_marker:{label}")
    if count > 1:
        raise ValueError(f"{path}:duplicate_marker:{label}")


def validate_markers(root: Path) -> None:
    for path, entry in EXPECTED_MARKERS.items():
        validate_marker(root / path.relative_to(ROOT), entry["label"], entry["marker"])


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_ok_fixture(tmp_root: Path) -> None:
    for path, entry in EXPECTED_MARKERS.items():
        write_text(tmp_root / path.relative_to(ROOT), entry["marker"] + "\n")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="lane14-fd-trailing-following-header-cluster-") as tmp_dir:
        tmp_root = Path(tmp_dir)

        build_ok_fixture(tmp_root)
        validate_markers(tmp_root)

        missing_root = tmp_root / "missing"
        build_ok_fixture(missing_root)
        missing_path = (
            missing_root
            / "scripts"
            / "zigux"
            / "mk_elfconfig_fd_invalid_class_trailing_then_following_header_test.zig"
        )
        missing_path.write_text("", encoding="utf-8")
        try:
            validate_markers(missing_root)
        except ValueError as exc:
            if "missing_marker:invalid_class_then_trailing_following_header" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing-marker self-test failure")

        duplicate_root = tmp_root / "duplicate"
        build_ok_fixture(duplicate_root)
        duplicate_path = (
            duplicate_root
            / "scripts"
            / "zigux"
            / "mk_elfconfig_fd_trailing_then_following_header_test.zig"
        )
        duplicate_marker = EXPECTED_MARKERS[
            ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_trailing_then_following_header_test.zig"
        ]["marker"]
        duplicate_path.write_text(
            "\n".join([duplicate_marker, duplicate_marker]) + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(duplicate_root)
        except ValueError as exc:
            if "duplicate_marker:not_elf_then_trailing_following_header" not in str(exc):
                raise
        else:
            raise AssertionError("expected duplicate-marker self-test failure")

    print("MK_ELFCONFIG_FD_TRAILING_FOLLOWING_HEADER_CLUSTER_MARKERS_SELF_TEST=pass")
    print("MK_ELFCONFIG_FD_TRAILING_FOLLOWING_HEADER_CLUSTER_MARKERS_SELF_TEST_CASE_COUNT=3")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the mk_elfconfig fd trailing-then-following-header standalone replay cluster stays present."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="override the repository root for validation",
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

    validate_markers(args.root.resolve())
    print("MK_ELFCONFIG_FD_TRAILING_FOLLOWING_HEADER_CLUSTER_MARKERS=pass")
    print(
        "MK_ELFCONFIG_FD_TRAILING_FOLLOWING_HEADER_CLUSTER_MARKERS_COUNT="
        f"{len(EXPECTED_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
