#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

REQUIRED_MARKERS = (
    "## Risk Register That Must Drive Prioritization",
    "The highest-risk items from the bundle are the ones that must shape scope:",
    "- mirror-tree sprawl",
    "- toolchain instability",
    "- ABI and layout drift",
    "- hidden runtime behavior",
    "- memory-ordering mistakes",
    "- insufficient validation before expansion",
    "- reviewability collapse",
    "- DMA and queueing regressions",
    "- resource-lifetime mis-modeling",
    "- overpromising full parity",
    "- upstream process misalignment",
    "- deep-core scope creep",
    "The most important operational consequence is this:",
    "- if a proposed Zigux task does not come with bounded scope, validation, rollback, and ownership, it is not ready for the product repo",
)

EXPECTED_SECTION_ORDER = (
    "## Workstreams and Ownership Model",
    "## Risk Register That Must Drive Prioritization",
    "## First Commit and Push Sequence for Zigux",
)


def roadmap_text(root: Path) -> str:
    return (root / ROADMAP_PATH).read_text(encoding="utf-8")


def collect_missing_markers(root: Path) -> list[str]:
    text = roadmap_text(root)
    missing: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            missing.append(marker)
    return missing


def section_order_status(root: Path) -> tuple[bool, str]:
    text = roadmap_text(root)
    positions: list[int] = []
    for heading in EXPECTED_SECTION_ORDER:
        pos = text.find(heading)
        if pos == -1:
            return False, f"missing section heading: {heading}"
        positions.append(pos)
    if positions != sorted(positions):
        return False, "section order drift"
    return True, "Workstreams->RiskRegister->CommitSequence"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## Workstreams and Ownership Model

The bundle supports a 15-workstream execution model.

## Risk Register That Must Drive Prioritization

The highest-risk items from the bundle are the ones that must shape scope:
- mirror-tree sprawl
- toolchain instability
- ABI and layout drift
- hidden runtime behavior
- memory-ordering mistakes
- insufficient validation before expansion
- reviewability collapse
- DMA and queueing regressions
- resource-lifetime mis-modeling
- overpromising full parity
- upstream process misalignment
- deep-core scope creep

The most important operational consequence is this:
- if a proposed Zigux task does not come with bounded scope, validation, rollback, and ownership, it is not ready for the product repo

## First Commit and Push Sequence for Zigux

This is the recommended near-term commit train after this roadmap lands.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_risk_register_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        missing = collect_missing_markers(root)
        ok, order = section_order_status(root)
        if missing or not ok or order != "Workstreams->RiskRegister->CommitSequence":
            raise AssertionError("baseline risk-register fixture should pass")
        case_count += 1

        for marker in (
            "- mirror-tree sprawl",
            "- DMA and queueing regressions",
            "- deep-core scope creep",
            "The most important operational consequence is this:",
            "- if a proposed Zigux task does not come with bounded scope, validation, rollback, and ownership, it is not ready for the product repo",
        ):
            _write(root / ROADMAP_PATH, _sample_roadmap().replace(marker + "\n", "", 1))
            missing = collect_missing_markers(root)
            if missing != [marker]:
                raise AssertionError(f"unexpected missing markers for {marker!r}: {missing}")
            case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "## Workstreams and Ownership Model\n\nThe bundle supports a 15-workstream execution model.\n\n"
                "## Risk Register That Must Drive Prioritization\n\n",
                "## Risk Register That Must Drive Prioritization\n\n"
                "The highest-risk items from the bundle are the ones that must shape scope:\n"
                "- mirror-tree sprawl\n"
                "- toolchain instability\n"
                "- ABI and layout drift\n"
                "- hidden runtime behavior\n"
                "- memory-ordering mistakes\n"
                "- insufficient validation before expansion\n"
                "- reviewability collapse\n"
                "- DMA and queueing regressions\n"
                "- resource-lifetime mis-modeling\n"
                "- overpromising full parity\n"
                "- upstream process misalignment\n"
                "- deep-core scope creep\n\n"
                "The most important operational consequence is this:\n"
                "- if a proposed Zigux task does not come with bounded scope, validation, rollback, and ownership, it is not ready for the product repo\n\n"
                "## Workstreams and Ownership Model\n\nThe bundle supports a 15-workstream execution model.\n\n",
                1,
            ),
        )
        ok, order = section_order_status(root)
        if ok or order != "section order drift":
            raise AssertionError(f"expected section order drift, got ok={ok!r}, order={order!r}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_RISK_REGISTER_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_RISK_REGISTER_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the landed Lane 01 roadmap risk-register packet remains aligned."
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

    missing = collect_missing_markers(args.root)
    if missing:
        for marker in missing:
            print(f"ERROR: missing marker: {marker}")
        return 1

    ok, order = section_order_status(args.root)
    if not ok:
        print(f"ERROR: {order}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_RISK_REGISTER=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_RISK_REGISTER_REQUIRED_LINE_COUNT={len(REQUIRED_MARKERS)}")
    print(f"LANE01_BOOTSTRAP_ROADMAP_RISK_REGISTER_SECTION_ORDER={order}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
