#!/usr/bin/env python3
"""Guard the Lane 01 Phase 4 roadmap packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

PHASE3_HEADING = "## Phase 3: ABI and Interop Substrate"
PHASE4_HEADING = "## Phase 4: Differential Validation and Rollback"
PHASE5_HEADING = "## Phase 5: Samples and Reference Patterns"

REQUIRED_LINES = [
    PHASE4_HEADING,
    "Primary product goal:",
    "- make every future Zigux port measurable and reversible",
    "Primary Linux anchors:",
    "- `lib/atomic64_test.c`",
    "- `lib/test_bitmap.c`",
    "- `samples/kprobes/kprobe_example.c`",
    "- `samples/vfs/test-fsmount.c`",
    "Required Zigux features:",
    "- `zigux/tests/` parity harnesses",
    "- perf baselines and thresholds",
    "- rollback ownership",
    "- lab and CI matrices",
    "- artifact-diff checks for host-side tools",
    "Recommended Zigux destinations:",
    "- `zigux/tests/atomic64_diff.zig`",
    "- `zigux/tests/bitmap_diff.zig`",
    "- `samples/zigux/kprobe_example.zig`",
    "- `samples/zigux/test_fsmount.zig`",
    "- `scripts/zigux/` diff and layout tools",
    "Why ZAR matters here:",
    "- This is the strongest area to port from ZAR’s current practice. ZAR already behaves like a validation-first system; Zigux should inherit that immediately.",
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


def check_phase4_packet(text: str) -> list[str]:
    errors: list[str] = []
    for line in REQUIRED_LINES:
        if line not in text:
            errors.append(f"missing required line: {line}")

    phase3_index = text.find(PHASE3_HEADING)
    phase4_index = text.find(PHASE4_HEADING)
    phase5_index = text.find(PHASE5_HEADING)
    if -1 in (phase3_index, phase4_index, phase5_index):
        errors.append("missing one or more phase headings needed for section order")
    elif not (phase3_index < phase4_index < phase5_index):
        errors.append("phase section order drifted from Phase3->Phase4->Phase5")

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
                PHASE3_HEADING,
                "",
                "Primary product goal:",
                "- define the permanent C/Zigux boundary",
                "",
                PHASE4_HEADING,
                "",
                "Primary product goal:",
                "- make every future Zigux port measurable and reversible",
                "",
                "Primary Linux anchors:",
                "- `lib/atomic64_test.c`",
                "- `lib/test_bitmap.c`",
                "- `samples/kprobes/kprobe_example.c`",
                "- `samples/vfs/test-fsmount.c`",
                "",
                "Required Zigux features:",
                "- `zigux/tests/` parity harnesses",
                "- perf baselines and thresholds",
                "- rollback ownership",
                "- lab and CI matrices",
                "- artifact-diff checks for host-side tools",
                "",
                "Recommended Zigux destinations:",
                "- `zigux/tests/atomic64_diff.zig`",
                "- `zigux/tests/bitmap_diff.zig`",
                "- `samples/zigux/kprobe_example.zig`",
                "- `samples/zigux/test_fsmount.zig`",
                "- `scripts/zigux/` diff and layout tools",
                "",
                "Why ZAR matters here:",
                "- This is the strongest area to port from ZAR’s current practice. ZAR already behaves like a validation-first system; Zigux should inherit that immediately.",
                "",
                PHASE5_HEADING,
                "",
                "Primary product goal:",
                "- make approved Zigux idioms reviewable and repeatable",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def assert_has_error(fragment: str, expected: str) -> None:
    errors = check_phase4_packet(fragment)
    if expected not in errors:
        raise AssertionError(f"expected error {expected!r}, got {errors!r}")


def swap_first(text: str, left: str, right: str) -> str:
    placeholder = "__LANE01_PHASE4_SWAP__"
    return (
        text.replace(left, placeholder, 1)
        .replace(right, left, 1)
        .replace(placeholder, right, 1)
    )


def run_self_test() -> None:
    sample_root = Path(tempfile.mkdtemp(prefix="lane01_phase4_selftest_"))
    try:
        write_sample_root(sample_root)
        valid_text = roadmap_text(sample_root)
        if check_phase4_packet(valid_text):
            raise AssertionError("valid sample root should pass")

        assert_has_error(
            valid_text.replace(PHASE4_HEADING, "## Phase 4: Drifted", 1),
            f"missing required line: {PHASE4_HEADING}",
        )
        assert_has_error(
            valid_text.replace("- `lib/atomic64_test.c`\n", "", 1),
            "missing required line: - `lib/atomic64_test.c`",
        )
        assert_has_error(
            valid_text.replace("- `samples/vfs/test-fsmount.c`\n", "", 1),
            "missing required line: - `samples/vfs/test-fsmount.c`",
        )
        assert_has_error(
            valid_text.replace("- rollback ownership\n", "", 1),
            "missing required line: - rollback ownership",
        )
        assert_has_error(
            valid_text.replace("- `scripts/zigux/` diff and layout tools\n", "", 1),
            "missing required line: - `scripts/zigux/` diff and layout tools",
        )
        assert_has_error(
            valid_text.replace(
                "- This is the strongest area to port from ZAR’s current practice. ZAR already behaves like a validation-first system; Zigux should inherit that immediately.\n",
                "",
                1,
            ),
            "missing required line: - This is the strongest area to port from ZAR’s current practice. ZAR already behaves like a validation-first system; Zigux should inherit that immediately.",
        )
        assert_has_error(
            swap_first(valid_text, PHASE3_HEADING, PHASE4_HEADING),
            "phase section order drifted from Phase3->Phase4->Phase5",
        )
        assert_has_error(
            valid_text.replace("Required Zigux features:", "Required features:", 1),
            "missing required line: Required Zigux features:",
        )
    finally:
        shutil.rmtree(sample_root, ignore_errors=True)

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE4_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE4_SELF_TEST_CASES={SELF_TEST_CASES}")


def main() -> int:
    args = parse_args()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root))

    if args.self_test:
        run_self_test()
        return 0

    text = roadmap_text(Path(args.root))
    errors = check_phase4_packet(text)
    if errors:
        for error in errors:
            print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE4_ERROR={error}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE4=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE4_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    print("LANE01_BOOTSTRAP_ROADMAP_PHASE4_SECTION_ORDER=Phase3->Phase4->Phase5")
    return 0


if __name__ == "__main__":
    sys.exit(main())
