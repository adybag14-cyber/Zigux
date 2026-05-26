#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

SECTION_HEADING = "## Purpose"
NEXT_HEADING = "## Inputs Reviewed"

REQUIRED_LINES = (
    "This document turns the `zigux_bundle_v2.zip` planning bundle into an actionable product roadmap for Zigux.",
    "Positioning:",
    "- `ZAR-Zig-Agent-Runtime` remains the experimental research and proving repo.",
    "- `Zigux` is the product repo.",
    "- Future ZAR work should only be prioritized if it directly reduces Zigux product risk, proves a future Zigux phase, or hardens Zigux validation, build, ABI, or driver delivery.",
    "This roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.",
)


def read_roadmap(root: Path) -> str:
    return (root / ROADMAP_PATH).read_text(encoding="utf-8")


def collect_missing_lines(root: Path) -> list[str]:
    roadmap = read_roadmap(root)
    missing: list[str] = []
    for line in (SECTION_HEADING, *REQUIRED_LINES, NEXT_HEADING):
        if line not in roadmap:
            missing.append(line)
    return missing


def has_expected_order(root: Path) -> bool:
    roadmap = read_roadmap(root)
    indexes = [
        roadmap.find(SECTION_HEADING),
        roadmap.find(REQUIRED_LINES[0]),
        roadmap.find(REQUIRED_LINES[1]),
        roadmap.find(REQUIRED_LINES[2]),
        roadmap.find(REQUIRED_LINES[3]),
        roadmap.find(REQUIRED_LINES[4]),
        roadmap.find(REQUIRED_LINES[5]),
        roadmap.find(NEXT_HEADING),
    ]
    return all(index != -1 for index in indexes) and indexes == sorted(indexes)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## Purpose

This document turns the `zigux_bundle_v2.zip` planning bundle into an actionable product roadmap for Zigux.

Positioning:
- `ZAR-Zig-Agent-Runtime` remains the experimental research and proving repo.
- `Zigux` is the product repo.
- Future ZAR work should only be prioritized if it directly reduces Zigux product risk, proves a future Zigux phase, or hardens Zigux validation, build, ABI, or driver delivery.

This roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.

## Inputs Reviewed

The roadmap is based on all bundle artifacts in `zigux_bundle_v2.zip`:
- `zigux_bundle_review_v2.csv`
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_purpose_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_missing_lines(root):
            raise AssertionError("baseline purpose fixture should keep all required lines")
        if not has_expected_order(root):
            raise AssertionError("baseline purpose fixture should preserve required order")
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{SECTION_HEADING}\n\n", "", 1))
        missing = collect_missing_lines(root)
        if missing != [SECTION_HEADING]:
            raise AssertionError(f"unexpected missing lines for heading case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{REQUIRED_LINES[1]}\n", "", 1))
        missing = collect_missing_lines(root)
        if missing != [REQUIRED_LINES[1]]:
            raise AssertionError(f"unexpected missing lines for positioning label case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{REQUIRED_LINES[4]}\n", "", 1))
        missing = collect_missing_lines(root)
        if missing != [REQUIRED_LINES[4]]:
            raise AssertionError(f"unexpected missing lines for future-zar bullet case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{REQUIRED_LINES[5]}\n", "", 1))
        missing = collect_missing_lines(root)
        if missing != [REQUIRED_LINES[5]]:
            raise AssertionError(f"unexpected missing lines for execution sentence case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                f"{REQUIRED_LINES[5]}\n\n{NEXT_HEADING}",
                f"{NEXT_HEADING}\n\n{REQUIRED_LINES[5]}",
                1,
            ),
        )
        if collect_missing_lines(root):
            raise AssertionError("reordered purpose fixture should still keep required lines present")
        if has_expected_order(root):
            raise AssertionError("reordered purpose fixture should fail order validation")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PURPOSE_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PURPOSE_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the landed Lane 01 roadmap Purpose packet remains aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the zigux-alpha roadmap file",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic Lane 01 roadmap fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_lines(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: missing line: {item}")
        return 1

    if not has_expected_order(args.root):
        print("ERROR: unexpected order inside the roadmap Purpose packet")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PURPOSE=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PURPOSE_REQUIRED_LINE_COUNT={len(REQUIRED_LINES) + 2}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
