#!/usr/bin/env python3
"""Guard the current Phase 1 direct-owner workflow packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
TESTS_README_REL = Path("zigux/tests/README.md")
DIRECT_OWNER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
DIRECT_ANCHOR_REL = Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")
STRING_REVIEW_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
FIND_BIT_REVIEW_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")

REQUIRED_FILES = (
    WORKFLOW_REL,
    CLOSURE_REL,
    TESTS_README_REL,
    DIRECT_OWNER_REL,
    DIRECT_ANCHOR_REL,
    STRING_REVIEW_REL,
    FIND_BIT_REVIEW_REL,
)

WORKFLOW_PACKET_STEPS = (
    (
        "Self-test current Phase 1 direct-owner checker",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    ),
    (
        "Check current Phase 1 direct-owner markers",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    ),
    (
        "Self-test current Phase 1 direct-anchor manifest gate",
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    ),
    (
        "Check current Phase 1 direct-anchor manifest gate",
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    ),
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
)

CLOSURE_MARKERS = (
    "- `scripts/zigux/check-phase1-direct-owner-markers.py`",
    "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
    "- `scripts/zigux/check-phase1-string-review-packet.py`",
    "- `PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",
    "- `PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py exact-checks helper-local string anchors plus the committed replaceChar and current string fixture packet across the helper, closure note, lane note, manifest, and fixture`",
)

TESTS_README_MARKERS = (
    "- `scripts/zigux/check-phase1-direct-owner-markers.py`",
    "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
    "- `scripts/zigux/check-phase1-string-review-packet.py`",
    "- `scripts/zigux/check-phase1-bench.py`",
    "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
)

DIRECT_OWNER_MARKERS = (
    "\"\"\"Guard the Phase 1 direct-owner marker packet against lane-note and helper drift.\"\"\"",
    'print("PHASE1_DIRECT_OWNER_MARKERS_SELF_TEST=pass")',
    'print("PHASE1_DIRECT_OWNER_MARKERS=pass")',
)

DIRECT_ANCHOR_MARKERS = (
    'description="Validate the Phase 1 direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string."',
    'print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass")',
    'print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass")',
)

STRING_REVIEW_MARKERS = (
    "\"\"\"Guard the Phase 1 string helper review packet against helper, manifest, fixture, and lane-note drift.\"\"\"",
    'print("PHASE1_STRING_REVIEW_PACKET_SELF_TEST=pass")',
    'print("phase1-string-review-packet:ok")',
)

FIND_BIT_REVIEW_MARKERS = (
    "\"\"\"Guard the Phase 1 find_bit review packet against helper, fixture, smoke, and lane drift.\"\"\"",
    'print("PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=pass")',
    'print("phase1-find-bit-review-packet:ok")',
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
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{marker}"]


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
        failures.append("workflow_chain:expected=adjacent_direct_owner_packet:actual=split_or_interleaved")

    return failures


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    workflow_text = read_text(root, WORKFLOW_REL)
    failures.extend(collect_workflow_failures(workflow_text))

    closure_text = read_text(root, CLOSURE_REL)
    for marker in CLOSURE_MARKERS:
        failures.extend(require_exact_occurrence(closure_text, f"{CLOSURE_REL.as_posix()}:{marker}", marker))

    tests_readme_text = read_text(root, TESTS_README_REL)
    for marker in TESTS_README_MARKERS:
        failures.extend(require_exact_occurrence(tests_readme_text, f"{TESTS_README_REL.as_posix()}:{marker}", marker))

    direct_owner_text = read_text(root, DIRECT_OWNER_REL)
    for marker in DIRECT_OWNER_MARKERS:
        failures.extend(require_exact_occurrence(direct_owner_text, f"{DIRECT_OWNER_REL.as_posix()}:{marker}", marker))

    direct_anchor_text = read_text(root, DIRECT_ANCHOR_REL)
    for marker in DIRECT_ANCHOR_MARKERS:
        failures.extend(require_exact_occurrence(direct_anchor_text, f"{DIRECT_ANCHOR_REL.as_posix()}:{marker}", marker))

    string_review_text = read_text(root, STRING_REVIEW_REL)
    for marker in STRING_REVIEW_MARKERS:
        failures.extend(require_exact_occurrence(string_review_text, f"{STRING_REVIEW_REL.as_posix()}:{marker}", marker))

    find_bit_review_text = read_text(root, FIND_BIT_REVIEW_REL)
    for marker in FIND_BIT_REVIEW_MARKERS:
        failures.extend(require_exact_occurrence(find_bit_review_text, f"{FIND_BIT_REVIEW_REL.as_posix()}:{marker}", marker))

    return failures


def build_sample_repo(root: Path) -> None:
    write_text(
        root,
        WORKFLOW_REL,
        "\n".join(workflow_step_block(step_name, run_command) for step_name, run_command in WORKFLOW_PACKET_STEPS) + "\n",
    )
    write_text(root, CLOSURE_REL, "\n".join(CLOSURE_MARKERS) + "\n")
    write_text(root, TESTS_README_REL, "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root, DIRECT_OWNER_REL, "\n".join(DIRECT_OWNER_MARKERS) + "\n")
    write_text(root, DIRECT_ANCHOR_REL, "\n".join(DIRECT_ANCHOR_MARKERS) + "\n")
    write_text(root, STRING_REVIEW_REL, "\n".join(STRING_REVIEW_MARKERS) + "\n")
    write_text(root, FIND_BIT_REVIEW_REL, "\n".join(FIND_BIT_REVIEW_MARKERS) + "\n")


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
    steps[2], steps[4] = steps[4], steps[2]
    path.write_text("\n".join(workflow_step_block(step_name, run_command) for step_name, run_command in steps) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[object, ...] | None]] = [("baseline", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", ("unlink", relative_path)))

    for relative_path, markers in (
        (CLOSURE_REL, CLOSURE_MARKERS),
        (TESTS_README_REL, TESTS_README_MARKERS),
        (DIRECT_OWNER_REL, DIRECT_OWNER_MARKERS),
        (DIRECT_ANCHOR_REL, DIRECT_ANCHOR_MARKERS),
        (STRING_REVIEW_REL, STRING_REVIEW_MARKERS),
        (FIND_BIT_REVIEW_REL, FIND_BIT_REVIEW_MARKERS),
    ):
        for marker in markers:
            cases.append((f"missing_marker:{relative_path.as_posix()}", ("remove", relative_path, marker)))
            cases.append((f"duplicate_marker:{relative_path.as_posix()}", ("duplicate", relative_path, marker)))

    for step_name, run_command in WORKFLOW_PACKET_STEPS:
        cases.append((f"missing_workflow_step:{step_name}", ("remove_workflow", step_name, run_command)))
        cases.append((f"duplicate_workflow_step:{step_name}", ("duplicate_workflow", step_name, run_command)))

    cases.append(("workflow_reordered", ("reorder_workflow",)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-direct-owner-workflow-packet-") as tmpdir:
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

            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-direct-owner-workflow-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-direct-owner-workflow-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_DIRECT_OWNER_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_DIRECT_OWNER_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
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
        print(f"PHASE1_DIRECT_OWNER_WORKFLOW_PACKET_SAMPLE_ROOT={destination}")
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_DIRECT_OWNER_WORKFLOW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_DIRECT_OWNER_WORKFLOW_PACKET=pass")
    print(f"PHASE1_DIRECT_OWNER_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_DIRECT_OWNER_WORKFLOW_PACKET_REQUIRED_STEP_COUNT={len(WORKFLOW_PACKET_STEPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
