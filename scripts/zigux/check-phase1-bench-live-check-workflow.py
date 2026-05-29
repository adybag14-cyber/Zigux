#!/usr/bin/env python3
"""Guard the Phase 1 bench checker's live workflow handoff."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")

BENCH_SELF_TEST_STEP = "Self-test current Phase 1 bench checker"
BENCH_SELF_TEST_RUN = "python3 scripts/zigux/check-phase1-bench.py --self-test"
BENCH_LIVE_CHECK_STEP = "Check current Phase 1 bench packet"
BENCH_LIVE_CHECK_RUN = "python3 scripts/zigux/check-phase1-bench.py"
FIND_BIT_BENCH_STEP = "Self-test current Phase 1 find-bit bench anchor checker"
FIND_BIT_BENCH_RUN = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test"

REQUIRED_STEPS = (
    (BENCH_SELF_TEST_STEP, BENCH_SELF_TEST_RUN),
    (BENCH_LIVE_CHECK_STEP, BENCH_LIVE_CHECK_RUN),
    (FIND_BIT_BENCH_STEP, FIND_BIT_BENCH_RUN),
)
REQUIRED_CHAIN = (
    BENCH_SELF_TEST_STEP,
    BENCH_LIVE_CHECK_STEP,
    FIND_BIT_BENCH_STEP,
)
BENCH_CHECKER_MARKERS = (
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
    "parser.add_argument('--self-test', action='store_true')",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {path}") from exc


def require_once(text: str, needle: str, label: str) -> None:
    count = text.count(needle)
    if count != 1:
        raise SystemExit(f"expected exactly one {label}, found {count}: {needle}")


def require_line_once(text: str, line: str, label: str) -> None:
    count = sum(1 for candidate in text.splitlines() if candidate.strip() == line)
    if count != 1:
        raise SystemExit(f"expected exactly one {label}, found {count}: {line}")


def require_order(text: str, chain: tuple[str, ...]) -> None:
    previous = -1
    for item in chain:
        index = text.find(item)
        if index == -1:
            raise SystemExit(f"missing ordered workflow item: {item}")
        if index <= previous:
            raise SystemExit(f"workflow item is out of order: {item}")
        previous = index


def validate_root(root: Path) -> None:
    workflow = read_text(root / WORKFLOW_REL)
    checker = read_text(root / BENCH_CHECKER_REL)

    for step_name, run_line in REQUIRED_STEPS:
        require_line_once(workflow, f"- name: {step_name}", f"workflow step {step_name!r}")
        require_line_once(workflow, f"run: {run_line}", f"workflow run line for {step_name!r}")
    require_order(workflow, REQUIRED_CHAIN)

    for marker in BENCH_CHECKER_MARKERS:
        require_once(checker, marker, f"bench checker marker {marker!r}")


def write_sample_root(root: Path) -> None:
    workflow_path = root / WORKFLOW_REL
    checker_path = root / BENCH_CHECKER_REL
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    checker_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(
        "name: zigux-bootstrap\n"
        "jobs:\n"
        "  bootstrap:\n"
        "    steps:\n"
        f"      - name: {BENCH_SELF_TEST_STEP}\n"
        f"        run: {BENCH_SELF_TEST_RUN}\n\n"
        f"      - name: {BENCH_LIVE_CHECK_STEP}\n"
        f"        run: {BENCH_LIVE_CHECK_RUN}\n\n"
        f"      - name: {FIND_BIT_BENCH_STEP}\n"
        f"        run: {FIND_BIT_BENCH_RUN}\n",
        encoding="utf-8",
    )
    checker_path.write_text(
        "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS\n"
        "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM\n"
        "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\n"
        "parser.add_argument('--self-test', action='store_true')\n",
        encoding="utf-8",
    )


def expect_failure(label: str, root: Path, expected: str) -> None:
    try:
        validate_root(root)
    except SystemExit as exc:
        message = str(exc)
        if expected not in message:
            raise SystemExit(f"{label}: expected failure containing {expected!r}, got {message!r}") from exc
        return
    raise SystemExit(f"{label}: expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_sample_root(root)
        validate_root(root)

        missing_check = root / "missing-check"
        write_sample_root(missing_check)
        workflow = (missing_check / WORKFLOW_REL).read_text(encoding="utf-8")
        workflow = workflow.replace(
            f"\n      - name: {BENCH_LIVE_CHECK_STEP}\n        run: {BENCH_LIVE_CHECK_RUN}\n",
            "\n",
        )
        (missing_check / WORKFLOW_REL).write_text(workflow, encoding="utf-8")
        expect_failure("missing live bench check", missing_check, BENCH_LIVE_CHECK_STEP)

        duplicate_check = root / "duplicate-check"
        write_sample_root(duplicate_check)
        workflow = (duplicate_check / WORKFLOW_REL).read_text(encoding="utf-8")
        workflow = workflow.replace(
            f"      - name: {FIND_BIT_BENCH_STEP}\n",
            f"      - name: {BENCH_LIVE_CHECK_STEP}\n        run: {BENCH_LIVE_CHECK_RUN}\n\n      - name: {FIND_BIT_BENCH_STEP}\n",
        )
        (duplicate_check / WORKFLOW_REL).write_text(workflow, encoding="utf-8")
        expect_failure("duplicate live bench check", duplicate_check, BENCH_LIVE_CHECK_STEP)

        reordered_check = root / "reordered-check"
        write_sample_root(reordered_check)
        workflow = (reordered_check / WORKFLOW_REL).read_text(encoding="utf-8")
        workflow = workflow.replace(
            f"      - name: {BENCH_SELF_TEST_STEP}\n        run: {BENCH_SELF_TEST_RUN}\n\n"
            f"      - name: {BENCH_LIVE_CHECK_STEP}\n        run: {BENCH_LIVE_CHECK_RUN}\n\n",
            f"      - name: {BENCH_LIVE_CHECK_STEP}\n        run: {BENCH_LIVE_CHECK_RUN}\n\n"
            f"      - name: {BENCH_SELF_TEST_STEP}\n        run: {BENCH_SELF_TEST_RUN}\n\n",
        )
        (reordered_check / WORKFLOW_REL).write_text(workflow, encoding="utf-8")
        expect_failure("reordered live bench check", reordered_check, BENCH_LIVE_CHECK_STEP)

        missing_marker = root / "missing-marker"
        write_sample_root(missing_marker)
        checker = (missing_marker / BENCH_CHECKER_REL).read_text(encoding="utf-8")
        checker = checker.replace("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\n", "")
        (missing_marker / BENCH_CHECKER_REL).write_text(checker, encoding="utf-8")
        expect_failure("missing bench marker", missing_marker, "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM")

    print("PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST=pass")
    print("PHASE1_BENCH_LIVE_CHECK_WORKFLOW_SELF_TEST_CASE_COUNT=5")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 1 bench workflow self-test is followed by the live repository check."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return
    if args.self_test:
        run_self_test()
        return

    validate_root(args.root)
    print("PHASE1_BENCH_LIVE_CHECK_WORKFLOW=pass")
    print(f"PHASE1_BENCH_LIVE_CHECK_WORKFLOW_REQUIRED_STEP_COUNT={len(REQUIRED_STEPS)}")
    print(f"PHASE1_BENCH_LIVE_CHECK_WORKFLOW_REQUIRED_MARKER_COUNT={len(BENCH_CHECKER_MARKERS)}")


if __name__ == "__main__":
    main()
