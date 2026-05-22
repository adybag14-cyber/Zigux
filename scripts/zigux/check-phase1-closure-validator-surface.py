#!/usr/bin/env python3
"""Guard the current Phase 1 closure-validator contract against surface drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")

REQUIRED_EXACT_LINES = (
    '"""Validate the current Phase 1 closure note against the live reminder packet."""',
    'PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")',
    'PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")',
    'DOCS_ROOT_REL = Path("Documentation/zigux/README.md")',
    'REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")',
    'SCRIPTS_README_REL = Path("scripts/zigux/README.md")',
    'STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")',
    'DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")',
    'ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")',
    'BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")',
    'SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")',
    'TESTS_README_REL = Path("zigux/tests/README.md")',
    'TESTS_BUILD_REL = Path("zigux/tests/build.zig")',
    'PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")',
    'WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")',
    'MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")',
    'ZIGUX_MAKEFILE_REL = Path("zigux/Makefile")',
    'BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")',
    'FIND_BIT_HELPER_REL = Path("tools/lib/find_bit.zig")',
    'RBTREE_HELPER_REL = Path("tools/lib/rbtree.zig")',
    'STRING_HELPER_REL = Path("tools/lib/string.zig")',
    'EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [',
    'EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [',
    'EXPECTED_LANE_RULE_SUMMARY = (',
    'EXPECTED_ANTI_OVERLAP_RULE = (',
    'EXPECTED_CLOSURE_MARKERS = {',
    'EXPECTED_MAKEFILE_MARKERS = (',
    'FORBIDDEN_MAKEFILE_MARKERS = (',
    'EXPECTED_FIND_BIT_REVIEW_ANCHORS = {',
    'EXPECTED_RBTREE_REVIEW_ANCHORS = {',
    'EXPECTED_BITMAP_REVIEW_ANCHORS = {',
    'EXPECTED_STRING_REVIEW_ANCHORS = {',
    'REQUIRED_FILES = (',
    'DELEGATED_CHECKERS = (',
    '(STRING_REVIEW_CHECKER_REL, "phase1-string-review-packet"),',
    '(DIRECT_OWNER_CHECKER_REL, "phase1-direct-owner-markers"),',
    '(ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts"),',
    '(BENCH_CHECKER_REL, "phase1-bench"),',
    '(SHARED_REMINDER_CHECKER_REL, "phase1-shared-reminder-packet"),',
    'print("PHASE1_CLOSURE_SELF_TEST=pass")',
    'print(f"PHASE1_CLOSURE_SELF_TEST_CASE_COUNT={len(cases)}")',
    'print("PHASE1_CLOSURE_VALIDATION=pass")',
    'print("PHASE1_CLOSURE_MODE=current-master-safe")',
)

REQUIRED_SUBSTRINGS = (
    '"route_summary_guard": "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",',
    '"shared_tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",',
    '"find_bit_bench_guard": "`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",',
    '"string_sysfs_review": "`PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`",',
    '"validator_state": "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",',
    '"phase14-validate:",',
    '"phase1-validate:",',
    '"phase1-test:",',
    '"phase1-bench:",',
    '"phase1:",',
    '"including andnot"',
    '"cached_leftmost_return_serials"',
    '"strnchrNul returns the first match, NUL, or count boundary"',
    '"strspn counts the accepted prefix with C-string semantics"',
)

FORBIDDEN_SUBSTRINGS = (
    'PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master',
    '`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`',
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_substring(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent_substring(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    target = root / VALIDATOR_REL
    if not target.is_file():
        return [f"missing_file:{VALIDATOR_REL.as_posix()}"]

    text = load_text(root, VALIDATOR_REL)
    failures: list[str] = []
    for marker in REQUIRED_EXACT_LINES:
        failures.extend(
            require_exact_line(
                text,
                f"{VALIDATOR_REL.as_posix()}:line:{marker}",
                marker,
            )
        )
    for marker in REQUIRED_SUBSTRINGS:
        failures.extend(
            require_exact_substring(
                text,
                f"{VALIDATOR_REL.as_posix()}:substring:{marker}",
                marker,
            )
        )
    for marker in FORBIDDEN_SUBSTRINGS:
        failures.extend(
            require_absent_substring(
                text,
                f"{VALIDATOR_REL.as_posix()}:forbidden:{marker}",
                marker,
            )
        )
    return failures


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_validator() -> str:
    body = ["#!/usr/bin/env python3"]
    body.extend(REQUIRED_EXACT_LINES)
    body.extend(REQUIRED_SUBSTRINGS)
    return "\n".join(body) + "\n"


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, str] | None]] = [("success", None)]
    for marker in REQUIRED_EXACT_LINES:
        cases.append((f"remove_line_{abs(hash(marker))}", ("line_remove", marker)))
        cases.append((f"duplicate_line_{abs(hash(marker))}", ("line_duplicate", marker)))
    for marker in REQUIRED_SUBSTRINGS:
        cases.append((f"remove_substring_{abs(hash(marker))}", ("substring_remove", marker)))
        cases.append((f"duplicate_substring_{abs(hash(marker))}", ("substring_duplicate", marker)))
    for marker in FORBIDDEN_SUBSTRINGS:
        cases.append((f"forbidden_{abs(hash(marker))}", ("forbidden_add", marker)))
    cases.append(("missing_file", ("missing_file", "")))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-validator-") as tmpdir:
            root = Path(tmpdir)
            write_text(root, VALIDATOR_REL, build_sample_validator())
            if mutation is not None:
                kind, marker = mutation
                target = root / VALIDATOR_REL
                if kind == "missing_file":
                    target.unlink()
                else:
                    text = target.read_text(encoding="utf-8")
                    if kind == "line_remove":
                        text = text.replace(marker + "\n", "", 1)
                    elif kind == "line_duplicate":
                        text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                    elif kind == "substring_remove":
                        text = text.replace(marker, "", 1)
                    elif kind == "substring_duplicate":
                        text = text.replace(marker, marker + "\n" + marker, 1)
                    elif kind == "forbidden_add":
                        text += marker + "\n"
                    target.write_text(text, encoding="utf-8")

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_VALIDATOR_SURFACE_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_SURFACE_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_VALIDATOR_SURFACE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
