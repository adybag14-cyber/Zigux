#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

PREVIOUS_HEADING = "## zigux-alpha Scope"
HEADING = "## Product Features by Phase"
NEXT_HEADING = "## Phase 1: Alpha Host-Side Helpers"


def read_roadmap(root: Path) -> str:
    return (root / ROADMAP_PATH).read_text(encoding="utf-8")


def collect_missing_markers(root: Path) -> list[str]:
    roadmap = read_roadmap(root)
    missing: list[str] = []
    for marker in (PREVIOUS_HEADING, HEADING, NEXT_HEADING):
        if marker not in roadmap:
            missing.append(marker)
    return missing


def has_expected_heading_order(root: Path) -> bool:
    roadmap = read_roadmap(root)
    previous_index = roadmap.find(PREVIOUS_HEADING)
    current_index = roadmap.find(HEADING)
    next_index = roadmap.find(NEXT_HEADING)
    return previous_index < current_index < next_index


def has_clean_bridge_section(root: Path) -> bool:
    roadmap = read_roadmap(root)
    current_index = roadmap.find(HEADING)
    next_index = roadmap.find(NEXT_HEADING)
    if current_index == -1 or next_index == -1 or next_index <= current_index:
        return False

    bridge = roadmap[current_index + len(HEADING) : next_index]
    return bridge.strip() == ""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## zigux-alpha Scope

`zigux-alpha/` is the staging area for:
- roadmap and phase sequencing

Those should eventually land in:
- `tools/lib/*.zig`
- `scripts/zigux/`

## Product Features by Phase

## Phase 1: Alpha Host-Side Helpers

Primary product goal:
- prove that Zig can live in-tree on low-risk host-side helper code
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_product_features_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_missing_markers(root):
            raise AssertionError("baseline product-features fixture should keep all headings")
        if not has_expected_heading_order(root):
            raise AssertionError("baseline product-features fixture should preserve heading order")
        if not has_clean_bridge_section(root):
            raise AssertionError("baseline product-features fixture should keep a clean bridge section")
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{HEADING}\n\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [HEADING]:
            raise AssertionError(f"unexpected missing markers for heading case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                f"{PREVIOUS_HEADING}\n\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        if missing != [PREVIOUS_HEADING]:
            raise AssertionError(f"unexpected missing markers for previous-heading case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{NEXT_HEADING}\n\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [NEXT_HEADING]:
            raise AssertionError(f"unexpected missing markers for next-heading case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                f"{PREVIOUS_HEADING}\n\n",
                f"{HEADING}\n\n{PREVIOUS_HEADING}\n\n",
                1,
            ),
        )
        if collect_missing_markers(root):
            raise AssertionError("reordered headings should still keep all markers present")
        if has_expected_heading_order(root):
            raise AssertionError("reordered headings should fail order validation")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                f"{HEADING}\n\n{NEXT_HEADING}",
                f"{HEADING}\n\nBridge prose should not be inserted here.\n\n{NEXT_HEADING}",
                1,
            ),
        )
        if not has_expected_heading_order(root):
            raise AssertionError("bridge-prose fixture should preserve heading order")
        if has_clean_bridge_section(root):
            raise AssertionError("bridge-prose fixture should fail clean-bridge validation")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PRODUCT_FEATURES_BY_PHASE_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PRODUCT_FEATURES_BY_PHASE_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that the landed Lane 01 Product Features by Phase bridge remains aligned."
        )
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
        help="exercise the checker against synthetic Lane 01 roadmap fixtures",
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
        print("ERROR: unexpected heading order for zigux-alpha Scope, Product Features by Phase, and Phase 1")
        return 1

    if not has_clean_bridge_section(args.root):
        print("ERROR: Product Features by Phase bridge should stay empty between the heading and Phase 1")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PRODUCT_FEATURES_BY_PHASE=pass")
    print("LANE01_BOOTSTRAP_ROADMAP_PRODUCT_FEATURES_BY_PHASE_REQUIRED_LINE_COUNT=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
