#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZIG_TOOL = ROOT / "scripts" / "zigux" / "mk_elfconfig.zig"

EXPECTED_MARKERS = {
    "split_exact_elf32_trailing_first_chunk": 'test "split-read exact 32-bit ELF header with trailing bytes queued exits after one read" {',
    "split_exact_elf64_trailing_first_chunk": 'test "split-read exact 64-bit ELF header with trailing bytes queued exits after one read" {',
    "split_exact_invalid_class_trailing_first_chunk": 'test "split-read exact invalid-class header with trailing bytes queued exits after one read" {',
    "split_exact_not_elf_trailing_first_chunk": 'test "split-read exact non-ELF header with trailing bytes queued exits after one read" {',
}


def validate_markers(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for label, marker in EXPECTED_MARKERS.items():
        count = text.count(marker)
        if count == 0:
            raise ValueError(f"{path}:missing_marker:{label}")
        if count > 1:
            raise ValueError(f"{path}:duplicate_marker:{label}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="lane14-first-chunk-") as tmp_dir:
        tmp_path = Path(tmp_dir) / "mk_elfconfig.zig"
        tmp_path.write_text(
            "\n".join(EXPECTED_MARKERS.values()) + "\n",
            encoding="utf-8",
        )
        validate_markers(tmp_path)

        missing_path = Path(tmp_dir) / "missing.zig"
        missing_path.write_text(
            "\n".join(list(EXPECTED_MARKERS.values())[:-1]) + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(missing_path)
        except ValueError as exc:
            if "missing_marker:split_exact_not_elf_trailing_first_chunk" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing-marker self-test failure")

    print("MK_ELFCONFIG_FIRST_CHUNK_TRAILING_MARKERS_SELF_TEST=pass")
    print("MK_ELFCONFIG_FIRST_CHUNK_TRAILING_MARKERS_SELF_TEST_CASE_COUNT=2")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that mk_elfconfig keeps the exact first-chunk trailing-byte proofs visible."
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
    print("MK_ELFCONFIG_FIRST_CHUNK_TRAILING_MARKERS=pass")
    print(f"MK_ELFCONFIG_FIRST_CHUNK_TRAILING_MARKERS_COUNT={len(EXPECTED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
