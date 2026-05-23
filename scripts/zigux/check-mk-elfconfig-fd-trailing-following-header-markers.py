#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZIG_TOOL = ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_trailing_then_following_header_test.zig"

EXPECTED_MARKERS = {
    "fd_trailing_then_following_header": 'test "fd-backed exact non-ELF header with trailing bytes folds a later ELF header into the next not-ELF packet" {',
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
    with tempfile.TemporaryDirectory(prefix="lane14-fd-trailing-following-header-") as tmp_dir:
        tmp_root = Path(tmp_dir)

        ok_path = tmp_root / "ok.zig"
        ok_path.write_text("\n".join(EXPECTED_MARKERS.values()) + "\n", encoding="utf-8")
        validate_markers(ok_path)

        missing_path = tmp_root / "missing.zig"
        missing_path.write_text("", encoding="utf-8")
        try:
            validate_markers(missing_path)
        except ValueError as exc:
            if "missing_marker:fd_trailing_then_following_header" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing-marker self-test failure")

        duplicate_path = tmp_root / "duplicate.zig"
        duplicate_path.write_text(
            "\n".join(
                [
                    EXPECTED_MARKERS["fd_trailing_then_following_header"],
                    EXPECTED_MARKERS["fd_trailing_then_following_header"],
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(duplicate_path)
        except ValueError as exc:
            if "duplicate_marker:fd_trailing_then_following_header" not in str(exc):
                raise
        else:
            raise AssertionError("expected duplicate-marker self-test failure")

    print("MK_ELFCONFIG_FD_TRAILING_FOLLOWING_HEADER_MARKERS_SELF_TEST=pass")
    print("MK_ELFCONFIG_FD_TRAILING_FOLLOWING_HEADER_MARKERS_SELF_TEST_CASE_COUNT=3")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that mk_elfconfig keeps the fd trailing-then-following-header replay visible."
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
    print("MK_ELFCONFIG_FD_TRAILING_FOLLOWING_HEADER_MARKERS=pass")
    print(f"MK_ELFCONFIG_FD_TRAILING_FOLLOWING_HEADER_MARKERS_COUNT={len(EXPECTED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
