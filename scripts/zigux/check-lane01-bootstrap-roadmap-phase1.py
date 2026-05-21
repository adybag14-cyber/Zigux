#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

HEADING = "## Phase 1: Alpha Host-Side Helpers"
INTRO_LABEL = "Primary product goal:"
INTRO_BULLET = "- prove that Zig can live in-tree on low-risk host-side helper code"
TARGETS_LABEL = "Primary Linux targets:"
TARGET_BULLETS = (
    "- `tools/lib/bitmap.c`",
    "- `tools/lib/find_bit.c`",
    "- `tools/lib/string.c`",
    "- `tools/lib/rbtree.c`",
)
FEATURES_LABEL = "Required Zigux features:"
FEATURE_BULLETS = (
    "- mixed-language helper build path",
    "- golden-output parity tests",
    "- clear ownership and review rules for `.zig` files beside `.c`",
)
DESTINATIONS_LABEL = "Recommended Zigux destinations:"
DESTINATION_BULLETS = (
    "- `tools/lib/bitmap.zig`",
    "- `tools/lib/find_bit.zig`",
    "- `tools/lib/string.zig`",
    "- `tools/lib/rbtree.zig`",
)
WHY_LABEL = "Why ZAR matters here:"
WHY_BULLET = (
    "- ZAR already shows disciplined phase tracking, probe-driven validation, "
    "and explicit boundaries. That process discipline should be ported immediately."
)
PREVIOUS_HEADING = "## Product Features by Phase"
NEXT_HEADING = "## Phase 2: Toolchain and Kbuild Enablement"


def collect_missing_markers(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    missing: list[str] = []
    required_markers = (
        HEADING,
        INTRO_LABEL,
        INTRO_BULLET,
        TARGETS_LABEL,
        *TARGET_BULLETS,
        FEATURES_LABEL,
        *FEATURE_BULLETS,
        DESTINATIONS_LABEL,
        *DESTINATION_BULLETS,
        WHY_LABEL,
        WHY_BULLET,
    )
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

## Product Features by Phase

## Phase 1: Alpha Host-Side Helpers

Primary product goal:
- prove that Zig can live in-tree on low-risk host-side helper code

Primary Linux targets:
- `tools/lib/bitmap.c`
- `tools/lib/find_bit.c`
- `tools/lib/string.c`
- `tools/lib/rbtree.c`

Required Zigux features:
- mixed-language helper build path
- golden-output parity tests
- clear ownership and review rules for `.zig` files beside `.c`

Recommended Zigux destinations:
- `tools/lib/bitmap.zig`
- `tools/lib/find_bit.zig`
- `tools/lib/string.zig`
- `tools/lib/rbtree.zig`

Why ZAR matters here:
- ZAR already shows disciplined phase tracking, probe-driven validation, and explicit boundaries. That process discipline should be ported immediately.

## Phase 2: Toolchain and Kbuild Enablement

Primary product goal:
- make Zigux buildable, reproducible, and acceptable inside Linux-style workflows
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase1_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_missing_markers(root):
            raise AssertionError("baseline Lane 01 Phase 1 roadmap fixture should pass")
        if not has_expected_heading_order(root):
            raise AssertionError("baseline Lane 01 Phase 1 heading order should pass")
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{HEADING}\n\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [HEADING]:
            raise AssertionError(f"unexpected missing markers for heading case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{INTRO_BULLET}\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [INTRO_BULLET]:
            raise AssertionError(f"unexpected missing markers for intro case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{TARGET_BULLETS[3]}\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [TARGET_BULLETS[3]]:
            raise AssertionError(f"unexpected missing markers for target case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{FEATURE_BULLETS[2]}\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [FEATURE_BULLETS[2]]:
            raise AssertionError(f"unexpected missing markers for feature case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                f"{DESTINATION_BULLETS[2]}\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        if missing != [DESTINATION_BULLETS[2]]:
            raise AssertionError(f"unexpected missing markers for destination case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{WHY_BULLET}\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [WHY_BULLET]:
            raise AssertionError(f"unexpected missing markers for rationale case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                f"{PREVIOUS_HEADING}\n\n{HEADING}",
                f"{HEADING}\n\n{PREVIOUS_HEADING}",
                1,
            ),
        )
        if collect_missing_markers(root):
            raise AssertionError("reordered-heading fixture should keep all markers present")
        if has_expected_heading_order(root):
            raise AssertionError("reordered-heading fixture should fail heading order")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE1_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE1_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the landed Lane 01 roadmap Phase 1 packet remains aligned."
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
        help="exercise the checker against synthetic Lane 01 Phase 1 roadmap fixtures",
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
        print("ERROR: unexpected heading order for Product Features by Phase, Phase 1, and Phase 2")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE1=pass")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_PHASE1_REQUIRED_LINE_COUNT="
        f"{len(TARGET_BULLETS) + len(FEATURE_BULLETS) + len(DESTINATION_BULLETS) + 7}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
