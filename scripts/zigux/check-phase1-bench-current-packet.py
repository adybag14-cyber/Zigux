#!/usr/bin/env python3
"""Guard the current Phase 1 bench packet across docs, tests, workflow, and checker surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[1] if len(HERE.parents) > 1 else HERE.parent

PHASE1_CLOSURE_REL = "Documentation/zigux/phase1-closure.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
TESTS_README_REL = "zigux/tests/README.md"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
BENCH_CHECKER_REL = "scripts/zigux/check-phase1-bench.py"

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    WORKFLOW_REL,
    BENCH_CHECKER_REL,
)

MARKERS = {
    PHASE1_CLOSURE_REL: (
        "- `scripts/zigux/check-phase1-bench.py`",
        "- `zigux/tests/phase1_bench.zig`",
        "- `zigux/tests/fixtures/phase1_bench_expectations.json`",
        "- `PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
        "- `PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",
    ),
    SCRIPTS_README_REL: (
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
    ),
    TESTS_README_REL: (
        "  * current direct-readback Phase 1 reminder packet:",
        "- `scripts/zigux/check-phase1-bench.py`",
        "  * broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
        "Tests-root reviewer prompt:",
    ),
    WORKFLOW_REL: (
        "      - name: Self-test current Phase 1 bench checker",
        "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    BENCH_CHECKER_REL: (
        "class DuplicateTrackingDict(dict[str, object]):",
        "def expectations_path(root: Path) -> Path:",
        "def bench_source_path(root: Path) -> Path:",
        "REQUIRED_EXACT_CHECKSUMS = set(EXPECTED_CHECKSUMS)",
        "FIND_BIT_REQUIRED_SOURCE_MARKERS = {",
        "RBTREE_REQUIRED_SOURCE_MARKERS = {",
        "SOURCE_MARKER_SETS = (",
        "def validate_bench_source(text: str) -> tuple[str, object]:",
        "def load_runtime_bench_source(path: Path) -> tuple[str, object]:",
        'return ("missing_bench_source_file", path)',
        'return ("expectations_json_error", exc)',
        'return ("expectations_checksums_find_bit_exact_required", key)',
        'return ("expectations_checksums_rbtree_exact_required", key)',
        'return ("missing_find_bit_exact_checksums", missing_exact)',
        'return ("missing_rbtree_exact_checksums", missing_exact)',
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
        'print(f"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}")',
        'print("PHASE1_BENCH_CHECK=pass")',
        'print(f"PHASE1_BENCH_EXPECTATIONS={expectations_file}")',
        'print(f"PHASE1_BENCH_SOURCE={phase1_bench}")',
    ),
}

FORBIDDEN_FRAGMENTS = {
    WORKFLOW_REL: (
        "run: zig build bench --build-file zigux/tests/build.zig",
    ),
    BENCH_CHECKER_REL: (
        "PHASE1_BENCH_EXPECTATION_COUNT",
        "PHASE1_BENCH_CHECK_REASON=bench_command_exit",
        "PHASE1_BENCH_CHECK_REASON=bench_command_missing",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            issues.append(f"missing_file:{relative_path}")
    if issues:
        return issues

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = text.count(marker)
            if count != 1:
                issues.append(f"{relative_path}:marker_count:{marker}:expected=1:actual={count}")
        for forbidden in FORBIDDEN_FRAGMENTS.get(relative_path, ()):
            count = text.count(forbidden)
            if count != 0:
                issues.append(f"{relative_path}:forbidden:{forbidden}:actual={count}")

    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        content = "\n".join(MARKERS[relative_path]) + "\n"
        write_text(root, relative_path, content)


def mutate_remove(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print(f"case=baseline actual={issues!r}")
            return 1

    cases = [
        ("missing_file", WORKFLOW_REL, None, "unlink"),
        ("missing_closure_marker", PHASE1_CLOSURE_REL, MARKERS[PHASE1_CLOSURE_REL][3], "remove"),
        ("duplicate_scripts_marker", SCRIPTS_README_REL, MARKERS[SCRIPTS_README_REL][1], "duplicate"),
        ("missing_tests_marker", TESTS_README_REL, MARKERS[TESTS_README_REL][2], "remove"),
        ("missing_workflow_hook", WORKFLOW_REL, MARKERS[WORKFLOW_REL][1], "remove"),
        ("missing_bench_marker", BENCH_CHECKER_REL, MARKERS[BENCH_CHECKER_REL][7], "remove"),
        ("forbidden_workflow_bench_run", WORKFLOW_REL, FORBIDDEN_FRAGMENTS[WORKFLOW_REL][0], "append"),
        ("forbidden_bench_reason", BENCH_CHECKER_REL, FORBIDDEN_FRAGMENTS[BENCH_CHECKER_REL][1], "append"),
    ]

    for name, relative_path, marker, op in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            target = root / relative_path
            if op == "unlink":
                target.unlink()
                expected = [f"missing_file:{relative_path}"]
            elif op == "remove":
                assert marker is not None
                mutate_remove(root, relative_path, marker)
                expected = [f"{relative_path}:marker_count:{marker}:expected=1:actual=0"]
            elif op == "duplicate":
                assert marker is not None
                mutate_duplicate(root, relative_path, marker)
                expected = [f"{relative_path}:marker_count:{marker}:expected=1:actual=2"]
            else:
                assert marker is not None
                target.write_text(target.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
                expected = [f"{relative_path}:forbidden:{marker}:actual=1"]

            issues = collect_issues(root)
            if issues != expected:
                print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
                print(f"case={name}")
                print(f"expected={expected!r}")
                print(f"actual={issues!r}")
                return 1

    print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_CURRENT_PACKET_SELF_TEST_CASE_COUNT={len(cases) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE1_BENCH_CURRENT_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_BENCH_CURRENT_PACKET=pass")
    print(f"PHASE1_BENCH_CURRENT_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BENCH_CURRENT_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
