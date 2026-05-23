#!/usr/bin/env python3
"""Check the current Phase 1 closure-validator packet contract."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")

REQUIRED_MARKERS = (
    'FIND_BIT_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")',
    'ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")',
    'BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")',
    'FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")',
    '"reminder_packet": "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",',
    '"closure_validator": "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",',
    '"route_summary_guard": "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",',
    '"shared_tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",',
    '"validator_state": "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",',
    '"find_bit_bench_guard": "`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",',
    '"find_bit_bench_anchor_guard": "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",',
    '(FIND_BIT_REVIEW_CHECKER_REL, "phase1-find-bit-review-packet")',
    '(ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts")',
    '(BENCH_CHECKER_REL, "phase1-bench")',
    '(FIND_BIT_BENCH_ANCHOR_CHECKER_REL, "phase1-find-bit-bench-anchors")',
    '("missing_find_bit_bench_guard",',
    '("missing_find_bit_bench_anchor_guard",',
    '("missing_route_summary_guard",',
    '("missing_shared_tests_route",',
    '("missing_validator_state",',
    '("missing_find_bit_review_checker",',
    '("missing_find_bit_bench_anchor_checker",',
    '("missing_makefile_marker",',
    '("forbidden_phase1_makefile_route",',
    'print("PHASE1_CLOSURE_SELF_TEST=pass")',
    'print("PHASE1_CLOSURE_VALIDATION=pass")',
    'print("PHASE1_CLOSURE_MODE=current-master-safe")',
)

FORBIDDEN_MARKERS = ("PHASE1_RBTREE_BENCH_GUARD",)


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
        if marker in text:
            failures.append(f"forbidden_marker:{marker}")
    return failures


def write_fixture(root: Path, text: str) -> None:
    path = root / VALIDATOR_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, str, str]] = [
        ("missing_find_bit_bench_guard", REQUIRED_MARKERS[9], ""),
        ("missing_find_bit_bench_anchor_guard", REQUIRED_MARKERS[10], ""),
        ("missing_route_summary_guard", REQUIRED_MARKERS[6], ""),
        ("missing_shared_tests_route", REQUIRED_MARKERS[7], ""),
        ("missing_validator_state", REQUIRED_MARKERS[8], ""),
        ("missing_find_bit_review_checker", REQUIRED_MARKERS[0], ""),
        ("missing_find_bit_bench_anchor_checker", REQUIRED_MARKERS[3], ""),
        ("missing_makefile_marker_case", REQUIRED_MARKERS[21], ""),
        ("forbidden_phase1_makefile_route_case", REQUIRED_MARKERS[22], ""),
    ]

    with tempfile.TemporaryDirectory(prefix="lane15-closure-validator-") as tmp:
        root = Path(tmp)
        write_fixture(root, FIXTURE_TEXT)
        baseline = collect_failures(root)
        if baseline:
            print(f"lane15-closure-validator-packet-self-test:baseline:{baseline}")
            return 1

    for name, needle, replacement in cases:
        with tempfile.TemporaryDirectory(prefix="lane15-closure-validator-") as tmp:
            root = Path(tmp)
            write_fixture(root, FIXTURE_TEXT.replace(needle, replacement, 1))
            failures = collect_failures(root)
            if not failures:
                print(f"lane15-closure-validator-packet-self-test:{name}:expected_failure")
                return 1

    with tempfile.TemporaryDirectory(prefix="lane15-closure-validator-") as tmp:
        root = Path(tmp)
        write_fixture(root, FIXTURE_TEXT + "\nPHASE1_RBTREE_BENCH_GUARD\n")
        failures = collect_failures(root)
        if not failures:
            print("lane15-closure-validator-packet-self-test:forbidden_marker:expected_failure")
            return 1

    print("PHASE1_CLOSURE_VALIDATOR_PACKET_SELF_TEST=pass")
    print("PHASE1_CLOSURE_VALIDATOR_PACKET_SELF_TEST_CASE_COUNT=11")
    return 0


FIXTURE_TEXT = """#!/usr/bin/env python3
from pathlib import Path

FIND_BIT_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-find-bit-review-packet.py\")
ROUTE_SUMMARY_CHECKER_REL = Path(\"scripts/zigux/check-phase1-route-summary-counts.py\")
BENCH_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bench.py\")
FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path(\"scripts/zigux/check-phase1-find-bit-bench-anchors.py\")

EXPECTED_CLOSURE_MARKERS = {
    \"reminder_packet\": \"`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`\",
    \"closure_validator\": \"`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`\",
    \"route_summary_guard\": \"`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`\",
    \"shared_tests_route\": \"`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`\",
    \"validator_state\": \"`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`\",
    \"find_bit_bench_guard\": \"`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`\",
    \"find_bit_bench_anchor_guard\": \"`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`\",
}

DELEGATED_CHECKERS = (
    (FIND_BIT_REVIEW_CHECKER_REL, \"phase1-find-bit-review-packet\"),
    (ROUTE_SUMMARY_CHECKER_REL, \"phase1-route-summary-counts\"),
    (BENCH_CHECKER_REL, \"phase1-bench\"),
    (FIND_BIT_BENCH_ANCHOR_CHECKER_REL, \"phase1-find-bit-bench-anchors\"),
)

CASES = [
    (\"missing_find_bit_bench_guard\", None),
    (\"missing_find_bit_bench_anchor_guard\", None),
    (\"missing_route_summary_guard\", None),
    (\"missing_shared_tests_route\", None),
    (\"missing_validator_state\", None),
    (\"missing_find_bit_review_checker\", None),
    (\"missing_find_bit_bench_anchor_checker\", None),
    (\"missing_makefile_marker\", None),
    (\"forbidden_phase1_makefile_route\", None),
]

print(\"PHASE1_CLOSURE_SELF_TEST=pass\")
print(\"PHASE1_CLOSURE_VALIDATION=pass\")
print(\"PHASE1_CLOSURE_MODE=current-master-safe\")
"""


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
    print("PHASE1_CLOSURE_VALIDATOR_REQUIRED_MARKER_COUNT=25")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
