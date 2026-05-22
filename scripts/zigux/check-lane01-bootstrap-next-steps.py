#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

SECTION_HEADING = "## What Should Start Next in Zigux"
SECTION_INTRO = "Immediate next steps after this document lands:"
NEXT_STEP_LINES = (
    "1. keep `zigux-alpha/` as the control-plane for startup planning only",
    "2. create `Documentation/zigux/` and `scripts/zigux/`",
    "3. create `zigux/tests/` differential harness scaffolding",
    "4. deliver Phase 1 host-side helper ports in `tools/lib/*.zig`",
    "5. do not start runtime kernel ports before the Phase 2-4 gates are in place",
)
PREVIOUS_HEADING = "## Recommended Validation Gates"
NEXT_HEADING = "## Final Direction"


def _roadmap_text(root: Path) -> str:
    return (root / ROADMAP_PATH).read_text(encoding="utf-8")


def collect_errors(root: Path) -> list[str]:
    text = _roadmap_text(root)
    errors: list[str] = []

    for marker in (SECTION_HEADING, SECTION_INTRO, PREVIOUS_HEADING, NEXT_HEADING, *NEXT_STEP_LINES):
        if marker not in text:
            errors.append(f"missing:{marker}")

    if errors:
        return errors

    previous_index = text.index(PREVIOUS_HEADING)
    section_index = text.index(SECTION_HEADING)
    intro_index = text.index(SECTION_INTRO)
    next_heading_index = text.index(NEXT_HEADING)

    if not previous_index < section_index < next_heading_index:
        errors.append("order:validation_gates_then_next_steps_then_final_direction")

    if not section_index < intro_index < next_heading_index:
        errors.append("order:next_steps_heading_then_intro")

    line_indexes = [text.index(line) for line in NEXT_STEP_LINES]
    if line_indexes != sorted(line_indexes):
        errors.append("order:next_step_lines")

    if not intro_index < line_indexes[0]:
        errors.append("order:intro_before_first_next_step")

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## Recommended Validation Gates

Every approved Zigux slice should declare and satisfy these gates.

## What Should Start Next in Zigux

Immediate next steps after this document lands:

1. keep `zigux-alpha/` as the control-plane for startup planning only
2. create `Documentation/zigux/` and `scripts/zigux/`
3. create `zigux/tests/` differential harness scaffolding
4. deliver Phase 1 host-side helper ports in `tools/lib/*.zig`
5. do not start runtime kernel ports before the Phase 2-4 gates are in place

## Final Direction

Zigux succeeds if it behaves like a disciplined Linux product program.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_next_steps_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_errors(root):
            raise AssertionError("baseline roadmap fixture should pass")
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{SECTION_HEADING}\n\n", "", 1))
        errors = collect_errors(root)
        expected = [f"missing:{SECTION_HEADING}"]
        if errors != expected:
            raise AssertionError(f"unexpected errors for heading case: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "1. keep `zigux-alpha/` as the control-plane for startup planning only\n",
                "",
                1,
            ),
        )
        errors = collect_errors(root)
        expected = [
            "missing:1. keep `zigux-alpha/` as the control-plane for startup planning only"
        ]
        if errors != expected:
            raise AssertionError(f"unexpected errors for control-plane case: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "5. do not start runtime kernel ports before the Phase 2-4 gates are in place\n",
                "",
                1,
            ),
        )
        errors = collect_errors(root)
        expected = [
            "missing:5. do not start runtime kernel ports before the Phase 2-4 gates are in place"
        ]
        if errors != expected:
            raise AssertionError(f"unexpected errors for no-runtime gate case: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "2. create `Documentation/zigux/` and `scripts/zigux/`\n"
                "3. create `zigux/tests/` differential harness scaffolding\n",
                "3. create `zigux/tests/` differential harness scaffolding\n"
                "2. create `Documentation/zigux/` and `scripts/zigux/`\n",
                1,
            ),
        )
        errors = collect_errors(root)
        expected = ["order:next_step_lines"]
        if errors != expected:
            raise AssertionError(f"unexpected errors for step-order case: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "## Recommended Validation Gates\n\nEvery approved Zigux slice should declare and satisfy these gates.\n\n"
                "## What Should Start Next in Zigux\n\nImmediate next steps after this document lands:\n\n",
                "## What Should Start Next in Zigux\n\nImmediate next steps after this document lands:\n\n"
                "## Recommended Validation Gates\n\nEvery approved Zigux slice should declare and satisfy these gates.\n\n",
                1,
            ),
        )
        errors = collect_errors(root)
        expected = ["order:validation_gates_then_next_steps_then_final_direction"]
        if errors != expected:
            raise AssertionError(f"unexpected errors for section-order case: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "Immediate next steps after this document lands:\n\n",
                "",
                1,
            ),
        )
        errors = collect_errors(root)
        expected = ["missing:Immediate next steps after this document lands:"]
        if errors != expected:
            raise AssertionError(f"unexpected errors for intro case: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

    print("LANE01_BOOTSTRAP_NEXT_STEPS_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_NEXT_STEPS_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap bootstrap next-steps contract remains aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic roadmap fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_errors(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("LANE01_BOOTSTRAP_NEXT_STEPS=pass")
    print(f"LANE01_BOOTSTRAP_NEXT_STEPS_REQUIRED_LINE_COUNT={len(NEXT_STEP_LINES)}")
    print("LANE01_BOOTSTRAP_NEXT_STEPS_SECTION_ORDER=ValidationGates->NextSteps->FinalDirection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())