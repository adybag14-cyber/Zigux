#!/usr/bin/env python3
"""Guard the current Phase 1 workflow slot inside zigux-bootstrap."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

ORDERED_STEPS = (
    "      - name: Run current Phase 2 validate make route",
    "      - name: Validate current Phase 2 tool packet",
    "      - name: Self-test current Phase 1 direct-owner checker",
    "      - name: Check current Phase 1 direct-owner markers",
    "      - name: Self-test current Phase 1 direct-anchor manifest gate",
    "      - name: Check current Phase 1 direct-anchor manifest gate",
    "      - name: Self-test current Phase 1 string review checker",
    "      - name: Check current Phase 1 string review packet",
    "      - name: Self-test current Phase 1 find-bit review checker",
    "      - name: Check current Phase 1 find-bit review packet",
    "      - name: Self-test current Phase 1 route summary checker",
    "      - name: Check current Phase 1 route summary packet",
    "      - name: Self-test current Phase 1 workflow slot checker",
    "      - name: Check current Phase 1 workflow slot packet",
    "      - name: Self-test current Phase 1 bench checker",
    "      - name: Self-test current Phase 1 find-bit bench anchor checker",
    "      - name: Check current Phase 1 find-bit bench anchor packet",
    "      - name: Self-test current Phase 1 shared reminder checker",
    "      - name: Check current Phase 1 shared reminder packet",
    "      - name: Self-test current Phase 1 closure validator",
    "      - name: Check current Phase 1 closure packet",
    "      - name: Self-test current Phase 3 interop packet",
    "      - name: Check current Phase 3 interop packet",
    "      - name: Run current Phase 3 shared tests-root packet",
    "      - name: Run current Phase 1 shared tests-root smoke",
    "      - name: Self-test current Phase 4 repo-reality warning checker",
    "      - name: Check current Phase 4 repo-reality warning packet",
)

EXACT_RUN_LINES = (
    "        run: python3 scripts/zigux/validate-phase2.py",
    "        run: python3 scripts/zigux/check-phase1-workflow-slot.py --self-test",
    "        run: python3 scripts/zigux/check-phase1-workflow-slot.py",
    "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py",
)

FORBIDDEN_LINES = (
    "      - name: Self-test current Phase 1 workflow viability checker",
    "      - name: Check current Phase 1 workflow viability packet",
    "      - name: Self-test current Phase 1 workflow preflight checker",
    "      - name: Check current Phase 1 workflow preflight packet",
    "        run: python3 scripts/zigux/check-phase1-bench.py",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_workflow(root: Path) -> str:
    return (root / WORKFLOW_REL).read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    workflow_path = root / WORKFLOW_REL
    if not workflow_path.exists():
        return [f"missing_file:{WORKFLOW_REL.as_posix()}"]

    text = read_workflow(root)
    lines = text.splitlines()
    failures: list[str] = []

    last_index = -1
    for step in ORDERED_STEPS:
        indexes = [idx for idx, line in enumerate(lines) if line == step]
        if len(indexes) != 1:
            failures.append(f"marker_count:{step}:expected=1:actual={len(indexes)}")
            continue
        if indexes[0] <= last_index:
            failures.append(f"order:{step}:index={indexes[0]}:previous={last_index}")
        last_index = indexes[0]

    for line in EXACT_RUN_LINES:
        count = sum(1 for current in lines if current == line)
        if count != 1:
            failures.append(f"run_count:{line}:expected=1:actual={count}")

    for line in FORBIDDEN_LINES:
        count = sum(1 for current in lines if current == line)
        if count != 0:
            failures.append(f"forbidden:{line}:actual={count}")

    return failures


def write_text(root: Path, relative: Path, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    sample_lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
        "      - name: Run current Phase 2 validate make route",
        "        run: make -C zigux phase2-validate",
        "      - name: Validate current Phase 2 tool packet",
        "        run: python3 scripts/zigux/validate-phase2.py",
        "      - name: Self-test current Phase 1 direct-owner checker",
        "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "      - name: Check current Phase 1 direct-owner markers",
        "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
        "      - name: Self-test current Phase 1 direct-anchor manifest gate",
        "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
        "      - name: Check current Phase 1 direct-anchor manifest gate",
        "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "      - name: Self-test current Phase 1 string review checker",
        "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
        "      - name: Check current Phase 1 string review packet",
        "        run: python3 scripts/zigux/check-phase1-string-review-packet.py",
        "      - name: Self-test current Phase 1 find-bit review checker",
        "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
        "      - name: Check current Phase 1 find-bit review packet",
        "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
        "      - name: Self-test current Phase 1 route summary checker",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "      - name: Check current Phase 1 route summary packet",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "      - name: Self-test current Phase 1 workflow slot checker",
        "        run: python3 scripts/zigux/check-phase1-workflow-slot.py --self-test",
        "      - name: Check current Phase 1 workflow slot packet",
        "        run: python3 scripts/zigux/check-phase1-workflow-slot.py",
        "      - name: Self-test current Phase 1 bench checker",
        "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "      - name: Self-test current Phase 1 find-bit bench anchor checker",
        "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
        "      - name: Check current Phase 1 find-bit bench anchor packet",
        "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
        "      - name: Self-test current Phase 1 shared reminder checker",
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "      - name: Check current Phase 1 shared reminder packet",
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "      - name: Self-test current Phase 1 closure validator",
        "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "      - name: Check current Phase 1 closure packet",
        "        run: python3 scripts/zigux/validate-phase1-closure.py",
        "      - name: Self-test current Phase 3 interop packet",
        "        run: python3 scripts/zigux/validate_phase3_selftest.py",
        "      - name: Check current Phase 3 interop packet",
        "        run: python3 scripts/zigux/run-phase3-checks.py",
        "      - name: Run current Phase 3 shared tests-root packet",
        "        run: zig build phase3-test --build-file zigux/tests/build.zig",
        "      - name: Run current Phase 1 shared tests-root smoke",
        "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
        "      - name: Self-test current Phase 4 repo-reality warning checker",
        "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
        "      - name: Check current Phase 4 repo-reality warning packet",
        "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py",
    ]
    write_text(root, WORKFLOW_REL, "\n".join(sample_lines) + "\n")


def mutate_missing_line(root: Path, target: str) -> None:
    path = root / WORKFLOW_REL
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line == target:
            del lines[index]
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(f"missing target line: {target}")


def mutate_duplicate_line(root: Path, target: str) -> None:
    path = root / WORKFLOW_REL
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line == target:
            lines.insert(index + 1, target)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(f"missing target line: {target}")


def mutate_swap_lines(root: Path, first: str, second: str) -> None:
    path = root / WORKFLOW_REL
    lines = path.read_text(encoding="utf-8").splitlines()
    first_index = lines.index(first)
    second_index = lines.index(second)
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def mutate_add_forbidden(root: Path, target: str) -> None:
    path = root / WORKFLOW_REL
    lines = path.read_text(encoding="utf-8").splitlines()
    lines.append(target)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, ...] | None]] = [
        ("success", None),
        ("missing_workflow", ("missing_file",)),
        ("missing_phase2_validate_packet", ("remove", ORDERED_STEPS[1])),
        ("missing_workflow_slot_self_test", ("remove", ORDERED_STEPS[12])),
        ("missing_workflow_slot_packet", ("remove", ORDERED_STEPS[13])),
        ("missing_phase1_smoke_step", ("remove", ORDERED_STEPS[-3])),
        ("missing_phase4_repo_reality_packet", ("remove", ORDERED_STEPS[-1])),
        ("duplicate_route_summary_step", ("duplicate", ORDERED_STEPS[11])),
        ("duplicate_workflow_slot_packet", ("duplicate", ORDERED_STEPS[13])),
        ("phase3_smoke_order_swap", ("swap", ORDERED_STEPS[23], ORDERED_STEPS[24])),
        ("forbidden_old_checker_step", ("forbidden", FORBIDDEN_LINES[0])),
        ("forbidden_bench_run_line", ("forbidden", FORBIDDEN_LINES[-1])),
    ]

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-workflow-slot-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            if mutation is not None:
                kind = mutation[0]
                if kind == "missing_file":
                    (root / WORKFLOW_REL).unlink()
                elif kind == "remove":
                    mutate_missing_line(root, mutation[1])
                elif kind == "duplicate":
                    mutate_duplicate_line(root, mutation[1])
                elif kind == "swap":
                    mutate_swap_lines(root, mutation[1], mutation[2])
                elif kind == "forbidden":
                    mutate_add_forbidden(root, mutation[1])
            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("PHASE1_WORKFLOW_SLOT_SELF_TEST=fail")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"PHASE1_WORKFLOW_SLOT_SELF_TEST_CASE_FAILED={name}")
                return 1

    print("PHASE1_WORKFLOW_SLOT_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_SLOT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample root for manual replay validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        root = Path(args.write_sample_root).resolve()
        build_sample_root(root)
        print(f"phase1-workflow-slot:sample-root-written:{root}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_WORKFLOW_SLOT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_WORKFLOW_SLOT=pass")
    print(f"PHASE1_WORKFLOW_SLOT_REQUIRED_STEP_COUNT={len(ORDERED_STEPS)}")
    print(f"PHASE1_WORKFLOW_SLOT_REQUIRED_RUN_LINE_COUNT={len(EXACT_RUN_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
