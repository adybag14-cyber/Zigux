#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZIG_TOOL = ROOT / "scripts" / "zigux" / "mk_elfconfig.zig"

EXPECTED_MARKERS = {
    "fd_exact_invalid_class_eof": 'test "fd-backed exact invalid-class header exits silently at EOF" {',
    "split_invalid_class_trailing_bytes": 'test "split-read invalid class exits silently and ignores trailing bytes" {',
    "split_exact_invalid_class_first_chunk": 'test "split-read exact invalid-class header in first chunk exits after one read" {',
    "split_exact_invalid_class_trailing_first_chunk": 'test "split-read exact invalid-class header with trailing bytes queued exits after one read" {',
    "split_exact_invalid_class_eof": 'test "split-read exact invalid-class header exits silently at EOF" {',
    "split_exact_invalid_class_late_failure": 'test "split-read exact invalid-class header ignores later read failure and exits silently" {',
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
    with tempfile.TemporaryDirectory(prefix="lane14-invalid-class-markers-") as tmp_dir:
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
            if "missing_marker:split_exact_invalid_class_late_failure" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing-marker self-test failure")

        duplicate_path = tmp_root / "duplicate.zig"
        duplicate_path.write_text(
            "\n".join(list(EXPECTED_MARKERS.values()) + [EXPECTED_MARKERS["fd_exact_invalid_class_eof"]]) + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(duplicate_path)
        except ValueError as exc:
            if "duplicate_marker:fd_exact_invalid_class_eof" not in str(exc):
                raise
        else:
            raise AssertionError("expected duplicate-marker self-test failure")

    print("MK_ELFCONFIG_INVALID_CLASS_MARKERS_SELF_TEST=pass")
    print("MK_ELFCONFIG_INVALID_CLASS_MARKERS_SELF_TEST_CASE_COUNT=3")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that mk_elfconfig keeps the exact invalid-class packet markers visible."
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
    print("MK_ELFCONFIG_INVALID_CLASS_MARKERS=pass")
    print(f"MK_ELFCONFIG_INVALID_CLASS_MARKERS_COUNT={len(EXPECTED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
