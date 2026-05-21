#!/usr/bin/env python3
"""Guard the current Lane 17 Phase 1 workflow-viability packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
NOTE_REL = Path("Documentation/zigux/phase1-workflow-viability.md")

PHASE1_PRE_BUFFER_STEPS = (
    ("Self-test current Phase 1 direct-owner checker", "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test"),
    ("Check current Phase 1 direct-owner markers", "python3 scripts/zigux/check-phase1-direct-owner-markers.py"),
    ("Self-test current Phase 1 string review checker", "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test"),
    ("Check current Phase 1 string review packet", "python3 scripts/zigux/check-phase1-string-review-packet.py"),
    ("Self-test current Phase 1 route summary checker", "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test"),
    ("Check current Phase 1 route summary packet", "python3 scripts/zigux/check-phase1-route-summary-counts.py"),
    ("Self-test current Phase 1 bench checker", "python3 scripts/zigux/check-phase1-bench.py --self-test"),
)

PHASE1_TAIL_STEPS = (
    ("Self-test current Phase 1 shared reminder checker", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test"),
    ("Check current Phase 1 shared reminder packet", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py"),
    ("Self-test current Phase 1 closure validator", "python3 scripts/zigux/validate-phase1-closure.py --self-test"),
    ("Check current Phase 1 closure packet", "python3 scripts/zigux/validate-phase1-closure.py"),
)

LANE_STEPS = (
    ("Self-test current Phase 1 workflow viability checker", "python3 scripts/zigux/check-phase1-workflow-viability.py --self-test"),
    ("Check current Phase 1 workflow viability", "python3 scripts/zigux/check-phase1-workflow-viability.py"),
)

PHASE2_GENKSYMS_TAIL_STEPS = (
    ("Run current Phase 2 genksyms unit replay", "zig test scripts/zigux/genksyms.zig"),
    ("Run current Phase 2 genksyms make route", "make -C zigux phase2-genksyms"),
    ("Run current Phase 2 validate make route", "make -C zigux phase2-validate"),
    ("Validate current Phase 2 tool packet", "python3 scripts/zigux/validate-phase2.py"),
)

PHASE3_BUFFER_STEPS = (
    ("Self-test current Phase 3 interop packet", "python3 scripts/zigux/validate_phase3_selftest.py"),
    ("Check current Phase 3 interop packet", "python3 scripts/zigux/run-phase3-checks.py"),
    ("Run current Phase 3 policy starter-packet replay", "make -C zigux phase3-policy-starter-packet-test"),
    ("Run current Phase 3 policy dump replay", "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig"),
    ("Self-test current Phase 3 low-level wrapper survey validator", "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"),
    ("Check current Phase 3 low-level wrapper survey packet", "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    ("Run current Phase 3 low-level wrapper replay", "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"),
    ("Run current Phase 3 shared tests-root packet", "zig build phase3-test --build-file zigux/tests/build.zig"),
    ("Run current Phase 3 ABI dump replay", "zig build phase3-dump --build-file zigux/tests/build.zig"),
    ("Run current Phase 1 shared tests-root smoke", "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig"),
)

PHASE4_TAIL_STEPS = (
    ("Self-test current Phase 4 repo-reality warning checker", "python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test"),
    ("Check current Phase 4 repo-reality warning packet", "python3 scripts/zigux/check-phase4-repo-reality-warning.py"),
    ("Self-test current Phase 4 reversible-delivery pin checker", "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test"),
    ("Check current Phase 4 reversible-delivery pin packet", "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py"),
    ("Self-test current Phase 4 tests README checker", "python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test"),
    ("Check current Phase 4 tests README packet", "python3 scripts/zigux/check-phase4-tests-readme-packet.py"),
    ("Validate Phase 4 rollback routes", "make -C zigux phase4-validate"),
    ("Run Phase 4 rollback tests", "make -C zigux phase4-test"),
    ("Self-test current Phase 4 artifact-diff helper", "python3 scripts/zigux/artifact_diff.py --self-test"),
    ("Self-test current Phase 4 artifact-diff contract checker", "python3 scripts/zigux/check-artifact-diff-contract.py --self-test"),
    ("Check current Phase 4 artifact-diff contract packet", "python3 scripts/zigux/check-artifact-diff-contract.py"),
    ("Self-test current Phase 4 artifact-diff determinism checker", "python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test"),
    ("Check current Phase 4 artifact-diff determinism packet", "python3 scripts/zigux/check-phase4-artifact-diff-determinism.py"),
    ("Self-test current Phase 4 artifact-diff validator replay checker", "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test"),
    ("Check current Phase 4 artifact-diff validator replay packet", "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py"),
)

PHASE11_PACKET_STEPS = (
    ("Self-test current Phase 11 build inventory checker", "python3 scripts/zigux/check-phase11-build-inventory.py --self-test"),
    ("Check current Phase 11 build inventory packet", "python3 scripts/zigux/check-phase11-build-inventory.py"),
    ("Self-test current Phase 11 HVC cleanup current-head checker", "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test"),
    ("Check current Phase 11 HVC cleanup current-head packet", "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py"),
    ("Run current Phase 11 HVC hv_ops layout proof", "zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig"),
    ("Run current Phase 11 HVC export surface layout proof", "zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig"),
    ("Run current Phase 11 HVC cleanup packet proof", "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig"),
)

REQUIRED_FILE_RELS = (
    WORKFLOW_REL,
    NOTE_REL,
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-route-summary-counts.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("scripts/zigux/check-phase1-workflow-viability.py"),
    Path("scripts/zigux/genksyms.zig"),
    Path("scripts/zigux/validate-phase2.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    Path("scripts/zigux/check-phase4-repo-reality-warning.py"),
    Path("scripts/zigux/check-phase4-reversible-delivery-pins.py"),
    Path("scripts/zigux/check-phase4-tests-readme-packet.py"),
    Path("scripts/zigux/artifact_diff.py"),
    Path("scripts/zigux/check-artifact-diff-contract.py"),
    Path("scripts/zigux/check-phase4-artifact-diff-determinism.py"),
    Path("scripts/zigux/check-phase4-artifact-diff-validator-replays.py"),
    Path("scripts/zigux/check-phase11-build-inventory.py"),
    Path("scripts/zigux/check-phase11-hvc-cleanup-current-head.py"),
    Path("zigux/Makefile"),
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/phase3_policy_dump_build.zig"),
    Path("zigux/tests/phase3_low_level_wrappers_build.zig"),
    Path("zigux/tests/phase11_hvc_hv_ops_layout_build.zig"),
    Path("zigux/tests/phase11_hvc_export_surface_layout_build.zig"),
    Path("zigux/tests/phase11_hvc_cleanup_packet_build.zig"),
)

REQUIRED_NOTE_LINES = (
    "- `PHASE1_WORKFLOW_STATUS=active`",
    "- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 workflow-viability guard`",
    "- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-viability`",
    "- `PHASE1_WORKFLOW_PHASE1_PRE_BUFFER=Self-test current Phase 1 direct-owner checker,Check current Phase 1 direct-owner markers,Self-test current Phase 1 string review checker,Check current Phase 1 string review packet,Self-test current Phase 1 route summary checker,Check current Phase 1 route summary packet,Self-test current Phase 1 bench checker`",
    "- `PHASE1_WORKFLOW_PHASE1_TAIL=Self-test current Phase 1 shared reminder checker,Check current Phase 1 shared reminder packet,Self-test current Phase 1 closure validator,Check current Phase 1 closure packet`",
    "- `PHASE1_WORKFLOW_INSERTION_POINT=after current Phase 1 closure packet and before current Phase 3 interop packet`",
    "- `PHASE1_WORKFLOW_REQUIRED_ADJACENCY=Check current Phase 1 closure packet,Self-test current Phase 1 workflow viability checker,Check current Phase 1 workflow viability,Self-test current Phase 3 interop packet`",
    "- `PHASE1_WORKFLOW_PHASE2_GENKSYMS_TAIL=Run current Phase 2 genksyms unit replay,Run current Phase 2 genksyms make route,Run current Phase 2 validate make route,Validate current Phase 2 tool packet`",
    "- `PHASE1_WORKFLOW_PHASE3_BUFFER=Self-test current Phase 3 interop packet,Check current Phase 3 interop packet,Run current Phase 3 policy starter-packet replay,Run current Phase 3 policy dump replay,Self-test current Phase 3 low-level wrapper survey validator,Check current Phase 3 low-level wrapper survey packet,Run current Phase 3 low-level wrapper replay,Run current Phase 3 shared tests-root packet,Run current Phase 3 ABI dump replay,Run current Phase 1 shared tests-root smoke`",
    "- `PHASE1_WORKFLOW_PHASE4_TAIL=Self-test current Phase 4 repo-reality warning checker,Check current Phase 4 repo-reality warning packet,Self-test current Phase 4 reversible-delivery pin checker,Check current Phase 4 reversible-delivery pin packet,Self-test current Phase 4 tests README checker,Check current Phase 4 tests README packet,Validate Phase 4 rollback routes,Run Phase 4 rollback tests,Self-test current Phase 4 artifact-diff helper,Self-test current Phase 4 artifact-diff contract checker,Check current Phase 4 artifact-diff contract packet,Self-test current Phase 4 artifact-diff determinism checker,Check current Phase 4 artifact-diff determinism packet,Self-test current Phase 4 artifact-diff validator replay checker,Check current Phase 4 artifact-diff validator replay packet`",
    "- `PHASE1_WORKFLOW_PHASE11_PACKET=Self-test current Phase 11 build inventory checker,Check current Phase 11 build inventory packet,Self-test current Phase 11 HVC cleanup current-head checker,Check current Phase 11 HVC cleanup current-head packet,Run current Phase 11 HVC hv_ops layout proof,Run current Phase 11 HVC export surface layout proof,Run current Phase 11 HVC cleanup packet proof`",
    "- `PHASE1_WORKFLOW_FORBIDDEN_HISTORICAL_SNIPPETS=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zig build test --build-file zigux/tests/build.zig,zig build bench --build-file zigux/tests/build.zig,make -C zigux phase1-validate,make -C zigux phase1-test,make -C zigux phase1-bench`",
)

FORBIDDEN_WORKFLOW_SNIPPETS = (
    "python3 scripts/zigux/validate-phase1.py",
    "python3 scripts/zigux/check-phase1-parity.py",
    "zig build test --build-file zigux/tests/build.zig",
    "zig build bench --build-file zigux/tests/build.zig",
    "make -C zigux phase1-validate",
    "make -C zigux phase1-test",
    "make -C zigux phase1-bench",
)

STEP_GROUPS = (
    PHASE1_PRE_BUFFER_STEPS,
    PHASE1_TAIL_STEPS,
    LANE_STEPS,
    PHASE2_GENKSYMS_TAIL_STEPS,
    PHASE3_BUFFER_STEPS,
    PHASE4_TAIL_STEPS,
    PHASE11_PACKET_STEPS,
)

WORKFLOW_BUILD_GROUPS = (
    PHASE2_GENKSYMS_TAIL_STEPS,
    PHASE1_PRE_BUFFER_STEPS,
    PHASE1_TAIL_STEPS,
    LANE_STEPS,
    PHASE3_BUFFER_STEPS,
    PHASE4_TAIL_STEPS,
    PHASE11_PACKET_STEPS,
)

STRICT_ORDER = (
    "Run current Phase 2 genksyms unit replay",
    "Run current Phase 2 genksyms make route",
    "Run current Phase 2 validate make route",
    "Validate current Phase 2 tool packet",
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
    "Self-test current Phase 1 workflow viability checker",
    "Check current Phase 1 workflow viability",
    "Self-test current Phase 3 interop packet",
    "Check current Phase 3 interop packet",
    "Run current Phase 3 policy starter-packet replay",
    "Run current Phase 3 policy dump replay",
    "Self-test current Phase 3 low-level wrapper survey validator",
    "Check current Phase 3 low-level wrapper survey packet",
    "Run current Phase 3 low-level wrapper replay",
    "Run current Phase 3 shared tests-root packet",
    "Run current Phase 3 ABI dump replay",
    "Run current Phase 1 shared tests-root smoke",
    "Self-test current Phase 4 repo-reality warning checker",
    "Check current Phase 4 repo-reality warning packet",
    "Self-test current Phase 4 reversible-delivery pin checker",
    "Check current Phase 4 reversible-delivery pin packet",
    "Self-test current Phase 4 tests README checker",
    "Check current Phase 4 tests README packet",
    "Validate Phase 4 rollback routes",
    "Run Phase 4 rollback tests",
    "Self-test current Phase 4 artifact-diff helper",
    "Self-test current Phase 4 artifact-diff contract checker",
    "Check current Phase 4 artifact-diff contract packet",
    "Self-test current Phase 4 artifact-diff determinism checker",
    "Check current Phase 4 artifact-diff determinism packet",
    "Self-test current Phase 4 artifact-diff validator replay checker",
    "Check current Phase 4 artifact-diff validator replay packet",
    "Self-test current Phase 11 build inventory checker",
    "Check current Phase 11 build inventory packet",
    "Self-test current Phase 11 HVC cleanup current-head checker",
    "Check current Phase 11 HVC cleanup current-head packet",
    "Run current Phase 11 HVC hv_ops layout proof",
    "Run current Phase 11 HVC export surface layout proof",
    "Run current Phase 11 HVC cleanup packet proof",
)

LANE_ADJACENT_CHAIN = (
    "Check current Phase 1 closure packet",
    "Self-test current Phase 1 workflow viability checker",
    "Check current Phase 1 workflow viability",
    "Self-test current Phase 3 interop packet",
)


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def count_exact_line(text: str, line: str) -> int:
    return sum(1 for current in text.splitlines() if current == line)


def require_once(text: str, label: str, line: str) -> list[str]:
    count = count_exact_line(text, line)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_step(workflow_text: str, step_name: str, run_command: str) -> list[str]:
    failures: list[str] = []
    failures.extend(require_once(workflow_text, f"workflow_step:{step_name}", f"      - name: {step_name}"))
    failures.extend(require_once(workflow_text, f"workflow_run:{step_name}", f"        run: {run_command}"))
    return failures


def require_order(workflow_text: str, step_names: tuple[str, ...]) -> list[str]:
    positions: list[int] = []
    for step_name in step_names:
        needle = f"- name: {step_name}"
        position = workflow_text.find(needle)
        if position == -1:
            return [f"workflow_order:missing:{step_name}"]
        positions.append(position)
    return [] if positions == sorted(positions) else ["workflow_order:out_of_order"]


def workflow_step_names(workflow_text: str) -> list[str]:
    prefix = "      - name: "
    return [line[len(prefix) :] for line in workflow_text.splitlines() if line.startswith(prefix)]


def require_adjacent_chain(workflow_text: str, step_names: tuple[str, ...]) -> list[str]:
    names = workflow_step_names(workflow_text)
    chain = list(step_names)
    for index in range(len(names) - len(chain) + 1):
        if names[index : index + len(chain)] == chain:
            return []
    return [f"workflow_adjacent_chain:missing:{'->'.join(step_names)}"]


def require_file_path(root: Path, relative_path: Path) -> list[str]:
    path = root / relative_path
    if not path.exists():
        return [f"missing_file:{relative_path.as_posix()}"]
    if not path.is_file():
        return [f"non_file_path:{relative_path.as_posix()}"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILE_RELS:
        failures.extend(require_file_path(root, relative_path))
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    note_text = load_text(root, NOTE_REL)

    for line in REQUIRED_NOTE_LINES:
        failures.extend(require_once(note_text, "note", line))

    for group in STEP_GROUPS:
        for step_name, run_command in group:
            failures.extend(require_step(workflow_text, step_name, run_command))

    failures.extend(require_adjacent_chain(workflow_text, LANE_ADJACENT_CHAIN))
    failures.extend(require_order(workflow_text, STRICT_ORDER))

    for forbidden in FORBIDDEN_WORKFLOW_SNIPPETS:
        if forbidden in workflow_text:
            failures.append(f"workflow_forbidden:{forbidden}:unexpected_present")

    return failures


def build_note_text() -> str:
    lines = [
        "# Phase 1 Workflow Viability",
        "",
        *REQUIRED_NOTE_LINES,
        "- keep the lane scoped to the current closure-validator-plus-viability packet instead of reviving the older validator-first, parity, or make-route Phase 1 replay family.",
        "- keep the current Phase 2 genksyms unit, make-route, validate-route, and tool-packet ladder intact when the lane is replayed onto newer workflow heads.",
        "- keep the workflow-viability pair immediately after the current Phase 1 closure packet so the lane stays additive to the live Phase 3 buffer instead of replacing it.",
        "- keep the current Phase 11 build-inventory and HVC cleanup packet explicit later in the workflow so a replayed lane branch cannot silently drop those newer checks.",
        "- if the workflow moves again, refresh this same three-file packet first instead of widening into unrelated Phase 1 reminder or closure lanes.",
        "",
    ]
    return "\n".join(lines)


def build_sample_workflow_text() -> str:
    lines = [
        "name: zigux-bootstrap",
        "",
        "jobs:",
        "  bootstrap:",
        "    runs-on: ubuntu-latest",
        "    steps:",
        "",
    ]
    for group in WORKFLOW_BUILD_GROUPS:
        for step_name, run_command in group:
            lines.append(f"      - name: {step_name}")
            lines.append(f"        run: {run_command}")
            lines.append("")
    return "\n".join(lines)


def build_sample_repo(root: Path) -> None:
    write_file(root, WORKFLOW_REL, build_sample_workflow_text())
    write_file(root, NOTE_REL, build_note_text())
    for relative_path in REQUIRED_FILE_RELS[2:]:
        write_file(root, relative_path, "# placeholder\n")


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    build_sample_repo(root)


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

        sample_root = root / "written-sample-root"
        write_sample_root(sample_root)
        if collect_failures(sample_root):
            print("self-test:write_sample_root_output_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        missing_path = root / "scripts/zigux/check-phase11-build-inventory.py"
        missing_path.unlink()
        failures = collect_failures(root)
        if "missing_file:scripts/zigux/check-phase11-build-inventory.py" not in failures:
            print("self-test:expected_missing_phase11_file_failure")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path = root / WORKFLOW_REL
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            rewrite_once(
                workflow_text,
                "      - name: Self-test current Phase 1 workflow viability checker\n",
                "      - name: Lane drift interposer\n        run: python3 drift.py\n\n      - name: Self-test current Phase 1 workflow viability checker\n",
            ),
            encoding="utf-8",
        )
        failures = collect_failures(root)
        if not any(failure.startswith("workflow_adjacent_chain:missing:") for failure in failures):
            print("self-test:expected_adjacent_chain_failure")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path = root / WORKFLOW_REL
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            workflow_text + "      - name: Run current Phase 2 genksyms make route\n        run: make -C zigux phase2-genksyms\n",
            encoding="utf-8",
        )
        failures = collect_failures(root)
        if "workflow_step:Run current Phase 2 genksyms make route:expected=1:actual=2" not in failures:
            print("self-test:expected_duplicate_phase2_genksyms_step_failure")
            return 1
        if "workflow_run:Run current Phase 2 genksyms make route:expected=1:actual=2" not in failures:
            print("self-test:expected_duplicate_phase2_genksyms_run_failure")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path = root / WORKFLOW_REL
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            workflow_text + "      - name: Self-test current Phase 11 build inventory checker\n        run: python3 scripts/zigux/check-phase11-build-inventory.py --self-test\n",
            encoding="utf-8",
        )
        failures = collect_failures(root)
        if "workflow_step:Self-test current Phase 11 build inventory checker:expected=1:actual=2" not in failures:
            print("self-test:expected_duplicate_phase11_step_failure")
            return 1
        case_count += 1

        build_sample_repo(root)
        note_path = root / NOTE_REL
        note_text = note_path.read_text(encoding="utf-8")
        note_path.write_text(
            rewrite_once(
                note_text,
                "- `PHASE1_WORKFLOW_PHASE11_PACKET=Self-test current Phase 11 build inventory checker,Check current Phase 11 build inventory packet,Self-test current Phase 11 HVC cleanup current-head checker,Check current Phase 11 HVC cleanup current-head packet,Run current Phase 11 HVC hv_ops layout proof,Run current Phase 11 HVC export surface layout proof,Run current Phase 11 HVC cleanup packet proof`\n",
            ),
            encoding="utf-8",
        )
        failures = collect_failures(root)
        if "note:expected=1:actual=0" not in failures:
            print("self-test:expected_missing_phase11_note_failure")
            return 1
        case_count += 1

        build_sample_repo(root)
        note_path = root / NOTE_REL
        note_text = note_path.read_text(encoding="utf-8")
        duplicate = "- `PHASE1_WORKFLOW_PHASE2_GENKSYMS_TAIL=Run current Phase 2 genksyms unit replay,Run current Phase 2 genksyms make route,Run current Phase 2 validate make route,Validate current Phase 2 tool packet`\n"
        note_path.write_text(note_text + duplicate, encoding="utf-8")
        failures = collect_failures(root)
        if "note:expected=1:actual=2" not in failures:
            print("self-test:expected_duplicate_phase2_note_failure")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path = root / WORKFLOW_REL
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            workflow_text + "      - name: Historical validator\n        run: python3 scripts/zigux/validate-phase1.py\n",
            encoding="utf-8",
        )
        failures = collect_failures(root)
        if "workflow_forbidden:python3 scripts/zigux/validate-phase1.py:unexpected_present" not in failures:
            print("self-test:expected_forbidden_failure")
            return 1
        case_count += 1

    print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_VIABILITY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument("--write-sample-root", type=Path, help="write a sample repository root and exit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"phase1-workflow-viability:sample-root-written:{args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("phase1-workflow-viability:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
