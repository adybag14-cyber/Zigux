#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZIG_TOOL = ROOT / "scripts" / "zigux" / "mk_elfconfig.zig"

EXPECTED_MARKERS = {
    "readheader_exact_elf32_failure": 'test "readHeader keeps exact 32-bit ELF bytes when the next read would fail" {',
    "readheader_exact_elf64_failure": 'test "readHeader keeps exact 64-bit ELF bytes when the next read would fail" {',
    "readheader_exact_invalid_class_failure": 'test "readHeader keeps exact invalid-class bytes when the next read would fail" {',
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
    with tempfile.TemporaryDirectory(prefix="lane14-exact-header-failure-") as tmp_dir:
        tmp_root = Path(tmp_dir)

        ok_path = tmp_root / "ok.zig"
        ok_path.write_text("\n".join(EXPECTED_MARKERS.values()) + "\n", encoding="utf-8")
        validate_markers(ok_path)

        missing_path = tmp_root / "missing.zig"
        missing_path.write_text(
            "\n".join(
                [
                    EXPECTED_MARKERS["readheader_exact_elf32_failure"],
                    EXPECTED_MARKERS["readheader_exact_elf64_failure"],
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(missing_path)
        except ValueError as exc:
            if "missing_marker:readheader_exact_invalid_class_failure" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing-marker self-test failure")

        duplicate_path = tmp_root / "duplicate.zig"
        duplicate_path.write_text(
            "\n".join(
                [
                    EXPECTED_MARKERS["readheader_exact_elf32_failure"],
                    EXPECTED_MARKERS["readheader_exact_elf32_failure"],
                    EXPECTED_MARKERS["readheader_exact_elf64_failure"],
                    EXPECTED_MARKERS["readheader_exact_invalid_class_failure"],
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(duplicate_path)
        except ValueError as exc:
            if "duplicate_marker:readheader_exact_elf32_failure" not in str(exc):
                raise
        else:
            raise AssertionError("expected duplicate-marker self-test failure")

        reordered_path = tmp_root / "reordered.zig"
        reordered_path.write_text(
            "\n".join(
                [
                    EXPECTED_MARKERS["readheader_exact_elf64_failure"],
                    EXPECTED_MARKERS["readheader_exact_elf32_failure"],
                    EXPECTED_MARKERS["readheader_exact_invalid_class_failure"],
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

    print("MK_ELFCONFIG_EXACT_HEADER_FAILURE_MARKERS_SELF_TEST=pass")
    print("MK_ELFCONFIG_EXACT_HEADER_FAILURE_MARKERS_SELF_TEST_CASE_COUNT=4")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that mk_elfconfig keeps the exact-header later-read-failure proofs visible."
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
    print("MK_ELFCONFIG_EXACT_HEADER_FAILURE_MARKERS=pass")
    print(f"MK_ELFCONFIG_EXACT_HEADER_FAILURE_MARKERS_COUNT={len(EXPECTED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
