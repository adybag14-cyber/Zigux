#!/usr/bin/env python3
"""Guard Lane 17's inherited Phase 12 workflow tail."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
NOTE_REL = Path("Documentation/zigux/phase1-workflow-viability.md")

PHASE12_TAIL_NOTE_LINE = (
    "- `PHASE1_WORKFLOW_PHASE10_PHASE12_TAIL=Self-test current Phase 10 bootstrap route checker,"
    "Check current Phase 10 bootstrap route,Validate Phase 10 checker-backed review packet,"
    "Run Phase 10 helper tests,Self-test current Phase 11 HVC cleanup current-head checker,"
    "Check current Phase 11 HVC cleanup current-head packet,Self-test current Phase 12 tail guard,"
    "Check current Phase 12 tail guard,Run current Phase 12 throughput-parity anchor`"
)
PHASE12_GUARD_LINE = "- `PHASE1_WORKFLOW_PHASE12_TAIL_GUARD=scripts/zigux/check-phase1-workflow-phase12-tail.py`"
PHASE12_ADJACENCY_LINE = (
    "- `PHASE1_WORKFLOW_PHASE12_TAIL_ADJACENCY=Check current Phase 11 HVC cleanup current-head packet,"
    "Self-test current Phase 12 tail guard,Check current Phase 12 tail guard,"
    "Run current Phase 12 throughput-parity anchor`"
)
PHASE12_SELFTEST_STEP = (
    "Self-test current Phase 12 tail guard",
    "python3 scripts/zigux/check-phase1-workflow-phase12-tail.py --self-test",
)
PHASE12_CHECK_STEP = (
    "Check current Phase 12 tail guard",
    "python3 scripts/zigux/check-phase1-workflow-phase12-tail.py",
)
PHASE12_ANCHOR_STEP = (
    "Run current Phase 12 throughput-parity anchor",
    "zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
)
PHASE12_CHAIN = (
    "Check current Phase 11 HVC cleanup current-head packet",
    PHASE12_SELFTEST_STEP[0],
    PHASE12_CHECK_STEP[0],
    PHASE12_ANCHOR_STEP[0],
)


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def count_exact_line(text: str, line: str) -> int:
    return sum(1 for current in text.splitlines() if current == line)


def require_once(text: str, label: str, line: str) -> list[str]:
    count = count_exact_line(text, line)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_step(workflow_text: str, step_name: str, run_command: str) -> list[str]:
    failures: list[str] = []
    failures.extend(require_once(workflow_text, f"workflow_step:{step_name}", f"      - name: {step_name}"))
    pair = f"      - name: {step_name}\n        run: {run_command}"
    pair_count = workflow_text.count(pair)
    if pair_count != 1:
        failures.append(f"workflow_run:{step_name}:expected=1:actual={pair_count}")
    return failures


def workflow_step_names(workflow_text: str) -> list[str]:
    prefix = "      - name: "
    return [line[len(prefix) :] for line in workflow_text.splitlines() if line.startswith(prefix)]


def require_adjacent_chain(workflow_text: str, step_names: tuple[str, ...]) -> list[str]:
    names = workflow_step_names(workflow_text)
    chain = list(step_names)
    max_start = len(names) - len(chain) + 1
    for index in range(max_start):
        if names[index : index + len(chain)] == chain:
            return []
    return [f"workflow_adjacent_chain:missing:{'->'.join(step_names)}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (WORKFLOW_REL, NOTE_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    note_text = load_text(root, NOTE_REL)

    failures.extend(require_once(note_text, "note", PHASE12_TAIL_NOTE_LINE))
    failures.extend(require_once(note_text, "note", PHASE12_GUARD_LINE))
    failures.extend(require_once(note_text, "note", PHASE12_ADJACENCY_LINE))
    failures.extend(require_step(workflow_text, *PHASE12_SELFTEST_STEP))
    failures.extend(require_step(workflow_text, *PHASE12_CHECK_STEP))
    failures.extend(require_step(workflow_text, *PHASE12_ANCHOR_STEP))
    failures.extend(require_adjacent_chain(workflow_text, PHASE12_CHAIN))
    return failures


def build_note_text() -> str:
    return "\n".join(
        (
            "# Phase 1 Workflow Viability",
            "",
            PHASE12_TAIL_NOTE_LINE,
            PHASE12_GUARD_LINE,
            PHASE12_ADJACENCY_LINE,
            "",
        )
    )


def build_workflow_text() -> str:
    return "\n".join(
        (
            "name: zigux-bootstrap",
            "jobs:",
            "  bootstrap:",
            "    runs-on: ubuntu-latest",
            "    steps:",
            "      - name: Check current Phase 11 HVC cleanup current-head packet",
            "        run: python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
            f"      - name: {PHASE12_SELFTEST_STEP[0]}",
            f"        run: {PHASE12_SELFTEST_STEP[1]}",
            f"      - name: {PHASE12_CHECK_STEP[0]}",
            f"        run: {PHASE12_CHECK_STEP[1]}",
            f"      - name: {PHASE12_ANCHOR_STEP[0]}",
            f"        run: {PHASE12_ANCHOR_STEP[1]}",
            "",
        )
    )


def build_sample_repo(root: Path) -> None:
    write_file(root, NOTE_REL, build_note_text())
    write_file(root, WORKFLOW_REL, build_workflow_text())


def rewrite_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise AssertionError(f"missing sample text: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-workflow-phase12-tail-") as tmpdir:
        root = Path(tmpdir)

        build_sample_repo(root)
        if collect_failures(root):
            print("self-test:unexpected_failures")
            return 1
        case_count += 1

        note_text = load_text(root, NOTE_REL)
        write_file(root, NOTE_REL, rewrite_once(note_text, PHASE12_TAIL_NOTE_LINE + "\n"))
        failures = collect_failures(root)
        if "note:expected=1:actual=0" not in failures:
            print("self-test:missing_phase12_tail_note")
            return 1
        case_count += 1
        build_sample_repo(root)

        note_text = load_text(root, NOTE_REL)
        write_file(root, NOTE_REL, rewrite_once(note_text, PHASE12_GUARD_LINE + "\n"))
        failures = collect_failures(root)
        if "note:expected=1:actual=0" not in failures:
            print("self-test:missing_phase12_guard_line")
            return 1
        case_count += 1
        build_sample_repo(root)

        note_text = load_text(root, NOTE_REL)
        write_file(root, NOTE_REL, rewrite_once(note_text, PHASE12_ADJACENCY_LINE + "\n"))
        failures = collect_failures(root)
        if "note:expected=1:actual=0" not in failures:
            print("self-test:missing_phase12_adjacency_line")
            return 1
        case_count += 1
        build_sample_repo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, f"      - name: {PHASE12_SELFTEST_STEP[0]}\n"))
        failures = collect_failures(root)
        if f"workflow_step:{PHASE12_SELFTEST_STEP[0]}:expected=1:actual=0" not in failures:
            print("self-test:missing_phase12_selftest")
            return 1
        case_count += 1
        build_sample_repo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, f"      - name: {PHASE12_CHECK_STEP[0]}\n"))
        failures = collect_failures(root)
        if f"workflow_step:{PHASE12_CHECK_STEP[0]}:expected=1:actual=0" not in failures:
            print("self-test:missing_phase12_check")
            return 1
        case_count += 1
        build_sample_repo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        old = (
            "      - name: Check current Phase 11 HVC cleanup current-head packet\n"
            "        run: python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py\n"
            f"      - name: {PHASE12_SELFTEST_STEP[0]}\n"
            f"        run: {PHASE12_SELFTEST_STEP[1]}\n"
            f"      - name: {PHASE12_CHECK_STEP[0]}\n"
            f"        run: {PHASE12_CHECK_STEP[1]}\n"
            f"      - name: {PHASE12_ANCHOR_STEP[0]}\n"
            f"        run: {PHASE12_ANCHOR_STEP[1]}\n"
        )
        new = (
            "      - name: Check current Phase 11 HVC cleanup current-head packet\n"
            "        run: python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py\n"
            f"      - name: {PHASE12_ANCHOR_STEP[0]}\n"
            f"        run: {PHASE12_ANCHOR_STEP[1]}\n"
            f"      - name: {PHASE12_SELFTEST_STEP[0]}\n"
            f"        run: {PHASE12_SELFTEST_STEP[1]}\n"
            f"      - name: {PHASE12_CHECK_STEP[0]}\n"
            f"        run: {PHASE12_CHECK_STEP[1]}\n"
        )
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, old, new))
        failures = collect_failures(root)
        expected = f"workflow_adjacent_chain:missing:{'->'.join(PHASE12_CHAIN)}"
        if expected not in failures:
            print("self-test:phase12_chain_not_detected")
            return 1
        case_count += 1

    print("PHASE1_WORKFLOW_PHASE12_TAIL_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_PHASE12_TAIL_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root.resolve())
    if failures:
        for failure in failures:
            print(f"phase1-workflow-phase12-tail:{failure}")
        return 1

    print("phase1-workflow-phase12-tail:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
