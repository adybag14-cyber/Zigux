#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

HEADING = "## What Should Start Next in Zigux"
INTRO = "Immediate next steps after this document lands:"
STEP_LINES = (
    "1. keep `zigux-alpha/` as the control-plane for startup planning only",
    "2. create `Documentation/zigux/` and `scripts/zigux/`",
    "3. create `zigux/tests/` differential harness scaffolding",
    "4. deliver Phase 1 host-side helper ports in `tools/lib/*.zig`",
    "5. do not start runtime kernel ports before the Phase 2-4 gates are in place",
)
PREVIOUS_HEADING = "## Recommended Validation Gates"
NEXT_HEADING = "## Final Direction"


def collect_missing_markers(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")

    missing: list[str] = []
    required_markers = (HEADING, INTRO, *STEP_LINES)
    for marker in required_markers:
        if marker not in roadmap:
            missing.append(marker)
    return missing


def has_expected_heading_order(root: Path) -> bool:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    previous_index = roadmap.find(PREVIOUS_HEADING)
    current_index = roadmap.find(HEADING)
    next_index = roadmap.find(NEXT_HEADING)
    return previous_index < current_index < next_index


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

        if collect_missing_markers(root):
            raise AssertionError("baseline Lane 01 roadmap next-steps fixture should pass")
        if not has_expected_heading_order(root):
            raise AssertionError("baseline Lane 01 roadmap next-steps heading order should pass")
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{HEADING}\n\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [HEADING]:
            raise AssertionError(f"unexpected missing markers for heading case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{INTRO}\n\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [INTRO]:
            raise AssertionError(f"unexpected missing markers for intro case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{STEP_LINES[0]}\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [STEP_LINES[0]]:
            raise AssertionError(f"unexpected missing markers for first-step case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{STEP_LINES[3]}\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [STEP_LINES[3]]:
            raise AssertionError(f"unexpected missing markers for fourth-step case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{STEP_LINES[4]}\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [STEP_LINES[4]]:
            raise AssertionError(f"unexpected missing markers for fifth-step case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        reordered = _sample_roadmap().replace(
            f"\n{HEADING}\n\n{INTRO}\n\n"
            + "\n".join(STEP_LINES)
            + "\n\n"
            + f"{NEXT_HEADING}\n\n"
            + "Zigux succeeds if it behaves like a disciplined Linux product program, not like a language rewrite experiment.\n",
            f"\n{NEXT_HEADING}\n\n"
            + "Zigux succeeds if it behaves like a disciplined Linux product program, not like a language rewrite experiment.\n\n"
            + f"{HEADING}\n\n{INTRO}\n\n"
            + "\n".join(STEP_LINES)
            + "\n",
            1,
        )
        _write(root / ROADMAP_PATH, reordered)
        if not collect_missing_markers(root) == []:
            raise AssertionError("reordered-heading fixture should keep all markers present")
        if has_expected_heading_order(root):
            raise AssertionError("reordered-heading fixture should fail heading order")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_NEXT_STEPS_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_NEXT_STEPS_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the landed Lane 01 roadmap next-steps packet remains aligned."
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
        help="exercise the checker against synthetic Lane 01 roadmap next-steps fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_markers(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: missing marker: {item}")
        return 1

    if not has_expected_heading_order(args.root):
        print(
            "ERROR: unexpected heading order for Recommended Validation Gates, "
            "What Should Start Next in Zigux, and Final Direction"
        )
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_NEXT_STEPS=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_NEXT_STEPS_REQUIRED_LINE_COUNT={len(STEP_LINES) + 2}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
