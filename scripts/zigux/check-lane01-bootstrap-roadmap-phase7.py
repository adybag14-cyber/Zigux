#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

PHASE6_HEADING = "## Phase 6: Greenfield Leaf Helpers"
PHASE7_HEADING = "## Phase 7: In-Kernel Leaf Libraries"
PHASE8_HEADING = "## Phase 8: Userspace-Adjacent Tooling Expansion"

REQUIRED_LINES = (
    PHASE7_HEADING,
    "Primary product goal:",
    "- bring the first reusable runtime helper families into the product path",
    "Primary Linux anchors:",
    "- `lib/string_helpers.c`",
    "- `lib/cmdline.c`",
    "- `lib/argv_split.c`",
    "- `lib/rbtree.c`",
    "Required Zigux features:",
    "- runtime-safe leaf helpers",
    "- stronger ownership and pointer discipline",
    "- integration with validation substrate",
    "Recommended Zigux destinations:",
    "- `lib/string_helpers.zig`",
    "- `lib/cmdline.zig`",
    "- `lib/argv_split.zig`",
    "- `lib/rbtree.zig`",
)


def collect_phase7_errors(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    errors: list[str] = []

    for line in REQUIRED_LINES:
        if line not in roadmap:
            errors.append(f"missing:{line}")

    positions = []
    for heading in (PHASE6_HEADING, PHASE7_HEADING, PHASE8_HEADING):
        idx = roadmap.find(heading)
        if idx == -1:
            errors.append(f"missing-heading:{heading}")
        positions.append(idx)

    if all(idx != -1 for idx in positions) and not (positions[0] < positions[1] < positions[2]):
        errors.append(
            f"heading-order:{PHASE6_HEADING} -> {PHASE7_HEADING} -> {PHASE8_HEADING}"
        )

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """## Phase 6: Greenfield Leaf Helpers

Primary product goal:
- allow low-risk new helper code in Zigux without taking runtime-core risk

Primary Linux anchors:
- `lib/base64.c`
- `lib/bsearch.c`
- `lib/checksum.c`
- `lib/hexdump.c`

Required Zigux features:
- leaf helper portability
- clear API parity
- perf gates for math-sensitive helpers

Recommended Zigux destinations:
- `lib/base64.zig`
- `lib/bsearch.zig`
- `lib/checksum.zig`
- `lib/hexdump.zig`

## Phase 7: In-Kernel Leaf Libraries

Primary product goal:
- bring the first reusable runtime helper families into the product path

Primary Linux anchors:
- `lib/string_helpers.c`
- `lib/cmdline.c`
- `lib/argv_split.c`
- `lib/rbtree.c`

Required Zigux features:
- runtime-safe leaf helpers
- stronger ownership and pointer discipline
- integration with validation substrate

Recommended Zigux destinations:
- `lib/string_helpers.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`
- `lib/rbtree.zig`

## Phase 8: Userspace-Adjacent Tooling Expansion

Primary product goal:
- prove Zigux inside serious repo-hosted tooling, not just tiny helpers
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase7_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_phase7_errors(root):
            raise AssertionError("baseline Phase 7 fixture should pass")
        case_count += 1

        cases = (
            (
                "heading",
                _sample_roadmap().replace(PHASE7_HEADING + "\n\n", "", 1),
                [f"missing:{PHASE7_HEADING}", f"missing-heading:{PHASE7_HEADING}"],
            ),
            (
                "anchor",
                _sample_roadmap().replace("- `lib/cmdline.c`\n", "", 1),
                ["missing:- `lib/cmdline.c`"],
            ),
            (
                "feature",
                _sample_roadmap().replace("- integration with validation substrate\n", "", 1),
                ["missing:- integration with validation substrate"],
            ),
            (
                "destination",
                _sample_roadmap().replace("- `lib/rbtree.zig`\n", "", 1),
                ["missing:- `lib/rbtree.zig`"],
            ),
            (
                "phase6",
                _sample_roadmap().replace(PHASE6_HEADING + "\n\n", "", 1),
                [f"missing-heading:{PHASE6_HEADING}"],
            ),
            (
                "phase8",
                _sample_roadmap().replace(PHASE8_HEADING + "\n\n", "", 1),
                [f"missing-heading:{PHASE8_HEADING}"],
            ),
            (
                "order",
                _sample_roadmap().replace(
                    PHASE7_HEADING
                    + "\n\nPrimary product goal:\n- bring the first reusable runtime helper families into the product path\n\nPrimary Linux anchors:\n- `lib/string_helpers.c`\n- `lib/cmdline.c`\n- `lib/argv_split.c`\n- `lib/rbtree.c`\n\nRequired Zigux features:\n- runtime-safe leaf helpers\n- stronger ownership and pointer discipline\n- integration with validation substrate\n\nRecommended Zigux destinations:\n- `lib/string_helpers.zig`\n- `lib/cmdline.zig`\n- `lib/argv_split.zig`\n- `lib/rbtree.zig`\n\n"
                    + PHASE8_HEADING,
                    PHASE8_HEADING
                    + "\n\n"
                    + PHASE7_HEADING
                    + "\n\nPrimary product goal:\n- bring the first reusable runtime helper families into the product path\n\nPrimary Linux anchors:\n- `lib/string_helpers.c`\n- `lib/cmdline.c`\n- `lib/argv_split.c`\n- `lib/rbtree.c`\n\nRequired Zigux features:\n- runtime-safe leaf helpers\n- stronger ownership and pointer discipline\n- integration with validation substrate\n\nRecommended Zigux destinations:\n- `lib/string_helpers.zig`\n- `lib/cmdline.zig`\n- `lib/argv_split.zig`\n- `lib/rbtree.zig`\n",
                    1,
                ),
                [
                    f"heading-order:{PHASE6_HEADING} -> {PHASE7_HEADING} -> {PHASE8_HEADING}"
                ],
            ),
        )

        for _, content, expected in cases:
            _write(root / ROADMAP_PATH, content)
            errors = collect_phase7_errors(root)
            if errors != expected:
                raise AssertionError(f"unexpected errors: {errors} != {expected}")
            case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE7_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE7_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap Phase 7 packet remains aligned."
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
        help="exercise the checker against synthetic Phase 7 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_phase7_errors(args.root)
    if errors:
        for entry in errors:
            print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE7_ERROR={entry}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE7=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE7_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    print("LANE01_BOOTSTRAP_ROADMAP_PHASE7_SECTION_ORDER=Phase6->Phase7->Phase8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())