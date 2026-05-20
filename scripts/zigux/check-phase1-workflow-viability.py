#!/usr/bin/env python3
"""Guard the current master Phase 1 workflow-viability packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

PHASE3_CHAIN = (
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
        "Run current Phase 3 policy starter-packet replay",
        "make -C zigux phase3-policy-starter-packet-test",
    ),
    (
        "Run current Phase 3 policy dump replay",
        "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    ),
    (
        "Self-test current Phase 3 low-level wrapper survey validator",
        "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    ),
    (
        "Check current Phase 3 low-level wrapper survey packet",
        "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    ),
    (
        "Run current Phase 3 low-level wrapper replay",
        "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
    (
        "Run current Phase 3 shared tests-root packet",
        "zig build phase3-test --build-file zigux/tests/build.zig",
    ),
    (
        "Run current Phase 3 ABI dump replay",
        "zig build phase3-dump --build-file zigux/tests/build.zig",
    ),
    (
        "Run current Phase 1 shared tests-root smoke",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
)

PHASE4_CHAIN = (
    (
        "Self-test current Phase 4 repo-reality warning checker",
        "python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
    ),
    (
        "Check current Phase 4 repo-reality warning packet",
        "python3 scripts/zigux/check-phase4-repo-reality-warning.py",
    ),
    (
        "Self-test current Phase 4 reversible-delivery pin checker",
        "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test",
    ),
    (
        "Check current Phase 4 reversible-delivery pin packet",
        "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py",
    ),
    (
        "Self-test current Phase 4 tests README checker",
        "python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test",
    ),
    (
        "Check current Phase 4 tests README packet",
        "python3 scripts/zigux/check-phase4-tests-readme-packet.py",
    ),
    ("Validate Phase 4 rollback routes", "make -C zigux phase4-validate"),
    ("Run Phase 4 rollback tests", "make -C zigux phase4-test"),
    (
        "Self-test current Phase 4 artifact-diff helper",
        "python3 scripts/zigux/artifact_diff.py --self-test",
    ),
    (
        "Self-test current Phase 4 artifact-diff contract checker",
        "python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
    ),
    (
        "Check current Phase 4 artifact-diff contract packet",
        "python3 scripts/zigux/check-artifact-diff-contract.py",
    ),
    (
        "Self-test current Phase 4 artifact-diff determinism checker",
        "python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    ),
    (
        "Check current Phase 4 artifact-diff determinism packet",
        "python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
    ),
    (
        "Self-test current Phase 4 artifact-diff validator replay checker",
        "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
    ),
    (
        "Check current Phase 4 artifact-diff validator replay packet",
        "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
    ),
)

PHASE6_CHAIN = (
    ("Validate current Phase 6 helper packet", "make -C zigux phase6-validate"),
    (
        "Run current Phase 6 leaf helper tests",
        "zig build test --build-file zigux/tests/phase6_build.zig --summary all",
    ),
    ("Run current Phase 6 shared perf route", "make -C zigux phase6-perf"),
)

PHASE8_CHAIN = (
    ("Validate Phase 8 tooling routes", "make -C zigux phase8-validate"),
    ("Run focused Phase 8 exec-cmd tests", "make -C zigux phase8-exec-cmd-test"),
    ("Run Phase 8 tooling tests", "make -C zigux phase8-test"),
)

PHASE9_CHAIN = (
    (
        "Self-test current Phase 9 review-checklist boundaries checker",
        "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test",
    ),
    (
        "Check current Phase 9 review-checklist boundaries packet",
        "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
    ),
    (
        "Self-test current Phase 9 freeze-map study-boundaries checker",
        "python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py --self-test",
    ),
    (
        "Check current Phase 9 freeze-map study-boundaries packet",
        "python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py",
    ),
    (
        "Self-test current Phase 9 trace-events runtime packet checker",
        "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test",
    ),
    (
        "Check current Phase 9 trace-events runtime packet",
        "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py",
    ),
    (
        "Run current Phase 9 trace-events runtime sample tests",
        "zig test samples/zigux/runtime_trace_events.zig",
    ),
    (
        "Run current Phase 9 unregistered gate companion tests",
        "zig test samples/zigux/runtime_trace_events_unregistered_gate.zig",
    ),
    (
        "Run current Phase 9 exit rollback guard companion tests",
        "zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
    ),
    (
        "Run current Phase 9 registration reentry companion tests",
        "zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
    ),
    (
        "Run current Phase 9 trace-events survey witness",
        "zig test zigux/tests/runtime_trace_events_survey.zig",
    ),
)

PHASE7_CHAIN = (
    (
        "Self-test current Phase 7 shared-control gap checker",
        "python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test",
    ),
    (
        "Check current Phase 7 shared-control gap packet",
        "python3 scripts/zigux/check-phase7-shared-control-gap.py",
    ),
)

PHASE10_TO_14_CHAIN = (
    (
        "Self-test current Phase 10 bootstrap route checker",
        "python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test",
    ),
    (
        "Check current Phase 10 bootstrap route",
        "python3 scripts/zigux/check-phase10-bootstrap-route.py",
    ),
    (
        "Validate Phase 10 checker-backed review packet",
        "make -C zigux phase10-validate",
    ),
    ("Run Phase 10 helper tests", "make -C zigux phase10-test"),
    ("Validate current Phase 11 support bundle", "make -C zigux phase11-validate"),
    (
        "Self-test current Phase 12 build-only surface checker",
        "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    ),
    (
        "Check current Phase 12 build-only surface",
        "python3 scripts/zigux/check-build-only-phase12-surface.py",
    ),
    (
        "Self-test current Phase 12 release-readiness packet checker",
        "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    ),
    (
        "Check current Phase 12 release-readiness packet",
        "python3 scripts/zigux/check-phase12-release-readiness-packet.py",
    ),
    (
        "Validate current Phase 12 support bundle",
        "python3 scripts/zigux/validate-phase12.py",
    ),
    ("Run current Phase 12 smoke packet", "make -C zigux phase12-smoke"),
    ("Run current Phase 12 shared test packet", "make -C zigux phase12-test"),
    ("Run current Phase 12 aggregate route", "make -C zigux phase12"),
    (
        "Self-test current Phase 14 shared smoke route checker",
        "python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    ),
    ("Run current Phase 14 validate route", "make -C zigux phase14-validate"),
    (
        "Run current Phase 12 throughput-parity anchor",
        "zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
    ),
)

REQUIRED_FILE_RELS = (
    WORKFLOW_REL,
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    Path("zigux/tests/phase3_policy_dump_build.zig"),
    Path("zigux/tests/phase3_low_level_wrappers_build.zig"),
    Path("zigux/tests/build.zig"),
    Path("scripts/zigux/check-phase4-repo-reality-warning.py"),
    Path("scripts/zigux/check-phase4-reversible-delivery-pins.py"),
    Path("scripts/zigux/check-phase4-tests-readme-packet.py"),
    Path("scripts/zigux/artifact_diff.py"),
    Path("scripts/zigux/check-artifact-diff-contract.py"),
    Path("scripts/zigux/check-phase4-artifact-diff-determinism.py"),
    Path("scripts/zigux/check-phase4-artifact-diff-validator-replays.py"),
    Path("zigux/tests/phase6_build.zig"),
    Path("scripts/zigux/check-phase9-review-checklist-phase-boundaries.py"),
    Path("scripts/zigux/check-phase9-freeze-map-study-boundaries.py"),
    Path("scripts/zigux/check-phase9-trace-events-runtime-packet.py"),
    Path("samples/zigux/runtime_trace_events.zig"),
    Path("samples/zigux/runtime_trace_events_unregistered_gate.zig"),
    Path("samples/zigux/runtime_trace_events_exit_rollback_guard.zig"),
    Path("samples/zigux/runtime_trace_events_registration_reentry_gate.zig"),
    Path("zigux/tests/runtime_trace_events_survey.zig"),
    Path("scripts/zigux/check-phase7-shared-control-gap.py"),
    Path("scripts/zigux/check-phase10-bootstrap-route.py"),
    Path("scripts/zigux/check-build-only-phase12-surface.py"),
    Path("scripts/zigux/check-phase12-release-readiness-packet.py"),
    Path("scripts/zigux/validate-phase12.py"),
    Path("scripts/zigux/check-phase14-shared-smoke-route.py"),
    Path("zigux/Makefile"),
)


def all_steps() -> tuple[tuple[str, str], ...]:
    return (
        PHASE3_CHAIN
        + PHASE4_CHAIN
        + PHASE6_CHAIN
        + PHASE8_CHAIN
        + PHASE9_CHAIN
        + PHASE7_CHAIN
        + PHASE10_TO_14_CHAIN
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
    failures.extend(
        require_once(
            workflow_text,
            f"workflow_step:{step_name}",
            f"      - name: {step_name}",
        )
    )
    pair = f"      - name: {step_name}\n        run: {run_command}"
    pair_count = workflow_text.count(pair)
    if pair_count != 1:
        failures.append(f"workflow_run:{step_name}:expected=1:actual={pair_count}")
    return failures


def workflow_step_names(workflow_text: str) -> list[str]:
    prefix = "      - name: "
    return [line[len(prefix) :] for line in workflow_text.splitlines() if line.startswith(prefix)]


def require_adjacent_chain(workflow_text: str, chain: tuple[tuple[str, str], ...], label: str) -> list[str]:
    names = workflow_step_names(workflow_text)
    expected = [step_name for step_name, _ in chain]
    max_start = len(names) - len(expected) + 1
    for index in range(max_start):
        if names[index : index + len(expected)] == expected:
            return []
    return [f"{label}:missing:{'->'.join(expected)}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILE_RELS:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    for step_name, run_command in all_steps():
        failures.extend(require_step(workflow_text, step_name, run_command))

    failures.extend(require_adjacent_chain(workflow_text, PHASE3_CHAIN, "phase3_chain"))
    failures.extend(require_adjacent_chain(workflow_text, PHASE4_CHAIN, "phase4_chain"))
    failures.extend(require_adjacent_chain(workflow_text, PHASE6_CHAIN, "phase6_chain"))
    failures.extend(require_adjacent_chain(workflow_text, PHASE8_CHAIN, "phase8_chain"))
    failures.extend(require_adjacent_chain(workflow_text, PHASE9_CHAIN, "phase9_chain"))
    failures.extend(require_adjacent_chain(workflow_text, PHASE7_CHAIN, "phase7_chain"))
    failures.extend(require_adjacent_chain(workflow_text, PHASE10_TO_14_CHAIN, "phase10_to_14_chain"))
    return failures


def build_workflow_text() -> str:
    lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    runs-on: ubuntu-latest",
        "    steps:",
    ]
    for step_name, run_command in all_steps():
        lines.append(f"      - name: {step_name}")
        lines.append(f"        run: {run_command}")
    lines.append("")
    return "\n".join(lines)


def build_sample_repo(root: Path) -> None:
    write_file(root, WORKFLOW_REL, build_workflow_text())
    for relative_path in REQUIRED_FILE_RELS[1:]:
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

        workflow_text = load_text(root, WORKFLOW_REL)
        write_file(
            root,
            WORKFLOW_REL,
            rewrite_once(
                workflow_text,
                "      - name: Check current Phase 1 closure packet\n",
            ),
        )
        failures = collect_failures(root)
        if "workflow_step:Check current Phase 1 closure packet:expected=1:actual=0" not in failures:
            print("self-test:missing_phase1_closure_step_not_detected")
            return 1
        case_count += 1
        build_sample_repo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        duplicate_block = (
            "      - name: Run current Phase 3 shared tests-root packet\n"
            "        run: zig build phase3-test --build-file zigux/tests/build.zig\n"
        )
        write_file(root, WORKFLOW_REL, workflow_text + duplicate_block)
        failures = collect_failures(root)
        if "workflow_step:Run current Phase 3 shared tests-root packet:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase3_shared_tests_step_not_detected")
            return 1
        if "workflow_run:Run current Phase 3 shared tests-root packet:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase3_shared_tests_run_not_detected")
            return 1
        case_count += 1
        build_sample_repo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        duplicate_block = (
            "      - name: Self-test current Phase 4 artifact-diff contract checker\n"
            "        run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test\n"
        )
        write_file(root, WORKFLOW_REL, workflow_text + duplicate_block)
        failures = collect_failures(root)
        if "workflow_step:Self-test current Phase 4 artifact-diff contract checker:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase4_contract_selftest_step_not_detected")
            return 1
        if "workflow_run:Self-test current Phase 4 artifact-diff contract checker:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase4_contract_selftest_run_not_detected")
            return 1
        case_count += 1
        build_sample_repo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        duplicate_block = (
            "      - name: Check current Phase 4 artifact-diff determinism packet\n"
            "        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py\n"
        )
        write_file(root, WORKFLOW_REL, workflow_text + duplicate_block)
        failures = collect_failures(root)
        if "workflow_step:Check current Phase 4 artifact-diff determinism packet:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase4_determinism_step_not_detected")
            return 1
        if "workflow_run:Check current Phase 4 artifact-diff determinism packet:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase4_determinism_run_not_detected")
            return 1
        case_count += 1
        build_sampleRepo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        duplicate_block = (
            "      - name: Validate current Phase 6 helper packet\n"
            "        run: make -C zigux phase6-validate\n"
        )
        write_file(root, WORKFLOW_REL, workflow_text + duplicate_block)
        failures = collect_failures(root)
        if "workflow_step:Validate current Phase 6 helper packet:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase6_validate_step_not_detected")
            return 1
        if "workflow_run:Validate current Phase 6 helper packet:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase6_validate_run_not_detected")
            return 1
        case_count += 1
        build_sample_repo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        duplicate_block = (
            "      - name: Self-test current Phase 9 freeze-map study-boundaries checker\n"
            "        run: python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py --self-test\n"
        )
        write_file(root, WORKFLOW_REL, workflow_text + duplicate_block)
        failures = collect_failures(root)
        if "workflow_step:Self-test current Phase 9 freeze-map study-boundaries checker:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase9_freeze_map_selftest_not_detected")
            return 1
        if "workflow_run:Self-test current Phase 9 freeze-map study-boundaries checker:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase9_freeze_map_selftest_run_not_detected")
            return 1
        case_count += 1
        build_sample_repo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        duplicate_block = (
            "      - name: Run current Phase 12 aggregate route\n"
            "        run: make -C zigux phase12\n"
        )
        write_file(root, WORKFLOW_REL, workflow_text + duplicate_block)
        failures = collect_failures(root)
        if "workflow_step:Run current Phase 12 aggregate route:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase12_aggregate_step_not_detected")
            return 1
        if "workflow_run:Run current Phase 12 aggregate route:expected=1:actual=2" not in failures:
            print("self-test:duplicate_phase12_aggregate_run_not_detected")
            return 1
        case_count += 1
        build_sample_repo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        old = (
            "      - name: Check current Phase 1 closure packet\n"
            "        run: python3 scripts/zigux/validate-phase1-closure.py\n"
            "      - name: Self-test current Phase 3 interop packet\n"
            "        run: python3 scripts/zigux/validate_phase3_selftest.py\n"
        )
        new = (
            "      - name: Self-test current Phase 3 interop packet\n"
            "        run: python3 scripts/zigux/validate_phase3_selftest.py\n"
            "      - name: Check current Phase 1 closure packet\n"
            "        run: python3 scripts/zigux/validate-phase1-closure.py\n"
        )
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, old, new))
        failures = collect_failures(root)
        if not any(failure.startswith("phase3_chain:missing:") for failure in failures):
            print("self-test:broken_phase3_chain_not_detected")
            return 1
        case_count += 1
        build_sample_repo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        old = (
            "      - name: Validate current Phase 11 support bundle\n"
            "        run: make -C zigux phase11-validate\n"
            "      - name: Self-test current Phase 12 build-only surface checker\n"
            "        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test\n"
        )
        new = (
            "      - name: Self-test current Phase 12 build-only surface checker\n"
            "        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test\n"
            "      - name: Validate current Phase 11 support bundle\n"
            "        run: make -C zigux phase11-validate\n"
        )
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, old, new))
        failures = collect_failures(root)
        if not any(failure.startswith("phase10_to_14_chain:missing:") for failure in failures):
            print("self-test:broken_phase12_tail_not_detected")
            return 1
        case_count += 1
        build_sample_repo(root)

        (root / "zigux/tests/runtime_trace_events_survey.zig").unlink()
        failures = collect_failures(root)
        if "missing_file:zigux/tests/runtime_trace_events_survey.zig" not in failures:
            print("self-test:missing_required_file_not_detected")
            return 1
        case_count += 1

    print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_VIABILITY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> None:
    build_sample_repo(root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    failures = collect_failures(args.root.resolve())
    if failures:
        for failure in failures:
            print(f"phase1-workflow-viability:{failure}")
        return 1

    print("PHASE1_WORKFLOW_VIABILITY=pass")
    print(f"PHASE1_WORKFLOW_MARKER_COUNT={len(all_steps())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())