#!/usr/bin/env python3
"""Guard Lane 17's current-master-safe Phase 1 workflow viability packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
SCRIPTS_ROOT_REL = Path("scripts/zigux/README.md")
TESTS_ROOT_REL = Path("zigux/tests/README.md")
SMOKE_TEST_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
PHASE1_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
CHECKER_REL = Path("scripts/zigux/check-phase1-workflow-viability.py")

REQUIRED_FILE_RELS = (
    WORKFLOW_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    CLOSURE_NOTE_REL,
    LANE_NOTE_REL,
    SCRIPTS_ROOT_REL,
    TESTS_ROOT_REL,
    SMOKE_TEST_REL,
    PHASE1_MANIFEST_REL,
    CHECKER_REL,
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-route-summary-counts.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    Path("scripts/zigux/check-phase4-repo-reality-warning.py"),
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/phase3_export_uapi_layout_build.zig"),
    Path("zigux/tests/phase3_policy_dump_build.zig"),
    Path("zigux/tests/phase3_low_level_wrappers_build.zig"),
)

REQUIRED_DOCS_ROOT_LINES = (
    "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
    "* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
)

REQUIRED_REVIEW_CHECKLIST_LINES = (
    "* if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
)

REQUIRED_NOTE_LINES = (
    "- `PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
    "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
)

REQUIRED_SCRIPTS_ROOT_LINES = (
    "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
    "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
)

REQUIRED_TESTS_ROOT_LINES = (
    "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "  * broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
)

PHASE1_TESTS_ROOT_PACKET_LINES = (
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "- `scripts/zigux/check-phase1-bench.py`",
    "- `zigux/tests/build.zig`",
    "- `zigux/tests/phase1_host_tools_smoke.zig`",
    "- `.github/workflows/zigux-bootstrap.yml`",
    "- `zigux/tests/fixtures/phase1_helper_manifest.json`",
)

PHASE1_PRELUDE_STEPS = (
    ("Self-test current Phase 1 direct-owner checker", "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test"),
    ("Check current Phase 1 direct-owner markers", "python3 scripts/zigux/check-phase1-direct-owner-markers.py"),
    ("Self-test current Phase 1 string review checker", "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test"),
    ("Check current Phase 1 string review packet", "python3 scripts/zigux/check-phase1-string-review-packet.py"),
)

PHASE1_TAIL_STEPS = (
    ("Self-test current Phase 1 route summary checker", "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test"),
    ("Check current Phase 1 route summary packet", "python3 scripts/zigux/check-phase1-route-summary-counts.py"),
    ("Self-test current Phase 1 bench checker", "python3 scripts/zigux/check-phase1-bench.py --self-test"),
    ("Self-test current Phase 1 shared reminder checker", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test"),
    ("Check current Phase 1 shared reminder packet", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py"),
    ("Self-test current Phase 1 closure validator", "python3 scripts/zigux/validate-phase1-closure.py --self-test"),
    ("Check current Phase 1 closure packet", "python3 scripts/zigux/validate-phase1-closure.py"),
)

PHASE3_BUFFER_STEPS = (
    ("Self-test current Phase 3 interop packet", "python3 scripts/zigux/validate_phase3_selftest.py"),
    ("Check current Phase 3 interop packet", "python3 scripts/zigux/run-phase3-checks.py"),
    ("Run current Phase 3 export/UAPI layout replay", "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"),
    ("Run current Phase 3 policy starter-packet replay", "make -C zigux phase3-policy-starter-packet-test"),
    ("Run current Phase 3 policy dump replay", "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig"),
    ("Self-test current Phase 3 low-level wrapper survey validator", "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"),
    ("Check current Phase 3 low-level wrapper survey packet", "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    ("Run current Phase 3 low-level wrapper replay", "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"),
    ("Run current Phase 3 shared tests-root packet", "zig build phase3-test --build-file zigux/tests/build.zig"),
    ("Run current Phase 3 ABI dump replay", "zig build phase3-dump --build-file zigux/tests/build.zig"),
    ("Run current Phase 1 shared tests-root smoke", "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig"),
)

PHASE4_LEAD_STEPS = (
    ("Self-test current Phase 4 repo-reality warning checker", "python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test"),
    ("Check current Phase 4 repo-reality warning packet", "python3 scripts/zigux/check-phase4-repo-reality-warning.py"),
)

ALL_REQUIRED_STEPS = PHASE1_PRELUDE_STEPS + PHASE1_TAIL_STEPS + PHASE3_BUFFER_STEPS + PHASE4_LEAD_STEPS
REQUIRED_ORDER = tuple(step for step, _ in ALL_REQUIRED_STEPS)
REQUIRED_CHAIN = (
    "Check current Phase 1 closure packet",
    "Self-test current Phase 3 interop packet",
    "Check current Phase 3 interop packet",
    "Run current Phase 3 export/UAPI layout replay",
)
PHASE1_PACKET_CHAIN = (
    "Self-test current Phase 1 direct-owner checker",
    "Check current Phase 1 direct-owner markers",
    "Self-test current Phase 1 string review checker",
    "Check current Phase 1 string review packet",
    "Self-test current Phase 1 route summary checker",
    "Check current Phase 1 route summary packet",
    "Self-test current Phase 1 bench checker",
    "Self-test current Phase 1 shared reminder checker",
    "Check current Phase 1 shared reminder packet",
    "Self-test current Phase 1 closure validator",
    "Check current Phase 1 closure packet",
)
SMOKE_TO_PHASE4_CHAIN = (
    "Run current Phase 1 shared tests-root smoke",
    "Self-test current Phase 4 repo-reality warning checker",
    "Check current Phase 4 repo-reality warning packet",
)

FORBIDDEN_WORKFLOW_SNIPPETS = (
    "python3 scripts/zigux/validate-phase1.py",
    "python3 scripts/zigux/check-phase1-parity.py",
    "zig build bench --build-file zigux/tests/build.zig",
    "make -C zigux phase1-validate",
    "make -C zigux phase1-test",
    "make -C zigux phase1-bench",
)


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_once(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def workflow_step_names(workflow_text: str) -> list[str]:
    prefix = "      - name: "
    return [line[len(prefix) :] for line in workflow_text.splitlines() if line.startswith(prefix)]


def require_step_pair(workflow_text: str, step_name: str, run_command: str) -> list[str]:
    failures: list[str] = []
    failures.extend(require_once(workflow_text, f"workflow_step:{step_name}", f"      - name: {step_name}"))
    block = f"      - name: {step_name}\n        run: {run_command}"
    failures.extend(require_once(workflow_text, f"workflow_run:{step_name}", block))
    return failures


def require_order(workflow_text: str, step_names: tuple[str, ...]) -> list[str]:
    names = workflow_step_names(workflow_text)
    positions: list[int] = []
    for step_name in step_names:
        try:
            positions.append(names.index(step_name))
        except ValueError:
            return [f"workflow_order:missing:{step_name}"]
    return [] if positions == sorted(positions) else ["workflow_order:out_of_order"]


def require_chain(workflow_text: str, chain: tuple[str, ...], label: str) -> list[str]:
    names = workflow_step_names(workflow_text)
    width = len(chain)
    for start in range(len(names) - width + 1):
        if tuple(names[start : start + width]) == chain:
            return []
    return [f"{label}:missing:{'->'.join(chain)}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILE_RELS:
        path = root / relative_path
        if not path.exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
        elif not path.is_file():
            failures.append(f"non_file_path:{relative_path.as_posix()}")
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    docs_root_text = load_text(root, DOCS_ROOT_REL)
    review_checklist_text = load_text(root, REVIEW_CHECKLIST_REL)
    note_text = load_text(root, CLOSURE_NOTE_REL)
    scripts_root_text = load_text(root, SCRIPTS_ROOT_REL)
    tests_root_text = load_text(root, TESTS_ROOT_REL)

    for line in REQUIRED_DOCS_ROOT_LINES:
        failures.extend(require_once(docs_root_text, "docs_root", line))

    for line in REQUIRED_REVIEW_CHECKLIST_LINES:
        failures.extend(require_once(review_checklist_text, "review_checklist", line))

    for line in REQUIRED_NOTE_LINES:
        failures.extend(require_once(note_text, "closure_note", line))

    for line in REQUIRED_SCRIPTS_ROOT_LINES:
        failures.extend(require_once(scripts_root_text, "scripts_root", line))

    for line in REQUIRED_TESTS_ROOT_LINES:
        failures.extend(require_once(tests_root_text, "tests_root", line))

    for line in PHASE1_TESTS_ROOT_PACKET_LINES:
        failures.extend(require_once(tests_root_text, "tests_root_packet", line))

    for step_name, run_command in ALL_REQUIRED_STEPS:
        failures.extend(require_step_pair(workflow_text, step_name, run_command))

    failures.extend(require_order(workflow_text, REQUIRED_ORDER))
    failures.extend(require_chain(workflow_text, PHASE1_PACKET_CHAIN, "workflow_phase1_packet"))
    failures.extend(require_chain(workflow_text, REQUIRED_CHAIN, "workflow_chain"))
    failures.extend(require_chain(workflow_text, SMOKE_TO_PHASE4_CHAIN, "workflow_phase4_lead"))

    for forbidden in FORBIDDEN_WORKFLOW_SNIPPETS:
        if forbidden in workflow_text:
            failures.append(f"workflow_forbidden:{forbidden}:unexpected_present")

    return failures


def sample_workflow_text() -> str:
    lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    runs-on: ubuntu-latest",
        "    steps:",
    ]
    for step_name, run_command in ALL_REQUIRED_STEPS:
        lines.append(f"      - name: {step_name}")
        lines.append(f"        run: {run_command}")
    lines.append("")
    return "\n".join(lines)


def sample_docs_root_text() -> str:
    return "\n".join(
        [
            "# Zigux Documentation",
            "",
            *REQUIRED_DOCS_ROOT_LINES,
            "",
        ]
    )


def sample_review_checklist_text() -> str:
    return "\n".join(
        [
            "# Zigux Review Checklist",
            "",
            *REQUIRED_REVIEW_CHECKLIST_LINES,
            "",
        ]
    )


def sample_closure_note_text() -> str:
    return "\n".join(
        [
            "# Phase 1 Closure",
            "",
            *REQUIRED_NOTE_LINES,
            "",
        ]
    )


def sample_scripts_root_text() -> str:
    return "\n".join(
        [
            "# scripts/zigux",
            "",
            *REQUIRED_SCRIPTS_ROOT_LINES,
            "",
        ]
    )


def sample_tests_root_text() -> str:
    return "\n".join(
        [
            "# zigux/tests",
            "",
            *PHASE1_TESTS_ROOT_PACKET_LINES,
            "",
            *REQUIRED_TESTS_ROOT_LINES,
            "",
        ]
    )


def write_placeholder_tree(root: Path) -> None:
    write_text(root, WORKFLOW_REL, sample_workflow_text())
    write_text(root, DOCS_ROOT_REL, sample_docs_root_text())
    write_text(root, REVIEW_CHECKLIST_REL, sample_review_checklist_text())
    write_text(root, CLOSURE_NOTE_REL, sample_closure_note_text())
    write_text(root, SCRIPTS_ROOT_REL, sample_scripts_root_text())
    write_text(root, TESTS_ROOT_REL, sample_tests_root_text())
    for relative_path in REQUIRED_FILE_RELS:
        if relative_path in (
            WORKFLOW_REL,
            DOCS_ROOT_REL,
            REVIEW_CHECKLIST_REL,
            CLOSURE_NOTE_REL,
            SCRIPTS_ROOT_REL,
            TESTS_ROOT_REL,
        ):
            continue
        write_text(root, relative_path, "# placeholder\n")


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    write_placeholder_tree(root)


def rewrite_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise AssertionError(f"missing sample text: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane17-workflow-viability-") as tmpdir:
        root = Path(tmpdir)

        write_placeholder_tree(root)
        if collect_failures(root):
            print("self-test:baseline_failed")
            return 1
        case_count += 1

        sample_root = root / "sample-root"
        write_sample_root(sample_root)
        if collect_failures(sample_root):
            print("self-test:written_sample_failed")
            return 1
        case_count += 1

        broken_root = root / "missing-file"
        write_sample_root(broken_root)
        (broken_root / CHECKER_REL).unlink()
        failures = collect_failures(broken_root)
        if f"missing_file:{CHECKER_REL.as_posix()}" not in failures:
            print("self-test:missing_checker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing-phase1-manifest"
        write_sample_root(broken_root)
        (broken_root / PHASE1_MANIFEST_REL).unlink()
        failures = collect_failures(broken_root)
        if f"missing_file:{PHASE1_MANIFEST_REL.as_posix()}" not in failures:
            print("self-test:missing_phase1_manifest_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing-lane-note"
        write_sample_root(broken_root)
        (broken_root / LANE_NOTE_REL).unlink()
        failures = collect_failures(broken_root)
        if f"missing_file:{LANE_NOTE_REL.as_posix()}" not in failures:
            print("self-test:missing_lane_note_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing-smoke-replay"
        write_sample_root(broken_root)
        (broken_root / SMOKE_TEST_REL).unlink()
        failures = collect_failures(broken_root)
        if f"missing_file:{SMOKE_TEST_REL.as_posix()}" not in failures:
            print("self-test:missing_smoke_replay_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing-docs-line"
        write_sample_root(broken_root)
        docs_root_text = load_text(broken_root, DOCS_ROOT_REL)
        write_text(
            broken_root,
            DOCS_ROOT_REL,
            rewrite_once(docs_root_text, REQUIRED_DOCS_ROOT_LINES[1] + "\n"),
        )
        failures = collect_failures(broken_root)
        if "docs_root:expected=1:actual=0" not in failures:
            print("self-test:missing_docs_line_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing-review-checklist-line"
        write_sample_root(broken_root)
        review_checklist_text = load_text(broken_root, REVIEW_CHECKLIST_REL)
        write_text(
            broken_root,
            REVIEW_CHECKLIST_REL,
            rewrite_once(review_checklist_text, REQUIRED_REVIEW_CHECKLIST_LINES[0] + "\n"),
        )
        failures = collect_failures(broken_root)
        if "review_checklist:expected=1:actual=0" not in failures:
            print("self-test:missing_review_checklist_line_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing-note-line"
        write_sample_root(broken_root)
        note_text = load_text(broken_root, CLOSURE_NOTE_REL)
        write_text(
            broken_root,
            CLOSURE_NOTE_REL,
            rewrite_once(note_text, REQUIRED_NOTE_LINES[0] + "\n"),
        )
        failures = collect_failures(broken_root)
        if "closure_note:expected=1:actual=0" not in failures:
            print("self-test:missing_note_line_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing-scripts-line"
        write_sample_root(broken_root)
        scripts_root_text = load_text(broken_root, SCRIPTS_ROOT_REL)
        write_text(
            broken_root,
            SCRIPTS_ROOT_REL,
            rewrite_once(scripts_root_text, REQUIRED_SCRIPTS_ROOT_LINES[0] + "\n"),
        )
        failures = collect_failures(broken_root)
        if "scripts_root:expected=1:actual=0" not in failures:
            print("self-test:missing_scripts_line_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing-tests-line"
        write_sample_root(broken_root)
        tests_root_text = load_text(broken_root, TESTS_ROOT_REL)
        write_text(
            broken_root,
            TESTS_ROOT_REL,
            rewrite_once(tests_root_text, REQUIRED_TESTS_ROOT_LINES[0] + "\n"),
        )
        failures = collect_failures(broken_root)
        if "tests_root:expected=1:actual=0" not in failures:
            print("self-test:missing_tests_line_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing-tests-packet-line"
        write_sample_root(broken_root)
        tests_root_text = load_text(broken_root, TESTS_ROOT_REL)
        write_text(
            broken_root,
            TESTS_ROOT_REL,
            rewrite_once(tests_root_text, PHASE1_TESTS_ROOT_PACKET_LINES[4] + "\n"),
        )
        failures = collect_failures(broken_root)
        if "tests_root_packet:expected=1:actual=0" not in failures:
            print("self-test:missing_tests_packet_line_not_detected")
            return 1
        case_count += 1

        broken_root = root / "duplicate-step"
        write_sample_root(broken_root)
        workflow_text = load_text(broken_root, WORKFLOW_REL)
        duplicate_block = (
            "      - name: Check current Phase 1 direct-owner markers\n"
            "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py\n"
        )
        write_text(broken_root, WORKFLOW_REL, workflow_text + duplicate_block)
        failures = collect_failures(broken_root)
        if "workflow_step:Check current Phase 1 direct-owner markers:expected=1:actual=2" not in failures:
            print("self-test:duplicate_step_not_detected")
            return 1
        case_count += 1

        broken_root = root / "broken-order"
        write_sample_root(broken_root)
        reordered = list(ALL_REQUIRED_STEPS)
        reordered[0], reordered[1] = reordered[1], reordered[0]
        lines = [
            "name: zigux-bootstrap",
            "jobs:",
            "  bootstrap:",
            "    runs-on: ubuntu-latest",
            "    steps:",
        ]
        for step_name, run_command in reordered:
            lines.append(f"      - name: {step_name}")
            lines.append(f"        run: {run_command}")
        lines.append("")
        write_text(broken_root, WORKFLOW_REL, "\n".join(lines))
        failures = collect_failures(broken_root)
        if "workflow_order:out_of_order" not in failures:
            print("self-test:broken_order_not_detected")
            return 1
        case_count += 1

        broken_root = root / "broken-phase1-chain"
        write_sample_root(broken_root)
        workflow_text = load_text(broken_root, WORKFLOW_REL)
        old = (
            "      - name: Check current Phase 1 string review packet\n"
            "        run: python3 scripts/zigux/check-phase1-string-review-packet.py\n"
            "      - name: Self-test current Phase 1 route summary checker\n"
            "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test\n"
        )
        new = (
            "      - name: Check current Phase 1 string review packet\n"
            "        run: python3 scripts/zigux/check-phase1-string-review-packet.py\n"
            "      - name: Drifted inserted step\n"
            "        run: python3 drift.py\n"
            "      - name: Self-test current Phase 1 route summary checker\n"
            "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test\n"
        )
        write_text(broken_root, WORKFLOW_REL, rewrite_once(workflow_text, old, new))
        failures = collect_failures(broken_root)
        expected = f"workflow_phase1_packet:missing:{'->'.join(PHASE1_PACKET_CHAIN)}"
        if expected not in failures:
            print("self-test:broken_phase1_chain_not_detected")
            return 1
        case_count += 1

        broken_root = root / "broken-chain"
        write_sample_root(broken_root)
        workflow_text = load_text(broken_root, WORKFLOW_REL)
        old = (
            "      - name: Check current Phase 1 closure packet\n"
            "        run: python3 scripts/zigux/validate-phase1-closure.py\n"
            "      - name: Self-test current Phase 3 interop packet\n"
            "        run: python3 scripts/zigux/validate_phase3_selftest.py\n"
        )
        new = (
            "      - name: Check current Phase 1 closure packet\n"
            "        run: python3 scripts/zigux/validate-phase1-closure.py\n"
            "      - name: Drifted inserted step\n"
            "        run: python3 drift.py\n"
            "      - name: Self-test current Phase 3 interop packet\n"
            "        run: python3 scripts/zigux/validate_phase3_selftest.py\n"
        )
        write_text(broken_root, WORKFLOW_REL, rewrite_once(workflow_text, old, new))
        failures = collect_failures(broken_root)
        expected = f"workflow_chain:missing:{'->'.join(REQUIRED_CHAIN)}"
        if expected not in failures:
            print("self-test:broken_chain_not_detected")
            return 1
        case_count += 1

        broken_root = root / "forbidden-history"
        write_sample_root(broken_root)
        workflow_text = load_text(broken_root, WORKFLOW_REL)
        write_text(
            broken_root,
            WORKFLOW_REL,
            workflow_text + "      - name: Historical validator\n        run: python3 scripts/zigux/validate-phase1.py\n",
        )
        failures = collect_failures(broken_root)
        marker = "workflow_forbidden:python3 scripts/zigux/validate-phase1.py:unexpected_present"
        if marker not in failures:
            print("self-test:forbidden_history_not_detected")
            return 1
        case_count += 1

    print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_VIABILITY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"phase1-workflow-viability:sample-root-written:{args.write_sample_root}")
        return 0

    failures = collect_failures(args.root.resolve())
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("phase1-workflow-viability:ok")
    print("phase1-workflow-viability:mode=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
