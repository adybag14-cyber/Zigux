#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

PHASE14_HEADING = "## Phase 14: Core-Adjacent Bounded Internals"
PHASE15_HEADING = "## Phase 15: Full-Parity Blockers and Long-Term Governance"
FREEZE_MAP_HEADING = "## Freeze Map for Near- and Mid-Term Planning"

PHASE15_MARKERS = (
    PHASE15_HEADING,
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


def collect_phase15_errors(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")

    errors: list[str] = []
    for marker in PHASE15_MARKERS:
        if marker not in roadmap:
            errors.append(f"missing:{marker}")

    try:
        phase14_index = roadmap.index(PHASE14_HEADING)
    except ValueError:
        errors.append(f"missing:{PHASE14_HEADING}")
        phase14_index = -1

    try:
        phase15_index = roadmap.index(PHASE15_HEADING)
    except ValueError:
        errors.append(f"missing:{PHASE15_HEADING}")
        phase15_index = -1

    try:
        freeze_map_index = roadmap.index(FREEZE_MAP_HEADING)
    except ValueError:
        errors.append(f"missing:{FREEZE_MAP_HEADING}")
        freeze_map_index = -1

    if phase14_index != -1 and phase15_index != -1 and phase14_index >= phase15_index:
        errors.append("order:Phase14->Phase15")
    if phase15_index != -1 and freeze_map_index != -1 and phase15_index >= freeze_map_index:
        errors.append("order:Phase15->FreezeMap")

    return errors


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

        if collect_phase15_errors(root):
            raise AssertionError("baseline Phase 15 roadmap fixture should pass")
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{PHASE15_HEADING}\n\n", "", 1))
        expected = [f"missing:{PHASE15_HEADING}", f"missing:{PHASE15_HEADING}"]
        if collect_phase15_errors(root) != expected:
            raise AssertionError("unexpected errors for missing Phase 15 heading")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("- govern the final mixed-language steady state honestly\n", "", 1),
        )
        expected = ["missing:- govern the final mixed-language steady state honestly"]
        if collect_phase15_errors(root) != expected:
            raise AssertionError("unexpected errors for missing Phase 15 goal marker")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("- `kernel/rcu/tree.c`\n", "", 1))
        expected = ["missing:- `kernel/rcu/tree.c`"]
        if collect_phase15_errors(root) != expected:
            raise AssertionError("unexpected errors for missing Phase 15 anchor marker")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("- Architecture Council review process\n", "", 1),
        )
        expected = ["missing:- Architecture Council review process"]
        if collect_phase15_errors(root) != expected:
            raise AssertionError("unexpected errors for missing Phase 15 feature marker")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("This phase is about discipline, not bravado.\n", "", 1),
        )
        expected = ["missing:This phase is about discipline, not bravado."]
        if collect_phase15_errors(root) != expected:
            raise AssertionError("unexpected errors for missing Phase 15 closeout line")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{PHASE14_HEADING}\n\n", "", 1))
        expected = [f"missing:{PHASE14_HEADING}"]
        if collect_phase15_errors(root) != expected:
            raise AssertionError("unexpected errors for missing Phase 14 heading")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{FREEZE_MAP_HEADING}\n\n", "", 1))
        expected = [f"missing:{FREEZE_MAP_HEADING}"]
        if collect_phase15_errors(root) != expected:
            raise AssertionError("unexpected errors for missing Freeze Map heading")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        reordered = _sample_roadmap().replace(
            f"\n## Phase 15: Full-Parity Blockers and Long-Term Governance\n\n"
            "Primary product goal:\n"
            "- govern the final mixed-language steady state honestly\n\n"
            "Primary Linux anchors:\n"
            "- `kernel/sched/core.c`\n"
            "- `mm/page_alloc.c`\n"
            "- `kernel/rcu/tree.c`\n"
            "- `net/core/skbuff.c`\n\n"
            "Required Zigux features:\n"
            "- freeze map\n"
            "- Architecture Council review process\n"
            "- parity scorecard\n"
            "- policy for code that remains in C indefinitely\n\n"
            "This phase is about discipline, not bravado.\n\n"
            "## Freeze Map for Near- and Mid-Term Planning\n\n"
            "Active freeze-in-C targets for the current product plan:\n"
            "- `kernel/sched/core.c`\n",
            "\n## Freeze Map for Near- and Mid-Term Planning\n\n"
            "Active freeze-in-C targets for the current product plan:\n"
            "- `kernel/sched/core.c`\n\n"
            "## Phase 15: Full-Parity Blockers and Long-Term Governance\n\n"
            "Primary product goal:\n"
            "- govern the final mixed-language steady state honestly\n\n"
            "Primary Linux anchors:\n"
            "- `kernel/sched/core.c`\n"
            "- `mm/page_alloc.c`\n"
            "- `kernel/rcu/tree.c`\n"
            "- `net/core/skbuff.c`\n\n"
            "Required Zigux features:\n"
            "- freeze map\n"
            "- Architecture Council review process\n"
            "- parity scorecard\n"
            "- policy for code that remains in C indefinitely\n\n"
            "This phase is about discipline, not bravado.\n",
            1,
        )
        _write(root / ROADMAP_PATH, reordered)
        expected = ["order:Phase15->FreezeMap"]
        if collect_phase15_errors(root) != expected:
            raise AssertionError("unexpected errors for Phase 15 / Freeze Map order drift")
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
        help="exercise the checker against synthetic roadmap fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_phase15_errors(args.root)
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE15=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE15_REQUIRED_LINE_COUNT={len(PHASE15_MARKERS)}")
    print("LANE01_BOOTSTRAP_ROADMAP_PHASE15_SECTION_ORDER=Phase14->Phase15->FreezeMap")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
