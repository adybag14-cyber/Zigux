#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parent

REQUIRED_FILES = [
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_diff_manifest.json",
    "zigux/tests/phase4_bitmap_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/phase9_build.zig",
]

REQUIRED_MAKE_PHONY_TARGETS = [
    "phase4-validate",
    "phase4-artifact-diff-contract",
    "phase4-test",
    "phase4-runtime-atomic64-diff",
    "phase4-runtime-atomic64-diff-survey",
    "phase4-perf-baseline-survey",
    "phase4-bitmap-diff",
    "phase4-bitmap-diff-survey",
    "phase4-bitmap-live-helper-replay",
    "phase4",
]

REQUIRED_MAKE_MARKERS = [
    "phase4-validate:",
    "scripts/zigux/validate-phase4.py --self-test",
    "scripts/zigux/validate-phase4.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "phase4-perf-baseline-survey:",
    "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-diff-survey:",
    "zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-live-helper-replay:",
]

REQUIRED_WORKFLOW_MARKERS = [
    "python3 scripts/zigux/validate-phase4.py --self-test",
    "python3 scripts/zigux/validate-phase4.py",
    "zig build test --build-file zigux/tests/phase4_build.zig",
]

REQUIRED_ARTIFACT_DOC_MARKERS = [
    "Current Phase 4 use",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_diff_manifest.json",
    "zigux/tests/phase4_bitmap_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/phase4-validation-matrix.md",
]

REQUIRED_ARTIFACT_DIFF_TOOLING_NOTE_MARKERS = [
    "- owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`",
    "- rollback owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`",
    "- fallback rule: if `scripts/zigux/artifact_diff.py` regresses, keep the committed expected artifact plus the current authoritative C or documented replay command as the source of truth until the helper contract is repaired",
    "- deterministic replay entrypoint: `python3 scripts/zigux/check-artifact-diff-contract.py` is the reviewable contract rerun for the shared host-side helper and should stay aligned with the outward line rules below",
    "- review rule: any change to the helper's emitted `ARTIFACT_DIFF=*`, `MODE=*`, `EXPECTED=*`, `ACTUAL=*`, `SHA256=*`, `EXPECTED_EXISTS=*`, `ACTUAL_EXISTS=*`, `EXPECTED_JSON_ERROR=*`, or `ACTUAL_JSON_ERROR=*` lines must update this note in the same change so the published host-side artifact packet stays reviewable",
]

REQUIRED_DOC_README_MARKERS = [
    "Phase 4 notes",
    "validate-phase4.py",
    "phase4-gate-evidence.md",
    "phase4-validation-matrix.md",
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
    "phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "intentionally unapproved perf-threshold posture",
]

REQUIRED_SCRIPT_README_MARKERS = [
    "Phase 4 flow",
    "validate-phase4.py",
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
    "phase4-gate-evidence.md",
    "phase4-validation-matrix.md",
    "phase4_build.zig",
    "phase4_runtime_atomic64_diff_survey.zig",
    "make -C zigux phase4-bitmap-live-helper-replay",
    "intentionally unapproved perf-threshold posture",
]

REQUIRED_TESTS_README_MARKERS = [
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_diff_manifest.json",
    "zigux/tests/phase4_bitmap_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
]

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 4 validation packet",
    "Documentation/zigux/phase4-validation-matrix.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zig build test --build-file zigux/tests/phase4_build.zig",
    "intentionally unapproved perf-threshold posture",
]

REQUIRED_PHASE4_MATRIX_MARKERS = [
    "phase4_runtime_atomic64_diff_manifest.json",
    "phase4_runtime_atomic64_diff_survey.zig",
    "bitmap_diff.zig",
    "phase4_bitmap_diff_manifest.json",
    "phase4_bitmap_diff_survey.zig",
    "phase4_bitmap_live_helper_replay.zig",
    "phase4_perf_baseline_manifest.json",
    "phase4_perf_baseline_survey.zig",
    "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land",
    "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "rollback owner",
    "Lab And CI Matrix",
    "threshold posture",
    "zig build test --build-file zigux/tests/phase4_build.zig",
    "Remaining Roadmap Gaps",
]

REQUIRED_PHASE4_BUILD_MARKERS = [
    'root_source_file = b.path("atomic64_diff.zig")',
    'root_source_file = b.path("phase4_runtime_atomic64_diff_survey.zig")',
    'root_source_file = b.path("phase4_perf_baseline_survey.zig")',
    'root_source_file = b.path("bitmap_diff.zig")',
    'root_source_file = b.path("phase4_bitmap_diff_survey.zig")',
    'root_source_file = b.path("phase4_bitmap_live_helper_replay.zig")',
    'name = "phase4-runtime-atomic64-diff-tests"',
    'name = "phase4-runtime-atomic64-diff-survey-tests"',
    'name = "phase4-perf-baseline-survey-tests"',
    'name = "phase4-bitmap-diff-tests"',
    'name = "phase4-bitmap-diff-survey-tests"',
    'name = "phase4-bitmap-live-helper-replay-tests"',
    '"phase4-perf-baseline-survey"',
]

FORBIDDEN_SCRIPT_README_MARKERS = [
    "phase4-perf-baseline-survey",
]

PHASE4_RUNTIME_ATOMIC64_EXPECTED_STRINGS = {
    "lane_key": "P4-L02",
    "phase": "Phase 4",
    "roadmap_target_path": "zigux/tests/atomic64_diff.zig",
    "owner": "ABI and Runtime Team",
    "rollback_owner": "ABI and Runtime Team",
    "live_gate_path": "zigux/tests/runtime_atomic64_diff.zig",
    "runtime_replay_path": "zigux/tests/runtime_atomic64_diff.zig",
    "phase4_gate_evidence_path": "Documentation/zigux/phase4-gate-evidence.md",
    "threshold_posture": "threshold_pending_until_runtime_atomic64_scope_widens",
}

PHASE4_RUNTIME_ATOMIC64_EXPECTED_TRUE_FIELDS = [
    "roadmap_atomic64_diff_present",
    "roadmap_atomic64_wrapper_targets_runtime_diff",
    "phase4_build_present",
    "phase4_build_uses_atomic64_wrapper",
    "phase4_validator_atomic64_diff_present",
    "phase4_validator_runtime_atomic64_diff_present",
    "phase9_build_present",
    "phase4_validation_matrix_atomic64_diff_note_present",
    "phase4_validation_matrix_runtime_atomic64_note_present",
]

PHASE4_RUNTIME_ATOMIC64_MANIFEST_SHA_TARGETS = {
    "live_gate_blob_sha": "zigux/tests/runtime_atomic64_diff.zig",
    "runtime_replay_blob_sha": "zigux/tests/runtime_atomic64_diff.zig",
    "phase4_build_blob_sha": "zigux/tests/phase4_build.zig",
    "phase4_validator_blob_sha": "scripts/zigux/validate-phase4.py",
    "phase4_validation_matrix_blob_sha": "Documentation/zigux/phase4-validation-matrix.md",
    "phase4_review_checklist_blob_sha": "Documentation/zigux/review-checklist.md",
    "phase9_build_blob_sha": "zigux/tests/phase9_build.zig",
}

PHASE4_RUNTIME_ATOMIC64_LINE_COUNT_TARGETS = {
    "live_gate_line_count": "zigux/tests/runtime_atomic64_diff.zig",
    "runtime_replay_line_count": "zigux/tests/runtime_atomic64_diff.zig",
}

PHASE4_RUNTIME_ATOMIC64_SURVEY_SHA_COUNTS = {
    "zigux/tests/runtime_atomic64_diff.zig": 2,
    "zigux/tests/phase4_build.zig": 1,
    "scripts/zigux/validate-phase4.py": 1,
    "Documentation/zigux/phase4-validation-matrix.md": 1,
    "Documentation/zigux/review-checklist.md": 1,
    "zigux/tests/phase9_build.zig": 1,
}

PHASE4_RUNTIME_ATOMIC64_REQUIRED_FIELD_MARKERS = {
    "roadmap_gap_summary": [
        "zigux/tests/atomic64_diff.zig",
        "zigux/tests/phase4_perf_baseline_manifest.json",
        "zigux/tests/phase4_perf_baseline_survey.zig",
    ],
    "reversible_delivery_evidence": [
        "zigux/tests/atomic64_diff.zig",
        "zigux/tests/runtime_atomic64_diff.zig",
        "zigux/tests/phase4_build.zig",
        "scripts/zigux/validate-phase4.py",
        "Documentation/zigux/phase4-gate-evidence.md",
        "Documentation/zigux/review-checklist.md",
        "Documentation/zigux/phase4-validation-matrix.md",
        "zigux/tests/phase4_perf_baseline_manifest.json",
        "zigux/tests/phase4_perf_baseline_survey.zig",
    ],
    "ready_next": [
        "Documentation/zigux/phase4-gate-evidence.md",
        "Documentation/zigux/phase4-validation-matrix.md",
        "zigux/tests/phase4_perf_baseline_manifest.json",
        "zigux/tests/phase4_perf_baseline_survey.zig",
    ],
}

PHASE4_BITMAP_EXPECTED_STRINGS = {
    "lane_key": "P4-L07",
    "phase": "Phase 4",
    "roadmap_target_path": "zigux/tests/bitmap_diff.zig",
    "live_gate_path": "zigux/tests/bitmap_diff.zig",
    "helper_replay_path": "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "owner": "Shared Subsystems Pod",
    "rollback_owner": "Shared Subsystems Pod",
    "shared_validator_path": "scripts/zigux/validate-phase4.py",
    "shared_matrix_path": "Documentation/zigux/phase4-validation-matrix.md",
    "shared_gate_evidence_path": "Documentation/zigux/phase4-gate-evidence.md",
    "gate_evidence_path": "Documentation/zigux/phase4-gate-evidence.md",
    "threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
}

PHASE4_BITMAP_EXPECTED_TRUE_FIELDS = [
    "roadmap_bitmap_diff_present",
    "phase4_build_present",
    "phase4_build_uses_bitmap_diff",
    "phase4_build_uses_bitmap_diff_survey",
]

PHASE4_BITMAP_REQUIRED_FIELD_MARKERS = {
    "roadmap_gap_summary": [
        "zigux/tests/bitmap_diff.zig",
        "phase4_build.zig",
        "Shared Subsystems Pod",
        "rollback owner",
    ],
    "reversible_delivery_evidence": [
        "zigux/tests/bitmap_diff.zig",
        "zigux/tests/phase4_bitmap_live_helper_replay.zig",
        "Documentation/zigux/phase4-gate-evidence.md",
        "zigux/tests/phase4_bitmap_diff_manifest.json",
        "zigux/tests/phase4_bitmap_diff_survey.zig",
        "zigux/tests/phase4_build.zig",
    ],
    "ready_next": [
        "scripts/zigux/validate-phase4.py",
        "Documentation/zigux/phase4-validation-matrix.md",
        "Shared Subsystems Pod",
        "samples",
        "perf-threshold approval",
    ],
}

PHASE4_BITMAP_PIN_TARGETS = {
    "live_gate_blob_sha": "zigux/tests/bitmap_diff.zig",
    "helper_replay_blob_sha": "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "gate_evidence_blob_sha": "Documentation/zigux/phase4-gate-evidence.md",
    "phase4_build_blob_sha": "zigux/tests/phase4_build.zig",
}

PHASE4_BITMAP_SURVEY_MARKERS = [
    "phase 4 bitmap survey keeps the roadmap rollback gate and helper replay measurable",
    "phase 4 bitmap survey keeps the shared build route explicit",
    "phase 4 bitmap survey keeps bitmap gate-evidence coverage explicit",
    "phase 4 bitmap survey keeps owner and rollback owner governance explicit",
    "phase4_bitmap_diff_manifest.json",
    "phase4_bitmap_live_helper_replay.zig",
    "Shared Subsystems Pod",
    "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
]

EXPECTED_ARTIFACT_DIFF_CONTRACT_SELF_TEST_LINES = [
    "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass",
    "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=17",
    "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=catalog_shape,review_note_marker_round_trip,review_note_marker_drift,helper_summary_round_trip,contract_summary_round_trip,helper_summary_status_drift,helper_summary_count_drift,helper_summary_duplicate_case_drift,helper_summary_case_order_drift,contract_summary_status_drift,contract_summary_base_count_drift,contract_summary_base_case_order_drift,contract_summary_repeat_count_drift,contract_summary_repeat_case_order_drift,contract_summary_case_count_drift,contract_summary_duplicate_case_drift,contract_summary_case_order_drift",
]

EXPECTED_ARTIFACT_DIFF_CONTRACT_LINES = [
    "ARTIFACT_DIFF_CONTRACT=pass",
    "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=23",
    "ARTIFACT_DIFF_CONTRACT_BASE_CASES=helper_self_test,cli_help_output,cli_missing_required_args,cli_missing_actual_operand,cli_invalid_mode,text_pass,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,sha256_pass,sha256_missing_expected,sha256_missing_actual,sha256_missing_both,sha256_drift",
    "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5",
    "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_repeat,sha256_drift_repeat",
    "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=28",
    "ARTIFACT_DIFF_CONTRACT_CASES=helper_self_test,helper_self_test_repeat,cli_help_output,cli_help_output_repeat,cli_missing_required_args,cli_missing_actual_operand,cli_invalid_mode,text_pass,text_pass_repeat,text_mismatch,text_missing_expected,text_missing_actual,text_missing_both,json_pass,json_mismatch,json_mismatch_repeat,json_missing_expected,json_missing_actual,json_missing_both,json_invalid_expected,json_invalid_actual,json_invalid_both,sha256_pass,sha256_missing_expected,sha256_missing_actual,sha256_missing_both,sha256_drift,sha256_drift_repeat",
]

EXPECTED_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_LINES = [
    "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass",
]

EXPECTED_ARTIFACT_DIFF_DETERMINISM_LINES = [
    "PHASE4_ARTIFACT_DIFF_DETERMINISM=pass",
    "PHASE4_ARTIFACT_DIFF_HELPER_CASE_COUNT=19",
    "PHASE4_ARTIFACT_DIFF_CONTRACT_CASE_COUNT=28",
    "PHASE4_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_repeat,sha256_drift_repeat",
]


def _missing_files(root: Path) -> list[str]:
    return [path for path in REQUIRED_FILES if not (root / path).exists()]


def _git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


def _line_value(lines: list[str], prefix: str) -> str | None:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :]
    return None


def _run_python_script(root: Path, relative_path: str, *args: str) -> tuple[int, list[str]]:
    result = subprocess.run(
        [sys.executable, str(root / relative_path), *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout.splitlines()


def _expect_exact_output(label: str, lines: list[str], expected_lines: list[str]) -> list[str]:
    if lines == expected_lines:
        return []
    return [
        f"{label}:unexpected_output",
        f"{label}:expected_count:{len(expected_lines)}",
        f"{label}:actual_count:{len(lines)}",
        f"{label}:expected_lines:{' || '.join(expected_lines)}",
        f"{label}:actual_lines:{' || '.join(lines)}",
    ]


def _collect_phony_targets(makefile: str) -> set[str]:
    targets: set[str] = set()
    for raw_line in makefile.splitlines():
        line = raw_line.strip()
        if not line.startswith("PHONY +="):
            continue
        _, value = line.split("+=", 1)
        for token in value.split():
            targets.add(token)
    return targets


def validate_root(root: Path) -> list[str]:
    problems: list[str] = []

    makefile = (root / "zigux/Makefile").read_text(encoding="utf-8")
    workflow = (root / ".github/workflows/zigux-bootstrap.yml").read_text(encoding="utf-8")
    artifact_doc = (root / "Documentation/zigux/artifact-diff.md").read_text(encoding="utf-8")
    doc_readme = (root / "Documentation/zigux/README.md").read_text(encoding="utf-8")
    script_readme = (root / "scripts/zigux/README.md").read_text(encoding="utf-8")
    tests_readme = (root / "zigux/tests/README.md").read_text(encoding="utf-8")
    review_checklist = (root / "Documentation/zigux/review-checklist.md").read_text(encoding="utf-8")
    phase4_matrix = (root / "Documentation/zigux/phase4-validation-matrix.md").read_text(
        encoding="utf-8"
    )
    phase4_build = (root / "zigux/tests/phase4_build.zig").read_text(encoding="utf-8")

    phony_targets = _collect_phony_targets(makefile)
    for target in REQUIRED_MAKE_PHONY_TARGETS:
        if target not in phony_targets:
            problems.append(f"make_phony:{target}")

    for marker in REQUIRED_MAKE_MARKERS:
        if marker not in makefile:
            problems.append(f"make:{marker}")
    for marker in REQUIRED_WORKFLOW_MARKERS:
        if marker not in workflow:
            problems.append(f"workflow:{marker}")
    for marker in REQUIRED_ARTIFACT_DOC_MARKERS:
        if marker not in artifact_doc:
            problems.append(f"artifact_doc:{marker}")
    for marker in REQUIRED_ARTIFACT_DIFF_TOOLING_NOTE_MARKERS:
        if marker not in artifact_doc:
            problems.append(f"artifact_doc_tooling_note:{marker}")
    for marker in REQUIRED_DOC_README_MARKERS:
        if marker not in doc_readme:
            problems.append(f"doc_readme:{marker}")
    for marker in REQUIRED_SCRIPT_README_MARKERS:
        if marker not in script_readme:
            problems.append(f"script_readme:{marker}")
    for marker in FORBIDDEN_SCRIPT_README_MARKERS:
        if marker in script_readme:
            problems.append(f"script_readme:forbidden:{marker}")
    for marker in REQUIRED_TESTS_README_MARKERS:
        if marker not in tests_readme:
            problems.append(f"tests_readme:{marker}")
    for marker in REQUIRED_REVIEW_CHECKLIST_MARKERS:
        if marker not in review_checklist:
            problems.append(f"review_checklist:{marker}")
    for marker in REQUIRED_PHASE4_MATRIX_MARKERS:
        if marker not in phase4_matrix:
            problems.append(f"phase4_matrix:{marker}")
    for marker in REQUIRED_PHASE4_BUILD_MARKERS:
        if marker not in phase4_build:
            problems.append(f"phase4_build:{marker}")

    return problems


def run_artifact_diff_contract_check(root: Path) -> list[str]:
    code, lines = _run_python_script(root, "scripts/zigux/check-artifact-diff-contract.py")
    if code != 0:
        return [f"artifact_diff_contract:exit:{code}"]
    return _expect_exact_output("artifact_diff_contract", lines, EXPECTED_ARTIFACT_DIFF_CONTRACT_LINES)


def run_artifact_diff_contract_self_test_check(root: Path) -> list[str]:
    code, lines = _run_python_script(root, "scripts/zigux/check-artifact-diff-contract.py", "--self-test")
    if code != 0:
        return [f"artifact_diff_contract_self_test:exit:{code}"]
    return _expect_exact_output(
        "artifact_diff_contract_self_test", lines, EXPECTED_ARTIFACT_DIFF_CONTRACT_SELF_TEST_LINES
    )


def run_phase4_artifact_diff_determinism_check(root: Path) -> list[str]:
    code, lines = _run_python_script(root, "scripts/zigux/check-phase4-artifact-diff-determinism.py")
    if code != 0:
        return [f"phase4_artifact_diff_determinism:exit:{code}"]
    return _expect_exact_output(
        "phase4_artifact_diff_determinism", lines, EXPECTED_ARTIFACT_DIFF_DETERMINISM_LINES
    )


def run_phase4_artifact_diff_determinism_self_test_check(root: Path) -> list[str]:
    code, lines = _run_python_script(
        root, "scripts/zigux/check-phase4-artifact-diff-determinism.py", "--self-test"
    )
    if code != 0:
        return [f"phase4_artifact_diff_determinism_self_test:exit:{code}"]
    return _expect_exact_output(
        "phase4_artifact_diff_determinism_self_test",
        lines,
        EXPECTED_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_LINES,
    )


def run_phase4_gate_evidence_check(root: Path) -> list[str]:
    code, lines = _run_python_script(root, "scripts/zigux/check-phase4-gate-evidence.py")
    if code != 0:
        return [f"phase4_gate_evidence:exit:{code}"]
    if "PHASE4_GATE_EVIDENCE_CHECK=pass" not in lines:
        return ["phase4_gate_evidence:missing_pass_marker"]
    if _line_value(lines, "PHASE4_GATE_EVIDENCE_TARGET_COUNT=") != "16":
        return ["phase4_gate_evidence:unexpected_target_count"]
    return []


def run_phase4_gate_evidence_self_test_check(root: Path) -> list[str]:
    code, lines = _run_python_script(root, "scripts/zigux/check-phase4-gate-evidence.py", "--self-test")
    if code != 0:
        return [f"phase4_gate_evidence_self_test:exit:{code}"]
    if "PHASE4_GATE_EVIDENCE_SELF_TEST=pass" not in lines:
        return ["phase4_gate_evidence_self_test:missing_pass_marker"]
    return []


def run_phase4_runtime_atomic64_packet_check(root: Path) -> list[str]:
    manifest = json.loads(
        (root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json").read_text(encoding="utf-8")
    )
    survey = (root / "zigux/tests/phase4_runtime_atomic64_diff_survey.zig").read_text(
        encoding="utf-8"
    )
    problems: list[str] = []

    for field, expected in PHASE4_RUNTIME_ATOMIC64_EXPECTED_STRINGS.items():
        if manifest.get(field) != expected:
            problems.append(f"runtime_atomic64_manifest:{field}:{manifest.get(field)}:{expected}")

    for field in PHASE4_RUNTIME_ATOMIC64_EXPECTED_TRUE_FIELDS:
        if manifest.get(field) is not True:
            problems.append(f"runtime_atomic64_manifest:{field}:{manifest.get(field)}:true")

    for field, markers in PHASE4_RUNTIME_ATOMIC64_REQUIRED_FIELD_MARKERS.items():
        value = manifest.get(field)
        if not isinstance(value, str):
            problems.append(f"runtime_atomic64_manifest:{field}:{value}:string")
            continue
        for marker in markers:
            if marker not in value:
                problems.append(f"runtime_atomic64_manifest_marker:{field}:{marker}")

    for field, relative_path in PHASE4_RUNTIME_ATOMIC64_MANIFEST_SHA_TARGETS.items():
        expected = _git_blob_sha1((root / relative_path).read_bytes())
        actual = manifest.get(field)
        if actual != expected:
            problems.append(f"runtime_atomic64_manifest:{field}:{actual}:{expected}")

    for field, relative_path in PHASE4_RUNTIME_ATOMIC64_LINE_COUNT_TARGETS.items():
        expected = len((root / relative_path).read_text(encoding="utf-8").splitlines())
        actual = manifest.get(field)
        if actual != expected:
            problems.append(f"runtime_atomic64_manifest_line_count:{field}:{actual}:{expected}")

    for relative_path, expected_count in PHASE4_RUNTIME_ATOMIC64_SURVEY_SHA_COUNTS.items():
        expected = _git_blob_sha1((root / relative_path).read_bytes())
        actual_count = survey.count(expected)
        if actual_count != expected_count:
            problems.append(
                f"runtime_atomic64_survey_sha_count:{relative_path}:{expected}:{actual_count}:{expected_count}"
            )
    return problems


def run_phase4_bitmap_packet_check(root: Path) -> list[str]:
    manifest = json.loads(
        (root / "zigux/tests/phase4_bitmap_diff_manifest.json").read_text(encoding="utf-8")
    )
    survey = (root / "zigux/tests/phase4_bitmap_diff_survey.zig").read_text(encoding="utf-8")
    problems: list[str] = []

    for field, expected in PHASE4_BITMAP_EXPECTED_STRINGS.items():
        if manifest.get(field) != expected:
            problems.append(f"bitmap_manifest:{field}:{manifest.get(field)}:{expected}")

    for field in PHASE4_BITMAP_EXPECTED_TRUE_FIELDS:
        if manifest.get(field) is not True:
            problems.append(f"bitmap_manifest:{field}:{manifest.get(field)}:true")

    for field, markers in PHASE4_BITMAP_REQUIRED_FIELD_MARKERS.items():
        value = manifest.get(field)
        if not isinstance(value, str):
            problems.append(f"bitmap_manifest:{field}:{value}:string")
            continue
        for marker in markers:
            if marker not in value:
                problems.append(f"bitmap_manifest_marker:{field}:{marker}")

    for field, relative_path in PHASE4_BITMAP_PIN_TARGETS.items():
        expected = _git_blob_sha1((root / relative_path).read_bytes())
        actual = manifest.get(field)
        if actual != expected:
            problems.append(f"bitmap_manifest_sha:{field}:{actual}:{expected}")
        if survey.count(expected) != 1:
            problems.append(f"bitmap_survey_sha_count:{field}:{expected}:{survey.count(expected)}:1")

    for marker in PHASE4_BITMAP_SURVEY_MARKERS:
        if marker not in survey:
            problems.append(f"bitmap_survey:{marker}")

    return problems


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_fixture_tree(root: Path) -> None:
    _write(root / "scripts/zigux/artifact_diff.py", "#!/usr/bin/env python3\n")
    _write(
        root / "scripts/zigux/check-artifact-diff-contract.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import sys",
                f"SELF_TEST_LINES = {EXPECTED_ARTIFACT_DIFF_CONTRACT_SELF_TEST_LINES!r}",
                f"CONTRACT_LINES = {EXPECTED_ARTIFACT_DIFF_CONTRACT_LINES!r}",
                "if '--self-test' in sys.argv:",
                "    for line in SELF_TEST_LINES:",
                "        print(line)",
                "else:",
                "    for line in CONTRACT_LINES:",
                "        print(line)",
                "",
            ]
        ),
    )
    _write(
        root / "scripts/zigux/check-phase4-artifact-diff-determinism.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import sys",
                f"SELF_TEST_LINES = {EXPECTED_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_LINES!r}",
                f"CHECK_LINES = {EXPECTED_ARTIFACT_DIFF_DETERMINISM_LINES!r}",
                "if '--self-test' in sys.argv:",
                "    for line in SELF_TEST_LINES:",
                "        print(line)",
                "else:",
                "    for line in CHECK_LINES:",
                "        print(line)",
                "",
            ]
        ),
    )
    _write(
        root / "scripts/zigux/check-phase4-gate-evidence.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import sys",
                "if '--self-test' in sys.argv:",
                "    print('PHASE4_GATE_EVIDENCE_SELF_TEST=pass')",
                "else:",
                "    print('PHASE4_GATE_EVIDENCE_CHECK=pass')",
                "    print('PHASE4_GATE_EVIDENCE_TARGET_COUNT=16')",
                "",
            ]
        ),
    )
    _write(root / "scripts/zigux/validate-phase4.py", "# fixture\n")
    _write(
        root / "Documentation/zigux/artifact-diff.md",
        "\n".join(
            [
                "Current Phase 4 use",
                "scripts/zigux/check-phase4-gate-evidence.py",
                "zigux/tests/atomic64_diff.zig",
                "zigux/tests/runtime_atomic64_diff.zig",
                "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
                "zigux/tests/bitmap_diff.zig",
                "zigux/tests/phase4_bitmap_diff_manifest.json",
                "zigux/tests/phase4_bitmap_diff_survey.zig",
                "zigux/tests/phase4_bitmap_live_helper_replay.zig",
                "zigux/tests/phase4_build.zig",
                "scripts/zigux/validate-phase4.py",
                "Documentation/zigux/phase4-validation-matrix.md",
                "",
                "## Phase 4 Tooling Review Note",
                "",
                *REQUIRED_ARTIFACT_DIFF_TOOLING_NOTE_MARKERS,
                "",
            ]
        ),
    )
    _write(
        root / "Documentation/zigux/README.md",
        "\n".join(REQUIRED_DOC_README_MARKERS + [""]),
    )
    _write(
        root / "scripts/zigux/README.md",
        "\n".join(REQUIRED_SCRIPT_README_MARKERS + [""]),
    )
    _write(
        root / "zigux/tests/README.md",
        "\n".join(REQUIRED_TESTS_README_MARKERS + [""]),
    )
    _write(
        root / "Documentation/zigux/review-checklist.md",
        "\n".join(REQUIRED_REVIEW_CHECKLIST_MARKERS + [""]),
    )
    _write(
        root / "Documentation/zigux/phase4-validation-matrix.md",
        "\n".join(REQUIRED_PHASE4_MATRIX_MARKERS + [""]),
    )
    phony_line = "PHONY += " + " ".join(REQUIRED_MAKE_PHONY_TARGETS)
    _write(
        root / "zigux/Makefile",
        "\n".join([phony_line, *REQUIRED_MAKE_MARKERS, ""]),
    )
    _write(
        root / ".github/workflows/zigux-bootstrap.yml",
        "\n".join(REQUIRED_WORKFLOW_MARKERS + [""]),
    )
    _write(root / "zigux/tests/atomic64_diff.zig", "// atomic64 diff\n")
    _write(root / "zigux/tests/runtime_atomic64_diff.zig", "// runtime atomic64 diff\n")
    _write(root / "zigux/tests/bitmap_diff.zig", "// bitmap diff\n")
    _write(root / "zigux/tests/phase4_bitmap_live_helper_replay.zig", "// helper replay\n")
    _write(root / "zigux/tests/phase4_perf_baseline_manifest.json", "{}\n")
    _write(root / "zigux/tests/phase4_perf_baseline_survey.zig", "// perf baseline survey\n")
    _write(root / "Documentation/zigux/phase4-gate-evidence.md", "phase4 gate evidence fixture\n")
    _write(root / "zigux/tests/phase4_build.zig", "\n".join(REQUIRED_PHASE4_BUILD_MARKERS + [""]))
    _write(root / "zigux/tests/phase9_build.zig", "// phase9 build\n")

    runtime_manifest = dict(PHASE4_RUNTIME_ATOMIC64_EXPECTED_STRINGS)
    runtime_manifest.update({field: True for field in PHASE4_RUNTIME_ATOMIC64_EXPECTED_TRUE_FIELDS})
    runtime_manifest.update(
        {
            field: _git_blob_sha1((root / path).read_bytes())
            for field, path in PHASE4_RUNTIME_ATOMIC64_MANIFEST_SHA_TARGETS.items()
        }
    )
    runtime_manifest.update(
        {
            field: len((root / path).read_text(encoding="utf-8").splitlines())
            for field, path in PHASE4_RUNTIME_ATOMIC64_LINE_COUNT_TARGETS.items()
        }
    )
    runtime_manifest.update(
        {
            "roadmap_gap_summary": "zigux/tests/atomic64_diff.zig and zigux/tests/phase4_perf_baseline_manifest.json plus zigux/tests/phase4_perf_baseline_survey.zig remain explicit in the bounded Phase 4 packet.",
            "reversible_delivery_evidence": "zigux/tests/atomic64_diff.zig zigux/tests/runtime_atomic64_diff.zig zigux/tests/phase4_build.zig scripts/zigux/validate-phase4.py Documentation/zigux/phase4-gate-evidence.md Documentation/zigux/review-checklist.md Documentation/zigux/phase4-validation-matrix.md zigux/tests/phase4_perf_baseline_manifest.json zigux/tests/phase4_perf_baseline_survey.zig",
            "ready_next": "Documentation/zigux/phase4-gate-evidence.md Documentation/zigux/phase4-validation-matrix.md zigux/tests/phase4_perf_baseline_manifest.json zigux/tests/phase4_perf_baseline_survey.zig",
        }
    )
    _write(
        root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
        json.dumps(runtime_manifest, indent=2) + "\n",
    )
    _write(
        root / "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
        "\n".join(
            runtime_manifest[field]
            for field in (
                "live_gate_blob_sha",
                "runtime_replay_blob_sha",
                "phase4_build_blob_sha",
                "phase4_validator_blob_sha",
                "phase4_validation_matrix_blob_sha",
                "phase4_review_checklist_blob_sha",
                "phase9_build_blob_sha",
            )
        )
        + "\n",
    )

    bitmap_manifest = dict(PHASE4_BITMAP_EXPECTED_STRINGS)
    bitmap_manifest.update({field: True for field in PHASE4_BITMAP_EXPECTED_TRUE_FIELDS})
    bitmap_manifest.update(
        {
            "roadmap_gap_summary": "zigux/tests/bitmap_diff.zig phase4_build.zig Shared Subsystems Pod rollback owner",
            "reversible_delivery_evidence": "zigux/tests/bitmap_diff.zig zigux/tests/phase4_bitmap_live_helper_replay.zig Documentation/zigux/phase4-gate-evidence.md zigux/tests/phase4_bitmap_diff_manifest.json zigux/tests/phase4_bitmap_diff_survey.zig zigux/tests/phase4_build.zig",
            "ready_next": "scripts/zigux/validate-phase4.py Documentation/zigux/phase4-validation-matrix.md Shared Subsystems Pod samples perf-threshold approval",
        }
    )
    for field, path in PHASE4_BITMAP_PIN_TARGETS.items():
        bitmap_manifest[field] = _git_blob_sha1((root / path).read_bytes())
    _write(root / "zigux/tests/phase4_bitmap_diff_manifest.json", json.dumps(bitmap_manifest, indent=2) + "\n")
    _write(
        root / "zigux/tests/phase4_bitmap_diff_survey.zig",
        "\n".join(PHASE4_BITMAP_SURVEY_MARKERS + [bitmap_manifest[field] for field in PHASE4_BITMAP_PIN_TARGETS]) + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_validator_") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)
        assert _missing_files(root) == []
        assert validate_root(root) == []
        assert run_artifact_diff_contract_check(root) == []
        assert run_artifact_diff_contract_self_test_check(root) == []
        assert run_phase4_artifact_diff_determinism_check(root) == []
        assert run_phase4_artifact_diff_determinism_self_test_check(root) == []
        assert run_phase4_gate_evidence_check(root) == []
        assert run_phase4_gate_evidence_self_test_check(root) == []
        assert run_phase4_runtime_atomic64_packet_check(root) == []
        assert run_phase4_bitmap_packet_check(root) == []

        bad_root = Path(tmp_dir) / "bad"
        build_fixture_tree(bad_root)
        makefile = bad_root / "zigux/Makefile"
        makefile.write_text(
            makefile.read_text(encoding="utf-8").replace("phase4-perf-baseline-survey ", "", 1),
            encoding="utf-8",
        )
        assert validate_root(bad_root) == ["make_phony:phase4-perf-baseline-survey"]

        bad_root2 = Path(tmp_dir) / "bad2"
        build_fixture_tree(bad_root2)
        makefile = bad_root2 / "zigux/Makefile"
        makefile.write_text(
            makefile.read_text(encoding="utf-8").replace(
                "phase4-perf-baseline-survey:\n", "", 1
            ),
            encoding="utf-8",
        )
        assert validate_root(bad_root2) == ["make:phase4-perf-baseline-survey:"]

    print("PHASE4_VALIDATE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 4 rollback-readiness packet.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated validator coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = _missing_files(ROOT)
    if missing:
        print("PHASE4_VALIDATION=fail")
        print("MISSING_PHASE4_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE4_FILES_END")
        return 1

    problems = validate_root(ROOT)
    if problems:
        print("PHASE4_VALIDATION=fail")
        print("MISSING_PHASE4_MARKERS_START")
        for item in problems:
            print(item)
        print("MISSING_PHASE4_MARKERS_END")
        return 1

    for label, failures in [
        ("ARTIFACT_DIFF_CONTRACT_CHECK", run_artifact_diff_contract_check(ROOT)),
        ("ARTIFACT_DIFF_CONTRACT_SELF_TEST_CHECK", run_artifact_diff_contract_self_test_check(ROOT)),
        ("PHASE4_ARTIFACT_DIFF_DETERMINISM_CHECK", run_phase4_artifact_diff_determinism_check(ROOT)),
        (
            "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CHECK",
            run_phase4_artifact_diff_determinism_self_test_check(ROOT),
        ),
        ("PHASE4_GATE_EVIDENCE_CHECK", run_phase4_gate_evidence_check(ROOT)),
        ("PHASE4_GATE_EVIDENCE_SELF_TEST_CHECK", run_phase4_gate_evidence_self_test_check(ROOT)),
        ("PHASE4_RUNTIME_ATOMIC64_PACKET_CHECK", run_phase4_runtime_atomic64_packet_check(ROOT)),
        ("PHASE4_BITMAP_PACKET_CHECK", run_phase4_bitmap_packet_check(ROOT)),
    ]:
        if failures:
            print("PHASE4_VALIDATION=fail")
            print(f"{label}_START")
            for item in failures:
                print(item)
            print(f"{label}_END")
            return 1

    print("PHASE4_VALIDATION=pass")
    print(f"PHASE4_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    marker_count = (
        len(REQUIRED_MAKE_PHONY_TARGETS)
        + len(REQUIRED_MAKE_MARKERS)
        + sum(
            len(group)
            for group in [
                REQUIRED_WORKFLOW_MARKERS,
                REQUIRED_ARTIFACT_DOC_MARKERS,
                REQUIRED_ARTIFACT_DIFF_TOOLING_NOTE_MARKERS,
                REQUIRED_DOC_README_MARKERS,
                REQUIRED_SCRIPT_README_MARKERS,
                REQUIRED_TESTS_README_MARKERS,
                REQUIRED_REVIEW_CHECKLIST_MARKERS,
                REQUIRED_PHASE4_MATRIX_MARKERS,
                REQUIRED_PHASE4_BUILD_MARKERS,
            ]
        )
    )
    print(f"PHASE4_REQUIRED_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
