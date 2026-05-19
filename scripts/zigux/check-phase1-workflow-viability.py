#!/usr/bin/env python3
"""Guard the current Lane 17 Phase 1 workflow-viability packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
NOTE_REL = Path("Documentation/zigux/phase1-workflow-viability.md")

PREFLIGHT_STEP = (
    "Preflight current Phase 1 workflow viability checker",
    "python3 scripts/zigux/check-phase1-workflow-viability.py --self-test",
)
PREFLIGHT_ORDER = (
    "Setup Python",
    "Preflight current Phase 1 workflow viability checker",
    "Setup pinned Zig toolchain",
)
PREFLIGHT_NOTE_LINE = (
    "- `PHASE1_WORKFLOW_PREFLIGHT=Preflight current Phase 1 workflow viability checker after Setup Python and before Setup pinned Zig toolchain`"
)
PHASE2_TAIL_NOTE_LINE = (
    "- `PHASE1_WORKFLOW_PHASE2_TAIL=Self-test current Phase 2 toolchain pin-scope checker,Check current Phase 2 toolchain pin-scope packet,Run current Phase 2 toolchain make route,Self-test current Phase 2 required-make-routes checker,Check current Phase 2 required-make-routes packet,Self-test current Phase 2 shared reminder checker,Check current Phase 2 shared reminder packet,Validate current Phase 2 tool packet`"
)
PHASE1_PRE_BUFFER_NOTE_LINE = (
    "- `PHASE1_WORKFLOW_PHASE1_PRE_BUFFER=Self-test current Phase 1 direct-owner checker,Check current Phase 1 direct-owner markers,Self-test current Phase 1 string review checker,Check current Phase 1 string review packet,Self-test current Phase 1 bench checker,Self-test current Phase 1 shared reminder checker,Check current Phase 1 shared reminder packet`"
)
PHASE8_BUFFER_NOTE_LINE = (
    "- `PHASE1_WORKFLOW_PHASE8_BUFFER=Validate Phase 8 tooling routes,Run focused Phase 8 exec-cmd tests,Run Phase 8 tooling tests`"
)
PHASE12_TAIL_NOTE_LINE = (
    "- `PHASE1_WORKFLOW_PHASE10_PHASE12_TAIL=Self-test current Phase 10 bootstrap route checker,Check current Phase 10 bootstrap route,Validate Phase 10 checker-backed review packet,Run Phase 10 helper tests,Self-test current Phase 11 HVC cleanup current-head checker,Check current Phase 11 HVC cleanup current-head packet,Self-test current Phase 12 tail guard,Check current Phase 12 tail guard,Run current Phase 12 throughput-parity anchor`"
)
PHASE12_TAIL_GUARD_NOTE_LINE = (
    "- `PHASE1_WORKFLOW_PHASE12_TAIL_GUARD=scripts/zigux/check-phase1-workflow-phase12-tail.py`"
)
PHASE12_TAIL_ADJACENCY_NOTE_LINE = (
    "- `PHASE1_WORKFLOW_PHASE12_TAIL_ADJACENCY=Check current Phase 11 HVC cleanup current-head packet,Self-test current Phase 12 tail guard,Check current Phase 12 tail guard,Run current Phase 12 throughput-parity anchor`"
)

PHASE2_TAIL_STEPS = (
    ("Self-test current Phase 2 toolchain pin-scope checker", "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test"),
    ("Check current Phase 2 toolchain pin-scope packet", "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py"),
    ("Run current Phase 2 toolchain make route", "make -C zigux phase2-toolchain"),
    ("Self-test current Phase 2 required-make-routes checker", "python3 scripts/zigux/check-phase2-required-make-routes.py --self-test"),
    ("Check current Phase 2 required-make-routes packet", "python3 scripts/zigux/check-phase2-required-make-routes.py"),
    ("Self-test current Phase 2 shared reminder checker", "python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test"),
    ("Check current Phase 2 shared reminder packet", "python3 scripts/zigux/check-phase2-docs-shared-reminder.py"),
    ("Validate current Phase 2 tool packet", "python3 scripts/zigux/validate-phase2.py"),
)

PHASE1_PRE_STEPS = (
    ("Self-test current Phase 1 direct-owner checker", "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test"),
    ("Check current Phase 1 direct-owner markers", "python3 scripts/zigux/check-phase1-direct-owner-markers.py"),
    ("Self-test current Phase 1 string review checker", "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test"),
    ("Check current Phase 1 string review packet", "python3 scripts/zigux/check-phase1-string-review-packet.py"),
    ("Self-test current Phase 1 bench checker", "python3 scripts/zigux/check-phase1-bench.py --self-test"),
    ("Self-test current Phase 1 shared reminder checker", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test"),
    ("Check current Phase 1 shared reminder packet", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py"),
)

PHASE1_PREBUFFER_CHAIN = tuple(step for step, _ in PHASE1_PRE_STEPS)

LANE_STEPS = (
    ("Self-test current Phase 1 workflow viability checker", "python3 scripts/zigux/check-phase1-workflow-viability.py --self-test"),
    ("Check current Phase 1 workflow viability", "python3 scripts/zigux/check-phase1-workflow-viability.py"),
)

LANE_ADJACENT_CHAIN = (
    "Check current Phase 1 shared reminder packet",
    "Self-test current Phase 1 workflow viability checker",
    "Check current Phase 1 workflow viability",
    "Self-test current Phase 3 interop packet",
)

PHASE3_BUFFER_STEPS = (
    ("Self-test current Phase 3 interop packet", "python3 scripts/zigux/validate_phase3_selftest.py"),
    ("Check current Phase 3 interop packet", "python3 scripts/zigux/run-phase3-checks.py"),
    ("Self-test current Phase 3 low-level wrapper survey validator", "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"),
    ("Check current Phase 3 low-level wrapper survey packet", "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    ("Run current Phase 3 low-level wrapper replay", "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"),
    ("Run current Phase 3 shared tests-root packet", "zig build phase3-test --build-file zigux/tests/build.zig"),
)
SMOKE_STEP = ("Run current Phase 1 shared tests-root smoke", "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig")

PHASE4_STEPS = (
    ("Self-test current Phase 4 repo-reality warning checker", "python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test"),
    ("Check current Phase 4 repo-reality warning packet", "python3 scripts/zigux/check-phase4-repo-reality-warning.py"),
    ("Self-test current Phase 4 reversible-delivery pin checker", "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test"),
    ("Check current Phase 4 reversible-delivery pin packet", "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py"),
    ("Self-test current Phase 4 tests README checker", "python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test"),
    ("Check current Phase 4 tests README packet", "python3 scripts/zigux/check-phase4-tests-readme-packet.py"),
    ("Self-test current Phase 4 artifact-diff helper", "python3 scripts/zigux/artifact_diff.py --self-test"),
    ("Self-test current Phase 4 artifact-diff determinism checker", "python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test"),
    ("Self-test current Phase 4 artifact-diff validator replay checker", "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test"),
    ("Check current Phase 4 artifact-diff validator replay packet", "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py"),
)

PHASE8_BUFFER_STEPS = (
    ("Validate Phase 8 tooling routes", "make -C zigux phase8-validate"),
    ("Run focused Phase 8 exec-cmd tests", "make -C zigux phase8-exec-cmd-test"),
    ("Run Phase 8 tooling tests", "make -C zigux phase8-test"),
)

PHASE9_BUFFER_STEPS = (
    ("Self-test current Phase 9 review-checklist boundaries checker", "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test"),
    ("Check current Phase 9 review-checklist boundaries packet", "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py"),
    ("Self-test current Phase 9 trace-events runtime packet checker", "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test"),
    ("Check current Phase 9 trace-events runtime packet", "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py"),
    ("Run current Phase 9 trace-events runtime sample tests", "zig test samples/zigux/runtime_trace_events.zig"),
    ("Run current Phase 9 unregistered gate companion tests", "zig test samples/zigux/runtime_trace_events_unregistered_gate.zig"),
    ("Run current Phase 9 exit rollback guard companion tests", "zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig"),
    ("Run current Phase 9 registration reentry companion tests", "zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig"),
)

PHASE7_HANDOFF_STEPS = (
    ("Self-test current Phase 7 shared-control gap checker", "python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test"),
    ("Check current Phase 7 shared-control gap packet", "python3 scripts/zigux/check-phase7-shared-control-gap.py"),
)

PHASE10_PHASE11_TAIL_STEPS = (
    ("Self-test current Phase 10 bootstrap route checker", "python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test"),
    ("Check current Phase 10 bootstrap route", "python3 scripts/zigux/check-phase10-bootstrap-route.py"),
    ("Validate Phase 10 checker-backed review packet", "make -C zigux phase10-validate"),
    ("Run Phase 10 helper tests", "make -C zigux phase10-test"),
    ("Self-test current Phase 11 HVC cleanup current-head checker", "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test"),
    ("Check current Phase 11 HVC cleanup current-head packet", "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py"),
)

PHASE12_TAIL_GUARD_STEPS = (
    ("Self-test current Phase 12 tail guard", "python3 scripts/zigux/check-phase1-workflow-phase12-tail.py --self-test"),
    ("Check current Phase 12 tail guard", "python3 scripts/zigux/check-phase1-workflow-phase12-tail.py"),
)
PHASE12_TAIL_CHAIN = (
    "Check current Phase 11 HVC cleanup current-head packet",
    "Self-test current Phase 12 tail guard",
    "Check current Phase 12 tail guard",
    "Run current Phase 12 throughput-parity anchor",
)
PHASE12_TAIL_STEP = (
    "Run current Phase 12 throughput-parity anchor",
    "zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
)

ALL_STEPS = (
    (PREFLIGHT_STEP,)
    + PHASE2_TAIL_STEPS
    + PHASE1_PRE_STEPS
    + LANE_STEPS
    + PHASE3_BUFFER_STEPS
    + (SMOKE_STEP,)
    + PHASE4_STEPS
    + PHASE8_BUFFER_STEPS
    + PHASE9_BUFFER_STEPS
    + PHASE7_HANDOFF_STEPS
    + PHASE10_PHASE11_TAIL_STEPS
    + PHASE12_TAIL_GUARD_STEPS
    + (PHASE12_TAIL_STEP,)
)

REQUIRED_FILE_RELS = (
    WORKFLOW_REL,
    NOTE_REL,
    Path("scripts/zigux/check-phase2-toolchain-pin-scope.py"),
    Path("scripts/zigux/check-phase2-required-make-routes.py"),
    Path("scripts/zigux/check-phase2-docs-shared-reminder.py"),
    Path("scripts/zigux/validate-phase2.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
    Path("scripts/zigux/check-phase1-workflow-viability.py"),
    Path("scripts/zigux/check-phase1-workflow-phase12-tail.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    Path("zigux/tests/phase3_low_level_wrappers_build.zig"),
    Path("zigux/tests/build.zig"),
    Path("scripts/zigux/check-phase4-repo-reality-warning.py"),
    Path("scripts/zigux/check-phase4-reversible-delivery-pins.py"),
    Path("scripts/zigux/check-phase4-tests-readme-packet.py"),
    Path("scripts/zigux/artifact_diff.py"),
    Path("scripts/zigux/check-phase4-artifact-diff-determinism.py"),
    Path("scripts/zigux/check-phase4-artifact-diff-validator-replays.py"),
    Path("scripts/zigux/check-phase9-review-checklist-phase-boundaries.py"),
    Path("scripts/zigux/check-phase9-trace-events-runtime-packet.py"),
    Path("samples/zigux/runtime_trace_events.zig"),
    Path("samples/zigux/runtime_trace_events_unregistered_gate.zig"),
    Path("samples/zigux/runtime_trace_events_exit_rollback_guard.zig"),
    Path("samples/zigux/runtime_trace_events_registration_reentry_gate.zig"),
    Path("scripts/zigux/check-phase7-shared-control-gap.py"),
    Path("scripts/zigux/check-phase10-bootstrap-route.py"),
    Path("scripts/zigux/check-phase11-hvc-cleanup-current-head.py"),
    Path("zigux/Makefile"),
)

REQUIRED_NOTE_LINES = (
    "- `PHASE1_WORKFLOW_STATUS=active`",
    "- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 workflow-viability guard`",
    "- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-viability`",
    PREFLIGHT_NOTE_LINE,
    PHASE2_TAIL_NOTE_LINE,
    PHASE1_PRE_BUFFER_NOTE_LINE,
    "- `PHASE1_WORKFLOW_INSERTION_POINT=after current Phase 1 shared reminder packet and before current Phase 3 interop packet`",
    "- `PHASE1_WORKFLOW_REQUIRED_ADJACENCY=Check current Phase 1 shared reminder packet,Self-test current Phase 1 workflow viability checker,Check current Phase 1 workflow viability,Self-test current Phase 3 interop packet`",
    "- `PHASE1_WORKFLOW_PHASE3_BUFFER=Self-test current Phase 3 interop packet,Check current Phase 3 interop packet,Self-test current Phase 3 low-level wrapper survey validator,Check current Phase 3 low-level wrapper survey packet,Run current Phase 3 low-level wrapper replay,Run current Phase 3 shared tests-root packet,Run current Phase 1 shared tests-root smoke`",
    "- `PHASE1_WORKFLOW_PHASE4_ARTIFACT_DIFF_TAIL=Self-test current Phase 4 artifact-diff helper,Self-test current Phase 4 artifact-diff determinism checker,Self-test current Phase 4 artifact-diff validator replay checker,Check current Phase 4 artifact-diff validator replay packet`",
    PHASE8_BUFFER_NOTE_LINE,
    "- `PHASE1_WORKFLOW_PHASE9_BUFFER=Self-test current Phase 9 review-checklist boundaries checker,Check current Phase 9 review-checklist boundaries packet,Self-test current Phase 9 trace-events runtime packet checker,Check current Phase 9 trace-events runtime packet,Run current Phase 9 trace-events runtime sample tests,Run current Phase 9 unregistered gate companion tests,Run current Phase 9 exit rollback guard companion tests,Run current Phase 9 registration reentry companion tests`",
    "- `PHASE1_WORKFLOW_PHASE7_HANDOFF=Self-test current Phase 7 shared-control gap checker,Check current Phase 7 shared-control gap packet`",
    PHASE12_TAIL_NOTE_LINE,
    PHASE12_TAIL_GUARD_NOTE_LINE,
    PHASE12_TAIL_ADJACENCY_NOTE_LINE,
    "- `PHASE1_WORKFLOW_FORBIDDEN_HISTORICAL_SNIPPETS=scripts/zigux/validate-phase1.py,scripts/zigux/validate-phase1-closure.py,make -C zigux phase1-validate,make -C zigux phase1-test,make -C zigux phase1-bench,python3 scripts/zigux/check-phase1-bench.py`",
)

FORBIDDEN_WORKFLOW_SNIPPETS = (
    "python3 scripts/zigux/validate-phase1.py",
    "python3 scripts/zigux/validate-phase1-closure.py",
    "make -C zigux phase1-validate",
    "make -C zigux phase1-test",
    "make -C zigux phase1-bench",
)

LIVE_BENCH_LINE = "        run: python3 scripts/zigux/check-phase1-bench.py"


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


def require_order(workflow_text: str, step_names: tuple[str, ...], label: str = "workflow_order") -> list[str]:
    positions: list[int] = []
    for step_name in step_names:
        needle = f"- name: {step_name}"
        position = workflow_text.find(needle)
        if position == -1:
            return [f"{label}:missing:{step_name}"]
        positions.append(position)
    return [] if positions == sorted(positions) else [f"{label}:out_of_order"]


def workflow_step_names(workflow_text: str) -> list[str]:
    names: list[str] = []
    for line in workflow_text.splitlines():
        prefix = "      - name: "
        if line.startswith(prefix):
            names.append(line[len(prefix) :])
    return names


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
    for relative_path in REQUIRED_FILE_RELS:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    note_text = load_text(root, NOTE_REL)

    for line in REQUIRED_NOTE_LINES:
        failures.extend(require_once(note_text, "note", line))

    for step_name, run_command in ALL_STEPS:
        failures.extend(require_step(workflow_text, step_name, run_command))

    failures.extend(require_order(workflow_text, PREFLIGHT_ORDER, "workflow_preflight_order"))
    failures.extend(require_adjacent_chain(workflow_text, PHASE1_PREBUFFER_CHAIN))
    failures.extend(require_adjacent_chain(workflow_text, LANE_ADJACENT_CHAIN))
    failures.extend(require_adjacent_chain(workflow_text, PHASE12_TAIL_CHAIN))

    order = (
        "Self-test current Phase 2 toolchain pin-scope checker",
        "Check current Phase 2 toolchain pin-scope packet",
        "Run current Phase 2 toolchain make route",
        "Self-test current Phase 2 required-make-routes checker",
        "Check current Phase 2 required-make-routes packet",
        "Self-test current Phase 2 shared reminder checker",
        "Check current Phase 2 shared reminder packet",
        "Validate current Phase 2 tool packet",
        "Check current Phase 1 shared reminder packet",
        "Self-test current Phase 1 workflow viability checker",
        "Check current Phase 1 workflow viability",
        "Self-test current Phase 3 interop packet",
        "Check current Phase 3 interop packet",
        "Self-test current Phase 3 low-level wrapper survey validator",
        "Check current Phase 3 low-level wrapper survey packet",
        "Run current Phase 3 low-level wrapper replay",
        "Run current Phase 3 shared tests-root packet",
        "Run current Phase 1 shared tests-root smoke",
        "Self-test current Phase 4 artifact-diff helper",
        "Self-test current Phase 4 artifact-diff determinism checker",
        "Self-test current Phase 4 artifact-diff validator replay checker",
        "Check current Phase 4 artifact-diff validator replay packet",
        "Validate Phase 8 tooling routes",
        "Run focused Phase 8 exec-cmd tests",
        "Run Phase 8 tooling tests",
        "Self-test current Phase 9 review-checklist boundaries checker",
        "Check current Phase 9 review-checklist boundaries packet",
        "Self-test current Phase 9 trace-events runtime packet checker",
        "Check current Phase 9 trace-events runtime packet",
        "Run current Phase 9 trace-events runtime sample tests",
        "Run current Phase 9 unregistered gate companion tests",
        "Run current Phase 9 exit rollback guard companion tests",
        "Run current Phase 9 registration reentry companion tests",
        "Self-test current Phase 7 shared-control gap checker",
        "Check current Phase 7 shared-control gap packet",
        "Self-test current Phase 10 bootstrap route checker",
        "Check current Phase 10 bootstrap route",
        "Self-test current Phase 11 HVC cleanup current-head checker",
        "Check current Phase 11 HVC cleanup current-head packet",
        "Self-test current Phase 12 tail guard",
        "Check current Phase 12 tail guard",
        "Run current Phase 12 throughput-parity anchor",
    )
    failures.extend(require_order(workflow_text, order))

    for forbidden in FORBIDDEN_WORKFLOW_SNIPPETS:
        if forbidden in workflow_text:
            failures.append(f"workflow_forbidden:{forbidden}:unexpected_present")

    live_bench_count = sum(1 for line in workflow_text.splitlines() if line == LIVE_BENCH_LINE)
    if live_bench_count != 0:
        failures.append(f"workflow_forbidden:live_phase1_bench:expected=0:actual={live_bench_count}")

    return failures


def build_note_text() -> str:
    return "\n".join(
        (
            "# Phase 1 Workflow Viability",
            "",
            *REQUIRED_NOTE_LINES,
            "- keep the lane scoped to the current Phase 1 workflow-viability pair instead of reviving the older closure-side Phase 1 validator routes.",
            "- run the lightweight Lane 17 preflight after Setup Python so this branch still emits lane-local signal even when the external pinned-Zig archive step fails first.",
            "- keep the current direct-owner, string-review, bench-selftest, and shared-reminder ladder intact before the lane-local viability pair.",
            "- keep the workflow-viability pair immediately after the current Phase 1 shared reminder packet, then preserve the current Phase 3 buffer before the shared Phase 1 smoke route.",
            "- keep the current Phase 4 artifact-diff helper and validator replay block ahead of the current Phase 8 tooling routes, then preserve the current Phase 9 review-checklist, trace-events packet, and companion sample tests before the Phase 7 shared-control pair.",
            "- keep the dedicated Phase 12 tail guard running immediately after the current Phase 11 packet and before the throughput-parity anchor so the inherited bootstrap tail stays enforced in CI.",
            "- if the workflow moves again, refresh this same lane-local packet first instead of widening into unrelated reminder or closure lanes.",
            "",
        )
    )


def build_workflow_text() -> str:
    lines = [
        "name: zigux-bootstrap",
        "",
        "jobs:",
        "  bootstrap:",
        "    runs-on: ubuntu-latest",
        "    steps:",
        "",
        "      - name: Setup Python",
        "        run: python3 --version",
        "",
        "      - name: Preflight current Phase 1 workflow viability checker",
        "        run: python3 scripts/zigux/check-phase1-workflow-viability.py --self-test",
        "",
        "      - name: Setup pinned Zig toolchain",
        "        run: printf 'pinned-zig\\n'",
        "",
    ]
    for step_name, run_command in ALL_STEPS[1:]:
        lines.append(f"      - name: {step_name}")
        lines.append(f"        run: {run_command}")
        lines.append("")
    return "\n".join(lines)


def build_sample_repo(root: Path) -> None:
    write_file(root, WORKFLOW_REL, build_workflow_text())
    write_file(root, NOTE_REL, build_note_text())
    for relative_path in REQUIRED_FILE_RELS[2:]:
        write_file(root, relative_path, "# placeholder\n")


def rewrite_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise AssertionError(f"missing sample text: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-workflow-viability-") as tmpdir:
        root = Path(tmpdir)

        build_sample_repo(root)
        if collect_failures(root):
            print("self-test:unexpected_failures")
            return 1
        case_count += 1

        note_text = load_text(root, NOTE_REL)
        write_file(root, NOTE_REL, rewrite_once(note_text, PREFLIGHT_NOTE_LINE + "\n"))
        failures = collect_failures(root)
        if "note:expected=1:actual=0" not in failures:
            print("self-test:missing_preflight_note_marker")
            return 1
        case_count += 1
        build_sampleRepo(root)

        note_text = load_text(root, NOTE_REL)
        write_file(root, NOTE_REL, note_text + PREFLIGHT_NOTE_LINE + "\n")
        failures = collect_failures(root)
        if "note:expected=1:actual=2" not in failures:
            print("self-test:duplicate_preflight_note_marker_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        note_text = load_text(root, NOTE_REL)
        write_file(root, NOTE_REL, rewrite_once(note_text, PHASE1_PRE_BUFFER_NOTE_LINE + "\n"))
        failures = collect_failures(root)
        if "note:expected=1:actual=0" not in failures:
            print("self-test:missing_phase1_prebuffer_note_marker")
            return 1
        case_count += 1
        build_sampleRepo(root)

        note_text = load_text(root, NOTE_REL)
        write_file(root, NOTE_REL, note_text + PHASE1_PRE_BUFFER_NOTE_LINE + "\n")
        failures = collect_failures(root)
        if "note:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase1_prebuffer_note_marker_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, "      - name: Preflight current Phase 1 workflow viability checker\n"))
        failures = collect_failures(root)
        if "workflow_step:Preflight current Phase 1 workflow viability checker:expected=1:actual=0" not in failures:
            print("self-test:missing_preflight_step")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        preflight_block = (
            "      - name: Preflight current Phase 1 workflow viability checker\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-viability.py --self-test\n"
        )
        write_file(root, WORKFLOW_REL, workflow_text + preflight_block)
        failures = collect_failures(root)
        if "workflow_step:Preflight current Phase 1 workflow viability checker:expected=1:actual=2" not in failures:
            print("self-test:duplicate_preflight_step_not_detected")
            return 1
        if "workflow_run:Preflight current Phase 1 workflow viability checker:expected=1:actual=2" not in failures:
            print("self-test:duplicate_preflight_run_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        old = (
            "      - name: Setup Python\n"
            "        run: python3 --version\n\n"
            "      - name: Preflight current Phase 1 workflow viability checker\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-viability.py --self-test\n\n"
            "      - name: Setup pinned Zig toolchain\n"
            "        run: printf 'pinned-zig\\n'\n"
        )
        new = (
            "      - name: Setup Python\n"
            "        run: python3 --version\n\n"
            "      - name: Setup pinned Zig toolchain\n"
            "        run: printf 'pinned-zig\\n'\n\n"
            "      - name: Preflight current Phase 1 workflow viability checker\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-viability.py --self-test\n"
        )
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, old, new))
        failures = collect_failures(root)
        if "workflow_preflight_order:out_of_order" not in failures:
            print("self-test:preflight_order_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        note_text = load_text(root, NOTE_REL)
        write_file(root, NOTE_REL, rewrite_once(note_text, PHASE8_BUFFER_NOTE_LINE + "\n"))
        failures = collect_failures(root)
        if "note:expected=1:actual=0" not in failures:
            print("self-test:missing_phase8_note_marker")
            return 1
        case_count += 1
        build_sampleRepo(root)

        note_text = load_text(root, NOTE_REL)
        write_file(root, NOTE_REL, note_text + PHASE8_BUFFER_NOTE_LINE + "\n")
        failures = collect_failures(root)
        if "note:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase8_note_marker_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        note_text = load_text(root, NOTE_REL)
        write_file(root, NOTE_REL, rewrite_once(note_text, PHASE12_TAIL_NOTE_LINE + "\n"))
        failures = collect_failures(root)
        if "note:expected=1:actual=0" not in failures:
            print("self-test:missing_phase12_tail_note_marker")
            return 1
        case_count += 1
        build_sampleRepo(root)

        note_text = load_text(root, NOTE_REL)
        write_file(root, NOTE_REL, note_text + PHASE12_TAIL_NOTE_LINE + "\n")
        failures = collect_failures(root)
        if "note:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase12_tail_note_marker_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        note_text = load_text(root, NOTE_REL)
        write_file(root, NOTE_REL, rewrite_once(note_text, PHASE12_TAIL_GUARD_NOTE_LINE + "\n"))
        failures = collect_failures(root)
        if "note:expected=1:actual=0" not in failures:
            print("self-test:missing_phase12_guard_note_marker")
            return 1
        case_count += 1
        build_sampleRepo(root)

        note_text = load_text(root, NOTE_REL)
        write_file(root, NOTE_REL, note_text + PHASE12_TAIL_GUARD_NOTE_LINE + "\n")
        failures = collect_failures(root)
        if "note:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase12_guard_note_marker_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        note_text = load_text(root, NOTE_REL)
        write_file(root, NOTE_REL, rewrite_once(note_text, PHASE12_TAIL_ADJACENCY_NOTE_LINE + "\n"))
        failures = collect_failures(root)
        if "note:expected=1:actual=0" not in failures:
            print("self-test:missing_phase12_adjacency_note_marker")
            return 1
        case_count += 1
        build_sampleRepo(root)

        note_text = load_text(root, NOTE_REL)
        write_file(root, NOTE_REL, note_text + PHASE12_TAIL_ADJACENCY_NOTE_LINE + "\n")
        failures = collect_failures(root)
        if "note:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase12_adjacency_note_marker_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, "      - name: Self-test current Phase 1 workflow viability checker\n"))
        failures = collect_failures(root)
        if "workflow_step:Self-test current Phase 1 workflow viability checker:expected=1:actual=0" not in failures:
            print("self-test:missing_lane_selftest_step")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        lane_selftest_block = (
            "      - name: Self-test current Phase 1 workflow viability checker\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-viability.py --self-test\n"
        )
        write_file(root, WORKFLOW_REL, workflow_text + lane_selftest_block)
        failures = collect_failures(root)
        if "workflow_step:Self-test current Phase 1 workflow viability checker:expected=1:actual=2" not in failures:
            print("self-test:duplicate_lane_selftest_step_not_detected")
            return 1
        if "workflow_run:Self-test current Phase 1 workflow viability checker:expected=1:actual=2" not in failures:
            print("self-test:duplicate_lane_selftest_run_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        lane_check_block = (
            "      - name: Check current Phase 1 workflow viability\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-viability.py\n"
        )
        write_file(root, WORKFLOW_REL, workflow_text + lane_check_block)
        failures = collect_failures(root)
        if "workflow_step:Check current Phase 1 workflow viability:expected=1:actual=2" not in failures:
            print("self-test:duplicate_lane_check_step_not_detected")
            return 1
        if "workflow_run:Check current Phase 1 workflow viability:expected=1:actual=2" not in failures:
            print("self-test:duplicate_lane_check_run_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        old = (
            "      - name: Self-test current Phase 1 direct-owner checker\n"
            "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test\n\n"
            "      - name: Check current Phase 1 direct-owner markers\n"
            "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py\n\n"
            "      - name: Self-test current Phase 1 string review checker\n"
            "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test\n\n"
            "      - name: Check current Phase 1 string review packet\n"
            "        run: python3 scripts/zigux/check-phase1-string-review-packet.py\n\n"
            "      - name: Self-test current Phase 1 bench checker\n"
            "        run: python3 scripts/zigux/check-phase1-bench.py --self-test\n\n"
            "      - name: Self-test current Phase 1 shared reminder checker\n"
            "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n\n"
            "      - name: Check current Phase 1 shared reminder packet\n"
            "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n"
        )
        new = (
            "      - name: Self-test current Phase 1 shared reminder checker\n"
            "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n\n"
            "      - name: Check current Phase 1 shared reminder packet\n"
            "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n\n"
            "      - name: Self-test current Phase 1 direct-owner checker\n"
            "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test\n\n"
            "      - name: Check current Phase 1 direct-owner markers\n"
            "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py\n\n"
            "      - name: Self-test current Phase 1 string review checker\n"
            "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test\n\n"
            "      - name: Check current Phase 1 string review packet\n"
            "        run: python3 scripts/zigux/check-phase1-string-review-packet.py\n\n"
            "      - name: Self-test current Phase 1 bench checker\n"
            "        run: python3 scripts/zigux/check-phase1-bench.py --self-test\n"
        )
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, old, new))
        failures = collect_failures(root)
        expected = f"workflow_adjacent_chain:missing:{'->'.join(PHASE1_PREBUFFER_CHAIN)}"
        if expected not in failures:
            print("self-test:broken_phase1_prebuffer_chain_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        old = (
            "      - name: Self-test current Phase 1 workflow viability checker\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-viability.py --self-test\n\n"
            "      - name: Check current Phase 1 workflow viability\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-viability.py\n\n"
            "      - name: Self-test current Phase 3 interop packet\n"
            "        run: python3 scripts/zigux/validate_phase3_selftest.py\n"
        )
        new = (
            "      - name: Self-test current Phase 3 interop packet\n"
            "        run: python3 scripts/zigux/validate_phase3_selftest.py\n\n"
            "      - name: Self-test current Phase 1 workflow viability checker\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-viability.py --self-test\n\n"
            "      - name: Check current Phase 1 workflow viability\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-viability.py\n"
        )
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, old, new))
        failures = collect_failures(root)
        if not any(failure.startswith("workflow_adjacent_chain:missing:") for failure in failures):
            print("self-test:broken_adjacent_chain_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, "      - name: Run current Phase 2 toolchain make route\n"))
        failures = collect_failures(root)
        if "workflow_step:Run current Phase 2 toolchain make route:expected=1:actual=0" not in failures:
            print("self-test:missing_phase2_make_route_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, "      - name: Validate Phase 8 tooling routes\n"))
        failures = collect_failures(root)
        if "workflow_step:Validate Phase 8 tooling routes:expected=1:actual=0" not in failures:
            print("self-test:missing_phase8_buffer_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, "      - name: Self-test current Phase 12 tail guard\n"))
        failures = collect_failures(root)
        if "workflow_step:Self-test current Phase 12 tail guard:expected=1:actual=0" not in failures:
            print("self-test:missing_phase12_selftest_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, "      - name: Check current Phase 12 tail guard\n"))
        failures = collect_failures(root)
        if "workflow_step:Check current Phase 12 tail guard:expected=1:actual=0" not in failures:
            print("self-test:missing_phase12_check_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        old = (
            "      - name: Check current Phase 11 HVC cleanup current-head packet\n"
            "        run: python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py\n\n"
            "      - name: Self-test current Phase 12 tail guard\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-phase12-tail.py --self-test\n\n"
            "      - name: Check current Phase 12 tail guard\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-phase12-tail.py\n\n"
            "      - name: Run current Phase 12 throughput-parity anchor\n"
            "        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig\n"
        )
        new = (
            "      - name: Check current Phase 11 HVC cleanup current-head packet\n"
            "        run: python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py\n\n"
            "      - name: Run current Phase 12 throughput-parity anchor\n"
            "        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig\n\n"
            "      - name: Self-test current Phase 12 tail guard\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-phase12-tail.py --self-test\n\n"
            "      - name: Check current Phase 12 tail guard\n"
            "        run: python3 scripts/zigux/check-phase1-workflow-phase12-tail.py\n"
        )
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, old, new))
        failures = collect_failures(root)
        expected = f"workflow_adjacent_chain:missing:{'->'.join(PHASE12_TAIL_CHAIN)}"
        if expected not in failures:
            print("self-test:broken_phase12_tail_chain_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        write_file(root, WORKFLOW_REL, workflow_text + "\n        run: make -C zigux phase1-test\n")
        failures = collect_failures(root)
        if "workflow_forbidden:make -C zigux phase1-test:unexpected_present" not in failures:
            print("self-test:forbidden_phase1_route_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        write_file(root, WORKFLOW_REL, workflow_text + "\n" + LIVE_BENCH_LINE + "\n")
        failures = collect_failures(root)
        if not any(failure.startswith("workflow_forbidden:live_phase1_bench:") for failure in failures):
            print("self-test:live_bench_not_detected")
            return 1
        case_count += 1

    print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_VIABILITY_SELF_TEST_CASE_COUNT={case_count}")
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
            print(f"phase1-workflow-viability:{failure}")
        return 1

    print("phase1-workflow-viability:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
