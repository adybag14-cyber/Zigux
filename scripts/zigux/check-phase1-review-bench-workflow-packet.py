#!/usr/bin/env python3
"""Validate the Phase 1 review-to-bench workflow packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) >= 3 else HERE.parent
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = [
    WORKFLOW_REL,
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-find-bit-review-packet.py"),
    Path("scripts/zigux/check-phase1-bitmap-direct-anchors.py"),
    Path("scripts/zigux/check-phase1-rbtree-review-packet.py"),
    Path("scripts/zigux/check-phase1-route-summary-counts.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py"),
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
]

WORKFLOW_PACKET = [
    (
        "Self-test current Phase 1 string review checker",
        "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    ),
    (
        "Check current Phase 1 string review packet",
        "python3 scripts/zigux/check-phase1-string-review-packet.py",
    ),
    (
        "Self-test current Phase 1 find-bit review checker",
        "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    ),
    (
        "Check current Phase 1 find-bit review packet",
        "python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    ),
    (
        "Self-test current Phase 1 bitmap direct-anchor checker",
        "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    ),
    (
        "Check current Phase 1 bitmap direct-anchor packet",
        "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    ),
    (
        "Self-test current Phase 1 rbtree review checker",
        "python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
    ),
    (
        "Check current Phase 1 rbtree review packet",
        "python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    ),
    (
        "Self-test current Phase 1 route summary checker",
        "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    ),
    (
        "Check current Phase 1 route summary packet",
        "python3 scripts/zigux/check-phase1-route-summary-counts.py",
    ),
    (
        "Self-test current Phase 1 bench checker",
        "python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    (
        "Self-test current Phase 1 find-bit bench anchor checker",
        "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    ),
    (
        "Check current Phase 1 find-bit bench anchor packet",
        "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    ),
    (
        "Self-test current Phase 1 shared reminder checker",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    ),
    (
        "Check current Phase 1 shared reminder packet",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    ),
]

FORBIDDEN_WORKFLOW_LINES = [
    "python3 scripts/zigux/check-phase1-bench.py",
    "zig build phase1-bench",
    "make -C zigux phase1-bench",
]


def repo_root(explicit_root: str | None) -> Path:
    return Path(explicit_root).resolve() if explicit_root else DEFAULT_ROOT


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def expected_step_text() -> str:
    return "\n".join(f"      - name: {name}\n        run: {run}" for name, run in WORKFLOW_PACKET) + "\n"


def collect_missing_files(root: Path) -> list[str]:
    return [rel.as_posix() for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_workflow_errors(root: Path) -> list[str]:
    workflow = read_text(root, WORKFLOW_REL)
    workflow_lines = workflow.splitlines()
    errors: list[str] = []
    cursor = 0

    for name, run in WORKFLOW_PACKET:
        name_line = f"      - name: {name}"
        run_line = f"        run: {run}"
        name_count = workflow_lines.count(name_line)
        run_count = workflow_lines.count(run_line)
        if name_count != 1:
            errors.append(f"workflow:name-count:{name}:{name_count}")
        if run_count != 1:
            errors.append(f"workflow:run-count:{run}:{run_count}")

        name_index = workflow.find(name_line, cursor)
        if name_index == -1:
            errors.append(f"workflow:missing-ordered-name:{name}")
            continue
        run_index = workflow.find(run_line, name_index)
        if run_index == -1:
            errors.append(f"workflow:missing-run-after-name:{name}")
            continue
        cursor = run_index + len(run_line)

    packet = expected_step_text()
    if packet not in workflow:
        errors.append("workflow:review-to-bench-packet-not-contiguous")

    for line in FORBIDDEN_WORKFLOW_LINES:
        if f"        run: {line}" in workflow_lines:
            errors.append(f"workflow:forbidden-direct-bench-run:{line}")

    return errors


def write_sample_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel == WORKFLOW_REL:
            path.write_text(expected_step_text(), encoding="utf-8")
        else:
            path.write_text("# fixture\n", encoding="utf-8")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_review_bench_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert collect_missing_files(root) == []
        assert collect_workflow_errors(root) == []

        workflow = root / WORKFLOW_REL
        text = workflow.read_text(encoding="utf-8")
        workflow.write_text(text.replace("Check current Phase 1 route summary packet", "Check stale route summary packet"), encoding="utf-8")
        assert any("route summary" in item for item in collect_workflow_errors(root))
        case_count += 1
        write_sample_root(root)

        workflow.write_text(text.replace(
            "      - name: Self-test current Phase 1 shared reminder checker\n",
            "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n"
            "      - name: Self-test current Phase 1 shared reminder checker\n",
        ), encoding="utf-8")
        assert "workflow:review-to-bench-packet-not-contiguous" in collect_workflow_errors(root)
        case_count += 1
        write_sample_root(root)

        workflow.write_text(text + "        run: python3 scripts/zigux/check-phase1-bench.py\n", encoding="utf-8")
        assert any("forbidden-direct-bench-run" in item for item in collect_workflow_errors(root))
        case_count += 1
        write_sample_root(root)

        (root / "scripts/zigux/check-phase1-rbtree-review-packet.py").unlink()
        assert collect_missing_files(root) == ["scripts/zigux/check-phase1-rbtree-review-packet.py"]
        case_count += 1

    print("PHASE1_REVIEW_BENCH_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_REVIEW_BENCH_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 1 review-to-bench workflow packet.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests.")
    parser.add_argument("--write-sample-root", help="Write a minimal passing fixture tree.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_REVIEW_BENCH_WORKFLOW_PACKET=fail")
        print("MISSING_PHASE1_REVIEW_BENCH_WORKFLOW_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_REVIEW_BENCH_WORKFLOW_PACKET_FILES_END")
        return 1

    workflow_errors = collect_workflow_errors(root)
    if workflow_errors:
        print("PHASE1_REVIEW_BENCH_WORKFLOW_PACKET=fail")
        print("PHASE1_REVIEW_BENCH_WORKFLOW_PACKET_ERRORS_START")
        for item in workflow_errors:
            print(item)
        print("PHASE1_REVIEW_BENCH_WORKFLOW_PACKET_ERRORS_END")
        return 1

    print("PHASE1_REVIEW_BENCH_WORKFLOW_PACKET=pass")
    print(f"PHASE1_REVIEW_BENCH_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_REVIEW_BENCH_WORKFLOW_PACKET_REQUIRED_STEP_COUNT={len(WORKFLOW_PACKET)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
