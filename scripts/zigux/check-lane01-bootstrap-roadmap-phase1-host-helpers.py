#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

PHASE1_MARKERS = (
    "## Phase 1: Alpha Host-Side Helpers",
    "Primary product goal:",
    "- prove that Zig can live in-tree on low-risk host-side helper code",
    "Primary Linux targets:",
    "- `tools/lib/bitmap.c`",
    "- `tools/lib/find_bit.c`",
    "- `tools/lib/string.c`",
    "- `tools/lib/rbtree.c`",
    "Required Zigux features:",
    "- mixed-language helper build path",
    "- golden-output parity tests",
    "- clear ownership and review rules for `.zig` files beside `.c`",
    "Recommended Zigux destinations:",
    "- `tools/lib/bitmap.zig`",
    "- `tools/lib/find_bit.zig`",
    "- `tools/lib/string.zig`",
    "- `tools/lib/rbtree.zig`",
    "Why ZAR matters here:",
    "- ZAR already shows disciplined phase tracking, probe-driven validation, and explicit boundaries. That process discipline should be ported immediately.",
)

PHASE1_SECTION_ORDER = (
    "## Product Features by Phase",
    "## Phase 1: Alpha Host-Side Helpers",
    "## Phase 2: Toolchain and Kbuild Enablement",
)


def collect_phase1_drift(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    missing: list[str] = []
    for marker in PHASE1_MARKERS:
        if marker not in roadmap:
            missing.append(marker)

    order_positions: list[int] = []
    for marker in PHASE1_SECTION_ORDER:
        position = roadmap.find(marker)
        if position == -1:
            missing.append(f"section-order:{marker}")
        else:
            order_positions.append(position)
    if len(order_positions) == len(PHASE1_SECTION_ORDER) and order_positions != sorted(order_positions):
        missing.append("section-order:ProductFeaturesByPhase->Phase1->Phase2")

    return missing


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
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase1_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_phase1_drift(root):
            raise AssertionError("baseline roadmap Phase 1 fixture should pass")
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("## Phase 1: Alpha Host-Side Helpers\n\n", "", 1),
        )
        missing = collect_phase1_drift(root)
        if "## Phase 1: Alpha Host-Side Helpers" not in missing:
            raise AssertionError(f"missing Phase 1 heading not reported: {missing}")
        if "section-order:## Phase 1: Alpha Host-Side Helpers" not in missing:
            raise AssertionError(f"missing Phase 1 order anchor not reported: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("- `tools/lib/rbtree.c`\n", "", 1),
        )
        missing = collect_phase1_drift(root)
        expected = ["- `tools/lib/rbtree.c`"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for Linux targets case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("- `tools/lib/string.zig`\n", "", 1),
        )
        missing = collect_phase1_drift(root)
        expected = ["- `tools/lib/string.zig`"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for destinations case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "- ZAR already shows disciplined phase tracking, probe-driven validation, and explicit boundaries. That process discipline should be ported immediately.\n",
                "",
                1,
            ),
        )
        missing = collect_phase1_drift(root)
        expected = [
            "- ZAR already shows disciplined phase tracking, probe-driven validation, and explicit boundaries. That process discipline should be ported immediately."
        ]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for Why ZAR matters case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "## Product Features by Phase\n\n## Phase 1: Alpha Host-Side Helpers\n\n",
                "## Phase 1: Alpha Host-Side Helpers\n\n## Product Features by Phase\n\n",
                1,
            ),
        )
        missing = collect_phase1_drift(root)
        expected = ["section-order:ProductFeaturesByPhase->Phase1->Phase2"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for section order case: {missing}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE1_HOST_HELPERS_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE1_HOST_HELPERS_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap Phase 1 host-helper packet remains aligned."
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
        help="exercise the checker against synthetic roadmap Phase 1 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_phase1_drift(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: {item}")
        return 1

    roadmap = (args.root / ROADMAP_PATH).read_text(encoding="utf-8")
    print("Lane 01 roadmap Phase 1 host-helper check passed.")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE1_HOST_HELPERS_REQUIRED_LINE_COUNT={len(PHASE1_MARKERS)}")
    print("LANE01_BOOTSTRAP_ROADMAP_PHASE1_HOST_HELPERS_SECTION_ORDER=ProductFeaturesByPhase->Phase1->Phase2")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_PHASE1_HOST_HELPERS_TARGET_COUNT="
        f"{roadmap.count('- `tools/lib/') // 2}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())