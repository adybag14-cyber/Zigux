#!/usr/bin/env python3
"""Fail-closed guard for the Lane 01 bootstrap README Windows note."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


README_PATH = Path("zigux-alpha/README.md")
WINDOWS_NOTE = "- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo."
ACTIVE_PRODUCT_SURFACES_HEADING = "Active product surfaces"
RULES_HEADING = "Rules"


def read_lines(root: Path) -> list[str]:
    readme = root / README_PATH
    if not readme.is_file():
        raise FileNotFoundError(f"missing file: {README_PATH}")
    return readme.read_text(encoding="utf-8").splitlines()


def find_unique_line(lines: list[str], expected: str) -> int:
    indexes = [index for index, line in enumerate(lines) if line == expected]
    if not indexes:
        raise ValueError(f"missing line: {expected}")
    if len(indexes) != 1:
        raise ValueError(f"expected exactly one copy of line: {expected}")
    return indexes[0]


def check_root(root: Path) -> int:
    lines = read_lines(root)

    rules_index = find_unique_line(lines, RULES_HEADING)
    windows_note_index = find_unique_line(lines, WINDOWS_NOTE)
    active_surfaces_index = find_unique_line(lines, ACTIVE_PRODUCT_SURFACES_HEADING)

    if windows_note_index <= rules_index:
        raise ValueError("Windows note must appear after the Rules heading")
    if active_surfaces_index - windows_note_index not in (1, 2):
        raise ValueError(
            "Windows note must stay at the end of Rules, directly above the Active product surfaces heading"
        )
    if active_surfaces_index - windows_note_index == 2 and lines[windows_note_index + 1] != "":
        raise ValueError(
            "Only one blank separator line may appear between the Windows note and Active product surfaces"
        )

    print("Lane 01 bootstrap README Windows note check passed.")
    print("LANE01_BOOTSTRAP_README_WINDOWS_NOTE_COUNT=1")
    return 0


def build_readme(lines: list[str]) -> str:
    return "\n".join(lines) + "\n"


def run_self_test() -> int:
    base_lines = [
        "# zigux-alpha",
        "",
        RULES_HEADING,
        "- Keep product planning and bootstrap artifacts here first.",
        WINDOWS_NOTE,
        ACTIVE_PRODUCT_SURFACES_HEADING,
        "- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.",
    ]

    cases: list[tuple[str, list[str], str | None]] = [
        ("pass", base_lines, None),
        (
            "missing_windows_note",
            [line for line in base_lines if line != WINDOWS_NOTE],
            "missing line",
        ),
        (
            "duplicate_windows_note",
            base_lines + [WINDOWS_NOTE],
            "expected exactly one copy",
        ),
        (
            "before_rules_heading",
            [WINDOWS_NOTE] + [line for line in base_lines if line != WINDOWS_NOTE],
            "after the Rules heading",
        ),
        (
            "not_adjacent_to_active_product_surfaces",
            [
                "# zigux-alpha",
                "",
                RULES_HEADING,
                "- Keep product planning and bootstrap artifacts here first.",
                WINDOWS_NOTE,
                "- extra line",
                ACTIVE_PRODUCT_SURFACES_HEADING,
            ],
            "Only one blank separator line",
        ),
        (
            "blank_separator_is_allowed",
            [
                "# zigux-alpha",
                "",
                RULES_HEADING,
                "- Keep product planning and bootstrap artifacts here first.",
                WINDOWS_NOTE,
                "",
                ACTIVE_PRODUCT_SURFACES_HEADING,
            ],
            None,
        ),
        (
            "nonblank_separator_is_rejected",
            [
                "# zigux-alpha",
                "",
                RULES_HEADING,
                "- Keep product planning and bootstrap artifacts here first.",
                WINDOWS_NOTE,
                "- extra line",
                ACTIVE_PRODUCT_SURFACES_HEADING,
            ],
            "Only one blank separator line",
        ),
        (
            "missing_active_product_surfaces_heading",
            [line for line in base_lines if line != ACTIVE_PRODUCT_SURFACES_HEADING],
            "missing line",
        ),
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        readme = root / README_PATH
        readme.parent.mkdir(parents=True, exist_ok=True)

        for name, lines, expected_error in cases:
            readme.write_text(build_readme(lines), encoding="utf-8")
            try:
                check_root(root)
            except Exception as exc:  # noqa: BLE001
                if expected_error is None:
                    raise AssertionError(f"{name}: unexpected failure: {exc}") from exc
                if expected_error not in str(exc):
                    raise AssertionError(
                        f"{name}: expected error containing {expected_error!r}, got {exc!r}"
                    ) from exc
            else:
                if expected_error is not None:
                    raise AssertionError(f"{name}: expected failure containing {expected_error!r}")

    print("LANE01_BOOTSTRAP_README_WINDOWS_NOTE_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_README_WINDOWS_NOTE_SELF_TEST_CASES={len(cases)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    try:
        return check_root(args.root)
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
