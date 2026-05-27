#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

REQUIRED_PATHS = (
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "Documentation/zigux/phase4-validation-lane-sequencing.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "scripts/zigux/check-phase4-perf-threshold-matrix.py",
    "scripts/zigux/check-phase4-remaining-gap-matrix.py",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/check-phase4-tests-readme-packet.py",
    "scripts/zigux/check-phase4-validation-lane-sequencing.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_diff_manifest.json",
    "zigux/tests/phase4_bitmap_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
)

WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASES = (
    "baseline_round_trip,",
    "workflow_order_drift,",
    "missing_make_phase4_validate_artifact_diff_contract_selftest_command,",
    "phase4_validate_contract_selftest_order_drift,",
    "missing_make_artifact_diff_contract_selftest_command,",
    "missing_make_route_counts_command,",
    "missing_make_reversible_delivery_selftest_command,",
    "missing_make_reversible_delivery_command,",
    "missing_make_remaining_gap_command,",
    "missing_make_validator_replays_selftest_command,",
    "missing_make_validator_replays_command,",
    "missing_make_validation_lane_sequencing_selftest_command,",
    "missing_make_validation_lane_sequencing_command,",
    "missing_make_perf_baseline_command,",
    "missing_workflow_validate_route,",
    "missing_workflow_test_route,",
    "missing_workflow_artifact_diff_contract_make_route,",
    "missing_workflow_artifact_diff_helper_selftest,",
    "missing_workflow_artifact_diff_contract_selftest,",
    "missing_workflow_artifact_diff_contract_check,",
    "missing_workflow_artifact_diff_determinism_selftest,",
    "missing_workflow_artifact_diff_determinism_check,",
    "missing_workflow_artifact_diff-validator-replays_selftest,",
    "missing_workflow_artifact_diff-validator-replays_check,",
    "missing_matrix_remaining_gap_marker,",
    "missing_gate_evidence_bitmap_build_route,",
    "missing_gate_evidence_bitmap_wrapper,",
    "missing_build_test_fsmount_route,",
    "missing_build_bitmap_diff_route,",
    "missing_build_bitmap_diff_survey_route,",
    "missing_build_bitmap_live_helper_replay_route,",
    "forbidden_perf_baseline_dependency",
)

ARTIFACT_DIFF_HELPER_SELF_TEST_CASES = (
    "text_pass,",
    "text_mismatch,",
    "json_pass,",
    "json_mismatch,",
    "json_invalid_expected,",
    "json_invalid_actual,",
    "json_invalid_both,",
    "json_missing_expected,",
    "json_missing_actual,",
    "json_missing_both,",
    "bytes_pass,",
    "bytes_drift,",
    "text_missing_expected,",
    "text_missing_actual,",
    "text_missing_both,",
    "bytes_missing_expected,",
    "bytes_missing_actual,",
    "bytes_missing_both,",
    "legacy_sha256_alias,",
    "missing_mode_value_rejected,",
    "missing_positional_arguments_rejected,",
    "invalid_mode_rejected,",
    "extra_positional_rejected",
)

PHASE4_TESTS_README_PACKET_SELF_TEST_CASES = (
    "baseline_round_trip,",
    "missing_header,",
    "missing_phase5_anchor,",
    "stale_phase4_heading,",
    "stale_phase4_note_reference,",
    "stale_phase4_gate_evidence_note_reference,",
    "stale_phase4_repo_reality_warning_reference,",
    "stale_phase4_validator_reference,",
    "stale_phase4_perf_manifest_reference,",
    "stale_phase4_perf_reference,",
    "stale_phase4_build_reference,",
    "stale_phase4_bitmap_reference,",
    "stale_phase4_bitmap_replay_reference,",
    "stale_phase4_atomic64_pair_reference,",
    "stale_phase4_perf_make_route,",
    "stale_phase4_gate_evidence_checker_reference,",
    "stale_phase4_reversible_delivery_checker_reference,",
    "stale_phase4_perf_checker_reference,",
    "stale_phase4_tests_readme_checker_reference",
)

REQUIRED_COMMAND_OUTPUT_MARKERS = {
    "phase4-repo-reality-warning-self-test": (
        ("PHASE4_REPO_REALITY_WARNING_SELF_TEST", "PHASE4_REPO_REALITY_WARNING_SELF_TEST=pass"),
        ("PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES", "PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32"),
    ),
    "phase4-repo-reality-warning": (("PHASE4_REPO_REALITY_WARNING", "PHASE4_REPO_REALITY_WARNING=pass"),),
    "phase4-reversible-delivery-pins-self-test": (
        ("PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST", "PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST=pass"),
        ("PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT", "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20"),
    ),
    "phase4-reversible-delivery-pins": (("PHASE4_REVERSIBLE_DELIVERY_PINS", "PHASE4_REVERSIBLE_DELIVERY_PINS=pass"),),
    "phase4-tests-readme-packet-self-test": (
        ("PHASE4_TESTS_README_PACKET_SELF_TEST", "PHASE4_TESTS_README_PACKET_SELF_TEST=pass"),
        ("PHASE4_TESTS_README_PACKET_SELF_TEST_CASES", "PHASE4_TESTS_README_PACKET_SELF_TEST_CASES=19"),
        ("PHASE4_TESTS_README_PACKET_SELF_TEST_CASE_NAMES", "PHASE4_TESTS_README_PACKET_SELF_TEST_CASE_NAMES=" + "".join(PHASE4_TESTS_README_PACKET_SELF_TEST_CASES)),
    ),
    "phase4-tests-readme-packet": (("PHASE4_TESTS_README_PACKET_CHECK", "PHASE4_TESTS_README_PACKET_CHECK=pass"),),
    "phase4-artifact-diff-helper-self-test": (
        ("ARTIFACT_DIFF_SELF_TEST", "ARTIFACT_DIFF_SELF_TEST=pass"),
        ("ARTIFACT_DIFF_SELF_TEST_CASE_COUNT", "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23"),
        ("ARTIFACT_DIFF_SELF_TEST_CASES", "ARTIFACT_DIFF_SELF_TEST_CASES=" + "".join(ARTIFACT_DIFF_HELPER_SELF_TEST_CASES)),
    ),
    "phase4-artifact-diff-contract-self-test": (
        ("ARTIFACT_DIFF_CONTRACT_SELF_TEST", "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass"),
        ("ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT", "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24"),
        ("ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES", "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES="),
    ),
    "phase4-artifact-diff-contract": (
        ("ARTIFACT_DIFF_CONTRACT", "ARTIFACT_DIFF_CONTRACT=pass"),
        ("ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT", "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=25"),
        ("ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT", "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5"),
        ("ARTIFACT_DIFF_CONTRACT_CASE_COUNT", "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30"),
    ),
    "phase4-artifact-diff-determinism-self-test": (
        ("PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST", "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass"),
        ("PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT", "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13"),
        ("PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES", "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES="),
    ),
    "phase4-artifact-diff-determinism": (
        ("PHASE4_ARTIFACT_DIFF_DETERMINISM", "PHASE4_ARTIFACT_DIFF_DETERMINISM=pass"),
        ("PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS", "PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS=11"),
        (
            "PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS",
            "PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS=0",
        ),
    ),
    "phase4-artifact-diff-validator-replays-self-test": (
        ("PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST", "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST=pass"),
        (
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT",
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14",
        ),
        (
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASES",
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASES=",
        ),
    ),
    "phase4-artifact-diff-validator-replays": (
        ("PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS", "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=pass"),
        (
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MODE",
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MODE=validator_present",
        ),
        (
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT",
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7",
        ),
        (
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKERS",
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKERS=",
        ),
        (
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT",
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=14",
        ),
    ),
    "phase4-gate-evidence-self-test": (("phase4 gate evidence self-test", "phase4 gate evidence self-test: PASS (45 cases)"),),
    "phase4-gate-evidence": (("phase4 gate evidence check passed", "phase4 gate evidence check passed"),),
    "phase4-perf-baseline-packet-self-test": (
        ("PHASE4_PERF_BASELINE_PACKET_SELF_TEST", "PHASE4_PERF_BASELINE_PACKET_SELF_TEST=pass"),
        ("PHASE4_PERF_BASELINE_PACKET_SELF_TEST_CASES", "PHASE4_PERF_BASELINE_PACKET_SELF_TEST_CASES=39"),
    ),
    "phase4-perf-baseline-packet": (("PHASE4_PERF_BASELINE_PACKET_CHECK", "PHASE4_PERF_BASELINE_PACKET_CHECK=pass"),),
    "phase4-perf-threshold-matrix-self-test": (
        ("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST", "PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=pass"),
        ("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST_CASES", "PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST_CASES=18"),
    ),
    "phase4-perf-threshold-matrix": (("PHASE4_PERF_THRESHOLD_MATRIX", "PHASE4_PERF_THRESHOLD_MATRIX=pass"),),
    "phase4-remaining-gap-matrix-self-test": (
        ("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST", "PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=pass"),
        ("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST_CASE_COUNT", "PHASE4_REMAINING_GAP_MATRIX_SELF_TEST_CASE_COUNT=38"),
    ),
    "phase4-remaining-gap-matrix": (
        ("PHASE4_REMAINING_GAP_MATRIX", "PHASE4_REMAINING_GAP_MATRIX=pass"),
        ("PHASE4_REMAINING_GAP_MATRIX_PACKET_COUNT", "PHASE4_REMAINING_GAP_MATRIX_PACKET_COUNT=6"),
    ),
    "phase4-validation-lane-sequencing-self-test": (
        ("PHASE4_VALIDATION_LANE_SEQUENCING_SELF_TEST", "PHASE4_VALIDATION_LANE_SEQUENCING_SELF_TEST=pass"),
        (
            "PHASE4_VALIDATION_LANE_SEQUENCING_SELF_TEST_CASES",
            "PHASE4_VALIDATION_LANE_SEQUENCING_SELF_TEST_CASES=10",
        ),
    ),
    "phase4-validation-lane-sequencing": (
        ("PHASE4_VALIDATION_LANE_SEQUENCING_CHECK", "PHASE4_VALIDATION_LANE_SEQUENCING_CHECK=pass"),
    ),
    "phase4-workflow-route-counts-self-test": (
        ("PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST", "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass"),
        ("PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASE_COUNT", "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASE_COUNT=32"),
        ("PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASES", "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASES=" + "".join(WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASES)),
        ("PHASE4_WORKFLOW_ROUTE_COUNT", "PHASE4_WORKFLOW_ROUTE_COUNT=12"),
        ("PHASE4_WORKFLOW_MARKER_COUNT", "PHASE4_WORKFLOW_MARKER_COUNT=20"),
        ("PHASE4_WORKFLOW_ORDER_MARKER_COUNT", "PHASE4_WORKFLOW_ORDER_MARKER_COUNT=10"),
        ("PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT", "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=7"),
    ),
    "phase4-workflow-route-counts": (
        ("PHASE4_WORKFLOW_ROUTE_COUNTS_CHECK", "PHASE4_WORKFLOW_ROUTE_COUNTS_CHECK=pass"),
        ("PHASE4_WORKFLOW_ROUTE_COUNTS", "PHASE4_WORKFLOW_ROUTE_COUNTS=pass"),
        ("PHASE4_WORKFLOW_ROUTE_COUNT", "PHASE4_WORKFLOW_ROUTE_COUNT=12"),
        ("PHASE4_WORKFLOW_MARKER_COUNT", "PHASE4_WORKFLOW_MARKER_COUNT=20"),
        ("PHASE4_WORKFLOW_ORDER_MARKER_COUNT", "PHASE4_WORKFLOW_ORDER_MARKER_COUNT=10"),
        ("PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT", "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=7"),
    ),
}

@dataclass(frozen=True)
class CheckSpec:
    name: str
    command: tuple[str, ...]

CHECKS = (
    CheckSpec("phase4-repo-reality-warning-self-test", ("python", "scripts/zigux/check-phase4-repo-reality-warning.py", "--self-test")),
    CheckSpec("phase4-repo-reality-warning", ("python", "scripts/zigux/check-phase4-repo-reality-warning.py")),
    CheckSpec("phase4-reversible-delivery-pins-self-test", ("python", "scripts/zigux/check-phase4-reversible-delivery-pins.py", "--self-test")),
    CheckSpec("phase4-reversible-delivery-pins", ("python", "scripts/zigux/check-phase4-reversible-delivery-pins.py")),
    CheckSpec("phase4-tests-readme-packet-self-test", ("python", "scripts/zigux/check-phase4-tests-readme-packet.py", "--self-test")),
    CheckSpec("phase4-tests-readme-packet", ("python", "scripts/zigux/check-phase4-tests-readme-packet.py")),
    CheckSpec("phase4-artifact-diff-helper-self-test", ("python", "scripts/zigux/artifact_diff.py", "--self-test")),
    CheckSpec("phase4-artifact-diff-contract-self-test", ("python", "scripts/zigux/check-artifact-diff-contract.py", "--self-test")),
    CheckSpec("phase4-artifact-diff-contract", ("python", "scripts/zigux/check-artifact-diff-contract.py")),
    CheckSpec("phase4-artifact-diff-determinism-self-test", ("python", "scripts/zigux/check-phase4-artifact-diff-determinism.py", "--self-test")),
    CheckSpec("phase4-artifact-diff-determinism", ("python", "scripts/zigux/check-phase4-artifact-diff-determinism.py")),
    CheckSpec("phase4-artifact-diff-validator-replays-self-test", ("python", "scripts/zigux/check-phase4-artifact-diff-validator-replays.py", "--self-test")),
    CheckSpec("phase4-artifact-diff-validator-replays", ("python", "scripts/zigux/check-phase4-artifact-diff-validator-replays.py")),
    CheckSpec("phase4-gate-evidence-self-test", ("python", "scripts/zigux/check-phase4-gate-evidence.py", "--self-test")),
    CheckSpec("phase4-gate-evidence", ("python", "scripts/zigux/check-phase4-gate-evidence.py")),
    CheckSpec("phase4-perf-baseline-packet-self-test", ("python", "scripts/zigux/check-phase4-perf-baseline-packet.py", "--self-test")),
    CheckSpec("phase4-perf-baseline-packet", ("python", "scripts/zigux/check-phase4-perf-baseline-packet.py")),
    CheckSpec("phase4-perf-threshold-matrix-self-test", ("python", "scripts/zigux/check-phase4-perf-threshold-matrix.py", "--self-test")),
    CheckSpec("phase4-perf-threshold-matrix", ("python", "scripts/zigux/check-phase4-perf-threshold-matrix.py")),
    CheckSpec("phase4-remaining-gap-matrix-self-test", ("python", "scripts/zigux/check-phase4-remaining-gap-matrix.py", "--self-test")),
    CheckSpec("phase4-remaining-gap-matrix", ("python", "scripts/zigux/check-phase4-remaining-gap-matrix.py")),
    CheckSpec("phase4-validation-lane-sequencing-self-test", ("python", "scripts/zigux/check-phase4-validation-lane-sequencing.py", "--self-test")),
    CheckSpec("phase4-validation-lane-sequencing", ("python", "scripts/zigux/check-phase4-validation-lane-sequencing.py")),
    CheckSpec("phase4-workflow-route-counts-self-test", ("python", "scripts/zigux/check-phase4-workflow-route-counts.py", "--self-test")),
    CheckSpec("phase4-workflow-route-counts", ("python", "scripts/zigux/check-phase4-workflow-route-counts.py")),
    CheckSpec("phase4-build-test", ("zig", "build", "test", "--build-file", "zigux/tests/phase4_build.zig")),
)

def command_for(spec: CheckSpec, root: Path) -> list[str]:
    command = list(spec.command)
    if command[0] == "python":
        return [sys.executable, str(root / command[1]), *command[2:]]
    if command[0] == "zig":
        return ["zig", *command[1:]]
    raise ValueError(f"unsupported command kind for {spec.name}: {command[0]}")

def is_zig_check(spec: CheckSpec) -> bool:
    return spec.command[0] == "zig"

def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, capture_output=True, text=True, cwd=cwd)

def append_output(issues: list[str], prefix: str, completed: subprocess.CompletedProcess[str]) -> None:
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    if stdout:
        issues.append(f"{prefix}:stdout={stdout}")
    if stderr:
        issues.append(f"{prefix}:stderr={stderr}")

def ensure_command_output_markers(spec: CheckSpec, completed: subprocess.CompletedProcess[str], issues: list[str]) -> None:
    stdout = completed.stdout
    for label, marker in REQUIRED_COMMAND_OUTPUT_MARKERS.get(spec.name, ()):  # pragma: no branch
        if marker not in stdout:
            issues.append(f"output_marker_missing:{spec.name}:{label}")

def collect_issues(root: Path, *, skip_zig_builds: bool = False) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_required_path:{rel}")
    if issues:
        return issues

    artifact_doc_text = (root / "Documentation/zigux/artifact-diff.md").read_text(encoding="utf-8")
    for marker in REQUIRED_ARTIFACT_DOC_MARKERS:
        if marker not in artifact_doc_text:
            issues.append(f"artifact_doc_marker_missing:{marker}")

    artifact_matrix_text = (root / "Documentation/zigux/phase4-validation-matrix.md").read_text(encoding="utf-8")
    for marker in REQUIRED_ARTIFACT_MATRIX_MARKERS:
        if marker not in artifact_matrix_text:
            issues.append(f"artifact_matrix_marker_missing:{marker}")

    for spec in CHECKS:
        if skip_zig_builds and is_zig_check(spec):
            continue
        completed = run_command(command_for(spec, root), root)
        if completed.returncode != 0:
            issues.append(f"live_failed:{spec.name}:exit={completed.returncode}")
            append_output(issues, f"live_failed:{spec.name}", completed)
            continue
        ensure_command_output_markers(spec, completed, issues)
    return issues

def run_check(root: Path, *, skip_zig_builds: bool = False) -> int:
    issues = collect_issues(root, skip_zig_builds=skip_zig_builds)
    if issues:
        print("PHASE4_VALIDATION=fail")
        print("PHASE4_VALIDATION_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE4_VALIDATION_ISSUES_END")
        return 1
    print("PHASE4_VALIDATION=pass")
    print(f"PHASE4_VALIDATION_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE4_VALIDATION_CHECK_COUNT={len(CHECKS)}")
    return 0

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def build_stub_script(
    path: Path,
    *,
    self_test_exit_code: int = 0,
    live_exit_code: int | None = None,
    self_test_stdout_lines: tuple[str, ...] = (),
    live_stdout_lines: tuple[str, ...] = (),
) -> None:
    live_exit = self_test_exit_code if live_exit_code is None else live_exit_code
    write_text(
        path,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import argparse",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--self-test', action='store_true')",
                "args = parser.parse_args()",
                f"SELF_TEST_EXIT_CODE = {self_test_exit_code}",
                f"LIVE_EXIT_CODE = {live_exit}",
                f"SELF_TEST_STDOUT_LINES = {list(self_test_stdout_lines)!r}",
                f"LIVE_STDOUT_LINES = {list(live_stdout_lines)!r}",
                "for line in (SELF_TEST_STDOUT_LINES if args.self_test else LIVE_STDOUT_LINES):",
                "    print(line)",
                "raise SystemExit(SELF_TEST_EXIT_CODE if args.self_test else LIVE_EXIT_CODE)",
            ]
        ) + "\n",
    )
    os.chmod(path, 0o755)

def build_fake_zig(path: Path, *, fail_build_file: str | None = None) -> None:
    write_text(
        path,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import sys",
                f"FAIL_BUILD_FILE = {fail_build_file!r}",
                "args = sys.argv[1:]",
                "if args[:2] != ['build', 'test']:",
                "    raise SystemExit(2)",
                "try:",
                "    build_file = args[args.index('--build-file') + 1]",
                "except (ValueError, IndexError):",
                "    raise SystemExit(3)",
                "if FAIL_BUILD_FILE is not None and build_file == FAIL_BUILD_FILE:",
                "    print(f'fake zig failed for {build_file}')",
                "    raise SystemExit(1)",
                "raise SystemExit(0)",
            ]
        ) + "\n",
    )
    os.chmod(path, 0o755)

def build_sample_repo(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        path = root / rel
        if rel.startswith("scripts/zigux/") and rel.endswith(".py"):
            build_stub_script(path)
        else:
            write_text(path, f"sample:{rel}\n")

def write_matrix_fixture(root: Path) -> None:
    write_text(root / "Documentation/zigux/phase4-validation-matrix.md", "\n".join(SAMPLE_PHASE4_VALIDATION_MATRIX_LINES) + "\n")

def configure_workflow_route_stub(root: Path) -> None:
    build_stub_script(
        root / "scripts/zigux/check-phase4-workflow-route-counts.py",
        self_test_stdout_lines=(
            "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass",
            "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASE_COUNT=32",
            "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASES=" + "".join(WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASES),
            "PHASE4_WORKFLOW_ROUTE_COUNT=12",
            "PHASE4_WORKFLOW_MARKER_COUNT=20",
            "PHASE4_WORKFLOW_ORDER_MARKER_COUNT=10",
            "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=7",
        ),
        live_stdout_lines=(
            "PHASE4_WORKFLOW_ROUTE_COUNTS_CHECK=pass",
            "PHASE4_WORKFLOW_ROUTE_COUNTS=pass",
            "PHASE4_WORKFLOW_ROUTE_COUNT=12",
            "PHASE4_WORKFLOW_MARKER_COUNT=20",
            "PHASE4_WORKFLOW_ORDER_MARKER_COUNT=10",
            "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=7",
        ),
    )

def configure_phase4_output_stubs(root: Path) -> None:
    build_stub_script(
        root / "scripts/zigux/check-phase4-repo-reality-warning.py",
        self_test_stdout_lines=("PHASE4_REPO_REALITY_WARNING_SELF_TEST=pass", "PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32"),
        live_stdout_lines=("PHASE4_REPO_REALITY_WARNING=pass",),
    )
    build_stub_script(
        root / "scripts/zigux/check-phase4-reversible-delivery-pins.py",
        self_test_stdout_lines=(
            "PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST=pass",
            "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20",
            "PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST_CASES=20",
        ),
        live_stdout_lines=("PHASE4_REVERSIBLE_DELIVERY_PINS=pass",),
    )
    build_stub_script(
        root / "scripts/zigux/check-phase4-tests-readme-packet.py",
        self_test_stdout_lines=(
            "PHASE4_TESTS_README_PACKET_SELF_TEST=pass",
            "PHASE4_TESTS_README_PACKET_SELF_TEST_CASES=19",
            "PHASE4_TESTS_README_PACKET_SELF_TEST_CASE_NAMES=" + "".join(PHASE4_TESTS_README_PACKET_SELF_TEST_CASES),
        ),
        live_stdout_lines=("PHASE4_TESTS_README_PACKET_CHECK=pass",),
    )
    build_stub_script(
        root / "scripts/zigux/artifact_diff.py",
        self_test_stdout_lines=(
            "ARTIFACT_DIFF_SELF_TEST=pass",
            "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23",
            "ARTIFACT_DIFF_SELF_TEST_CASES=" + "".join(ARTIFACT_DIFF_HELPER_SELF_TEST_CASES),
        ),
    )
    build_stub_script(
        root / "scripts/zigux/check-artifact-diff-contract.py",
        self_test_stdout_lines=(
            "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass",
            "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24",
            "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=",
        ),
        live_stdout_lines=(
            "ARTIFACT_DIFF_CONTRACT=pass",
            "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=25",
            "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5",
            "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30",
        ),
    )
    build_stub_script(
        root / "scripts/zigux/check-phase4-artifact-diff-determinism.py",
        self_test_stdout_lines=(
            "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass",
            "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13",
            "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES=",
        ),
        live_stdout_lines=(
            "PHASE4_ARTIFACT_DIFF_DETERMINISM=pass",
            "PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS=11",
            "PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS=0",
        ),
    )
    build_stub_script(
        root / "scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
        self_test_stdout_lines=(
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST=pass",
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14",
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASES=",
        ),
        live_stdout_lines=(
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=pass",
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MODE=validator_present",
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7",
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKERS=",
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=14",
        ),
    )
    build_stub_script(
        root / "scripts/zigux/check-phase4-gate-evidence.py",
        self_test_stdout_lines=("phase4 gate evidence self-test: PASS (45 cases)",),
        live_stdout_lines=("phase4 gate evidence check passed",),
    )
    build_stub_script(
        root / "scripts/zigux/check-phase4-perf-baseline-packet.py",
        self_test_stdout_lines=("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=pass", "PHASE4_PERF_BASELINE_PACKET_SELF_TEST_CASES=39"),
        live_stdout_lines=("PHASE4_PERF_BASELINE_PACKET_CHECK=pass",),
    )
    build_stub_script(
        root / "scripts/zigux/check-phase4-perf-threshold-matrix.py",
        self_test_stdout_lines=("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=pass", "PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST_CASES=18"),
        live_stdout_lines=("PHASE4_PERF_THRESHOLD_MATRIX=pass",),
    )
    build_stub_script(
        root / "scripts/zigux/check-phase4-remaining-gap-matrix.py",
        self_test_stdout_lines=("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=pass", "PHASE4_REMAINING_GAP_MATRIX_SELF_TEST_CASE_COUNT=38"),
        live_stdout_lines=("PHASE4_REMAINING_GAP_MATRIX=pass", "PHASE4_REMAINING_GAP_MATRIX_PACKET_COUNT=6"),
    )
    build_stub_script(
        root / "scripts/zigux/check-phase4-validation-lane-sequencing.py",
        self_test_stdout_lines=(
            "PHASE4_VALIDATION_LANE_SEQUENCING_SELF_TEST=pass",
            "PHASE4_VALIDATION_LANE_SEQUENCING_SELF_TEST_CASES=10",
        ),
        live_stdout_lines=("PHASE4_VALIDATION_LANE_SEQUENCING_CHECK=pass",),
    )
    configure_workflow_route_stub(root)

def write_artifact_diff_fixture(root: Path) -> None:
    lines = ["# Artifact Diff Policy", "", "Current Phase 4 use"]
    lines.extend(f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:])
    write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join(lines) + "\n")

def build_validator_fixture_root(root: Path, *, fail_build_file: str | None = None) -> None:
    build_sample_repo(root)
    write_artifact_diff_fixture(root)
    write_matrix_fixture(root)
    configure_phase4_output_stubs(root)
    build_fake_zig(root / "zig", fail_build_file=fail_build_file)

def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4-validate-self-test-") as tmp:
        root = Path(tmp)
        original_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{root}{os.pathsep}{original_path}"

        cases = 0

        def reset_fixture(*, fail_build_file: str | None = None) -> None:
            build_validator_fixture_root(root, fail_build_file=fail_build_file)

        reset_fixture()
        if collect_issues(root):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("baseline fixture did not validate cleanly")
            return 1

        cases += 1

        reset_fixture()
        (root / REQUIRED_PATHS[0]).unlink()
        if f"missing_required_path:{REQUIRED_PATHS[0]}" not in collect_issues(root):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("missing required path case did not fail closed")
            return 1
        cases += 1

        reset_fixture()
        write_text(root / "Documentation/zigux/artifact-diff.md", "# Artifact Diff Policy\n\n")
        if "artifact_doc_marker_missing:Current Phase 4 use" not in collect_issues(root):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("artifact doc marker case did not fail closed")
            return 1
        cases += 1

        reset_fixture()
        write_text(root / "Documentation/zigux/phase4-validation-matrix.md", "# Phase 4 Validation Matrix\n## Lab And CI Matrix\n")
        if "artifact_matrix_marker_missing:`MODE=...`" not in collect_issues(root):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("artifact matrix marker case did not fail closed")
            return 1
        cases += 1

        reset_fixture()
        build_stub_script(root / "scripts/zigux/check-phase4-repo-reality-warning.py", self_test_exit_code=1, live_exit_code=0)
        if "live_failed:phase4-repo-reality-warning-self-test:exit=1" not in collect_issues(root):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("repo reality self-test failure was not detected")
            return 1
        cases += 1

        reset_fixture()
        build_stub_script(root / "scripts/zigux/check-phase4-repo-reality-warning.py", self_test_stdout_lines=("PHASE4_REPO_REALITY_WARNING_SELF_TEST=pass",), live_stdout_lines=("PHASE4_REPO_REALITY_WARNING=pass",))
        if "output_marker_missing:phase4-repo-reality-warning-self-test:PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES" not in collect_issues(root):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("repo reality marker drift was not detected")
            return 1
        cases += 1

        reset_fixture()
        build_stub_script(root / "scripts/zigux/check-phase4-perf-baseline-packet.py", self_test_exit_code=0, live_exit_code=1)
        if "live_failed:phase4-perf-baseline-packet:exit=1" not in collect_issues(root):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("perf baseline live failure was not detected")
            return 1
        cases += 1

        reset_fixture()
        build_stub_script(root / "scripts/zigux/check-phase4-perf-baseline-packet.py", self_test_stdout_lines=("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=pass",), live_stdout_lines=("PHASE4_PERF_BASELINE_PACKET_CHECK=pass",))
        if "output_marker_missing:phase4-perf-baseline-packet-self-test:PHASE4_PERF_BASELINE_PACKET_SELF_TEST_CASES" not in collect_issues(root):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("perf baseline marker drift was not detected")
            return 1
        cases += 1

        reset_fixture()
        build_stub_script(root / "scripts/zigux/check-phase4-perf-threshold-matrix.py", self_test_exit_code=0, live_exit_code=1)
        if "live_failed:phase4-perf-threshold-matrix:exit=1" not in collect_issues(root):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("perf threshold matrix live failure was not detected")
            return 1
        cases += 1

        reset_fixture()
        build_stub_script(root / "scripts/zigux/check-phase4-perf-threshold-matrix.py", self_test_stdout_lines=("PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=pass",), live_stdout_lines=("PHASE4_PERF_THRESHOLD_MATRIX=pass",))
        if "output_marker_missing:phase4-perf-threshold-matrix-self-test:PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST_CASES" not in collect_issues(root):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("perf threshold matrix marker drift was not detected")
            return 1
        cases += 1

        reset_fixture()
        build_stub_script(
            root / "scripts/zigux/check-artifact-diff-contract.py",
            self_test_stdout_lines=(
                "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass",
                "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24",
            ),
            live_stdout_lines=(
                "ARTIFACT_DIFF_CONTRACT=pass",
                "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=25",
                "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5",
                "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30",
            ),
        )
        if "output_marker_missing:phase4-artifact-diff-contract-self-test:ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES" not in collect_issues(root):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("artifact-diff contract marker drift was not detected")
            return 1
        cases += 1

        reset_fixture()
        build_stub_script(
            root / "scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
            self_test_stdout_lines=(
                "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST=pass",
                "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14",
                "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASES=",
            ),
            live_stdout_lines=(
                "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=pass",
                "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MODE=validator_present",
                "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7",
                "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKERS=",
            ),
        )
        if "output_marker_missing:phase4-artifact-diff-validator-replays:PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT" not in collect_issues(root):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("artifact-diff validator replay marker drift was not detected")
            return 1
        cases += 1

        reset_fixture()
        build_stub_script(root / "scripts/zigux/check-phase4-validation-lane-sequencing.py", self_test_exit_code=0, live_exit_code=1)
        if "live_failed:phase4-validation-lane-sequencing:exit=1" not in collect_issues(root):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("validation lane sequencing live failure was not detected")
            return 1
        cases += 1

        reset_fixture()
        build_stub_script(
            root / "scripts/zigux/check-phase4-validation-lane-sequencing.py",
            self_test_stdout_lines=("PHASE4_VALIDATION_LANE_SEQUENCING_SELF_TEST=pass",),
            live_stdout_lines=("PHASE4_VALIDATION_LANE_SEQUENCING_CHECK=pass",),
        )
        if "output_marker_missing:phase4-validation-lane-sequencing-self-test:PHASE4_VALIDATION_LANE_SEQUENCING_SELF_TEST_CASES" not in collect_issues(root):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("validation lane sequencing marker drift was not detected")
            return 1
        cases += 1

        reset_fixture()
        build_stub_script(
            root / "scripts/zigux/check-phase4-workflow-route-counts.py",
            self_test_stdout_lines=(
                "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass",
                "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASE_COUNT=32",
                "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASES=" + "".join(WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASES),
                "PHASE4_WORKFLOW_MARKER_COUNT=20",
                "PHASE4_WORKFLOW_ORDER_MARKER_COUNT=10",
                "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=7",
            ),
            live_stdout_lines=(
                "PHASE4_WORKFLOW_ROUTE_COUNTS_CHECK=pass",
                "PHASE4_WORKFLOW_ROUTE_COUNTS=pass",
                "PHASE4_WORKFLOW_ROUTE_COUNT=12",
                "PHASE4_WORKFLOW_MARKER_COUNT=20",
                "PHASE4_WORKFLOW_ORDER_MARKER_COUNT=10",
                "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=7",
            ),
        )
        if "output_marker_missing:phase4-workflow-route-counts-self-test:PHASE4_WORKFLOW_ROUTE_COUNT" not in collect_issues(root):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("workflow-route-count telemetry drift was not detected")
            return 1
        cases += 1

        reset_fixture(fail_build_file="zigux/tests/phase4_build.zig")
        if collect_issues(root, skip_zig_builds=True):
            print("PHASE4_VALIDATE_SELF_TEST=fail")
            print("skip-zig-builds did not suppress the Zig check")
            return 1
        cases += 1

        os.environ["PATH"] = original_path
        print("PHASE4_VALIDATE_SELF_TEST=pass")
        print(f"PHASE4_VALIDATE_SELF_TEST_CASE_COUNT={cases}")
        return 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--skip-zig-builds", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        return run_check(args.root.resolve(), skip_zig_builds=args.skip_zig_builds)
    except Exception as exc:  # pragma: no cover
        print(f"PHASE4_VALIDATION=fail: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())