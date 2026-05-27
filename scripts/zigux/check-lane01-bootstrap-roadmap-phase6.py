#!/usr/bin/env python3
"""Guard the Lane 01 Phase 6 roadmap packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

PHASE5_HEADING = "## Phase 5: Samples and Reference Patterns"
PHASE6_HEADING = "## Phase 6: Greenfield Leaf Helpers"
PHASE7_HEADING = "## Phase 7: In-Kernel Leaf Libraries"

REQUIRED_LINES = [
    PHASE6_HEADING,
    "Primary product goal:",
    "- allow low-risk new helper code in Zigux without taking runtime-core risk",
    "Primary Linux anchors:",
    "- `lib/base64.c`",
    "- `lib/bsearch.c`",
    "- `lib/checksum.c`",
    "- `lib/hexdump.c`",
    "Required Zigux features:",
    "- leaf helper portability",
    "- clear API parity",
    "- perf gates for math-sensitive helpers",
    "Recommended Zigux destinations:",
    "- `lib/base64.zig`",
    "- `lib/bsearch.zig`",
    "- `lib/checksum.zig`",
    "- `lib/hexdump.zig`",
]

SELF_TEST_CASES = 8


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root")
    return parser.parse_args()


def roadmap_text(root: Path) -> str:
    roadmap = root / ROADMAP_PATH
    return roadmap.read_text(encoding="utf-8")


def check_phase6_packet(text: str) -> list[str]:
    errors: list[str] = []
    for line in REQUIRED_LINES:
        if line not in text:
            errors.append(f"missing required line: {line}")

    phase5_index = text.find(PHASE5_HEADING)
    phase6_index = text.find(PHASE6_HEADING)
    phase7_index = text.find(PHASE7_HEADING)
    if -1 in (phase5_index, phase6_index, phase7_index):
        errors.append("missing one or more phase headings needed for section order")
    elif not (phase5_index < phase6_index < phase7_index):
        errors.append("phase section order drifted from Phase5->Phase6->Phase7")

    return errors


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    (root / ROADMAP_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / ROADMAP_PATH).write_text(
        "\n".join(
            [
                "# ZAR to Zigux Product Roadmap",
                "",
                PHASE5_HEADING,
                "",
                "Primary product goal:",
                "- make approved Zigux idioms reviewable and repeatable",
                "",
                PHASE6_HEADING,
                "",
                "Primary product goal:",
                "- allow low-risk new helper code in Zigux without taking runtime-core risk",
                "",
                "Primary Linux anchors:",
                "- `lib/base64.c`",
                "- `lib/bsearch.c`",
                "- `lib/checksum.c`",
                "- `lib/hexdump.c`",
                "",
                "Required Zigux features:",
                "- leaf helper portability",
                "- clear API parity",
                "- perf gates for math-sensitive helpers",
                "",
                "Recommended Zigux destinations:",
                "- `lib/base64.zig`",
                "- `lib/bsearch.zig`",
                "- `lib/checksum.zig`",
                "- `lib/hexdump.zig`",
                "",
                PHASE7_HEADING,
                "",
                "Primary product goal:",
                "- bring the first reusable runtime helper families into the product path",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def assert_has_error(fragment: str, expected: str) -> None:
    errors = check_phase6_packet(fragment)
    if expected not in errors:
        raise AssertionError(f"expected error {expected!r}, got {errors!r}")


def swap_first(text: str, left: str, right: str) -> str:
    placeholder = "__LANE01_PHASE6_SWAP__"
    return (
        text.replace(left, placeholder, 1)
        .replace(right, left, 1)
        .replace(placeholder, right, 1)
    )


def run_self_test() -> None:
    sample_root = Path(tempfile.mkdtemp(prefix="lane01_phase6_selftest_"))
    try:
        write_sample_root(sample_root)
        valid_text = roadmap_text(sample_root)
        if check_phase6_packet(valid_text):
            raise AssertionError("valid sample root should pass")

        assert_has_error(
            valid_text.replace(PHASE6_HEADING, "## Phase 6: Drifted", 1),
            f"missing required line: {PHASE6_HEADING}",
        )
        assert_has_error(
            valid_text.replace("- `lib/base64.c`\n", "", 1),
            "missing required line: - `lib/base64.c`",
        )
        assert_has_error(
            valid_text.replace("- `lib/hexdump.c`\n", "", 1),
            "missing required line: - `lib/hexdump.c`",
        )
        assert_has_error(
            valid_text.replace("- clear API parity\n", "", 1),
            "missing required line: - clear API parity",
        )
        assert_has_error(
            valid_text.replace("- `lib/checksum.zig`\n", "", 1),
            "missing required line: - `lib/checksum.zig`",
        )
        assert_has_error(
            swap_first(valid_text, PHASE5_HEADING, PHASE6_HEADING),
            "phase section order drifted from Phase5->Phase6->Phase7",
        )
        assert_has_error(
            swap_first(valid_text, PHASE6_HEADING, PHASE7_HEADING),
            "phase section order drifted from Phase5->Phase6->Phase7",
        )
        assert_has_error(
            valid_text.replace("Required Zigux features:", "Required features:", 1),
            "missing required line: Required Zigux features:",
        )
    finally:
        shutil.rmtree(sample_root, ignore_errors=True)

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE6_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE6_SELF_TEST_CASES={SELF_TEST_CASES}")


def main() -> int:
    args = parse_args()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root))

    if args.self_test:
        run_self_test()
        return 0

    text = roadmap_text(Path(args.root))
    errors = check_phase6_packet(text)
    if errors:
        for error in errors:
            print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE6_ERROR={error}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE6=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE6_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    print("LANE01_BOOTSTRAP_ROADMAP_PHASE6_SECTION_ORDER=Phase5->Phase6->Phase7")
    return 0


if __name__ == "__main__":
    sys.exit(main())
