#!/usr/bin/env python3
"""Guard the live Phase 1 closure-validator workflow packet on current master."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
ROUTE_SUMMARY_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
BENCH_REL = Path("scripts/zigux/check-phase1-bench.py")
FIND_BIT_BENCH_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")
SHARED_REMINDER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")

REQUIRED_FILES = (
    WORKFLOW_REL,
    ROUTE_SUMMARY_REL,
    BENCH_REL,
    FIND_BIT_BENCH_REL,
    SHARED_REMINDER_REL,
    CLOSURE_VALIDATOR_REL,
)

WORKFLOW_PACKET_STEPS = (
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
    (
        "Self-test current Phase 1 closure validator",
        "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    ),
    (
        "Check current Phase 1 closure packet",
        "python3 scripts/zigux/validate-phase1-closure.py",
    ),
    (
        "Self-test current Phase 3 interop packet",
        "python3 scripts/zigux/validate_phase3_selftest.py",
    ),
    (
        "Check current Phase 3 interop packet",
        "python3 scripts/zigux/run-phase3-checks.py",
    ),
    (
        "Run current Phase 1 shared tests-root smoke",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
)

EXACT_MARKERS = {
    str(ROUTE_SUMMARY_REL): (
        '"""Guard the current Phase 1 route-summary packet across closure, Makefile, and workflow."""',
        'print("PHASE1_ROUTE_SUMMARY_COUNTS=pass")',
        'print("PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass")',
    ),
    str(BENCH_REL): (
        "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
        "def run_self_test() -> None:",
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
    ),
    str(FIND_BIT_BENCH_REL): (
        'description="Validate that the live find_bit helper still carries the current bench-adjacent edge anchors, including the landed andnot, clump-forward-skip, and tail-word next-skip paths."',
        'print("PHASE1_FIND_BIT_BENCH_ANCHORS=pass")',
        'print("PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass")',
    ),
    str(SHARED_REMINDER_REL): (
        '"""Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow."""',
        'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
        'print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")',
    ),
    str(CLOSURE_VALIDATOR_REL): (
        '(SHARED_REMINDER_CHECKER_REL, "phase1-shared-reminder-packet"),',
        'print("PHASE1_CLOSURE_SELF_TEST=pass")',
        'print("PHASE1_CLOSURE_VALIDATION=pass")',
    ),
}

FORBIDDEN_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase1-bench.py",
    "- name: Self-test Phase 1 route summary checker",
    "- name: Check Phase 1 route summary packet",
    "- name: Self-test Phase 1 shared reminder checker",
    "- name: Check Phase 1 shared reminder packet",
    "- name: Self-test Phase 1 closure validator",
    "- name: Check Phase 1 closure packet",
    "- name: Check Phase 3 interop packet",
    "- name: Run Phase 1 shared tests-root smoke",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_line_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent_line_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def workflow_step_block(step_name: str, run_command: str) -> str:
    return f"      - name: {step_name}\n        run: {run_command}"


def collect_workflow_failures(text: str) -> list[str]:
    failures: list[str] = []
    positions: list[int] = []
    step_names = [line[len("      - name: ") :] for line in text.splitlines() if line.startswith("      - name: ")]

    for step_name, run_command in WORKFLOW_PACKET_STEPS:
        block = workflow_step_block(step_name, run_command)
        count = text.count(block)
        if count != 1:
            failures.append(f"workflow_pair:{step_name}:expected=1:actual={count}")
            continue
        positions.append(text.index(block))

        name_count = sum(1 for current in step_names if current == step_name)
        if name_count != 1:
            failures.append(f"workflow_step_name:{step_name}:expected=1:actual={name_count}")

    if failures:
        return failures

    if positions != sorted(positions):
        failures.append("workflow_order:expected=strictly_increasing:actual=out_of_order")

    expected_chain = tuple(step_name for step_name, _ in WORKFLOW_PACKET_STEPS)
    width = len(expected_chain)
    if not any(tuple(step_names[idx : idx + width]) == expected_chain for idx in range(len(step_names) - width + 1)):
        failures.append("workflow_chain:expected=adjacent_closure_validator_packet:actual=split_or_interleaved")

    for marker in FORBIDDEN_WORKFLOW_LINES:
        failures.extend(require_absent_line_occurrence(text, f"{WORKFLOW_REL.as_posix()}:{marker}", marker))

    return failures


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    workflow_text = read_text(root, WORKFLOW_REL)
    failures.extend(collect_workflow_failures(workflow_text))

    for relative_path, markers in EXACT_MARKERS.items():
        text = read_text(root, Path(relative_path))
        for marker in markers:
            failures.extend(require_exact_occurrence(text, f"{relative_path}:{marker}", marker))

    return failures


def build_sample_repo(root: Path) -> None:
    write_text(
        root,
        WORKFLOW_REL,
        "\n".join(workflow_step_block(step_name, run_command) for step_name, run_command in WORKFLOW_PACKET_STEPS) + "\n",
    )
    for relative_path, markers in EXACT_MARKERS.items():
        write_text(root, Path(relative_path), "\n".join(markers) + "\n")


def remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def duplicate_marker(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def remove_workflow_step(root: Path, step_name: str, run_command: str) -> None:
    path = root / WORKFLOW_REL
    block = workflow_step_block(step_name, run_command)
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(block + "\n", "", 1), encoding="utf-8")


def duplicate_workflow_step(root: Path, step_name: str, run_command: str) -> None:
    path = root / WORKFLOW_REL
    block = workflow_step_block(step_name, run_command)
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(block, block + "\n" + block, 1), encoding="utf-8")


def reorder_workflow(root: Path) -> None:
    path = root / WORKFLOW_REL
    steps = list(WORKFLOW_PACKET_STEPS)
    steps[7], steps[8] = steps[8], steps[7]
    path.write_text(
        "\n".join(workflow_step_block(step_name, run_command) for step_name, run_command in steps) + "\n",
        encoding="utf-8",
    )


def append_forbidden_workflow_line(root: Path, marker: str) -> None:
    path = root / WORKFLOW_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text + "        " + marker + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[object, ...] | None]] = [("baseline", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", ("unlink", relative_path)))

    for relative_path, markers in EXACT_MARKERS.items():
        rel = Path(relative_path)
        for marker in markers:
            cases.append((f"missing_marker:{relative_path}", ("remove", rel, marker)))
            cases.append((f"duplicate_marker:{relative_path}", ("duplicate", rel, marker)))

    for step_name, run_command in WORKFLOW_PACKET_STEPS:
        cases.append((f"missing_workflow_step:{step_name}", ("remove_workflow", step_name, run_command)))
        cases.append((f"duplicate_workflow_step:{step_name}", ("duplicate_workflow", step_name, run_command)))

    cases.append(("workflow_reordered", ("reorder_workflow",)))
    for marker in FORBIDDEN_WORKFLOW_LINES:
        cases.append((f"forbidden_workflow_line:{marker}", ("forbidden_workflow", marker)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-validator-workflow-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if mutation is not None:
                kind = mutation[0]
                if kind == "unlink":
                    (root / mutation[1]).unlink()
                elif kind == "remove":
                    remove_marker(root, mutation[1], mutation[2])
                elif kind == "duplicate":
                    duplicate_marker(root, mutation[1], mutation[2])
                elif kind == "remove_workflow":
                    remove_workflow_step(root, mutation[1], mutation[2])
                elif kind == "duplicate_workflow":
                    duplicate_workflow_step(root, mutation[1], mutation[2])
                elif kind == "reorder_workflow":
                    reorder_workflow(root)
                elif kind == "forbidden_workflow":
                    append_forbidden_workflow_line(root, mutation[1])

            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-validator-workflow-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-validator-workflow-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_VALIDATOR_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument("--write-sample-root", help="write a current-like sample root")
    args = parser.parse_args()

    if args.write_sample_root:
        destination = Path(args.write_sample_root).resolve()
        build_sample_repo(destination)
        print(f"PHASE1_CLOSURE_VALIDATOR_WORKFLOW_PACKET_SAMPLE_ROOT={destination}")
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_CLOSURE_VALIDATOR_WORKFLOW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_VALIDATOR_WORKFLOW_PACKET=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_CLOSURE_VALIDATOR_WORKFLOW_PACKET_REQUIRED_STEP_COUNT={len(WORKFLOW_PACKET_STEPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
