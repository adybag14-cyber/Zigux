#!/usr/bin/env python3
"""Guard the current Phase 1 closure-validator delegate packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

VALIDATOR_REL = "scripts/zigux/validate-phase1-closure.py"
CLOSURE_REL = "Documentation/zigux/phase1-closure.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
TESTS_README_REL = "zigux/tests/README.md"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = (
    VALIDATOR_REL,
    CLOSURE_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    WORKFLOW_REL,
)

EXPECTED_DELEGATE_PATHS = (
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/check-phase1-find-bit-review-packet.py",
    "scripts/zigux/check-phase1-rbtree-review-packet.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    "scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
)

EXPECTED_VALIDATOR_MARKERS = (
    '"""Validate the current Phase 1 closure note against the live reminder packet."""',
    "DELEGATED_CHECKERS = (",
    'print("PHASE1_CLOSURE_SELF_TEST=pass")',
    'print("PHASE1_CLOSURE_VALIDATION=pass")',
    'print("PHASE1_CLOSURE_MODE=current-master-safe")',
)

EXPECTED_CLOSURE_MARKERS = (
    "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",
    "`PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",
    "`PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py exact-checks helper-local rbtree anchors plus the committed duplicate-search and cached-leftmost replay packet across the helper, closure note, lane note, manifest, fixture, and shared smoke route`",
    "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
)

EXPECTED_SCRIPTS_README_MARKERS = (
    "`python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
    "`scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    "`scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
)

EXPECTED_TESTS_README_MARKERS = (
    "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
    "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "- `scripts/zigux/validate-phase1-closure.py`",
    "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
)

EXPECTED_WORKFLOW_DIRECT_LINES = (
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
)

FORBIDDEN_WORKFLOW_DIRECT_LINES = (
    "run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    "run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    "run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
)


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def require_present_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    validator_text = read_text(root, VALIDATOR_REL)
    closure_text = read_text(root, CLOSURE_REL)
    scripts_text = read_text(root, SCRIPTS_README_REL)
    tests_text = read_text(root, TESTS_README_REL)
    workflow_text = read_text(root, WORKFLOW_REL)

    for marker in EXPECTED_VALIDATOR_MARKERS:
        failures.extend(require_occurrence(validator_text, f"{VALIDATOR_REL}:{marker}", marker))
    for delegate_path in EXPECTED_DELEGATE_PATHS:
        failures.extend(require_occurrence(validator_text, f"{VALIDATOR_REL}:delegate:{delegate_path}", f'Path("{delegate_path}")'))

    for marker in EXPECTED_CLOSURE_MARKERS:
        failures.extend(require_occurrence(closure_text, f"{CLOSURE_REL}:{marker}", marker))
    for marker in EXPECTED_SCRIPTS_README_MARKERS:
        failures.extend(require_occurrence(scripts_text, f"{SCRIPTS_README_REL}:{marker}", marker))
    for marker in EXPECTED_TESTS_README_MARKERS:
        failures.extend(require_occurrence(tests_text, f"{TESTS_README_REL}:{marker}", marker))

    for marker in EXPECTED_WORKFLOW_DIRECT_LINES:
        failures.extend(require_present_line(workflow_text, f"{WORKFLOW_REL}:{marker}", marker))
    for marker in FORBIDDEN_WORKFLOW_DIRECT_LINES:
        failures.extend(require_absent_line(workflow_text, f"{WORKFLOW_REL}:{marker}", marker))

    return failures


def write_text(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    validator_lines = list(EXPECTED_VALIDATOR_MARKERS)
    validator_lines.extend(f'REL = Path("{path}")' for path in EXPECTED_DELEGATE_PATHS)
    write_text(root, VALIDATOR_REL, "\n".join(validator_lines) + "\n")
    write_text(root, CLOSURE_REL, "\n".join(EXPECTED_CLOSURE_MARKERS) + "\n")
    write_text(root, SCRIPTS_README_REL, "\n".join(EXPECTED_SCRIPTS_README_MARKERS) + "\n")
    write_text(root, TESTS_README_REL, "\n".join(EXPECTED_TESTS_README_MARKERS) + "\n")
    write_text(root, WORKFLOW_REL, "\n".join(EXPECTED_WORKFLOW_DIRECT_LINES) + "\n")


def remove_once(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def duplicate_once(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def append_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text + marker + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("success", None),
        ("missing_validator_file", lambda root: (root / VALIDATOR_REL).unlink()),
        ("missing_validator_delegate", lambda root: remove_once(root, VALIDATOR_REL, 'REL = Path("scripts/zigux/check-phase1-rbtree-review-packet.py")')),
        ("duplicate_validator_delegate", lambda root: duplicate_once(root, VALIDATOR_REL, 'REL = Path("scripts/zigux/check-phase1-bitmap-direct-anchors.py")')),
        ("missing_validator_pass_marker", lambda root: remove_once(root, VALIDATOR_REL, 'print("PHASE1_CLOSURE_VALIDATION=pass")')),
        ("missing_closure_marker", lambda root: remove_once(root, CLOSURE_REL, EXPECTED_CLOSURE_MARKERS[2])),
        ("missing_scripts_marker", lambda root: remove_once(root, SCRIPTS_README_REL, EXPECTED_SCRIPTS_README_MARKERS[0])),
        ("missing_tests_marker", lambda root: remove_once(root, TESTS_README_REL, EXPECTED_TESTS_README_MARKERS[0])),
        ("missing_workflow_direct_line", lambda root: remove_once(root, WORKFLOW_REL, EXPECTED_WORKFLOW_DIRECT_LINES[0])),
        ("duplicate_workflow_direct_line", lambda root: duplicate_once(root, WORKFLOW_REL, EXPECTED_WORKFLOW_DIRECT_LINES[3])),
        ("forbidden_rbtree_workflow_line", lambda root: append_line(root, WORKFLOW_REL, FORBIDDEN_WORKFLOW_DIRECT_LINES[0])),
        ("forbidden_bitmap_workflow_line", lambda root: append_line(root, WORKFLOW_REL, FORBIDDEN_WORKFLOW_DIRECT_LINES[2])),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-delegate-packet-") as tmp:
            root = Path(tmp)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print(f"phase1-closure-delegate:self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-delegate:self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_DELEGATE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_DELEGATE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_CLOSURE_DELEGATE_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_DELEGATE_PACKET=pass")
    print(f"PHASE1_CLOSURE_DELEGATE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_CLOSURE_DELEGATE_PACKET_DELEGATE_COUNT={len(EXPECTED_DELEGATE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
