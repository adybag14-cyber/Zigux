#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")
PREVIOUS_HEADING = "## Recommended Validation Gates"
SECTION_HEADING = "## What Should Start Next in Zigux"
NEXT_HEADING = "## Final Direction"
EXPECTED_LINES = (
    "Immediate next steps after this document lands:",
    "1. keep `zigux-alpha/` as the control-plane for startup planning only",
    "2. create `Documentation/zigux/` and `scripts/zigux/`",
    "3. create `zigux/tests/` differential harness scaffolding",
    "4. deliver Phase 1 host-side helper ports in `tools/lib/*.zig`",
    "5. do not start runtime kernel ports before the Phase 2-4 gates are in place",
)


def extract_next_steps_packet(root: Path) -> tuple[str, ...]:
    roadmap_lines = (root / ROADMAP_PATH).read_text(encoding="utf-8").splitlines()

    try:
        previous = roadmap_lines.index(PREVIOUS_HEADING)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {PREVIOUS_HEADING}") from exc

    try:
        start = roadmap_lines.index(SECTION_HEADING, previous + 1)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {SECTION_HEADING}") from exc

    try:
        end = roadmap_lines.index(NEXT_HEADING, start + 1)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {NEXT_HEADING}") from exc

    return tuple(line for line in roadmap_lines[start + 1 : end] if line.strip())


def check_next_steps_packet(root: Path) -> list[str]:
    try:
        packet = extract_next_steps_packet(root)
    except AssertionError as exc:
        return [str(exc)]

    if packet != EXPECTED_LINES:
        return [
            "next-steps packet mismatch",
            f"expected:{EXPECTED_LINES!r}",
            f"actual:{packet!r}",
        ]

    return []


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

Zigux succeeds if it behaves like a disciplined Linux product program, not like a language rewrite experiment.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_next_steps_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        errors = check_next_steps_packet(root)
        if errors:
            raise AssertionError(
                f"baseline Lane 01 roadmap next-steps fixture should pass: {errors}"
            )
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{SECTION_HEADING}\n\n", "", 1))
        errors = check_next_steps_packet(root)
        if errors != [f"missing heading: {SECTION_HEADING}"]:
            raise AssertionError(f"unexpected section-heading error: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{NEXT_HEADING}\n", "", 1))
        errors = check_next_steps_packet(root)
        if errors != [f"missing heading: {NEXT_HEADING}"]:
            raise AssertionError(f"unexpected next-heading error: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "3. create `zigux/tests/` differential harness scaffolding\n", "", 1
            ),
        )
        errors = check_next_steps_packet(root)
        if not errors or errors[0] != "next-steps packet mismatch":
            raise AssertionError(f"expected missing-line mismatch, got: {errors}")
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
        errors = check_next_steps_packet(root)
        if not errors or errors[0] != "next-steps packet mismatch":
            raise AssertionError(f"expected reorder mismatch, got: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "5. do not start runtime kernel ports before the Phase 2-4 gates are in place\n",
                "5. do not start runtime kernel ports before the Phase 2-4 gates are in place\n"
                "6. synthetic later-lane shortcut\n",
                1,
            ),
        )
        errors = check_next_steps_packet(root)
        if not errors or errors[0] != "next-steps packet mismatch":
            raise AssertionError(f"expected extra-line mismatch, got: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "Immediate next steps after this document lands:\n", "", 1
            ),
        )
        errors = check_next_steps_packet(root)
        if not errors or errors[0] != "next-steps packet mismatch":
            raise AssertionError(f"expected intro-line mismatch, got: {errors}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_NEXT_STEPS_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_NEXT_STEPS_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap next-steps packet remains aligned."
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
        help="exercise the checker against synthetic Lane 01 roadmap fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check_next_steps_packet(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Lane 01 bootstrap roadmap next-steps check passed.")
    print(
        f"LANE01_BOOTSTRAP_ROADMAP_NEXT_STEPS_REQUIRED_LINE_COUNT={len(EXPECTED_LINES)}"
    )
    print(
        "LANE01_BOOTSTRAP_ROADMAP_NEXT_STEPS_SECTION_ORDER="
        "RecommendedValidationGates->WhatShouldStartNextInZigux->FinalDirection"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
