#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")
PREVIOUS_HEADING = "## Recommended Validation Gates"
NEXT_HEADING = "## What Should Start Next in Zigux"
EXPECTED_LINES = (
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


def extract_validation_gates_packet(root: Path) -> tuple[str, ...]:
    roadmap_lines = (root / ROADMAP_PATH).read_text(encoding="utf-8").splitlines()

    try:
        start = roadmap_lines.index(PREVIOUS_HEADING)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {PREVIOUS_HEADING}") from exc

    try:
        end = roadmap_lines.index(NEXT_HEADING, start + 1)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {NEXT_HEADING}") from exc

    return tuple(line for line in roadmap_lines[start + 1 : end] if line.strip())


def check_validation_gates(root: Path) -> list[str]:
    try:
        packet = extract_validation_gates_packet(root)
    except AssertionError as exc:
        return [str(exc)]

    if packet != EXPECTED_LINES:
        return [
            "validation-gates packet mismatch",
            f"expected:{EXPECTED_LINES!r}",
            f"actual:{packet!r}",
        ]

    return []


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## First Commit and Push Sequence for Zigux

This is the recommended near-term commit train after this roadmap lands.

## Recommended Validation Gates

Every approved Zigux slice should declare and satisfy these gates.

1. Build gate
- deterministic artifact generation where applicable
- pinned toolchain version
- reproducible host-side outputs

2. ABI gate
- layout assertions
- calling-convention checks
- one blessed export surface

3. Behavior gate
- differential tests against current C behavior
- fixture or known-vector parity

4. Performance gate
- perf thresholds for algorithmic helpers and driver-sensitive paths

5. Runtime gate
- load/unload behavior for runtime modules
- teardown parity
- queueing and failure-path coverage for drivers

6. Rollback gate
- named owner
- explicit fallback to current C implementation
- clear disable path when regressions appear

## What Should Start Next in Zigux

Immediate next steps after this document lands:
- keep `zigux-alpha/` as the control-plane for startup planning only
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_validation_gates_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        errors = check_validation_gates(root)
        if errors:
            raise AssertionError(
                f"baseline Lane 01 roadmap validation-gates fixture should pass: {errors}"
            )
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{PREVIOUS_HEADING}\n\n", "", 1))
        errors = check_validation_gates(root)
        if errors != [f"missing heading: {PREVIOUS_HEADING}"]:
            raise AssertionError(f"unexpected previous-heading error: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{NEXT_HEADING}\n", "", 1))
        errors = check_validation_gates(root)
        if errors != [f"missing heading: {NEXT_HEADING}"]:
            raise AssertionError(f"unexpected next-heading error: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("- pinned toolchain version\n", "", 1),
        )
        errors = check_validation_gates(root)
        if not errors or errors[0] != "validation-gates packet mismatch":
            raise AssertionError(f"expected missing-line mismatch, got: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "2. ABI gate\n- layout assertions\n- calling-convention checks\n",
                "2. ABI gate\n- calling-convention checks\n- layout assertions\n",
                1,
            ),
        )
        errors = check_validation_gates(root)
        if not errors or errors[0] != "validation-gates packet mismatch":
            raise AssertionError(f"expected reorder mismatch, got: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "- queueing and failure-path coverage for drivers\n",
                "- queueing and failure-path coverage for drivers\n- synthetic runtime promise\n",
                1,
            ),
        )
        errors = check_validation_gates(root)
        if not errors or errors[0] != "validation-gates packet mismatch":
            raise AssertionError(f"expected extra-line mismatch, got: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "6. Rollback gate\n- named owner\n- explicit fallback to current C implementation\n- clear disable path when regressions appear\n",
                "6. Rollback gate\n- named owner\n- explicit fallback to current C implementation\n",
                1,
            ),
        )
        errors = check_validation_gates(root)
        if not errors or errors[0] != "validation-gates packet mismatch":
            raise AssertionError(f"expected closing gate mismatch, got: {errors}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap validation-gates packet remains aligned."
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

    errors = check_validation_gates(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Lane 01 bootstrap roadmap validation-gates check passed.")
    print(f"LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES_REQUIRED_LINE_COUNT={len(EXPECTED_LINES)}")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES_SECTION_ORDER="
        "RecommendedValidationGates->1Buildgate->2ABIgate->3Behaviorgate->"
        "4Performancegate->5Runtimegate->6Rollbackgate->WhatShouldStartNextinZigux"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
