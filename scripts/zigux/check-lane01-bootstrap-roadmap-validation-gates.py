#!/usr/bin/env python3
"""Guard the Lane 01 roadmap Recommended Validation Gates packet."""

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

PREV_HEADING = "## First Commit and Push Sequence for Zigux"
SECTION_HEADING = "## Recommended Validation Gates"
NEXT_HEADING = "## What Should Start Next in Zigux"

EXPECTED_SECTION_LINES = (
    "Every approved Zigux slice should declare and satisfy these gates.",
    "1. Build gate",
    "- deterministic artifact generation where applicable",
    "- pinned toolchain version",
    "- reproducible host-side outputs",
    "2. ABI gate",
    "- layout assertions",
    "- calling-convention checks",
    "- one blessed export surface",
    "3. Behavior gate",
    "- differential tests against current C behavior",
    "- fixture or known-vector parity",
    "4. Performance gate",
    "- perf thresholds for algorithmic helpers and driver-sensitive paths",
    "5. Runtime gate",
    "- load/unload behavior for runtime modules",
    "- teardown parity",
    "- queueing and failure-path coverage for drivers",
    "6. Rollback gate",
    "- named owner",
    "- explicit fallback to current C implementation",
    "- clear disable path when regressions appear",
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
        raise AssertionError("invalid heading order before validation-gates section")

    if end <= start + 1:
        raise AssertionError("validation-gates section is empty")

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

## First Commit and Push Sequence for Zigux

This is the recommended near-term commit train after this roadmap lands.

## Recommended Validation Gates

{section}

## What Should Start Next in Zigux

Immediate next steps after this document lands:
- keep `zigux-alpha/` as the control-plane for startup planning only
"""


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        got = ",".join(actual) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(
            f"lane01-roadmap-validation-gates-self-test:{label}:got={got}:want={want}"
        )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(
        prefix="zigux_lane01_roadmap_validation_gates_"
    ) as tmp_dir:
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

        _write(
            path,
            _read(path).replace("- fixture or known-vector parity\n", "", 1),
        )
        _assert_only(
            validate(root),
            ["missing_section_line:- fixture or known-vector parity"],
            "missing_behavior_marker",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        _write(
            path,
            _read(path).replace(
                "1. Build gate\n"
                "- deterministic artifact generation where applicable\n"
                "- pinned toolchain version\n"
                "- reproducible host-side outputs\n"
                "2. ABI gate\n",
                "2. ABI gate\n"
                "- layout assertions\n"
                "- calling-convention checks\n"
                "- one blessed export surface\n"
                "1. Build gate\n"
                "- deterministic artifact generation where applicable\n"
                "- pinned toolchain version\n"
                "- reproducible host-side outputs\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "misordered_section_line:1. Build gate:found_at=6:expected_at=2",
                "misordered_section_line:- deterministic artifact generation where applicable:found_at=7:expected_at=3",
                "misordered_section_line:- pinned toolchain version:found_at=8:expected_at=4",
                "misordered_section_line:- reproducible host-side outputs:found_at=9:expected_at=5",
                "misordered_section_line:2. ABI gate:found_at=2:expected_at=6",
                "misordered_section_line:- layout assertions:found_at=3:expected_at=7",
                "misordered_section_line:- calling-convention checks:found_at=4:expected_at=8",
                "misordered_section_line:- one blessed export surface:found_at=5:expected_at=9",
                "misordered_section_line:3. Behavior gate:found_at=13:expected_at=10",
                "misordered_section_line:- differential tests against current C behavior:found_at=14:expected_at=11",
                "misordered_section_line:- fixture or known-vector parity:found_at=15:expected_at=12",
                "misordered_section_line:4. Performance gate:found_at=16:expected_at=13",
                "misordered_section_line:- perf thresholds for algorithmic helpers and driver-sensitive paths:found_at=17:expected_at=14",
                "misordered_section_line:5. Runtime gate:found_at=18:expected_at=15",
                "misordered_section_line:- load/unload behavior for runtime modules:found_at=19:expected_at=16",
                "misordered_section_line:- teardown parity:found_at=20:expected_at=17",
                "misordered_section_line:- queueing and failure-path coverage for drivers:found_at=21:expected_at=18",
                "misordered_section_line:6. Rollback gate:found_at=22:expected_at=19",
                "misordered_section_line:- named owner:found_at=23:expected_at=20",
                "misordered_section_line:- explicit fallback to current C implementation:found_at=24:expected_at=21",
                "misordered_section_line:- clear disable path when regressions appear:found_at=25:expected_at=22",
            ],
            "misordered_gate_blocks",
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
        _write(path, _sample_roadmap())
        case_count += 1

        _write(
            path,
            _read(path).replace(
                "- clear disable path when regressions appear\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            ["missing_section_line:- clear disable path when regressions appear"],
            "missing_rollback_line",
        )
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 01 roadmap validation-gates packet aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    problems = validate(args.root)
    if problems:
        print("LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES=fail")
        print("LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES_ISSUES_START")
        for problem in problems:
            print(problem)
        print("LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES_ISSUES_END")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES=pass")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES_REQUIRED_LINE_COUNT="
        f"{len(EXPECTED_SECTION_LINES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
