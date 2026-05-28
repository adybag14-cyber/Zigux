#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()
ROADMAP_REL = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

SECTION_HEADING = "## Bundle Normalization Notes"
PREVIOUS_HEADING = "## Inputs Reviewed"
NEXT_HEADING = "## Licensing and Reuse Policy"

EXPECTED_SECTION_LINES = (
    "The workbook and CSV corpus are directionally aligned, but the workbook executive summary contains stale aggregate counts.",
    "Normalized counts from the extracted structured files:",
    "- phases: `15`",
    "- phase targets: `60`",
    "- parity-focus rows: `12`",
    "- workstreams: `15`",
    "- risks: `12`",
    "- structure rules: `18`",
    "- source anchors: `61`",
    "Stale executive-summary metadata in the workbook that should not drive planning:",
    "- phases: `17`",
    "- file-level target rows: `62`",
    "- workstreams: `17`",
    "- risks: `14`",
    "For execution, use the structured CSV/workbook tables themselves, not the executive-summary metrics block.",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def read_section(root: Path) -> list[str]:
    roadmap = root / ROADMAP_REL
    lines = roadmap.read_text(encoding="utf-8").splitlines()

    try:
        start = lines.index(SECTION_HEADING)
    except ValueError as exc:
        raise AssertionError("missing Bundle Normalization Notes heading") from exc

    try:
        end = lines.index(NEXT_HEADING, start + 1)
    except ValueError as exc:
        raise AssertionError("missing Licensing and Reuse Policy heading") from exc

    if end <= start + 1:
        raise AssertionError("bundle-normalization-notes section is empty")

    return [line for line in lines[start + 1 : end] if line]


def validate(root: Path) -> list[str]:
    roadmap = root / ROADMAP_REL
    if not roadmap.exists():
        return [f"missing_file:{ROADMAP_REL.as_posix()}"]

    try:
        actual_lines = read_section(root)
    except AssertionError as exc:
        return [str(exc)]

    problems: list[str] = []
    if actual_lines != list(EXPECTED_SECTION_LINES):
        expected_set = set(EXPECTED_SECTION_LINES)
        actual_set = set(actual_lines)

        for expected in EXPECTED_SECTION_LINES:
            if expected not in actual_set:
                problems.append(f"missing_section_line:{expected}")

        for actual in actual_lines:
            if actual not in expected_set:
                problems.append(f"unexpected_section_line:{actual}")

        if not problems:
            for index, expected in enumerate(EXPECTED_SECTION_LINES):
                actual_index = actual_lines.index(expected)
                if actual_index != index:
                    problems.append(
                        "misordered_section_line:"
                        f"{expected}:found_at={actual_index + 1}:expected_at={index + 1}"
                    )

    return problems


def _sample_roadmap() -> str:
    section = "\n".join(EXPECTED_SECTION_LINES)
    return f"""# ZAR to Zigux Product Roadmap

## Purpose

This document turns the `zigux_bundle_v2.zip` planning bundle into an actionable product roadmap for Zigux.

## Bootstrap Status Note

This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.

For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.

## Inputs Reviewed

The roadmap is based on all bundle artifacts in `zigux_bundle_v2.zip`:
- `zigux_bundle_review_v2.csv`

{SECTION_HEADING}

{section}

{NEXT_HEADING}

For Zigux product work, licensing is not the blocker.
"""


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        got = ",".join(actual) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"lane01-roadmap-normalization-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_roadmap_normalization_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_REL, _sample_roadmap())
        _assert_only(validate(root), [], "baseline")
        case_count += 1

        path = root / ROADMAP_REL
        _write(path, _read(path).replace(f"{SECTION_HEADING}\n\n", "", 1))
        _assert_only(
            validate(root),
            ["missing Bundle Normalization Notes heading"],
            "missing_section_heading",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        path = root / ROADMAP_REL
        _write(path, _read(path).replace("- source anchors: `61`\n", "", 1))
        _assert_only(
            validate(root),
            ["missing_section_line:- source anchors: `61`"],
            "missing_normalized_count",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        path = root / ROADMAP_REL
        _write(
            path,
            _read(path).replace(
                "- phases: `15`\n- phase targets: `60`\n",
                "- phase targets: `60`\n- phases: `15`\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "misordered_section_line:- phases: `15`:found_at=4:expected_at=3",
                "misordered_section_line:- phase targets: `60`:found_at=3:expected_at=4",
            ],
            "misordered_normalized_counts",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        path = root / ROADMAP_REL
        _write(path, _read(path).replace("- workstreams: `17`\n", "", 1))
        _assert_only(
            validate(root),
            ["missing_section_line:- workstreams: `17`"],
            "missing_stale_count",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        path = root / ROADMAP_REL
        _write(path, _read(path).replace(f"{NEXT_HEADING}\n\n", "", 1))
        _assert_only(
            validate(root),
            ["missing Licensing and Reuse Policy heading"],
            "missing_next_heading",
        )
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_NORMALIZATION_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_NORMALIZATION_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 01 roadmap Bundle Normalization Notes packet aligned with the bootstrap charter."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    problems = validate(args.root)
    if problems:
        print("LANE01_BOOTSTRAP_ROADMAP_NORMALIZATION=fail")
        print("LANE01_BOOTSTRAP_ROADMAP_NORMALIZATION_ISSUES_START")
        for problem in problems:
            print(problem)
        print("LANE01_BOOTSTRAP_ROADMAP_NORMALIZATION_ISSUES_END")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_NORMALIZATION=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_NORMALIZATION_REQUIRED_LINE_COUNT={len(EXPECTED_SECTION_LINES)}")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_NORMALIZATION_SECTION_ORDER="
        f"{PREVIOUS_HEADING.removeprefix('## ').replace(' ', '')}->"
        f"{SECTION_HEADING.removeprefix('## ').replace(' ', '')}->"
        f"{NEXT_HEADING.removeprefix('## ').replace(' ', '')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
