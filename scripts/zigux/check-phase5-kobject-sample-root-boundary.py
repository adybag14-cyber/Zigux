#!/usr/bin/env python3
"""Fail-closed check for the Phase 5 kobject sample-root review packet."""

from __future__ import annotations

import argparse
import pathlib
import sys


REQUIRED_MARKERS = (
    "samples/zigux/kobject_example.zig",
    "approved in-memory ownership-and-lifetime idiom",
    "samples/kobject/kobject-example.c",
    "phase5-kobject-sample-survey.md",
    "phase5_kobject_example_survey.zig",
    "`ownershipSummary()` and sample-owned `runOwnershipReplay()` explicit as the reviewable lifecycle cues",
    "`runInputValidationReplay()` explicit for the shared `baz`/`bar` dispatch plus parse-failure visibility",
    "initialized-only abandonment cue",
    "already-registered duplicate-registration and replay-restart rejection",
    "registered teardown reset",
    "post-`exit()` show-or-store rejection explicit",
    "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample",
    "Documentation/zigux/phase7-cmdline-slice.md",
    "zigux/tests/phase7_cmdline.zig",
    "zigux/tests/phase7_cmdline_survey.zig",
    "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    "lib/rbtree.zig",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_survey.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "scripts/zigux/check-phase7-build-wiring.py",
    "zigux/tests/phase7_build.zig",
)


SELFTEST_GOOD_TEXT = """
* samples/zigux/kobject_example.zig
* approved in-memory ownership-and-lifetime idiom
* samples/kobject/kobject-example.c
* phase5-kobject-sample-survey.md
* phase5_kobject_example_survey.zig
* `ownershipSummary()` and sample-owned `runOwnershipReplay()` explicit as the reviewable lifecycle cues
* `runInputValidationReplay()` explicit for the shared `baz`/`bar` dispatch plus parse-failure visibility
* initialized-only abandonment cue
* already-registered duplicate-registration and replay-restart rejection
* registered teardown reset
* post-`exit()` show-or-store rejection explicit
* current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample
* Documentation/zigux/phase7-cmdline-slice.md
* zigux/tests/phase7_cmdline.zig
* zigux/tests/phase7_cmdline_survey.zig
* current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample
* Documentation/zigux/phase7-rbtree-slice.md
* Documentation/zigux/phase7-make-wrapper-selftest-alignment.md
* lib/rbtree.zig
* zigux/tests/phase7_rbtree.zig
* zigux/tests/phase7_rbtree_survey.zig
* zigux/tests/phase7_rbtree_manifest.json
* scripts/zigux/check-phase7-rbtree-parity.py
* scripts/zigux/check-phase7-build-wiring.py
* zigux/tests/phase7_build.zig
""".strip()


def check_text(text: str) -> list[str]:
    return [marker for marker in REQUIRED_MARKERS if marker not in text]


def run_self_test() -> int:
    missing = check_text(SELFTEST_GOOD_TEXT)
    if missing:
        print("self-test unexpectedly missed markers:", file=sys.stderr)
        for marker in missing:
            print(f"  - {marker}", file=sys.stderr)
        return 1

    bad_text = SELFTEST_GOOD_TEXT.replace(
        "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample",
        "",
        1,
    )
    missing = check_text(bad_text)
    if missing != [
        "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample"
    ]:
        print("self-test did not fail closed on the rbtree boundary marker", file=sys.stderr)
        print(missing, file=sys.stderr)
        return 1

    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that samples/zigux/README.md keeps the landed Phase 5 "
            "kobject packet and the explicit no-rbtree Phase 5 boundary aligned."
        )
    )
    parser.add_argument(
        "readme",
        nargs="?",
        default="samples/zigux/README.md",
        help="Path to the Phase 5 sample-root README to inspect.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the script's built-in safety checks and exit.",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    text = pathlib.Path(args.readme).read_text(encoding="utf-8")
    missing = check_text(text)
    if missing:
        print("missing required Phase 5 kobject sample-root markers:", file=sys.stderr)
        for marker in missing:
            print(f"  - {marker}", file=sys.stderr)
        return 1

    print(
        "ok: samples/zigux/README.md keeps the Phase 5 kobject packet and "
        "the no-rbtree Phase 5 boundary explicit"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
