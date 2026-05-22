#!/usr/bin/env python3
"""Guard the current Phase 1 scripts-plus-workflow closure packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
DIRECT_OWNER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
STRING_REVIEW_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
ROUTE_SUMMARY_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
BENCH_REL = Path("scripts/zigux/check-phase1-bench.py")
SHARED_REMINDER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    SCRIPTS_README_REL,
    WORKFLOW_REL,
    DIRECT_OWNER_REL,
    STRING_REVIEW_REL,
    ROUTE_SUMMARY_REL,
    BENCH_REL,
    SHARED_REMINDER_REL,
    VALIDATOR_REL,
    TESTS_BUILD_REL,
)

REQUIRED_MARKERS = {
    PHASE1_CLOSURE_REL: (
        "The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet: `.github/workflows/zigux-bootstrap.yml` self-tests the directly readable Phase 1 direct-owner, string-review, route-summary, bench, shared-reminder, and closure-validator checks, replays the route-summary, direct-owner, string-review, shared-reminder, closure-validator, and shared tests-root smoke steps on current `master`, and currently keeps the bench checker at self-test coverage only.",
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    ),
    SCRIPTS_README_REL: (
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
        "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    ),
    WORKFLOW_REL: (
        "      - name: Self-test current Phase 1 direct-owner checker",
        "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "      - name: Check current Phase 1 direct-owner markers",
        "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
        "      - name: Self-test current Phase 1 string review checker",
        "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
        "      - name: Check current Phase 1 string review packet",
        "        run: python3 scripts/zigux/check-phase1-string-review-packet.py",
        "      - name: Self-test current Phase 1 route summary checker",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "      - name: Check current Phase 1 route summary packet",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "      - name: Self-test current Phase 1 bench checker",
        "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "      - name: Self-test current Phase 1 shared reminder checker",
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "      - name: Check current Phase 1 shared reminder packet",
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "      - name: Self-test current Phase 1 closure validator",
        "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "      - name: Check current Phase 1 closure packet",
        "        run: python3 scripts/zigux/validate-phase1-closure.py",
        "      - name: Run current Phase 1 shared tests-root smoke",
        "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
    DIRECT_OWNER_REL: (
        'print("phase1-direct-owner-markers:ok")',
        "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [",
    ),
    STRING_REVIEW_REL: (
        'print("phase1-string-review-packet:ok")',
        "EXPECTED_HELPER_TEST_ANCHORS = [",
    ),
    ROUTE_SUMMARY_REL: (
        'print("PHASE1_ROUTE_SUMMARY_COUNTS=pass")',
        'print("PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass")',
    ),
    BENCH_REL: (
        'print("PHASE1_BENCH_CHECK=pass")',
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
        "FIND_BIT_REQUIRED_EXACT_CHECKSUMS = {",
    ),
    SHARED_REMINDER_REL: (
        'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
        'print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")',
    ),
    VALIDATOR_REL: (
        'print("PHASE1_CLOSURE_VALIDATION=pass")',
        'print("PHASE1_CLOSURE_SELF_TEST=pass")',
        '`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`',
    ),
    TESTS_BUILD_REL: (
        '.root_source_file = b.path("phase1_host_tools_smoke.zig"),',
        '.name = "phase1-host-tools-smoke",',
    ),
}

FORBIDDEN_MARKERS = {
    SCRIPTS_README_REL: (
        "python3 scripts/zigux/check-phase1-parity.py --self-test",
        "python3 scripts/zigux/check-phase1-parity.py",
        "python3 scripts/zigux/validate-phase1.py --self-test",
        "python3 scripts/zigux/validate-phase1.py",
    ),
    WORKFLOW_REL: (
        "      - name: Check current Phase 1 bench checker",
        "        run: python3 scripts/zigux/check-phase1-bench.py",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, relative_path)
        for idx, marker in enumerate(markers):
            if relative_path == WORKFLOW_REL:
                failures.extend(
                    require_exact_line(
                        text,
                        f"{relative_path.as_posix()}:marker_{idx}",
                        marker,
                    )
                )
            else:
                failures.extend(
                    require_exact_occurrence(
                        text,
                        f"{relative_path.as_posix()}:marker_{idx}",
                        marker,
                    )
                )
        for forbidden in FORBIDDEN_MARKERS.get(relative_path, ()):
            if relative_path == WORKFLOW_REL:
                count = sum(
                    1 for line in text.splitlines() if line.strip() == forbidden.strip()
                )
            else:
                count = text.count(forbidden)
            if count:
                failures.append(
                    f"{relative_path.as_posix()}:forbidden:{count}:{forbidden}"
                )
    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_file(
            root,
            relative_path,
            "# sample\n\n" + "\n".join(REQUIRED_MARKERS[relative_path]) + "\n",
        )


def mutate_missing_marker(root: Path, relative_path: Path, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_marker(root: Path, relative_path: Path, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def mutate_add_forbidden(root: Path, relative_path: Path, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text + marker + "\n", encoding="utf-8")


def write_sample_root(destination: Path) -> None:
    build_sample_root(destination)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-scripts-workflow-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_root(root)
        failures = collect_failures(root)
        if failures:
            print("phase1-scripts-workflow:self-test:unexpected_failures")
            for failure in failures:
                print(failure)
            return 1
        case_count += 1

    for relative_path, markers in REQUIRED_MARKERS.items():
        for marker in markers:
            with tempfile.TemporaryDirectory(
                prefix="phase1-scripts-workflow-missing-"
            ) as tmpdir:
                root = Path(tmpdir)
                build_sample_root(root)
                mutate_missing_marker(root, relative_path, marker)
                if not collect_failures(root):
                    print(
                        "phase1-scripts-workflow:self-test:expected_missing_marker_failure"
                    )
                    return 1
                case_count += 1

            with tempfile.TemporaryDirectory(
                prefix="phase1-scripts-workflow-duplicate-"
            ) as tmpdir:
                root = Path(tmpdir)
                build_sample_root(root)
                mutate_duplicate_marker(root, relative_path, marker)
                if not collect_failures(root):
                    print(
                        "phase1-scripts-workflow:self-test:expected_duplicate_marker_failure"
                    )
                    return 1
                case_count += 1

    for relative_path, markers in FORBIDDEN_MARKERS.items():
        for marker in markers:
            with tempfile.TemporaryDirectory(
                prefix="phase1-scripts-workflow-forbidden-"
            ) as tmpdir:
                root = Path(tmpdir)
                build_sample_root(root)
                mutate_add_forbidden(root, relative_path, marker)
                if not collect_failures(root):
                    print(
                        "phase1-scripts-workflow:self-test:expected_forbidden_marker_failure"
                    )
                    return 1
                case_count += 1

    for relative_path in REQUIRED_FILES:
        with tempfile.TemporaryDirectory(
            prefix="phase1-scripts-workflow-missing-file-"
        ) as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            (root / relative_path).unlink()
            if not collect_failures(root):
                print("phase1-scripts-workflow:self-test:expected_missing_file_failure")
                return 1
            case_count += 1

    print("PHASE1_SCRIPTS_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_SCRIPTS_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument(
        "--self-test", action="store_true", help="run built-in checker self-test"
    )
    parser.add_argument(
        "--write-sample-root",
        help="write a minimal current-like sample root for focused validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_SCRIPTS_WORKFLOW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_SCRIPTS_WORKFLOW_PACKET=pass")
    print(f"PHASE1_SCRIPTS_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_SCRIPTS_WORKFLOW_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
