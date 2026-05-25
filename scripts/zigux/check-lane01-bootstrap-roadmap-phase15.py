#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")
PREVIOUS_HEADING = "## Phase 14: Core-Adjacent Bounded Internals"
SECTION_HEADING = "## Phase 15: Full-Parity Blockers and Long-Term Governance"
NEXT_HEADING = "## Freeze Map for Near- and Mid-Term Planning"
EXPECTED_LINES = (
    "Primary product goal:",
    "- govern the final mixed-language steady state honestly",
    "Primary Linux anchors:",
    "- `kernel/sched/core.c`",
    "- `mm/page_alloc.c`",
    "- `kernel/rcu/tree.c`",
    "- `net/core/skbuff.c`",
    "Required Zigux features:",
    "- freeze map",
    "- Architecture Council review process",
    "- parity scorecard",
    "- policy for code that remains in C indefinitely",
    "This phase is about discipline, not bravado.",
)


def extract_phase15_packet(root: Path) -> tuple[str, ...]:
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


def check_phase15_packet(root: Path) -> list[str]:
    try:
        packet = extract_phase15_packet(root)
    except AssertionError as exc:
        return [str(exc)]

    if packet != EXPECTED_LINES:
        return [
            "phase15 packet mismatch",
            f"expected:{EXPECTED_LINES!r}",
            f"actual:{packet!r}",
        ]

    return []


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## Phase 14: Core-Adjacent Bounded Internals

Primary product goal:
- study or wrap critical shared infrastructure without claiming premature parity

## Phase 15: Full-Parity Blockers and Long-Term Governance

Primary product goal:
- govern the final mixed-language steady state honestly

Primary Linux anchors:
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

Required Zigux features:
- freeze map
- Architecture Council review process
- parity scorecard
- policy for code that remains in C indefinitely

This phase is about discipline, not bravado.

## Freeze Map for Near- and Mid-Term Planning

Active freeze-in-C targets for the current product plan:
- `kernel/sched/core.c`
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase15_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        errors = check_phase15_packet(root)
        if errors:
            raise AssertionError(
                f"baseline Lane 01 roadmap Phase 15 fixture should pass: {errors}"
            )
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{SECTION_HEADING}\n\n", "", 1))
        errors = check_phase15_packet(root)
        if errors != [f"missing heading: {SECTION_HEADING}"]:
            raise AssertionError(f"unexpected section-heading error: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{NEXT_HEADING}\n", "", 1))
        errors = check_phase15_packet(root)
        if errors != [f"missing heading: {NEXT_HEADING}"]:
            raise AssertionError(f"unexpected next-heading error: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("- parity scorecard\n", "", 1),
        )
        errors = check_phase15_packet(root)
        if not errors or errors[0] != "phase15 packet mismatch":
            raise AssertionError(f"expected missing-line mismatch, got: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "- Architecture Council review process\n- parity scorecard\n",
                "- parity scorecard\n- Architecture Council review process\n",
                1,
            ),
        )
        errors = check_phase15_packet(root)
        if not errors or errors[0] != "phase15 packet mismatch":
            raise AssertionError(f"expected reorder mismatch, got: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "- policy for code that remains in C indefinitely\n",
                "- policy for code that remains in C indefinitely\n- synthetic lane expansion promise\n",
                1,
            ),
        )
        errors = check_phase15_packet(root)
        if not errors or errors[0] != "phase15 packet mismatch":
            raise AssertionError(f"expected extra-line mismatch, got: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "This phase is about discipline, not bravado.\n",
                "",
                1,
            ),
        )
        errors = check_phase15_packet(root)
        if not errors or errors[0] != "phase15 packet mismatch":
            raise AssertionError(f"expected closing-sentence mismatch, got: {errors}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE15_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE15_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap Phase 15 packet remains aligned."
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

    errors = check_phase15_packet(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Lane 01 bootstrap roadmap Phase 15 check passed.")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE15_REQUIRED_LINE_COUNT={len(EXPECTED_LINES)}")
    print("LANE01_BOOTSTRAP_ROADMAP_PHASE15_SECTION_ORDER=Phase14->Phase15->FreezeMap")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
