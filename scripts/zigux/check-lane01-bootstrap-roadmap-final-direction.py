#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

HEADING = "## Final Direction"
INTRO = (
    "Zigux succeeds if it behaves like a disciplined Linux product program, "
    "not like a language rewrite experiment."
)
MEANS_LINE = "That means:"
MEANS_BULLETS = (
    "- small support root",
    "- co-located subsystem ports",
    "- strong validation",
    "- explicit freeze map",
    "- commit trains that move from bounded helper wins to toolchain maturity to substrate maturity to runtime pilots",
)
QUESTION_LINE = "ZAR future work should now be judged against one question:"
QUESTION_BULLET = (
    "- does this make a future Zigux commit smaller, safer, or more testable?"
)
YES_LINE = "If yes, keep investing."
NO_LINE = "If no, keep it in research and do not let it drive the product roadmap."
PREVIOUS_HEADING = "## What Should Start Next in Zigux"


def collect_missing_markers(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")

    missing: list[str] = []
    required_markers = (
        HEADING,
        INTRO,
        MEANS_LINE,
        *MEANS_BULLETS,
        QUESTION_LINE,
        QUESTION_BULLET,
        YES_LINE,
        NO_LINE,
    )
    for marker in required_markers:
        if marker not in roadmap:
            missing.append(marker)
    return missing


def has_expected_heading_position(root: Path) -> bool:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    previous_index = roadmap.find(PREVIOUS_HEADING)
    current_index = roadmap.find(HEADING)
    if not previous_index < current_index:
        return False
    return roadmap.find("\n## ", current_index + len(HEADING)) == -1


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## What Should Start Next in Zigux

Immediate next steps after this document lands:

1. keep `zigux-alpha/` as the control-plane for startup planning only
2. create `Documentation/zigux/` and `scripts/zigux/`
3. create `zigux/tests/` differential harness scaffolding
4. deliver Phase 1 host-side helper ports in `tools/lib/*.zig`
5. do not start runtime kernel ports before the Phase 2-4 gates are in place

## Final Direction

Zigux succeeds if it behaves like a disciplined Linux product program, not like a language rewrite experiment.

That means:
- small support root
- co-located subsystem ports
- strong validation
- explicit freeze map
- commit trains that move from bounded helper wins to toolchain maturity to substrate maturity to runtime pilots

ZAR future work should now be judged against one question:
- does this make a future Zigux commit smaller, safer, or more testable?

If yes, keep investing.
If no, keep it in research and do not let it drive the product roadmap.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_final_direction_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_missing_markers(root):
            raise AssertionError("baseline Lane 01 roadmap final-direction fixture should pass")
        if not has_expected_heading_position(root):
            raise AssertionError("baseline Lane 01 roadmap final-direction heading position should pass")
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

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{MEANS_BULLETS[4]}\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [MEANS_BULLETS[4]]:
            raise AssertionError(f"unexpected missing markers for means-bullet case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{QUESTION_BULLET}\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [QUESTION_BULLET]:
            raise AssertionError(f"unexpected missing markers for question case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{NO_LINE}\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [NO_LINE]:
            raise AssertionError(f"unexpected missing markers for closing case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap() + "\n## Not Final\n\nThis should make the final-direction packet fail its position check.\n",
        )
        if collect_missing_markers(root) != []:
            raise AssertionError("trailing-heading fixture should keep all markers present")
        if has_expected_heading_position(root):
            raise AssertionError("trailing-heading fixture should fail heading position")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_FINAL_DIRECTION_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_FINAL_DIRECTION_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the landed Lane 01 roadmap final-direction packet remains aligned."
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
        help="exercise the checker against synthetic Lane 01 roadmap final-direction fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_markers(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: missing marker: {item}")
        return 1

    if not has_expected_heading_position(args.root):
        print(
            "ERROR: unexpected heading position for What Should Start Next in Zigux and Final Direction"
        )
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_FINAL_DIRECTION=pass")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_FINAL_DIRECTION_REQUIRED_LINE_COUNT="
        f"{len(MEANS_BULLETS) + 7}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
