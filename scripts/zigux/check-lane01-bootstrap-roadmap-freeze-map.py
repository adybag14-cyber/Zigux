#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")
PREVIOUS_HEADING = "## Phase 15: Full-Parity Blockers and Long-Term Governance"
SECTION_HEADING = "## Freeze Map for Near- and Mid-Term Planning"
NEXT_HEADING = "## Workstreams and Ownership Model"
EXPECTED_LINES = (
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


def extract_freeze_map_packet(root: Path) -> tuple[str, ...]:
    roadmap_lines = (root / ROADMAP_PATH).read_text(encoding="utf-8").splitlines()

    try:
        start = roadmap_lines.index(SECTION_HEADING)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {SECTION_HEADING}") from exc

    try:
        end = roadmap_lines.index(NEXT_HEADING, start + 1)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {NEXT_HEADING}") from exc

    return tuple(line for line in roadmap_lines[start + 1 : end] if line.strip())


def check_section_order(root: Path) -> str | None:
    roadmap_lines = (root / ROADMAP_PATH).read_text(encoding="utf-8").splitlines()
    try:
        previous_index = roadmap_lines.index(PREVIOUS_HEADING)
    except ValueError:
        return f"missing heading: {PREVIOUS_HEADING}"
    try:
        section_index = roadmap_lines.index(SECTION_HEADING)
    except ValueError:
        return f"missing heading: {SECTION_HEADING}"
    try:
        next_index = roadmap_lines.index(NEXT_HEADING)
    except ValueError:
        return f"missing heading: {NEXT_HEADING}"
    if not previous_index < section_index < next_index:
        return (
            "section-order mismatch: "
            f"{PREVIOUS_HEADING}->{SECTION_HEADING}->{NEXT_HEADING}"
        )
    return None


def check_freeze_map(root: Path) -> list[str]:
    errors: list[str] = []

    order_error = check_section_order(root)
    if order_error:
        errors.append(order_error)

    try:
        packet = extract_freeze_map_packet(root)
    except AssertionError as exc:
        errors.append(str(exc))
        return errors

    if packet != EXPECTED_LINES:
        errors.extend(
            (
                "freeze-map packet mismatch",
                f"expected:{EXPECTED_LINES!r}",
                f"actual:{packet!r}",
            )
        )
    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## Phase 15: Full-Parity Blockers and Long-Term Governance

This phase is about discipline, not bravado.

## Freeze Map for Near- and Mid-Term Planning

Active freeze-in-C targets for the current product plan:
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

Boundary-study-only targets before any direct port decision:
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

What this means for ZAR future work:
- research on these areas can continue in ZAR if it improves understanding
- those experiments should not be represented as near-term Zigux delivery commitments

## Workstreams and Ownership Model

The bundle supports a 15-workstream execution model.
"""


def write_sample_root(root: Path) -> None:
    _write(root / ROADMAP_PATH, _sample_roadmap())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_freeze_map_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)

        errors = check_freeze_map(root)
        if errors:
            raise AssertionError(
                f"baseline Lane 01 freeze-map fixture should pass: {errors}"
            )
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(SECTION_HEADING + "\n\n", "", 1),
        )
        errors = check_freeze_map(root)
        if f"missing heading: {SECTION_HEADING}" not in errors:
            raise AssertionError(f"expected missing section heading error, got: {errors}")
        write_sample_root(root)
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("- `net/core/skbuff.c`\n", "", 1),
        )
        errors = check_freeze_map(root)
        if not errors or errors[0] != "freeze-map packet mismatch":
            raise AssertionError(f"expected packet mismatch for missing freeze target, got: {errors}")
        write_sample_root(root)
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "- those experiments should not be represented as near-term Zigux delivery commitments\n",
                "",
                1,
            ),
        )
        errors = check_freeze_map(root)
        if not errors or errors[0] != "freeze-map packet mismatch":
            raise AssertionError(f"expected packet mismatch for missing closeout, got: {errors}")
        write_sample_root(root)
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "Boundary-study-only targets before any direct port decision:\n"
                "- `kernel/workqueue.c`\n"
                "- `kernel/trace/ring_buffer.c`\n",
                "- `kernel/workqueue.c`\n"
                "- `kernel/trace/ring_buffer.c`\n"
                "Boundary-study-only targets before any direct port decision:\n",
                1,
            ),
        )
        errors = check_freeze_map(root)
        if not errors or errors[0] != "freeze-map packet mismatch":
            raise AssertionError(f"expected packet mismatch for reordered boundary-study block, got: {errors}")
        write_sample_root(root)
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(PREVIOUS_HEADING, "## Phase 15", 1),
        )
        errors = check_freeze_map(root)
        if f"missing heading: {PREVIOUS_HEADING}" not in errors:
            raise AssertionError(f"expected missing previous heading error, got: {errors}")
        write_sample_root(root)
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "## Freeze Map for Near- and Mid-Term Planning\n\n"
                "Active freeze-in-C targets for the current product plan:\n"
                "- `kernel/sched/core.c`\n"
                "- `mm/page_alloc.c`\n"
                "- `kernel/rcu/tree.c`\n"
                "- `net/core/skbuff.c`\n\n"
                "Boundary-study-only targets before any direct port decision:\n"
                "- `kernel/workqueue.c`\n"
                "- `kernel/trace/ring_buffer.c`\n\n"
                "What this means for ZAR future work:\n"
                "- research on these areas can continue in ZAR if it improves understanding\n"
                "- those experiments should not be represented as near-term Zigux delivery commitments\n\n"
                "## Workstreams and Ownership Model",
                "## Workstreams and Ownership Model\n\n"
                "The bundle supports a 15-workstream execution model.\n\n"
                "## Freeze Map for Near- and Mid-Term Planning",
                1,
            ),
        )
        errors = check_freeze_map(root)
        if "section-order mismatch: ## Phase 15: Full-Parity Blockers and Long-Term Governance->## Freeze Map for Near- and Mid-Term Planning->## Workstreams and Ownership Model" not in errors:
            raise AssertionError(f"expected section-order mismatch, got: {errors}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_FREEZE_MAP_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_FREEZE_MAP_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap freeze-map packet remains aligned."
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
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal sample root that satisfies this checker",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    errors = check_freeze_map(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_FREEZE_MAP=pass")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_FREEZE_MAP_REQUIRED_LINE_COUNT="
        f"{len(EXPECTED_LINES)}"
    )
    print("LANE01_BOOTSTRAP_ROADMAP_FREEZE_MAP_SECTION_ORDER=Phase15->FreezeMap->Workstreams")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
