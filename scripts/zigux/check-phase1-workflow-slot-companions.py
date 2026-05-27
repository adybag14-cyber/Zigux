#!/usr/bin/env python3
"""Guard the current Lane 17 workflow-slot companion packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
SLOT_CHECKER_REL = Path("scripts/zigux/check-phase1-workflow-slot.py")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")

WORKFLOW_REQUIRED_CHAIN = (
    "      - name: Check current Phase 1 shared reminder packet",
    "      - name: Self-test current Phase 1 workflow-slot checker",
    "      - name: Check current Phase 1 workflow-slot packet",
    "      - name: Self-test current Phase 1 closure validator",
    "      - name: Check current Phase 1 closure packet",
    "      - name: Self-test current Phase 3 interop packet",
)

WORKFLOW_REQUIRED_LINES = (
    "        run: python3 scripts/zigux/check-phase1-workflow-slot.py --self-test",
    "        run: python3 scripts/zigux/check-phase1-workflow-slot.py",
    "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "        run: python3 scripts/zigux/validate-phase1-closure.py",
    "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

SLOT_CHECKER_MARKERS = (
    'WORKFLOW_SLOT_SELF_TEST_STEP = "      - name: Self-test current Phase 1 workflow-slot checker"',
    'WORKFLOW_SLOT_CHECK_STEP = "      - name: Check current Phase 1 workflow-slot packet"',
    '"      - name: Check current Phase 1 shared reminder packet"',
    '"      - name: Self-test current Phase 1 closure validator"',
    '"      - name: Check current Phase 1 closure packet"',
    '"      - name: Self-test current Phase 3 interop packet"',
    '"      - name: Run current Phase 1 shared tests-root smoke"',
    '"      - name: Check current Phase 4 repo-reality warning packet"',
)

CLOSURE_NOTE_MARKERS = (
    "PHASE1_CURRENT_REMINDER_PACKET=",
    ".github/workflows/zigux-bootstrap.yml",
    "PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py",
    "PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

LANE_NOTE_MARKERS = (
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/phase1_host_tools_smoke.zig",
)

CHECKLIST_MARKERS = (
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)


def repo_root(path: str | None) -> Path:
    return Path(path).resolve() if path else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative: Path) -> str:
    return (root / relative).read_text(encoding="utf-8")


def write_text(root: Path, relative: Path, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_file(root: Path, relative: Path) -> list[str]:
    path = root / relative
    if not path.exists():
        return [f"missing_file:{relative.as_posix()}"]
    if not path.is_file():
        return [f"non_file_path:{relative.as_posix()}"]
    return []


def require_contains(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count >= 1 else [f"missing_marker:{label}:{marker}"]


def require_exact_line_count(text: str, line: str, expected: int = 1) -> list[str]:
    count = sum(1 for current in text.splitlines() if current == line)
    return [] if count == expected else [f"line_count:{line}:expected={expected}:actual={count}"]


def require_adjacent_chain(text: str, chain: tuple[str, ...]) -> list[str]:
    lines = [line for line in text.splitlines() if line.startswith("      - name: ")]
    span = len(chain)
    for index in range(len(lines) - span + 1):
        if tuple(lines[index : index + span]) == chain:
            return []
    return [f"adjacent_chain_missing:{' -> '.join(chain)}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative in (
        WORKFLOW_REL,
        SLOT_CHECKER_REL,
        CLOSURE_NOTE_REL,
        LANE_NOTE_REL,
        CHECKLIST_REL,
    ):
        failures.extend(require_file(root, relative))
    if failures:
        return failures

    workflow_text = read_text(root, WORKFLOW_REL)
    slot_checker_text = read_text(root, SLOT_CHECKER_REL)
    closure_note_text = read_text(root, CLOSURE_NOTE_REL)
    lane_note_text = read_text(root, LANE_NOTE_REL)
    checklist_text = read_text(root, CHECKLIST_REL)

    failures.extend(require_adjacent_chain(workflow_text, WORKFLOW_REQUIRED_CHAIN))
    for line in WORKFLOW_REQUIRED_LINES:
        failures.extend(require_exact_line_count(workflow_text, line))

    for marker in SLOT_CHECKER_MARKERS:
        failures.extend(require_contains(slot_checker_text, SLOT_CHECKER_REL.as_posix(), marker))
    for marker in CLOSURE_NOTE_MARKERS:
        failures.extend(require_contains(closure_note_text, CLOSURE_NOTE_REL.as_posix(), marker))
    for marker in LANE_NOTE_MARKERS:
        failures.extend(require_contains(lane_note_text, LANE_NOTE_REL.as_posix(), marker))
    for marker in CHECKLIST_MARKERS:
        failures.extend(require_contains(checklist_text, CHECKLIST_REL.as_posix(), marker))

    return failures


def build_sample_root(root: Path) -> None:
    workflow_lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
        "      - name: Self-test current Phase 1 shared reminder checker",
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "      - name: Check current Phase 1 shared reminder packet",
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "      - name: Self-test current Phase 1 workflow-slot checker",
        "        run: python3 scripts/zigux/check-phase1-workflow-slot.py --self-test",
        "      - name: Check current Phase 1 workflow-slot packet",
        "        run: python3 scripts/zigux/check-phase1-workflow-slot.py",
        "      - name: Self-test current Phase 1 closure validator",
        "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "      - name: Check current Phase 1 closure packet",
        "        run: python3 scripts/zigux/validate-phase1-closure.py",
        "      - name: Self-test current Phase 3 interop packet",
        "        run: python3 scripts/zigux/validate_phase3_selftest.py",
        "      - name: Check current Phase 3 interop packet",
        "        run: python3 scripts/zigux/run-phase3-checks.py",
        "      - name: Run current Phase 1 shared tests-root smoke",
        "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
        "      - name: Check current Phase 4 repo-reality warning packet",
        "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py",
    ]
    write_text(root, WORKFLOW_REL, "\n".join(workflow_lines) + "\n")

    slot_checker_text = """#!/usr/bin/env python3
WORKFLOW_SLOT_SELF_TEST_STEP = \"      - name: Self-test current Phase 1 workflow-slot checker\"
WORKFLOW_SLOT_CHECK_STEP = \"      - name: Check current Phase 1 workflow-slot packet\"
ORDERED = (
    \"      - name: Check current Phase 1 shared reminder packet\",
    \"      - name: Self-test current Phase 1 workflow-slot checker\",
    \"      - name: Check current Phase 1 workflow-slot packet\",
    \"      - name: Self-test current Phase 1 closure validator\",
    \"      - name: Check current Phase 1 closure packet\",
    \"      - name: Self-test current Phase 3 interop packet\",
    \"      - name: Run current Phase 1 shared tests-root smoke\",
    \"      - name: Check current Phase 4 repo-reality warning packet\",
)
"""
    write_text(root, SLOT_CHECKER_REL, slot_checker_text)

    closure_note = """# Phase 1 Closure
- PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,.github/workflows/zigux-bootstrap.yml
- PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py
- PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py
- PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig
"""
    write_text(root, CLOSURE_NOTE_REL, closure_note)

    lane_note = """# Phase 1 Host-Helper Lane Sequencing
scripts/zigux/check-phase1-shared-reminder-packet.py
scripts/zigux/check-phase1-direct-owner-markers.py
scripts/zigux/check-phase1-route-summary-counts.py
scripts/zigux/validate-phase1-closure.py
zigux/tests/phase1_host_tools_smoke.zig
"""
    write_text(root, LANE_NOTE_REL, lane_note)

    checklist = """# Zigux Review Checklist
scripts/zigux/check-phase1-shared-reminder-packet.py
scripts/zigux/validate-phase1-closure.py
scripts/zigux/check-phase1-route-summary-counts.py
zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig
"""
    write_text(root, CHECKLIST_REL, checklist)


def remove_once(path: Path, needle: str) -> None:
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        raise ValueError(f"missing needle: {needle}")
    path.write_text(text.replace(needle, "", 1), encoding="utf-8")


def run_self_test() -> int:
    cases = (
        ("success", None),
        ("missing_slot_checker", ("delete", SLOT_CHECKER_REL)),
        ("missing_workflow_slot_step", ("remove", WORKFLOW_REL, "      - name: Check current Phase 1 workflow-slot packet\n")),
        ("broken_slot_adjacency", ("insert", WORKFLOW_REL, "      - name: Lane drift spacer\n        run: python3 drift.py\n", "      - name: Self-test current Phase 1 workflow-slot checker\n")),
        ("missing_closure_route_summary", ("remove", CLOSURE_NOTE_REL, "PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py")),
        ("missing_lane_note_marker", ("remove", LANE_NOTE_REL, "scripts/zigux/check-phase1-direct-owner-markers.py")),
        ("missing_checklist_smoke_route", ("remove", CHECKLIST_REL, "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig")),
    )

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-workflow-slot-companions-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            if mutation is not None:
                kind = mutation[0]
                if kind == "delete":
                    (root / mutation[1]).unlink()
                elif kind == "remove":
                    remove_once(root / mutation[1], mutation[2])
                elif kind == "insert":
                    path = root / mutation[1]
                    text = path.read_text(encoding="utf-8")
                    anchor = mutation[3]
                    if anchor not in text:
                        raise ValueError(f"missing anchor: {anchor}")
                    text = text.replace(anchor, mutation[2] + anchor, 1)
                    path.write_text(text, encoding="utf-8")
            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("PHASE1_WORKFLOW_SLOT_COMPANIONS_SELF_TEST=fail")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"PHASE1_WORKFLOW_SLOT_COMPANIONS_SELF_TEST_CASE_FAILED={name}")
                return 1

    print("PHASE1_WORKFLOW_SLOT_COMPANIONS_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_SLOT_COMPANIONS_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument("--write-sample-root", help="write a current-like sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        root = Path(args.write_sample_root).resolve()
        if root.exists():
            shutil.rmtree(root)
        root.mkdir(parents=True, exist_ok=True)
        build_sample_root(root)
        print(f"phase1-workflow-slot-companions:sample-root-written:{root}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_WORKFLOW_SLOT_COMPANIONS=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_WORKFLOW_SLOT_COMPANIONS=pass")
    print(f"PHASE1_WORKFLOW_SLOT_COMPANION_MARKER_COUNT={len(SLOT_CHECKER_MARKERS) + len(CLOSURE_NOTE_MARKERS) + len(LANE_NOTE_MARKERS) + len(CHECKLIST_MARKERS)}")
    print(f"PHASE1_WORKFLOW_SLOT_COMPANION_WORKFLOW_LINE_COUNT={len(WORKFLOW_REQUIRED_CHAIN) + len(WORKFLOW_REQUIRED_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
