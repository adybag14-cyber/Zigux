#!/usr/bin/env python3
"""Guard the Lane 01 roadmap workstreams packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

SECTION_MARKERS = (
    "## Freeze Map for Near- and Mid-Term Planning",
    "## Workstreams and Ownership Model",
    "## Risk Register That Must Drive Prioritization",
)

WORKSTREAM_LINES = (
    "- Architecture Council",
    "- PMO / Release Management",
    "- Host Tools Alpha Pod",
    "- Toolchain and Kbuild Team",
    "- ABI and Runtime Team",
    "- Validation and Perf Team",
    "- Developer Enablement",
    "- Kernel Leaf Libraries Pod",
    "- Repo Tooling Pod",
    "- Runtime Pilot Pod",
    "- Virtio Driver Pod",
    "- Simple Drivers Pod",
    "- Complex Drivers and Infra Pod",
    "- Shared Subsystems Pod",
    "- Core-Adjacent Pod",
)

DECLARATION_LINES = (
    "- owner",
    "- phase",
    "- status bucket",
    "- validation gate",
    "- rollback owner",
)


def extract_section(text: str, start: str, end: str) -> str:
    try:
        start_index = text.index(start)
    except ValueError as exc:
        raise AssertionError(f"Missing required heading: {start}") from exc

    try:
        end_index = text.index(end, start_index)
    except ValueError as exc:
        raise AssertionError(f"Missing required heading: {end}") from exc

    return text[start_index:end_index]


def require_once(section: str, marker: str) -> None:
    count = section.count(marker)
    if count != 1:
        raise AssertionError(
            f"Expected marker {marker!r} exactly once in workstreams packet, found {count}."
        )


def require_order(section: str, ordered_markers: tuple[str, ...]) -> None:
    last_index = -1
    for marker in ordered_markers:
        index = section.find(marker)
        if index == -1:
            raise AssertionError(f"Missing required marker: {marker}")
        if index <= last_index:
            raise AssertionError(f"Out-of-order marker: {marker}")
        last_index = index


def check(root: Path) -> None:
    roadmap = root / ROADMAP_PATH
    if not roadmap.is_file():
        raise AssertionError(f"Missing roadmap file: {ROADMAP_PATH}")

    text = roadmap.read_text(encoding="utf-8")
    require_order(text, SECTION_MARKERS)

    section = extract_section(text, SECTION_MARKERS[1], SECTION_MARKERS[2])
    require_once(section, "The bundle supports a 15-workstream execution model.")
    require_once(section, "Core workstreams:")
    require_order(section, WORKSTREAM_LINES)
    require_order(section, DECLARATION_LINES)

    for marker in WORKSTREAM_LINES + DECLARATION_LINES:
        require_once(section, marker)


def write_sample_root(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    roadmap = root / ROADMAP_PATH
    roadmap.parent.mkdir(parents=True, exist_ok=True)
    roadmap.write_text(
        """# ZAR to Zigux Product Roadmap

## Freeze Map for Near- and Mid-Term Planning

Placeholder.

## Workstreams and Ownership Model

The bundle supports a 15-workstream execution model.

Core workstreams:
- Architecture Council
- PMO / Release Management
- Host Tools Alpha Pod
- Toolchain and Kbuild Team
- ABI and Runtime Team
- Validation and Perf Team
- Developer Enablement
- Kernel Leaf Libraries Pod
- Repo Tooling Pod
- Runtime Pilot Pod
- Virtio Driver Pod
- Simple Drivers Pod
- Complex Drivers and Infra Pod
- Shared Subsystems Pod
- Core-Adjacent Pod

For Zigux, that means every active commit series should declare:
- owner
- phase
- status bucket
- validation gate
- rollback owner

## Risk Register That Must Drive Prioritization

Placeholder.
""",
        encoding="utf-8",
    )


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="lane01_workstreams_") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        check(root)

        broken_root = root / "broken"
        shutil.copytree(root, broken_root)
        broken_text = (broken_root / ROADMAP_PATH).read_text(encoding="utf-8")
        broken_text = broken_text.replace("- Repo Tooling Pod\n", "", 1)
        (broken_root / ROADMAP_PATH).write_text(broken_text, encoding="utf-8")
        try:
            check(broken_root)
        except AssertionError:
            pass
        else:
            raise AssertionError("Self-test expected a missing workstream failure.")

    print("LANE01_BOOTSTRAP_ROADMAP_WORKSTREAMS_SELF_TEST=pass")
    print("LANE01_BOOTSTRAP_ROADMAP_WORKSTREAMS_SELF_TEST_CASES=2")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    if args.self_test:
        self_test()
        return 0

    check(args.root)
    print("Lane 01 roadmap workstreams check passed.")
    print("LANE01_BOOTSTRAP_ROADMAP_WORKSTREAMS_REQUIRED_LINE_COUNT=21")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_WORKSTREAMS_SECTION_ORDER="
        "FreezeMap->WorkstreamsAndOwnershipModel->RiskRegister"
    )
    print("LANE01_BOOTSTRAP_ROADMAP_WORKSTREAMS_WORKSTREAM_COUNT=15")
    print("LANE01_BOOTSTRAP_ROADMAP_WORKSTREAMS_DECLARATION_COUNT=5")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"LANE01_BOOTSTRAP_ROADMAP_WORKSTREAMS=fail: {exc}", file=sys.stderr)
        raise SystemExit(1)
