#!/usr/bin/env python3
"""Guard the current Phase 1 closure-validator packet against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")

REQUIRED_MARKERS = (
    'PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")',
    'PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")',
    'DOCS_ROOT_REL = Path("Documentation/zigux/README.md")',
    'REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")',
    'SCRIPTS_README_REL = Path("scripts/zigux/README.md")',
    'STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")',
    'FIND_BIT_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")',
    'RBTREE_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-rbtree-review-packet.py")',
    'DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")',
    'DIRECT_ANCHOR_MANIFEST_GATE_REL = Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")',
    'ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")',
    'BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")',
    'FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")',
    'BITMAP_DIRECT_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-bitmap-direct-anchors.py")',
    'SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")',
    '"reminder_packet": "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",',
    '"closure_validator": "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",',
    '"route_summary_guard": "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",',
    '"shared_tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",',
    '"validator_state": "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",',
    '"find_bit_bench_guard": "`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",',
    '"rbtree_bench_guard": "`PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",',
    '"find_bit_bench_anchor_guard": "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",',
    '"find_bit_review_guard": "`PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",',
    '"rbtree_review_guard": "`PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py exact-checks helper-local rbtree anchors plus the committed duplicate-search and cached-leftmost replay packet across the helper, closure note, lane note, manifest, fixture, and shared smoke route`",',
    '"direct_anchor_manifest_gate": "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",',
    '"bitmap_direct_review": "`PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet because the shared Phase 1 replay still only owns allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer handling, and partial-window xor replay, so current master keeps fill-tail clamp, raw copy alias, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, complement-tail masking, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage review-visible at the helper surface`",',
    '(STRING_REVIEW_CHECKER_REL, "phase1-string-review-packet")',
    '(FIND_BIT_REVIEW_CHECKER_REL, "phase1-find-bit-review-packet")',
    '(RBTREE_REVIEW_CHECKER_REL, "phase1-rbtree-review-packet")',
    '(DIRECT_OWNER_CHECKER_REL, "phase1-direct-owner-markers")',
    '(DIRECT_ANCHOR_MANIFEST_GATE_REL, "phase1-direct-anchor-manifest-gate")',
    '(ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts")',
    '(BENCH_CHECKER_REL, "phase1-bench")',
    '(FIND_BIT_BENCH_ANCHOR_CHECKER_REL, "phase1-find-bit-bench-anchors")',
    '(BITMAP_DIRECT_ANCHOR_CHECKER_REL, "phase1-bitmap-direct-anchors")',
    '(SHARED_REMINDER_CHECKER_REL, "phase1-shared-reminder-packet")',
    '("missing_find_bit_bench_guard",',
    '("missing_rbtree_bench_guard",',
    '("missing_find_bit_bench_anchor_guard",',
    '("missing_find_bit_review_guard",',
    '("missing_rbtree_review_guard",',
    '("missing_direct_anchor_manifest_gate_marker",',
    '("missing_route_summary_guard",',
    '("missing_shared_tests_route",',
    '("missing_validator_state",',
    '("missing_find_bit_review_checker",',
    '("missing_rbtree_review_checker",',
    '("missing_find_bit_bench_anchor_checker",',
    '("missing_bitmap_direct_anchor_checker",',
    '("missing_direct_anchor_manifest_gate_checker",',
    '("missing_makefile_marker",',
    '("forbidden_phase1_makefile_route",',
    'print("PHASE1_CLOSURE_SELF_TEST=pass")',
    'print("PHASE1_CLOSURE_VALIDATION=pass")',
    'print("PHASE1_CLOSURE_MODE=current-master-safe")',
)

FORBIDDEN_MARKERS = (
    '`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`',
    '`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`',
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def collect_failures(root: Path) -> list[str]:
    path = root / VALIDATOR_REL
    if not path.is_file():
        return [f"missing_file:{VALIDATOR_REL.as_posix()}"]

    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for marker in REQUIRED_MARKERS:
        count = text.count(marker)
        if count != 1:
            failures.append(f"missing_or_duplicated:{count}:{marker}")
    for marker in FORBIDDEN_MARKERS:
        if text.count(marker) != 0:
            failures.append(f"forbidden_marker:{marker}")
    return failures


def write_validator(root: Path, text: str) -> None:
    path = root / VALIDATOR_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


FIXTURE_TEXT = """#!/usr/bin/env python3
from pathlib import Path

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
FIND_BIT_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")
RBTREE_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-rbtree-review-packet.py")
DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
DIRECT_ANCHOR_MANIFEST_GATE_REL = Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")
ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")
BITMAP_DIRECT_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-bitmap-direct-anchors.py")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")

EXPECTED_CLOSURE_MARKERS = {
    "reminder_packet": "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
    "closure_validator": "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "route_summary_guard": "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    "shared_tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "validator_state": "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "find_bit_bench_guard": "`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
    "rbtree_bench_guard": "`PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",
    "find_bit_bench_anchor_guard": "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",
    "find_bit_review_guard": "`PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",
    "rbtree_review_guard": "`PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py exact-checks helper-local rbtree anchors plus the committed duplicate-search and cached-leftmost replay packet across the helper, closure note, lane note, manifest, fixture, and shared smoke route`",
    "direct_anchor_manifest_gate": "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",
    "bitmap_direct_review": "`PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet because the shared Phase 1 replay still only owns allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer handling, and partial-window xor replay, so current master keeps fill-tail clamp, raw copy alias, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, complement-tail masking, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage review-visible at the helper surface`",
}

DELEGATED_CHECKERS = (
    (STRING_REVIEW_CHECKER_REL, "phase1-string-review-packet"),
    (FIND_BIT_REVIEW_CHECKER_REL, "phase1-find-bit-review-packet"),
    (RBTREE_REVIEW_CHECKER_REL, "phase1-rbtree-review-packet"),
    (DIRECT_OWNER_CHECKER_REL, "phase1-direct-owner-markers"),
    (DIRECT_ANCHOR_MANIFEST_GATE_REL, "phase1-direct-anchor-manifest-gate"),
    (ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts"),
    (BENCH_CHECKER_REL, "phase1-bench"),
    (FIND_BIT_BENCH_ANCHOR_CHECKER_REL, "phase1-find-bit-bench-anchors"),
    (BITMAP_DIRECT_ANCHOR_CHECKER_REL, "phase1-bitmap-direct-anchors"),
    (SHARED_REMINDER_CHECKER_REL, "phase1-shared-reminder-packet"),
)

CASES = [
    ("missing_find_bit_bench_guard", None),
    ("missing_rbtree_bench_guard", None),
    ("missing_find_bit_bench_anchor_guard", None),
    ("missing_find_bit_review_guard", None),
    ("missing_rbtree_review_guard", None),
    ("missing_direct_anchor_manifest_gate_marker", None),
    ("missing_route_summary_guard", None),
    ("missing_shared_tests_route", None),
    ("missing_validator_state", None),
    ("missing_find_bit_review_checker", None),
    ("missing_rbtree_review_checker", None),
    ("missing_find_bit_bench_anchor_checker", None),
    ("missing_bitmap_direct_anchor_checker", None),
    ("missing_direct_anchor_manifest_gate_checker", None),
    ("missing_makefile_marker", None),
    ("forbidden_phase1_makefile_route", None),
]

print("PHASE1_CLOSURE_SELF_TEST=pass")
print("PHASE1_CLOSURE_VALIDATION=pass")
print("PHASE1_CLOSURE_MODE=current-master-safe")
"""


def run_self_test() -> int:
    cases = [
        ("missing_find_bit_bench_guard", REQUIRED_MARKERS[20]),
        ("missing_rbtree_bench_guard", REQUIRED_MARKERS[21]),
        ("missing_find_bit_bench_anchor_guard", REQUIRED_MARKERS[22]),
        ("missing_find_bit_review_guard", REQUIRED_MARKERS[23]),
        ("missing_rbtree_review_guard", REQUIRED_MARKERS[24]),
        ("missing_direct_anchor_manifest_gate_marker", REQUIRED_MARKERS[25]),
        ("missing_route_summary_guard", REQUIRED_MARKERS[17]),
        ("missing_shared_tests_route", REQUIRED_MARKERS[18]),
        ("missing_validator_state", REQUIRED_MARKERS[19]),
        ("missing_find_bit_review_checker", REQUIRED_MARKERS[6]),
        ("missing_rbtree_review_checker", REQUIRED_MARKERS[7]),
        ("missing_find_bit_bench_anchor_checker", REQUIRED_MARKERS[12]),
        ("missing_bitmap_direct_anchor_checker", REQUIRED_MARKERS[13]),
        ("missing_direct_anchor_manifest_gate_checker", REQUIRED_MARKERS[9]),
        ("missing_makefile_marker", REQUIRED_MARKERS[42]),
        ("forbidden_phase1_makefile_route", REQUIRED_MARKERS[43]),
    ]

    with tempfile.TemporaryDirectory(prefix="lane15-closure-validator-packet-") as tmp:
        root = Path(tmp)
        write_validator(root, FIXTURE_TEXT)
        baseline = collect_failures(root)
        if baseline:
            print(f"lane15-closure-validator-packet-self-test:baseline:{baseline}")
            return 1

    for name, needle in cases:
        with tempfile.TemporaryDirectory(prefix="lane15-closure-validator-packet-") as tmp:
            root = Path(tmp)
            write_validator(root, FIXTURE_TEXT.replace(needle, "", 1))
            failures = collect_failures(root)
            if not failures:
                print(f"lane15-closure-validator-packet-self-test:{name}:expected_failure")
                return 1

    with tempfile.TemporaryDirectory(prefix="lane15-closure-validator-packet-") as tmp:
        root = Path(tmp)
        write_validator(root, FIXTURE_TEXT + "\n`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`\n")
        failures = collect_failures(root)
        if not failures:
            print("lane15-closure-validator-packet-self-test:forbidden_old_validator_state:expected_failure")
            return 1

    with tempfile.TemporaryDirectory(prefix="lane15-closure-validator-packet-") as tmp:
        root = Path(tmp)
        write_validator(root, FIXTURE_TEXT)
        failures = collect_failures(root.parent / "missing-root")
        if failures != [f"missing_file:{VALIDATOR_REL.as_posix()}"]:
            print(f"lane15-closure-validator-packet-self-test:missing_file:unexpected={failures}")
            return 1

    print("PHASE1_CLOSURE_VALIDATOR_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_PACKET_SELF_TEST_CASE_COUNT={len(cases) + 3}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_VALIDATOR_PACKET=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_SOURCE={VALIDATOR_REL.as_posix()}")
    print(f"PHASE1_CLOSURE_VALIDATOR_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
