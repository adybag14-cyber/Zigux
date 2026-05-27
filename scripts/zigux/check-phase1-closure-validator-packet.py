#!/usr/bin/env python3
"""Guard the current Phase 1 closure-validator packet against reminder drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    VALIDATOR_REL,
    CLOSURE_NOTE_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    WORKFLOW_REL,
    LANE_NOTE_REL,
    MANIFEST_REL,
)

VALIDATOR_REQUIRED_MARKERS = (
    'PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")',
    'SCRIPTS_README_REL = Path("scripts/zigux/README.md")',
    'TESTS_README_REL = Path("zigux/tests/README.md")',
    'ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")',
    'BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")',
    'FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")',
    'BITMAP_DIRECT_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-bitmap-direct-anchors.py")',
    'SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")',
    '"find_bit_bench_guard":',
    '"rbtree_bench_guard":',
    '"find_bit_review_guard":',
    '"rbtree_review_guard":',
    '"direct_anchor_manifest_gate":',
    'print("PHASE1_CLOSURE_VALIDATION=pass")',
    'print("PHASE1_CLOSURE_MODE=current-master-safe")',
    'print("PHASE1_CLOSURE_SELF_TEST=pass")',
)

VALIDATOR_DELEGATE_MARKERS = (
    '(STRING_REVIEW_CHECKER_REL, "phase1-string-review-packet"),',
    '(FIND_BIT_REVIEW_CHECKER_REL, "phase1-find-bit-review-packet"),',
    '(RBTREE_REVIEW_CHECKER_REL, "phase1-rbtree-review-packet"),',
    '(DIRECT_OWNER_CHECKER_REL, "phase1-direct-owner-markers"),',
    '(DIRECT_ANCHOR_MANIFEST_GATE_REL, "phase1-direct-anchor-manifest-gate"),',
    '(ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts"),',
    '(BENCH_CHECKER_REL, "phase1-bench"),',
    '(FIND_BIT_BENCH_ANCHOR_CHECKER_REL, "phase1-find-bit-bench-anchors"),',
    '(BITMAP_DIRECT_ANCHOR_CHECKER_REL, "phase1-bitmap-direct-anchors"),',
    '(SHARED_REMINDER_CHECKER_REL, "phase1-shared-reminder-packet"),',
)

CLOSURE_NOTE_MARKERS = (
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",
    "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",
)

SCRIPTS_README_MARKERS = (
    "`python3 scripts/zigux/validate-phase1-closure.py`",
    "`scripts/zigux/check-phase1-bitmap-direct-anchors.py`",
    "`scripts/zigux/check-phase1-bench.py`",
)

TESTS_README_MARKERS = (
    "- `scripts/zigux/validate-phase1-closure.py`",
    "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
    "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
)

WORKFLOW_MARKERS = (
    "python3 scripts/zigux/validate-phase1-closure.py",
    "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-bench.py --self-test",
)


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def require_exact_once(text: str, rel: Path, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{rel.as_posix()}:expected_once:{marker}:actual_count={count}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{rel.as_posix()}" for rel in REQUIRED_FILES if not (root / rel).is_file()]
    if failures:
        return failures

    validator_text = read_text(root, VALIDATOR_REL)
    closure_text = read_text(root, CLOSURE_NOTE_REL)
    scripts_text = read_text(root, SCRIPTS_README_REL)
    tests_text = read_text(root, TESTS_README_REL)
    workflow_text = read_text(root, WORKFLOW_REL)

    for marker in VALIDATOR_REQUIRED_MARKERS:
        failures.extend(require_exact_once(validator_text, VALIDATOR_REL, marker))
    for marker in VALIDATOR_DELEGATE_MARKERS:
        failures.extend(require_exact_once(validator_text, VALIDATOR_REL, marker))
    for marker in CLOSURE_NOTE_MARKERS:
        failures.extend(require_exact_once(closure_text, CLOSURE_NOTE_REL, marker))
    for marker in SCRIPTS_README_MARKERS:
        failures.extend(require_exact_once(scripts_text, SCRIPTS_README_REL, marker))
    for marker in TESTS_README_MARKERS:
        failures.extend(require_exact_once(tests_text, TESTS_README_REL, marker))
    for marker in WORKFLOW_MARKERS:
        failures.extend(require_exact_once(workflow_text, WORKFLOW_REL, marker))

    return failures


def make_fixture_tree(root: Path) -> None:
    write_text(
        root / VALIDATOR_REL,
        "\n".join(
            [
                VALIDATOR_REQUIRED_MARKERS[0],
                VALIDATOR_REQUIRED_MARKERS[1],
                VALIDATOR_REQUIRED_MARKERS[2],
                VALIDATOR_REQUIRED_MARKERS[3],
                VALIDATOR_REQUIRED_MARKERS[4],
                VALIDATOR_REQUIRED_MARKERS[5],
                VALIDATOR_REQUIRED_MARKERS[6],
                VALIDATOR_REQUIRED_MARKERS[7],
                *VALIDATOR_REQUIRED_MARKERS[8:],
                *VALIDATOR_DELEGATE_MARKERS,
            ]
        )
        + "\n",
    )
    write_text(root / CLOSURE_NOTE_REL, "\n".join(CLOSURE_NOTE_MARKERS) + "\n")
    write_text(root / SCRIPTS_README_REL, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root / TESTS_README_REL, "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root / WORKFLOW_REL, "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(root / LANE_NOTE_REL, "phase1 lane note fixture\n")
    write_text(root / MANIFEST_REL, "{\n  \"phase\": \"Phase 1\"\n}\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise ValueError(f"missing expected marker: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    cases = (
        ("baseline", None, True),
        ("missing_validator_file", lambda root: (root / VALIDATOR_REL).unlink(), False),
        (
            "missing_validator_required_marker",
            lambda root: write_text(
                root / VALIDATOR_REL,
                replace_once(read_text(root, VALIDATOR_REL), VALIDATOR_REQUIRED_MARKERS[8] + "\n"),
            ),
            False,
        ),
        (
            "missing_delegate_label",
            lambda root: write_text(
                root / VALIDATOR_REL,
                replace_once(read_text(root, VALIDATOR_REL), VALIDATOR_DELEGATE_MARKERS[0] + "\n"),
            ),
            False,
        ),
        (
            "missing_closure_marker",
            lambda root: write_text(
                root / CLOSURE_NOTE_REL,
                replace_once(read_text(root, CLOSURE_NOTE_REL), CLOSURE_NOTE_MARKERS[0] + "\n"),
            ),
            False,
        ),
        (
            "missing_scripts_marker",
            lambda root: write_text(
                root / SCRIPTS_README_REL,
                replace_once(read_text(root, SCRIPTS_README_REL), SCRIPTS_README_MARKERS[1] + "\n"),
            ),
            False,
        ),
        (
            "missing_tests_marker",
            lambda root: write_text(
                root / TESTS_README_REL,
                replace_once(read_text(root, TESTS_README_REL), TESTS_README_MARKERS[1] + "\n"),
            ),
            False,
        ),
        (
            "missing_workflow_marker",
            lambda root: write_text(
                root / WORKFLOW_REL,
                replace_once(read_text(root, WORKFLOW_REL), WORKFLOW_MARKERS[0] + "\n"),
            ),
            False,
        ),
    )

    checks_run = 0
    for name, mutate, should_pass in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-closure-validator-packet-{name}-") as tmpdir:
            root = Path(tmpdir)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if should_pass:
                if failures:
                    print(f"phase1-closure-validator-packet:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-validator-packet:{name}:expected_failure")
                return 1
            checks_run += 1

    print("PHASE1_CLOSURE_VALIDATOR_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in checker self-tests")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a current-like sample root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        make_fixture_tree(args.write_sample_root.resolve())
        print(f"PHASE1_CLOSURE_VALIDATOR_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    failures = collect_failures(args.root.resolve())
    if failures:
        print("PHASE1_CLOSURE_VALIDATOR_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_VALIDATOR_PACKET=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_CLOSURE_VALIDATOR_PACKET_REQUIRED_MARKER_COUNT="
        f"{len(VALIDATOR_REQUIRED_MARKERS) + len(VALIDATOR_DELEGATE_MARKERS) + len(CLOSURE_NOTE_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(WORKFLOW_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
