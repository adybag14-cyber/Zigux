#!/usr/bin/env python3
"""Guard the Lane 01 roadmap Freeze Map packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = (
    Path(__file__).resolve().parents[2]
    if len(Path(__file__).resolve().parents) > 2
    else Path.cwd()
)
ROADMAP_REL = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

PREV_HEADING = "## Phase 15: Full-Parity Blockers and Long-Term Governance"
SECTION_HEADING = "## Freeze Map for Near- and Mid-Term Planning"
NEXT_HEADING = "## Workstreams and Ownership Model"

EXPECTED_SECTION_LINES = (
    "Active freeze-in-C targets for the current product plan:",
    "- `kernel/sched/core.c`",
    "- `mm/page_alloc.c`",
    "- `kernel/rcu/tree.c`",
    "- `net/core/skbuff.c`",
    "Boundary-study-only targets before any direct port decision:",
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
    "What this means for ZAR future work:",
    "- research on these areas can continue in ZAR if it improves understanding",
    "- those experiments should not be represented as near-term Zigux delivery commitments",
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
        prev_index = lines.index(PREV_HEADING)
    except ValueError as exc:
        raise AssertionError(f"missing previous heading: {PREV_HEADING}") from exc

    try:
        start = lines.index(SECTION_HEADING)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {SECTION_HEADING}") from exc

    try:
        end = lines.index(NEXT_HEADING, start + 1)
    except ValueError as exc:
        raise AssertionError(f"missing next heading: {NEXT_HEADING}") from exc

    if prev_index >= start:
        raise AssertionError("invalid heading order before freeze-map section")

    if end <= start + 1:
        raise AssertionError("freeze-map section is empty")

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

## Phase 15: Full-Parity Blockers and Long-Term Governance

This phase is about discipline, not bravado.

## Freeze Map for Near- and Mid-Term Planning

{section}

## Workstreams and Ownership Model

The bundle supports a 15-workstream execution model.
"""


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        got = ",".join(actual) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(
            f"lane01-roadmap-freeze-map-self-test:{label}:got={got}:want={want}"
        )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_roadmap_freeze_map_") as tmp_dir:
        root = Path(tmp_dir)
        path = root / ROADMAP_REL

        _write(path, _sample_roadmap())
        _assert_only(validate(root), [], "baseline")
        case_count += 1

        _write(path, _read(path).replace(f"{SECTION_HEADING}\n\n", "", 1))
        _assert_only(
            validate(root),
            [f"missing heading: {SECTION_HEADING}"],
            "missing_heading",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        _write(path, _read(path).replace("- `kernel/rcu/tree.c`\n", "", 1))
        _assert_only(
            validate(root),
            ["missing_section_line:- `kernel/rcu/tree.c`"],
            "missing_freeze_target",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        _write(
            path,
            _read(path).replace(
                "- `kernel/workqueue.c`\n- `kernel/trace/ring_buffer.c`\n",
                "- `kernel/trace/ring_buffer.c`\n- `kernel/workqueue.c`\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "misordered_section_line:- `kernel/workqueue.c`:found_at=8:expected_at=7",
                "misordered_section_line:- `kernel/trace/ring_buffer.c`:found_at=7:expected_at=8",
            ],
            "misordered_boundary_targets",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        _write(
            path,
            _read(path).replace("What this means for ZAR future work:\n", "", 1),
        )
        _assert_only(
            validate(root),
            ["missing_section_line:What this means for ZAR future work:"],
            "missing_zar_heading",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        _write(path, _read(path).replace(f"{NEXT_HEADING}\n\n", "", 1))
        _assert_only(
            validate(root),
            [f"missing next heading: {NEXT_HEADING}"],
            "missing_next_heading",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        _write(path, _read(path).replace(f"{PREV_HEADING}\n\n", "", 1))
        _assert_only(
            validate(root),
            [f"missing previous heading: {PREV_HEADING}"],
            "missing_previous_heading",
        )
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_FREEZE_MAP_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_FREEZE_MAP_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 01 roadmap freeze-map packet aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    problems = validate(args.root)
    if problems:
        print("LANE01_BOOTSTRAP_ROADMAP_FREEZE_MAP=fail")
        print("LANE01_BOOTSTRAP_ROADMAP_FREEZE_MAP_ISSUES_START")
        for problem in problems:
            print(problem)
        print("LANE01_BOOTSTRAP_ROADMAP_FREEZE_MAP_ISSUES_END")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_FREEZE_MAP=pass")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_FREEZE_MAP_REQUIRED_LINE_COUNT="
        f"{len(EXPECTED_SECTION_LINES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
