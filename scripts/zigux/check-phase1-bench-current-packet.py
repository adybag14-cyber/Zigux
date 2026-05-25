#!/usr/bin/env python3
"""Guard the current Phase 1 bench packet across reminder and checker surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

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
        "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "- `PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
        "- `PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",
    ),
    SCRIPTS_README_REL: (
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
        "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
        "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
    ),
    TESTS_README_REL: (
        "- `scripts/zigux/check-phase1-bench.py`",
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "  * broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
        "- Does the bounded Phase 1 reminder keep the restored closure note, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?",
    ),
    WORKFLOW_REL: (
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    BENCH_CHECKER_REL: (
        'class DuplicateTrackingDict(dict[str, object]):',
        'def repo_root(root: str | None) -> Path:',
        'def expectations_path(root: Path) -> Path:',
        'def bench_source_path(root: Path) -> Path:',
        'def find_zig(explicit: str | None) -> str:',
        'raise SystemExit("zig not found; pass --zig or add zig to PATH")',
        'def parse_output(stdout: str) -> tuple[dict[str, str], dict[str, int]]:',
        'def load_expectations_text(text: str) -> object:',
        'return json.loads(text, object_pairs_hook=DuplicateTrackingDict)',
        'def load_runtime_expectations(path: Path) -> tuple[str, object]:',
        'return ("missing_expectations_file", path)',
        'return ("expectations_json_error", exc)',
        'def validate_bench_source(text: str) -> tuple[str, object]:',
        'def load_runtime_bench_source(path: Path) -> tuple[str, object]:',
        'return ("missing_bench_source_file", path)',
        'FIND_BIT_REQUIRED_SOURCE_MARKERS = {',
        'RBTREE_REQUIRED_SOURCE_MARKERS = {',
        'SOURCE_MARKER_SETS = (',
        '"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"',
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
        'print(f"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}")',
        'parser.add_argument("--repo-root", "--root", dest="repo_root", help="Override the repository root used for validation.")',
        'print("PHASE1_BENCH_CHECK=pass")',
        'print(f"PHASE1_BENCH_EXPECTATIONS={expectations_file}")',
        'print(f"PHASE1_BENCH_SOURCE={phase1_bench}")',
        'print(f"PHASE1_BENCH_ZIG={zig}")',
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
        "def emit_bench_command_failure(",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues = [f"missing_file:{path}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if issues:
        return issues

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        lines = [line.strip() for line in text.splitlines()]
        for marker in markers:
            count = lines.count(marker) if relative_path == WORKFLOW_REL else text.count(marker)
            if count != 1:
                issues.append(
                    f"{relative_path}:marker_count:{marker}:expected=1:actual={count}"
                )

        for fragment in FORBIDDEN_FRAGMENTS.get(relative_path, ()):
            count = text.count(fragment)
            if count:
                issues.append(f"{relative_path}:forbidden:{fragment}:actual={count}")

    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_text(relative_path: str) -> str:
    if relative_path == WORKFLOW_REL:
        return "\n".join(
            [
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: self-test bench checker",
                "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
                "",
            ]
        )
    return "\n".join(MARKERS[relative_path]) + "\n"


def build_sample_root(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root, relative_path, build_sample_text(relative_path))


def mutate_remove_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, "", 1), encoding="utf-8")


def write_sample_root(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    build_sample_root(target)


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_root(root)
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            for issue in issues:
                print(issue)
            return 1
        case_count += 1

    mutation_cases = [
        (PHASE1_CLOSURE_REL, MARKERS[PHASE1_CLOSURE_REL][4]),
        (PHASE1_CLOSURE_REL, MARKERS[PHASE1_CLOSURE_REL][5]),
        (SCRIPTS_README_REL, MARKERS[SCRIPTS_README_REL][0]),
        (SCRIPTS_README_REL, MARKERS[SCRIPTS_README_REL][3]),
        (TESTS_README_REL, MARKERS[TESTS_README_REL][2]),
        (TESTS_README_REL, MARKERS[TESTS_README_REL][3]),
        (WORKFLOW_REL, MARKERS[WORKFLOW_REL][0]),
        (BENCH_CHECKER_REL, MARKERS[BENCH_CHECKER_REL][4]),
        (BENCH_CHECKER_REL, MARKERS[BENCH_CHECKER_REL][13]),
        (BENCH_CHECKER_REL, MARKERS[BENCH_CHECKER_REL][15]),
        (BENCH_CHECKER_REL, MARKERS[BENCH_CHECKER_REL][22]),
    ]

    for relative_path, marker in mutation_cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            mutate_remove_marker(root, relative_path, marker)
            issues = collect_issues(root)
            expected = f"{relative_path}:marker_count:{marker}:expected=1:actual=0"
            if issues != [expected]:
                print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
                print(f"expected={expected}")
                print(f"actual={issues!r}")
                return 1
            case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-forbidden-") as tmpdir:
        root = Path(tmpdir)
        build_sample_root(root)
        workflow = root / WORKFLOW_REL
        workflow.write_text(
            workflow.read_text(encoding="utf-8")
            + "        run: zig build bench --build-file zigux/tests/build.zig\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        expected = (
            f"{WORKFLOW_REL}:forbidden:run: zig build bench --build-file zigux/tests/build.zig:actual=1"
        )
        if issues != [expected]:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print(f"expected={expected}")
            print(f"actual={issues!r}")
            return 1
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-missing-") as tmpdir:
        root = Path(tmpdir)
        build_sample_root(root)
        (root / BENCH_CHECKER_REL).unlink()
        issues = collect_issues(root)
        expected = f"missing_file:{BENCH_CHECKER_REL}"
        if issues != [expected]:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print(f"expected={expected}")
            print(f"actual={issues!r}")
            return 1
        case_count += 1

    print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_CURRENT_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample root for checker replay",
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    args = parser.parse_args()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        print(f"PHASE1_BENCH_CURRENT_PACKET_SAMPLE_ROOT={Path(args.write_sample_root).resolve()}")
        return 0

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
