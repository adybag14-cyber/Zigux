#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

HEADING = "## Phase 3: ABI and Interop Substrate"
INTRO_LABEL = "Primary product goal:"
INTRO_BULLET = "- define the permanent C/Zigux boundary"
TARGETS_LABEL = "Primary Linux anchors:"
TARGET_BULLETS = (
    "- `rust/exports.c`",
    "- `lib/bitmap.c`",
    "- `lib/rbtree.c`",
    "- `lib/cpumask.c`",
)
FEATURES_LABEL = "Required Zigux features:"
FEATURE_BULLETS = (
    "- explicit export shims",
    "- generated or curated bindings",
    "- layout assertions",
    "- explicit panic policy",
    "- explicit allocator policy",
    "- approved atomic, barrier, and MMIO wrappers",
    "- narrow unsafe surface",
)
DESTINATIONS_LABEL = "Recommended Zigux destinations:"
DESTINATION_BULLETS = (
    "- `zigux/kernel/`",
    "- `zigux/helpers/`",
    "- `zigux/bindings/`",
    "- `zigux/uapi/`",
    "- `zigux/unsafe/`",
    "- `include/linux/zigux.h`",
    "- `include/zigux/abi.h`",
)
WHY_LABEL = "Why ZAR matters here:"
WHY_BULLET = (
    "- ZAR’s exported runtime state, ABI gating, and explicit failure-code discipline "
    "are directly useful as a product engineering habit, even though the actual Zigux "
    "substrate must be Linux-kernel-specific."
)
PREVIOUS_HEADING = "## Phase 2: Toolchain and Kbuild Enablement"
NEXT_HEADING = "## Phase 4: Differential Validation and Rollback"


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

## Phase 2: Toolchain and Kbuild Enablement

Primary product goal:
- make Zigux buildable, reproducible, and acceptable inside Linux-style workflows

## Phase 3: ABI and Interop Substrate

Primary product goal:
- define the permanent C/Zigux boundary

Primary Linux anchors:
- `rust/exports.c`
- `lib/bitmap.c`
- `lib/rbtree.c`
- `lib/cpumask.c`

Required Zigux features:
- explicit export shims
- generated or curated bindings
- layout assertions
- explicit panic policy
- explicit allocator policy
- approved atomic, barrier, and MMIO wrappers
- narrow unsafe surface

Recommended Zigux destinations:
- `zigux/kernel/`
- `zigux/helpers/`
- `zigux/bindings/`
- `zigux/uapi/`
- `zigux/unsafe/`
- `include/linux/zigux.h`
- `include/zigux/abi.h`

Why ZAR matters here:
- ZAR’s exported runtime state, ABI gating, and explicit failure-code discipline are directly useful as a product engineering habit, even though the actual Zigux substrate must be Linux-kernel-specific.

## Phase 4: Differential Validation and Rollback

Primary product goal:
- make every future Zigux port measurable and reversible
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase3_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_missing_markers(root):
            raise AssertionError("baseline Lane 01 Phase 3 roadmap fixture should pass")
        if not has_expected_heading_order(root):
            raise AssertionError("baseline Lane 01 Phase 3 heading order should pass")
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

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{FEATURE_BULLETS[6]}\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [FEATURE_BULLETS[6]]:
            raise AssertionError(f"unexpected missing markers for feature case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                f"{DESTINATION_BULLETS[6]}\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        if missing != [DESTINATION_BULLETS[6]]:
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
                f"{PREVIOUS_HEADING}\n\nPrimary product goal:\n- make Zigux buildable, reproducible, and acceptable inside Linux-style workflows\n\n{HEADING}",
                f"{HEADING}\n\n{PREVIOUS_HEADING}",
                1,
            ),
        )
        if collect_missing_markers(root):
            raise AssertionError("reordered-heading fixture should keep all markers present")
        if has_expected_heading_order(root):
            raise AssertionError("reordered-heading fixture should fail heading order")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE3_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE3_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the landed Lane 01 roadmap Phase 3 packet remains aligned."
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
        help="exercise the checker against synthetic Lane 01 Phase 3 roadmap fixtures",
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
        print("ERROR: unexpected heading order for Phase 2, Phase 3, and Phase 4")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE3=pass")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_PHASE3_REQUIRED_LINE_COUNT="
        f"{len(TARGET_BULLETS) + len(FEATURE_BULLETS) + len(DESTINATION_BULLETS) + 8}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
