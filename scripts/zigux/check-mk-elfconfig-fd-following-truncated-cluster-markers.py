#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_MARKERS = {
    "fd_elf32_following_truncated": (
        ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_elf32_following_truncated_test.zig",
        'test "fd-backed exact 32-bit ELF header leaves a following truncated packet for the next call" {',
    ),
    "fd_elf64_following_truncated": (
        ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_elf64_following_truncated_test.zig",
        'test "fd-backed exact 64-bit ELF header leaves a following truncated packet for the next call" {',
    ),
    "fd_invalid_class_following_truncated": (
        ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_invalid_class_following_truncated_test.zig",
        'test "fd-backed exact invalid-class header leaves a following truncated packet for the next call" {',
    ),
    "fd_not_elf_following_truncated": (
        ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_not_elf_following_truncated_test.zig",
        'test "fd-backed exact non-ELF header leaves a following truncated packet for the next call" {',
    ),
}


def validate_markers(root: Path) -> None:
    for label, (path, marker) in EXPECTED_MARKERS.items():
        text = (root / path.relative_to(ROOT)).read_text(encoding="utf-8")
        count = text.count(marker)
        if count == 0:
            raise ValueError(f"{path}:missing_marker:{label}")
        if count > 1:
            raise ValueError(f"{path}:duplicate_marker:{label}")


def write_fixture(root: Path, label: str, content: str) -> None:
    path, _ = EXPECTED_MARKERS[label]
    fixture_path = root / path.relative_to(ROOT)
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_text(content, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="lane14-fd-following-truncated-cluster-") as tmp_dir:
        tmp_root = Path(tmp_dir)

        for label, (_, marker) in EXPECTED_MARKERS.items():
            write_fixture(tmp_root, label, marker + "\n")
        validate_markers(tmp_root)

        missing_root = tmp_root / "missing"
        for label, (_, marker) in EXPECTED_MARKERS.items():
            if label == "fd_invalid_class_following_truncated":
                write_fixture(missing_root, label, "")
            else:
                write_fixture(missing_root, label, marker + "\n")
        try:
            validate_markers(missing_root)
        except ValueError as exc:
            if "missing_marker:fd_invalid_class_following_truncated" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing-marker self-test failure")

        duplicate_root = tmp_root / "duplicate"
        for label, (_, marker) in EXPECTED_MARKERS.items():
            if label == "fd_not_elf_following_truncated":
                write_fixture(duplicate_root, label, marker + "\n" + marker + "\n")
            else:
                write_fixture(duplicate_root, label, marker + "\n")
        try:
            validate_markers(duplicate_root)
        except ValueError as exc:
            if "duplicate_marker:fd_not_elf_following_truncated" not in str(exc):
                raise
        else:
            raise AssertionError("expected duplicate-marker self-test failure")

    print("MK_ELFCONFIG_FD_FOLLOWING_TRUNCATED_CLUSTER_MARKERS_SELF_TEST=pass")
    print("MK_ELFCONFIG_FD_FOLLOWING_TRUNCATED_CLUSTER_MARKERS_SELF_TEST_CASE_COUNT=3")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that mk_elfconfig keeps the full fd-to-truncated handoff quartet visible."
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
    print("MK_ELFCONFIG_FD_FOLLOWING_TRUNCATED_CLUSTER_MARKERS=pass")
    print(f"MK_ELFCONFIG_FD_FOLLOWING_TRUNCATED_CLUSTER_MARKERS_COUNT={len(EXPECTED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
