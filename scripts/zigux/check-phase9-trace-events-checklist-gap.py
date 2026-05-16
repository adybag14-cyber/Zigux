#!/usr/bin/env python3
"""PHASE9_CHECK_PACKET=trace_events_checklist_gap

Fail-closed checker for the current Phase 9 checklist overclaim gap. This stays
intentionally narrow: it records that the live runtime-pilot packet on current
`master` has narrowed to the surviving trace-events sample plus reminder
surfaces, while the shared review checklist still carries the older loader-era
inventory.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE9_CHECK_PACKET=trace_events_checklist_gap"
SEQUENCING_PATH = Path("Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
SAMPLE_PATH = Path("samples/zigux/runtime_trace_events.zig")
GAP_NOTE_PATH = Path("Documentation/zigux/phase9-trace-events-checklist-gap.md")

SEQUENCING_MARKERS = [
    "Current `master` keeps a narrow Phase 9 runtime-pilot packet.",
    "`samples/zigux/runtime_trace_events.zig`",
    "`.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking",
    "does not currently expose the broader shared runtime-loader packet",
]

TESTS_README_MARKERS = [
    "`samples/zigux/runtime_trace_events.zig`",
    "`.provides_selftest_hook = true`",
    "initialized, selftest_complete, and exited lifecycle tracking",
    "there is no shared `zigux/tests/runtime_*` replay packet, `zigux/tests/phase9_build.zig`, `make -C zigux phase9*` route family, or dedicated shared `validate-phase9.py` visible on current `master`",
]

SAMPLE_MARKERS = [
    ".provides_selftest_hook = true",
    "pub fn runSelftest(self: *Self) !EmissionSummary {",
    "pub fn exit(self: *Self) !void {",
    'test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity" {',
    'test "trace-events sample keeps failed-exit rollback explicit after selftest-ready replay" {',
    'test "trace-events sample keeps rejected re-selftest rollback explicit" {',
]

STALE_REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 9 runtime-loader packet",
    "`zigux/tests/phase9_build.zig`",
    "`zigux/kernel/runtime_loader.zig`",
    "the four `samples/zigux/runtime_*_loader.zig` scaffolds",
]

GAP_NOTE_MARKERS = [
    "- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP=present`",
    "- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP_KIND=review_checklist_runtime_loader_overclaim`",
    "- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP_SCOPE=surviving_trace_events_packet_only`",
    "- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP_STATUS_BUCKET=runtime_pilot_review_only`",
    "- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP_OWNER=Runtime Pilot Lane`",
    "Refresh `Documentation/zigux/review-checklist.md` and",
    "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`",
]


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def source_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    if MARKER not in source_text():
        errors.append("checker marker missing from checker source")

    for rel in [
        SEQUENCING_PATH,
        REVIEW_CHECKLIST_PATH,
        TESTS_README_PATH,
        SAMPLE_PATH,
        GAP_NOTE_PATH,
    ]:
        if not (root / rel).exists():
            errors.append(f"missing file: {rel.as_posix()}")
    if errors:
        return errors

    sequencing = read_text(root, SEQUENCING_PATH)
    review_checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    tests_readme = read_text(root, TESTS_README_PATH)
    sample = read_text(root, SAMPLE_PATH)
    gap_note = read_text(root, GAP_NOTE_PATH)

    for marker in SEQUENCING_MARKERS:
        if marker not in sequencing:
            errors.append(
                f"missing sequencing marker in {SEQUENCING_PATH.as_posix()}: {marker}"
            )

    for marker in TESTS_README_MARKERS:
        if marker not in tests_readme:
            errors.append(
                f"missing tests-readme marker in {TESTS_README_PATH.as_posix()}: {marker}"
            )

    for marker in SAMPLE_MARKERS:
        if marker not in sample:
            errors.append(f"missing sample marker in {SAMPLE_PATH.as_posix()}: {marker}")

    for marker in STALE_REVIEW_CHECKLIST_MARKERS:
        if marker not in review_checklist:
            errors.append(
                "review checklist no longer shows the documented Phase 9 gap marker "
                f"in {REVIEW_CHECKLIST_PATH.as_posix()}: {marker}"
            )

    for marker in GAP_NOTE_MARKERS:
        if marker not in gap_note:
            errors.append(f"missing gap-note marker in {GAP_NOTE_PATH.as_posix()}: {marker}")

    return errors


def write(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_sequencing_note() -> str:
    return """# Phase 9 Runtime Pilot Lane Sequencing

Current `master` keeps a narrow Phase 9 runtime-pilot packet.

- surviving direct runtime-module sample: `samples/zigux/runtime_trace_events.zig`
- surviving runtime-module evidence inside that sample: `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking

Current `master` does not currently expose the broader shared runtime-loader packet that earlier reminder surfaces described.
"""


def fixture_review_checklist() -> str:
    return """# Zigux Review Checklist

* if the change touches the shared Phase 9 runtime-loader packet, keep `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader.zig`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds visible as shared packet vocabulary
"""


def fixture_tests_readme() -> str:
    return """# zigux/tests

Phase 9 review packet
  * the surviving trace-events sample still keeps the roadmap-backed runtime pilot shape concrete by exposing `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking inside `samples/zigux/runtime_trace_events.zig`, so reviewers can still inspect one real runtime-module and selftest-hook surface while the broader shared loader packet remains backlog
  * there is no shared `zigux/tests/runtime_*` replay packet, `zigux/tests/phase9_build.zig`, `make -C zigux phase9*` route family, or dedicated shared `validate-phase9.py` visible on current `master`
"""


def fixture_sample() -> str:
    return """const std = @import(\"std\");

pub const ModuleDescriptor = struct {
    provides_selftest_hook: bool,
};

pub fn descriptor() ModuleDescriptor {
    return .{ .provides_selftest_hook = true };
}

pub fn runSelftest(self: *Self) !EmissionSummary {
    _ = self;
    return undefined;
}

pub fn exit(self: *Self) !void {
    _ = self;
}

test \"trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity\" {
    try std.testing.expect(true);
}

test \"trace-events sample keeps failed-exit rollback explicit after selftest-ready replay\" {
    try std.testing.expect(true);
}

test \"trace-events sample keeps rejected re-selftest rollback explicit\" {
    try std.testing.expect(true);
}
"""


def fixture_gap_note() -> str:
    return """# Phase 9 Trace-Events Checklist Gap

- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP=present`
- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP_KIND=review_checklist_runtime_loader_overclaim`
- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP_SCOPE=surviving_trace_events_packet_only`
- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP_STATUS_BUCKET=runtime_pilot_review_only`
- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP_OWNER=Runtime Pilot Lane`

Refresh `Documentation/zigux/review-checklist.md` and
`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`
"""


def run_self_test() -> int:
    cases = 4
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(root, SEQUENCING_PATH, fixture_sequencing_note())
        write(root, REVIEW_CHECKLIST_PATH, fixture_review_checklist())
        write(root, TESTS_README_PATH, fixture_tests_readme())
        write(root, SAMPLE_PATH, fixture_sample())
        write(root, GAP_NOTE_PATH, fixture_gap_note())
        errors = check(root)
        if errors:
            print("PHASE9_TRACE_EVENTS_CHECKLIST_GAP_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        write(
            root,
            GAP_NOTE_PATH,
            fixture_gap_note().replace(
                "- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP_OWNER=Runtime Pilot Lane`\n",
                "",
            ),
        )
        if not check(root):
            print("PHASE9_TRACE_EVENTS_CHECKLIST_GAP_SELF_TEST=fail")
            print("expected missing gap-note owner marker to fail")
            return 1

        write(root, GAP_NOTE_PATH, fixture_gap_note())
        write(
            root,
            TESTS_README_PATH,
            fixture_tests_readme().replace(
                "  * there is no shared `zigux/tests/runtime_*` replay packet, `zigux/tests/phase9_build.zig`, `make -C zigux phase9*` route family, or dedicated shared `validate-phase9.py` visible on current `master`\n",
                "",
            ),
        )
        if not check(root):
            print("PHASE9_TRACE_EVENTS_CHECKLIST_GAP_SELF_TEST=fail")
            print("expected missing tests-readme backlog marker to fail")
            return 1

        write(root, TESTS_README_PATH, fixture_tests_readme())
        write(
            root,
            REVIEW_CHECKLIST_PATH,
            fixture_review_checklist().replace(
                "and the four `samples/zigux/runtime_*_loader.zig` scaffolds visible as shared packet vocabulary",
                "visible as shared packet vocabulary",
            ),
        )
        if not check(root):
            print("PHASE9_TRACE_EVENTS_CHECKLIST_GAP_SELF_TEST=fail")
            print("expected missing stale review-checklist marker to fail")
            return 1

    print("PHASE9_TRACE_EVENTS_CHECKLIST_GAP_SELF_TEST=pass")
    print(f"PHASE9_TRACE_EVENTS_CHECKLIST_GAP_SELF_TEST_CASES={cases}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    errors = check(Path.cwd())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())