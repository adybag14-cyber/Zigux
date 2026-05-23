#!/usr/bin/env python3
"""Guard the live Phase 1 rbtree bench-adjacent packet on current master."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
RBTREE_HELPER_REL = Path("tools/lib/rbtree.zig")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    CLOSURE_VALIDATOR_REL,
    BENCH_CHECKER_REL,
    RBTREE_HELPER_REL,
    WORKFLOW_REL,
)

REQUIRED_MARKERS = {
    PHASE1_CLOSURE_REL: (
        "Current `master` also keeps the stricter rbtree bench-exactness packet explicit in that same checker: `scripts/zigux/check-phase1-bench.py` now hard-codes `PHASE1_BENCH_RBTREE_ITERATIONS=4000` and exact-checks `PHASE1_BENCH_RBTREE_CHECKSUM`, `PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM`, `PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM`, `PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM`, and `PHASE1_BENCH_RBTREE_CACHED_CHECKSUM` whenever the broader expectations packet returns.",
        "- `PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",
        "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the dedicated manifest-backed `cached_root_alias_anchor`, the cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness.",
        "Current `master` still keeps both Linux-style alias proofs named explicitly in `zigux/tests/fixtures/phase1_helper_manifest.json`, while the shared host-tools smoke route and committed Phase 1 fixture already recheck duplicate-range iteration plus the exact cached-leftmost-return packet, so leave rbtree parked unless one of those helper-local anchors or committed replay fields drifts and do not batch a second cached-root widening into the same reopen step.",
    ),
    CLOSURE_VALIDATOR_REL: (
        'BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")',
        '    "rbtree_bench_guard": "`PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",',
        '    "tools/lib/rbtree.zig": EXPECTED_RBTREE_REVIEW_ANCHORS,',
        '    (BENCH_CHECKER_REL, "phase1-bench"),',
        'require_expected_mapping(f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig", review_anchors.get("tools/lib/rbtree.zig"), EXPECTED_RBTREE_REVIEW_ANCHORS)',
    ),
    BENCH_CHECKER_REL: (
        '"PHASE1_BENCH_RBTREE_ITERATIONS": 4000,',
        '"PHASE1_BENCH_RBTREE_CHECKSUM",',
        '"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",',
        '"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",',
        '"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",',
        '"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",',
        'RBTREE_REQUIRED_ITERATIONS = {"PHASE1_BENCH_RBTREE_ITERATIONS"}',
        "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
        '"rbtree_bench_fn": "fn rbtreeBench() struct { checksum: u64 } {",',
        '"rbtree_postorder_safe_fn": "fn rbtreePostorderSafeBench() struct { checksum: u64 } {",',
        '"rbtree_find_add_fn": "fn rbtreeFindAddBench() struct { checksum: u64 } {",',
        '"rbtree_duplicate_fn": "fn rbtreeDuplicateBench() struct { checksum: u64 } {",',
        '"rbtree_cached_fn": "fn rbtreeCachedBench() struct { checksum: u64 } {",',
        '"rbtree_iterations_print": \'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_ITERATIONS={d}\\n", .{iterations_rbtree});\',',
        '"rbtree_cached_print": \'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\\n", .{rbtree_cached_result.checksum});\',',
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
    ),
    RBTREE_HELPER_REL: (
        'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers" {',
        'test "rbtree low-level Linux-style aliases mirror node-state helpers" {',
        'test "rbtree matchIterator walks the duplicate range in order" {',
        'test "rbtree cached root keeps the leftmost pointer in sync" {',
        'test "rbtree cached-root Linux-style aliases mirror the primary helpers" {',
        'test "rbtree eraseInitCached clears singleton cached roots before reseed" {',
    ),
    WORKFLOW_REL: (
        "      - name: Self-test current Phase 1 bench checker",
        "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "      - name: Self-test current Phase 1 shared reminder checker",
        "      - name: Check current Phase 1 shared reminder packet",
        "      - name: Self-test current Phase 1 closure validator",
    ),
}

FORBIDDEN_WORKFLOW_LINES = (
    "        run: python3 scripts/zigux/check-phase1-bench.py",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_workflow_order_failures(text: str) -> list[str]:
    failures: list[str] = []
    names = [line for line in text.splitlines() if line.startswith("      - name: ")]
    wanted = [
        "      - name: Self-test current Phase 1 bench checker",
        "      - name: Self-test current Phase 1 shared reminder checker",
        "      - name: Check current Phase 1 shared reminder packet",
        "      - name: Self-test current Phase 1 closure validator",
    ]
    positions: list[int] = []
    for line in wanted:
        count = names.count(line)
        if count != 1:
            failures.append(f"workflow_name:{line}:expected=1:actual={count}")
            continue
        positions.append(names.index(line))
    if failures:
        return failures
    if positions != sorted(positions):
        failures.append("workflow_order:phase1_rbtree_bench_packet:expected=strictly_increasing:actual=out_of_order")
    return failures


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = text.count(marker)
            if count != 1:
                failures.append(f"{relative_path.as_posix()}:expected_once:actual_count={count}:{marker}")

    workflow_text = read_text(root, WORKFLOW_REL)
    failures.extend(collect_workflow_order_failures(workflow_text))
    for line in FORBIDDEN_WORKFLOW_LINES:
        count = sum(1 for current in workflow_text.splitlines() if current == line)
        if count != 0:
            failures.append(f"{WORKFLOW_REL.as_posix()}:forbidden_line:actual_count={count}:{line}")

    return failures


def build_sample_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        write_text(root, relative_path, "\n".join(markers) + "\n")


def remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    text = read_text(root, relative_path)
    write_text(root, relative_path, text.replace(marker + "\n", "", 1))


def add_forbidden_workflow_line(root: Path, line: str) -> None:
    text = read_text(root, WORKFLOW_REL)
    write_text(root, WORKFLOW_REL, text + line + "\n")


def reorder_workflow(root: Path) -> None:
    text = read_text(root, WORKFLOW_REL).splitlines()
    bench_index = text.index("      - name: Self-test current Phase 1 bench checker")
    shared_index = text.index("      - name: Self-test current Phase 1 shared reminder checker")
    text[bench_index], text[shared_index] = text[shared_index], text[bench_index]
    write_text(root, WORKFLOW_REL, "\n".join(text) + "\n")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, object] | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", ("missing_file", relative_path)))

    for relative_path, markers in REQUIRED_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path.as_posix()}", ("remove", relative_path, marker)))

    cases.append(("workflow_forbidden_line", ("forbidden", FORBIDDEN_WORKFLOW_LINES[0])))
    cases.append(("workflow_reordered", ("reorder", None)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-rbtree-bench-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if mutation is not None:
                kind = mutation[0]
                if kind == "missing_file":
                    (root / mutation[1]).unlink()
                elif kind == "remove":
                    remove_marker(root, mutation[1], mutation[2])
                elif kind == "forbidden":
                    add_forbidden_workflow_line(root, mutation[1])
                elif kind == "reorder":
                    reorder_workflow(root)

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print(f"self-test:{name}:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_RBTREE_BENCH_PACKET_SELF_TEST=pass")
    print(f"PHASE1_RBTREE_BENCH_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test only")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_RBTREE_BENCH_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_RBTREE_BENCH_PACKET=pass")
    print(f"PHASE1_RBTREE_BENCH_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
