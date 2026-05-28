#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
FIND_BIT_BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")

REQUIRED_FILES = (
    WORKFLOW_REL,
    BENCH_CHECKER_REL,
    FIND_BIT_BENCH_CHECKER_REL,
    SHARED_REMINDER_CHECKER_REL,
)

WORKFLOW_SEQUENCE = (
    (
        "phase1_route_summary_self_test",
        "      - name: Self-test current Phase 1 route summary checker\n"
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    ),
    (
        "phase1_route_summary_packet",
        "      - name: Check current Phase 1 route summary packet\n"
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    ),
    (
        "phase1_bench_self_test",
        "      - name: Self-test current Phase 1 bench checker\n"
        "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    (
        "phase1_find_bit_bench_anchor_self_test",
        "      - name: Self-test current Phase 1 find-bit bench anchor checker\n"
        "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    ),
    (
        "phase1_find_bit_bench_anchor_packet",
        "      - name: Check current Phase 1 find-bit bench anchor packet\n"
        "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    ),
    (
        "phase1_shared_reminder_self_test",
        "      - name: Self-test current Phase 1 shared reminder checker\n"
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    ),
    (
        "phase1_shared_reminder_packet",
        "      - name: Check current Phase 1 shared reminder packet\n"
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    ),
    (
        "phase1_closure_validator_self_test",
        "      - name: Self-test current Phase 1 closure validator\n"
        "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    ),
)

FORBIDDEN_WORKFLOW_MARKERS = (
    "      - name: Run Phase 1 helper benchmark smoke\n"
    "        run: zig build phase1-bench --build-file zigux/tests/build.zig",
)

BENCH_SOURCE_MARKERS = (
    "EXPECTED_ITERATIONS = {",
    '"PHASE1_BENCH_RBTREE_ITERATIONS": 4000,',
    "EXPECTED_CHECKSUMS = [",
    '"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",',
    "def validate_bench_source(text: str) -> tuple[str, object]:",
    "def run_self_test() -> None:",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def require_file(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"missing required file: {rel}") from None


def marker_positions(text: str, markers: tuple[tuple[str, str], ...]) -> list[tuple[str, int]]:
    positions: list[tuple[str, int]] = []
    for label, marker in markers:
        count = text.count(marker)
        if count == 0:
            raise SystemExit(f"missing workflow marker: {label}")
        if count > 1:
            raise SystemExit(f"duplicate workflow marker: {label}")
        positions.append((label, text.index(marker)))
    return positions


def validate_workflow(text: str) -> None:
    positions = marker_positions(text, WORKFLOW_SEQUENCE)
    previous_label, previous_pos = positions[0]
    for label, pos in positions[1:]:
        if pos <= previous_pos:
            raise SystemExit(
                f"workflow marker out of order: {label} must follow {previous_label}"
            )
        previous_label, previous_pos = label, pos
    for marker in FORBIDDEN_WORKFLOW_MARKERS:
        if marker in text:
            raise SystemExit("stale direct Phase 1 benchmark smoke route is present")


def validate_bench_checker(text: str) -> None:
    for marker in BENCH_SOURCE_MARKERS:
        if marker not in text:
            raise SystemExit(f"missing bench checker source marker: {marker}")


def check_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        require_file(root, rel)
    validate_workflow(require_file(root, WORKFLOW_REL))
    validate_bench_checker(require_file(root, BENCH_CHECKER_REL))


def sample_workflow() -> str:
    blocks = [marker for _, marker in WORKFLOW_SEQUENCE]
    return "name: zigux-bootstrap\n\njobs:\n  bootstrap:\n    steps:\n" + "\n\n".join(blocks) + "\n"


def sample_bench_checker() -> str:
    return "\n".join(
        (
            "EXPECTED_ITERATIONS = {",
            '    "PHASE1_BENCH_RBTREE_ITERATIONS": 4000,',
            "}",
            "EXPECTED_CHECKSUMS = [",
            '    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",',
            "]",
            "def validate_bench_source(text: str) -> tuple[str, object]:",
            "    return ('pass', {})",
            "def run_self_test() -> None:",
            "    pass",
            "",
        )
    )


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    (root / WORKFLOW_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / BENCH_CHECKER_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / WORKFLOW_REL).write_text(sample_workflow(), encoding="utf-8")
    (root / BENCH_CHECKER_REL).write_text(sample_bench_checker(), encoding="utf-8")
    for rel in (FIND_BIT_BENCH_CHECKER_REL, SHARED_REMINDER_CHECKER_REL):
        (root / rel).write_text("# sample checker placeholder\n", encoding="utf-8")


def expect_failure(label: str, root: Path, mutator) -> None:
    write_sample_root(root)
    mutator(root)
    try:
        check_root(root)
    except SystemExit:
        return
    raise SystemExit(f"self-test case unexpectedly passed: {label}")


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux-phase1-bench-workflow-") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        check_root(root)

        def drop_bench_marker(case_root: Path) -> None:
            workflow = case_root / WORKFLOW_REL
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace(WORKFLOW_SEQUENCE[2][1], ""),
                encoding="utf-8",
            )

        def duplicate_anchor_marker(case_root: Path) -> None:
            workflow = case_root / WORKFLOW_REL
            text = workflow.read_text(encoding="utf-8")
            workflow.write_text(
                text + "\n" + WORKFLOW_SEQUENCE[4][1] + "\n",
                encoding="utf-8",
            )

        def swap_bench_and_route(case_root: Path) -> None:
            workflow = case_root / WORKFLOW_REL
            text = workflow.read_text(encoding="utf-8")
            text = text.replace(WORKFLOW_SEQUENCE[1][1], "__ROUTE_PACKET__")
            text = text.replace(WORKFLOW_SEQUENCE[2][1], WORKFLOW_SEQUENCE[1][1])
            text = text.replace("__ROUTE_PACKET__", WORKFLOW_SEQUENCE[2][1])
            workflow.write_text(text, encoding="utf-8")

        def stale_direct_bench_route(case_root: Path) -> None:
            workflow = case_root / WORKFLOW_REL
            workflow.write_text(
                workflow.read_text(encoding="utf-8") + "\n" + FORBIDDEN_WORKFLOW_MARKERS[0] + "\n",
                encoding="utf-8",
            )

        def drop_bench_source_marker(case_root: Path) -> None:
            bench = case_root / BENCH_CHECKER_REL
            bench.write_text(
                bench.read_text(encoding="utf-8").replace(BENCH_SOURCE_MARKERS[3], ""),
                encoding="utf-8",
            )

        cases = (
            ("drop_bench_marker", drop_bench_marker),
            ("duplicate_anchor_marker", duplicate_anchor_marker),
            ("swap_bench_and_route", swap_bench_and_route),
            ("stale_direct_bench_route", stale_direct_bench_route),
            ("drop_bench_source_marker", drop_bench_source_marker),
        )
        for label, mutator in cases:
            expect_failure(label, root, mutator)

    print("PHASE1_BENCH_WORKFLOW_PACKET_SELF_TEST=pass")
    print("PHASE1_BENCH_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT=6")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check the current Phase 1 bench workflow packet ordering."
    )
    parser.add_argument("--root", help="repository root to check")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument("--write-sample-root", help="write a passing sample repository root")
    args = parser.parse_args()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return
    if args.self_test:
        self_test()
        return

    check_root(repo_root(args.root))
    print("PHASE1_BENCH_WORKFLOW_PACKET=pass")
    print(f"PHASE1_BENCH_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BENCH_WORKFLOW_PACKET_REQUIRED_STEP_COUNT={len(WORKFLOW_SEQUENCE)}")


if __name__ == "__main__":
    main()
