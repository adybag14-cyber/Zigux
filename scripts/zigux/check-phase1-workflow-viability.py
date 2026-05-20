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

LANE_ADJACENT_CHAIN = (
    "Check current Phase 1 closure packet",
    "Self-test current Phase 1 workflow viability checker",
    "Check current Phase 1 workflow viability",
    "Self-test current Phase 3 interop packet",
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

REQUIRED_FILE_RELS = (
    WORKFLOW_REL,
    NOTE_REL,
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("scripts/zigux/check-phase1-workflow-viability.py"),
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
    Path("zigux/Makefile"),
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/phase3_policy_dump_build.zig"),
    Path("zigux/tests/phase3_low_level_wrappers_build.zig"),
)

REQUIRED_NOTE_LINES = (
    "- `PHASE1_WORKFLOW_STATUS=active`",
    "- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 workflow-viability guard`",
    "- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-viability`",
    "- `PHASE1_WORKFLOW_PHASE1_TAIL=Self-test current Phase 1 shared reminder checker,Check current Phase 1 shared reminder packet,Self-test current Phase 1 closure validator,Check current Phase 1 closure packet`",
    "- `PHASE1_WORKFLOW_INSERTION_POINT=after current Phase 1 closure packet and before current Phase 3 interop packet`",
    "- `PHASE1_WORKFLOW_REQUIRED_ADJACENCY=Check current Phase 1 closure packet,Self-test current Phase 1 workflow viability checker,Check current Phase 1 workflow viability,Self-test current Phase 3 interop packet`",
    "- `PHASE1_WORKFLOW_PHASE3_BUFFER=Self-test current Phase 3 interop packet,Check current Phase 3 interop packet,Run current Phase 3 policy starter-packet replay,Run current Phase 3 policy dump replay,Self-test current Phase 3 low-level wrapper survey validator,Check current Phase 3 low-level wrapper survey packet,Run current Phase 3 low-level wrapper replay,Run current Phase 3 shared tests-root packet,Run current Phase 3 ABI dump replay,Run current Phase 1 shared tests-root smoke`",
    "- `PHASE1_WORKFLOW_PHASE4_TAIL=Self-test current Phase 4 repo-reality warning checker,Check current Phase 4 repo-reality warning packet,Self-test current Phase 4 reversible-delivery pin checker,Check current Phase 4 reversible-delivery pin packet,Self-test current Phase 4 tests README checker,Check current Phase 4 tests README packet,Validate Phase 4 rollback routes,Run Phase 4 rollback tests,Self-test current Phase 4 artifact-diff helper,Self-test current Phase 4 artifact-diff contract checker,Check current Phase 4 artifact-diff contract packet,Self-test current Phase 4 artifact-diff determinism checker,Check current Phase 4 artifact-diff determinism packet,Self-test current Phase 4 artifact-diff validator replay checker,Check current Phase 4 artifact-diff validator replay packet`",
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
    names: list[str] = []
    prefix = "      - name: "
    for line in workflow_text.splitlines():
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

    for step_name, run_command in PHASE1_TAIL_STEPS + LANE_STEPS + PHASE3_BUFFER_STEPS + PHASE4_TAIL_STEPS:
        failures.extend(require_step(workflow_text, step_name, run_command))

    failures.extend(require_adjacent_chain(workflow_text, LANE_ADJACENT_CHAIN))

    strict_order = (
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
    )
    failures.extend(require_order(workflow_text, strict_order))

    for forbidden in FORBIDDEN_WORKFLOW_SNIPPETS:
        if forbidden in workflow_text:
            failures.append(f"workflow_forbidden:{forbidden}:unexpected_present")

    return failures


def build_note_text() -> str:
    return "\n".join(
        (
            "# Phase 1 Workflow Viability",
            "",
            *REQUIRED_NOTE_LINES,
            "- keep the lane scoped to the current closure-validator-plus-viability packet instead of reviving the older validator-first, parity, or make-route Phase 1 replay family.",
            "- keep the workflow-viability pair immediately after the current Phase 1 closure packet, then preserve the current Phase 3 policy starter and dump replays before the low-level-wrapper block.",
            "- keep the current Phase 4 repo-reality, reversible-delivery, tests-README, rollback, and artifact-diff checks explicit after the Phase 3 buffer when this packet is replayed.",
            "- if the workflow moves again, refresh this same three-file packet first instead of widening into unrelated Phase 1 reminder or closure lanes.",
            "",
        )
    )


def build_workflow_text() -> str:
    lines = ["name: zigux-bootstrap", "", "jobs:", "  bootstrap:", "    runs-on: ubuntu-latest", "    steps:", ""]
    for step_name, run_command in PHASE1_TAIL_STEPS + LANE_STEPS + PHASE3_BUFFER_STEPS + PHASE4_TAIL_STEPS:
        lines.append(f"      - name: {step_name}")
        lines.append(f"        run: {run_command}")
        lines.append("")
    return "\n".join(lines)


def build_sample_repo(root: Path) -> None:
    write_file(root, WORKFLOW_REL, build_workflow_text())
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
        workflow_path = root / WORKFLOW_REL
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            rewrite_once(
                workflow_text,
                "      - name: Self-test current Phase 1 workflow viability checker\n        run: python3 scripts/zigux/check-phase1-workflow-viability.py --self-test\n",
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
        inserted = (
            "      - name: Legacy inserted drift\n"
            "        run: python3 legacy.py\n\n"
            "      - name: Self-test current Phase 1 workflow viability checker\n"
        )
        workflow_path.write_text(
            rewrite_once(
                workflow_text,
                "      - name: Self-test current Phase 1 workflow viability checker\n",
                inserted,
            ),
            encoding="utf-8",
        )
        failures = collect_failures(root)
        if not any(
            failure.startswith("workflow_step:Self-test current Phase 1 workflow viability checker:expected=1:actual=2")
            or failure.startswith("workflow_adjacent_chain:missing:")
            for failure in failures
        ):
            print("self-test:expected_duplicate_or_chain_failure")
            return 1
        case_count += 1

        build_sample_repo(root)
        note_path = root / NOTE_REL
        note_text = note_path.read_text(encoding="utf-8")
        note_path.write_text(
            rewrite_once(
                note_text,
                "- `PHASE1_WORKFLOW_REQUIRED_ADJACENCY=Check current Phase 1 closure packet,Self-test current Phase 1 workflow viability checker,Check current Phase 1 workflow viability,Self-test current Phase 3 interop packet`\n",
            ),
            encoding="utf-8",
        )
        failures = collect_failures(root)
        if not any(failure.startswith("note:expected=1:actual=0") for failure in failures):
            print("self-test:expected_note_failure")
            return 1
        case_count += 1

        duplicate_note_lines = (
            "- `PHASE1_WORKFLOW_REQUIRED_ADJACENCY=Check current Phase 1 closure packet,Self-test current Phase 1 workflow viability checker,Check current Phase 1 workflow viability,Self-test current Phase 3 interop packet`\n",
            "- `PHASE1_WORKFLOW_STATUS=active`\n",
            "- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 workflow-viability guard`\n",
            "- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-viability`\n",
            "- `PHASE1_WORKFLOW_INSERTION_POINT=after current Phase 1 closure packet and before current Phase 3 interop packet`\n",
            "- `PHASE1_WORKFLOW_PHASE1_TAIL=Self-test current Phase 1 shared reminder checker,Check current Phase 1 shared reminder packet,Self-test current Phase 1 closure validator,Check current Phase 1 closure packet`\n",
            "- `PHASE1_WORKFLOW_PHASE3_BUFFER=Self-test current Phase 3 interop packet,Check current Phase 3 interop packet,Run current Phase 3 policy starter-packet replay,Run current Phase 3 policy dump replay,Self-test current Phase 3 low-level wrapper survey validator,Check current Phase 3 low-level wrapper survey packet,Run current Phase 3 low-level wrapper replay,Run current Phase 3 shared tests-root packet,Run current Phase 3 ABI dump replay,Run current Phase 1 shared tests-root smoke`\n",
            "- `PHASE1_WORKFLOW_PHASE4_TAIL=Self-test current Phase 4 repo-reality warning checker,Check current Phase 4 repo-reality warning packet,Self-test current Phase 4 reversible-delivery pin checker,Check current Phase 4 reversible-delivery pin packet,Self-test current Phase 4 tests README checker,Check current Phase 4 tests README packet,Validate Phase 4 rollback routes,Run Phase 4 rollback tests,Self-test current Phase 4 artifact-diff helper,Self-test current Phase 4 artifact-diff contract checker,Check current Phase 4 artifact-diff contract packet,Self-test current Phase 4 artifact-diff determinism checker,Check current Phase 4 artifact-diff determinism packet,Self-test current Phase 4 artifact-diff validator replay checker,Check current Phase 4 artifact-diff validator replay packet`\n",
            "- `PHASE1_WORKFLOW_FORBIDDEN_HISTORICAL_SNIPPETS=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zig build test --build-file zigux/tests/build.zig,zig build bench --build-file zigux/tests/build.zig,make -C zigux phase1-validate,make -C zigux phase1-test,make -C zigux phase1-bench`\n",
        )
        for duplicate_line in duplicate_note_lines:
            build_sample_repo(root)
            note_path = root / NOTE_REL
            note_text = note_path.read_text(encoding="utf-8")
            note_path.write_text(note_text + duplicate_line, encoding="utf-8")
            failures = collect_failures(root)
            if "note:expected=1:actual=2" not in failures:
                print("self-test:duplicate_note_line_not_detected")
                return 1
            case_count += 1

        duplicate_workflow_checks = (
            (
                "Check current Phase 1 shared reminder packet",
                "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
                "duplicate_shared_reminder",
            ),
            (
                "Check current Phase 1 closure packet",
                "python3 scripts/zigux/validate-phase1-closure.py",
                "duplicate_closure",
            ),
            (
                "Self-test current Phase 1 workflow viability checker",
                "python3 scripts/zigux/check-phase1-workflow-viability.py --self-test",
                "duplicate_lane_selftest",
            ),
            (
                "Check current Phase 1 workflow viability",
                "python3 scripts/zigux/check-phase1-workflow-viability.py",
                "duplicate_lane_check",
            ),
            (
                "Self-test current Phase 3 interop packet",
                "python3 scripts/zigux/validate_phase3_selftest.py",
                "duplicate_phase3_interop_selftest",
            ),
            (
                "Run current Phase 3 policy starter-packet replay",
                "make -C zigux phase3-policy-starter-packet-test",
                "duplicate_phase3_policy_starter",
            ),
            (
                "Run current Phase 3 policy dump replay",
                "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
                "duplicate_phase3_policy_dump",
            ),
            (
                "Run current Phase 1 shared tests-root smoke",
                "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
                "duplicate_phase1_smoke",
            ),
            (
                "Validate Phase 4 rollback routes",
                "make -C zigux phase4-validate",
                "duplicate_phase4_validate",
            ),
            (
                "Self-test current Phase 4 artifact-diff helper",
                "python3 scripts/zigux/artifact_diff.py --self-test",
                "duplicate_phase4_helper",
            ),
            (
                "Self-test current Phase 4 artifact-diff contract checker",
                "python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
                "duplicate_phase4_contract_selftest",
            ),
            (
                "Check current Phase 4 artifact-diff contract packet",
                "python3 scripts/zigux/check-artifact-diff-contract.py",
                "duplicate_phase4_contract_check",
            ),
            (
                "Check current Phase 4 artifact-diff validator replay packet",
                "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
                "duplicate_phase4_validator",
            ),
        )
        for step_name, run_command, label in duplicate_workflow_checks:
            build_sample_repo(root)
            workflow_path = root / WORKFLOW_REL
            workflow_text = workflow_path.read_text(encoding="utf-8")
            workflow_path.write_text(
                workflow_text + f"      - name: {step_name}\n        run: {run_command}\n",
                encoding="utf-8",
            )
            failures = collect_failures(root)
            if f"workflow_step:{step_name}:expected=1:actual=2" not in failures:
                print(f"self-test:{label}_step_not_detected")
                return 1
            if f"workflow_run:{step_name}:expected=1:actual=2" not in failures:
                print(f"self-test:{label}_run_not_detected")
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
        if not any(failure == "workflow_forbidden:python3 scripts/zigux/validate-phase1.py:unexpected_present" for failure in failures):
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
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a current-like sample repository root for replay and exit",
    )
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
