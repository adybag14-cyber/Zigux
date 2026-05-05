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
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent

REQUIRED_FILES = [
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_build.zig",
]

REQUIRED_MAKE_MARKERS = [
    "PHONY += phase4-validate phase4-test",
    "phase4-validate:",
    "scripts/zigux/validate-phase4.py",
    "phase4-test:",
    "zigux/tests/phase4_build.zig",
]
REQUIRED_WORKFLOW_MARKERS = [
    "python3 scripts/zigux/validate-phase4.py",
    "python3 scripts/zigux/validate-phase4.py --self-test",
    "zig build test --build-file zigux/tests/phase4_build.zig",
]
REQUIRED_DOC_MARKERS = [
    "Current Phase 4 use",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
]
REQUIRED_PHASE4_GATE_EVIDENCE_MARKERS = [
    "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions",
    "PHASE4_VALIDATOR_BLOB_SHA=",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=14",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=",
    "PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=16",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=14",
    "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false",
    "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false",
    "hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
]
REQUIRED_TESTS_README_MARKERS = [
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
]
REQUIRED_SCRIPT_README_MARKERS = [
    "validate-phase4.py",
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
    "phase4_runtime_atomic64_diff_survey.zig",
    "Phase 4 flow",
    "phase4_build.zig",
    "phase4-gate-evidence.md",
    "phase4-validation-matrix.md",
    "make -C zigux phase4-bitmap-live-helper-replay",
    "intentionally unapproved perf-threshold posture",
]
FORBIDDEN_SCRIPT_README_MARKERS = [
    "make -C zigux phase4-perf-baseline-survey",
    "phase4-perf-baseline-survey",
]
REQUIRED_DOC_README_MARKERS = [
    "Phase 4 notes",
    "validate-phase4.py",
    "phase4-gate-evidence.md",
    "phase4-validation-matrix.md",
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
    "phase4_runtime_atomic64_diff_survey.zig",
    "intentionally unapproved perf-threshold posture",
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
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
    "phase4_runtime_atomic64_diff_manifest.json",
    "phase4_runtime_atomic64_diff_survey.zig",
    "bitmap_diff.zig",
    "phase4_bitmap_live_helper_replay.zig",
    "rollback owner",
    "Lab And CI Matrix",
    "threshold posture",
    "zig build test --build-file zigux/tests/phase4_build.zig",
    "Remaining Roadmap Gaps",
    "samples/zigux/kprobe_example.zig",
    "samples/kprobes/kprobe_example.c",
    "samples/zigux/test_fsmount.zig",
    "samples/vfs/test-fsmount.c",
    "hard perf thresholds and acceptable limits for the atomic64 and bitmap gates remain intentionally unapproved",
]
REQUIRED_PHASE4_BUILD_MARKERS = [
    "atomic64_diff.zig",
    "phase4_runtime_atomic64_diff_survey.zig",
    "bitmap_diff.zig",
    "phase4_bitmap_live_helper_replay.zig",
    "phase4-runtime-atomic64-diff-tests",
    "phase4-runtime-atomic64-diff-survey-tests",
    "phase4-bitmap-diff-tests",
    "phase4-bitmap-live-helper-replay-tests",
]
EXACT_ONCE_TESTS_README_MARKERS = [
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/bitmap_diff.zig",
]
EXACT_ONCE_SCRIPT_README_MARKERS = [
    "Phase 4 flow",
    "phase4-gate-evidence.md",
    "phase4-validation-matrix.md",
    "phase4_runtime_atomic64_diff_survey.zig",
    "make -C zigux phase4-bitmap-live-helper-replay",
    "intentionally unapproved perf-threshold posture",
]
EXACT_ONCE_DOC_README_MARKERS = [
    "Phase 4 notes",
    "validate-phase4.py",
    "phase4-gate-evidence.md",
    "phase4-validation-matrix.md",
    "runtime_atomic64_diff.zig",
    "phase4_runtime_atomic64_diff_survey.zig",
    "intentionally unapproved perf-threshold posture",
]
EXACT_ONCE_REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 4 validation packet",
]
EXACT_ONCE_ARTIFACT_DOC_MARKERS = [
    "scripts/zigux/check-phase4-gate-evidence.py",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "scripts/zigux/validate-phase4.py",
]

EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES = [
    "helper_self_test",
    "helper_self_test_repeat",
    "cli_missing_required_args",
    "cli_missing_actual_operand",
    "text_pass",
    "text_pass_repeat",
    "text_mismatch",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "json_pass",
    "json_mismatch",
    "json_mismatch_repeat",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "sha256_pass",
    "sha256_missing_expected",
    "sha256_missing_actual",
    "sha256_missing_both",
    "sha256_drift",
    "sha256_drift_repeat",
]
EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES = [
    "helper_self_test_repeat",
    "text_pass_repeat",
    "json_mismatch_repeat",
    "sha256_drift_repeat",
]
EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES = [
    case
    for case in EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES
    if case not in EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES
]
EXPECTED_ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES = [
    "catalog_shape",
    "helper_summary_round_trip",
    "contract_summary_round_trip",
    "helper_summary_status_drift",
    "helper_summary_count_drift",
    "helper_summary_duplicate_case_drift",
    "helper_summary_case_order_drift",
    "contract_summary_status_drift",
    "contract_summary_base_count_drift",
    "contract_summary_base_case_order_drift",
    "contract_summary_repeat_count_drift",
    "contract_summary_repeat_case_order_drift",
    "contract_summary_case_count_drift",
    "contract_summary_duplicate_case_drift",
    "contract_summary_case_order_drift",
]
EXPECTED_PHASE4_GATE_EVIDENCE_TARGET_COUNT = 16
EXPECTED_PHASE4_GATE_EVIDENCE_SELF_TEST_CASES = [
    "baseline_round_trip",
    "shipped_target_count_drift",
    "missing_exact_readback_heading",
    "validator_blob_pin_drift",
    "phase4_build_manifest_blob_pin_drift",
    "phase4_build_survey_blob_pin_drift",
    "phase9_build_manifest_blob_pin_drift",
    "phase9_build_survey_blob_pin_drift",
    "gate_evidence_self_test_case_count_drift",
    "gate_evidence_self_test_cases_drift",
    "shared_validator_reruns_gate_evidence_self_test_drift",
    "shared_validator_expected_target_count_drift",
    "shared_validator_expected_self_test_case_count_drift",
    "missing_note_file",
]
PHASE4_RUNTIME_ATOMIC64_PIN_TARGETS = {
    "phase4_build_blob_sha": "zigux/tests/phase4_build.zig",
    "phase4_validator_blob_sha": "scripts/zigux/validate-phase4.py",
    "phase4_validation_matrix_blob_sha": "Documentation/zigux/phase4-validation-matrix.md",
    "phase9_build_blob_sha": "zigux/tests/phase9_build.zig",
}


def _missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def _count_marker(text: str, marker: str) -> int:
    return text.count(marker)


def _require_exact_once(text: str, marker: str, prefix: str, missing_markers: list[str]) -> None:
    count = _count_marker(text, marker)
    if count != 1:
        missing_markers.append(f"{prefix}:exact_once:{marker}:{count}")


def _line_value(lines: list[str], prefix: str) -> str | None:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :]
    return None


def _expected_case_line(cases: list[str]) -> str:
    return ",".join(cases)


def _git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


def validate_root(root: Path) -> list[str]:
    missing_markers: list[str] = []

    makefile = (root / "zigux/Makefile").read_text(encoding="utf-8")
    workflow = (root / ".github/workflows/zigux-bootstrap.yml").read_text(encoding="utf-8")
    artifact_doc = (root / "Documentation/zigux/artifact-diff.md").read_text(encoding="utf-8")
    phase4_gate_evidence = (root / "Documentation/zigux/phase4-gate-evidence.md").read_text(
        encoding="utf-8"
    )
    tests_readme = (root / "zigux/tests/README.md").read_text(encoding="utf-8")
    script_readme = (root / "scripts/zigux/README.md").read_text(encoding="utf-8")
    doc_readme = (root / "Documentation/zigux/README.md").read_text(encoding="utf-8")
    review_checklist = (root / "Documentation/zigux/review-checklist.md").read_text(
        encoding="utf-8"
    )
    phase4_matrix = (root / "Documentation/zigux/phase4-validation-matrix.md").read_text(
        encoding="utf-8"
    )
    phase4_build = (root / "zigux/tests/phase4_build.zig").read_text(encoding="utf-8")

    for marker in REQUIRED_MAKE_MARKERS:
        if marker not in makefile:
            missing_markers.append(f"make:{marker}")
    for marker in REQUIRED_WORKFLOW_MARKERS:
        if marker not in workflow:
            missing_markers.append(f"workflow:{marker}")
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in artifact_doc:
            missing_markers.append(f"doc:{marker}")
    for marker in REQUIRED_PHASE4_GATE_EVIDENCE_MARKERS:
        if marker not in phase4_gate_evidence:
            missing_markers.append(f"gate_evidence:{marker}")
    for marker in REQUIRED_TESTS_README_MARKERS:
        if marker not in tests_readme:
            missing_markers.append(f"tests_readme:{marker}")
    for marker in REQUIRED_SCRIPT_README_MARKERS:
        if marker not in script_readme:
            missing_markers.append(f"script_readme:{marker}")
    for marker in FORBIDDEN_SCRIPT_README_MARKERS:
        count = _count_marker(script_readme, marker)
        if count != 0:
            missing_markers.append(f"script_readme:forbidden:{marker}:{count}")
    for marker in REQUIRED_DOC_README_MARKERS:
        if marker not in doc_readme:
            missing_markers.append(f"doc_readme:{marker}")
    for marker in REQUIRED_REVIEW_CHECKLIST_MARKERS:
        if marker not in review_checklist:
            missing_markers.append(f"review_checklist:{marker}")
    for marker in REQUIRED_PHASE4_MATRIX_MARKERS:
        if marker not in phase4_matrix:
            missing_markers.append(f"phase4_matrix:{marker}")
    for marker in REQUIRED_PHASE4_BUILD_MARKERS:
        if marker not in phase4_build:
            missing_markers.append(f"phase4_build:{marker}")

    _require_exact_once(artifact_doc, "Current Phase 4 use", "doc", missing_markers)
    for marker in EXACT_ONCE_ARTIFACT_DOC_MARKERS:
        _require_exact_once(artifact_doc, marker, "doc", missing_markers)
    for marker in EXACT_ONCE_TESTS_README_MARKERS:
        _require_exact_once(tests_readme, marker, "tests_readme", missing_markers)
    for marker in EXACT_ONCE_SCRIPT_README_MARKERS:
        _require_exact_once(script_readme, marker, "script_readme", missing_markers)
    for marker in EXACT_ONCE_DOC_README_MARKERS:
        _require_exact_once(doc_readme, marker, "doc_readme", missing_markers)
    for marker in EXACT_ONCE_REVIEW_CHECKLIST_MARKERS:
        _require_exact_once(review_checklist, marker, "review_checklist", missing_markers)

    return missing_markers


def _run_python_script(root: Path, relative_path: str, *args: str) -> tuple[int, list[str]]:
    result = subprocess.run(
        [sys.executable, str(root / relative_path), *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout.splitlines()


def run_artifact_diff_contract_check(root: Path) -> list[str]:
    returncode, lines = _run_python_script(root, "scripts/zigux/check-artifact-diff-contract.py")
    if returncode != 0:
        return [f"artifact_diff_contract:exit:{returncode}"]
    if "ARTIFACT_DIFF_CONTRACT=pass" not in lines:
        return ["artifact_diff_contract:missing_pass_marker"]

    expected = [
        (
            "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=",
            str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES)),
            "missing_base_case_count_marker",
            "unexpected_base_case_count",
        ),
        (
            "ARTIFACT_DIFF_CONTRACT_BASE_CASES=",
            _expected_case_line(EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES),
            "missing_base_cases_marker",
            "unexpected_base_cases",
        ),
        (
            "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=",
            str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES)),
            "missing_repeat_case_count_marker",
            "unexpected_repeat_case_count",
        ),
        (
            "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=",
            _expected_case_line(EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES),
            "missing_repeat_cases_marker",
            "unexpected_repeat_cases",
        ),
        (
            "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=",
            str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES)),
            "missing_case_count_marker",
            "unexpected_case_count",
        ),
        (
            "ARTIFACT_DIFF_CONTRACT_CASES=",
            _expected_case_line(EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES),
            "missing_cases_marker",
            "unexpected_cases",
        ),
    ]
    for prefix, expected_value, missing_code, drift_code in expected:
        actual = _line_value(lines, prefix)
        if actual is None:
            return [f"artifact_diff_contract:{missing_code}"]
        if actual != expected_value:
            return [f"artifact_diff_contract:{drift_code}:{actual}"]
    return []


def run_artifact_diff_contract_self_test_check(root: Path) -> list[str]:
    returncode, lines = _run_python_script(
        root, "scripts/zigux/check-artifact-diff-contract.py", "--self-test"
    )
    if returncode != 0:
        return [f"artifact_diff_contract_self_test:exit:{returncode}"]
    if "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass" not in lines:
        return ["artifact_diff_contract_self_test:missing_pass_marker"]

    case_count = _line_value(lines, "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=")
    if case_count is None:
        return ["artifact_diff_contract_self_test:missing_case_count_marker"]
    if case_count != str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES)):
        return [f"artifact_diff_contract_self_test:unexpected_case_count:{case_count}"]

    cases = _line_value(lines, "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=")
    if cases is None:
        return ["artifact_diff_contract_self_test:missing_cases_marker"]
    if cases != _expected_case_line(EXPECTED_ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES):
        return [f"artifact_diff_contract_self_test:unexpected_cases:{cases}"]
    return []


def run_phase4_gate_evidence_check(root: Path) -> list[str]:
    returncode, lines = _run_python_script(root, "scripts/zigux/check-phase4-gate-evidence.py")
    if returncode != 0:
        return [f"phase4_gate_evidence:exit:{returncode}"]
    if "PHASE4_GATE_EVIDENCE_CHECK=pass" not in lines:
        return ["phase4_gate_evidence:missing_pass_marker"]

    target_count = _line_value(lines, "PHASE4_GATE_EVIDENCE_TARGET_COUNT=")
    if target_count is None:
        return ["phase4_gate_evidence:missing_target_count_marker"]
    if target_count != str(EXPECTED_PHASE4_GATE_EVIDENCE_TARGET_COUNT):
        return [f"phase4_gate_evidence:unexpected_target_count:{target_count}"]
    return []


def run_phase4_gate_evidence_self_test_check(root: Path) -> list[str]:
    returncode, lines = _run_python_script(
        root, "scripts/zigux/check-phase4-gate-evidence.py", "--self-test"
    )
    if returncode != 0:
        return [f"phase4_gate_evidence_self_test:exit:{returncode}"]
    if "PHASE4_GATE_EVIDENCE_SELF_TEST=pass" not in lines:
        return ["phase4_gate_evidence_self_test:missing_pass_marker"]

    case_count = _line_value(lines, "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=")
    if case_count is None:
        return ["phase4_gate_evidence_self_test:missing_case_count_marker"]
    if case_count != str(len(EXPECTED_PHASE4_GATE_EVIDENCE_SELF_TEST_CASES)):
        return [f"phase4_gate_evidence_self_test:unexpected_case_count:{case_count}"]

    cases = _line_value(lines, "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=")
    if cases is None:
        return ["phase4_gate_evidence_self_test:missing_cases_marker"]
    if cases != _expected_case_line(EXPECTED_PHASE4_GATE_EVIDENCE_SELF_TEST_CASES):
        return [f"phase4_gate_evidence_self_test:unexpected_cases:{cases}"]
    return []


def run_phase4_runtime_atomic64_packet_check(root: Path) -> list[str]:
    manifest_path = root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json"
    survey_path = root / "zigux/tests/phase4_runtime_atomic64_diff_survey.zig"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"phase4_runtime_atomic64_packet:invalid_manifest_json:{exc.msg}"]

    survey_text = survey_path.read_text(encoding="utf-8")
    missing: list[str] = []
    for field, relative_path in PHASE4_RUNTIME_ATOMIC64_PIN_TARGETS.items():
        expected = _git_blob_sha1((root / relative_path).read_bytes())
        actual = manifest.get(field)
        if actual is None:
            missing.append(f"phase4_runtime_atomic64_packet:missing_manifest_field:{field}")
            continue
        if actual != expected:
            missing.append(
                f"phase4_runtime_atomic64_packet:unexpected_manifest_sha:{field}:{actual}:{expected}"
            )
        count = survey_text.count(expected)
        if count != 1:
            missing.append(
                f"phase4_runtime_atomic64_packet:survey_sha_exact_count:{field}:{expected}:{count}"
            )
    return missing


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _write_contract_checker_fixture(
    path: Path,
    *,
    base_case_count: str | None,
    base_cases: list[str] | None,
    repeat_case_count: str | None,
    repeat_cases: list[str] | None,
    case_count: str | None,
    cases: list[str] | None,
    include_pass: bool = True,
    self_test_case_count: str | None,
    self_test_cases: list[str] | None,
    include_self_test_pass: bool = True,
) -> None:
    lines = ["#!/usr/bin/env python3", "import sys", "if '--self-test' in sys.argv:"]
    if include_self_test_pass:
        lines.append("    print('ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass')")
    if self_test_case_count is not None:
        lines.append(f"    print('ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT={self_test_case_count}')")
    if self_test_cases is not None:
        lines.append(
            "    print('ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES="
            + ",".join(self_test_cases)
            + "')"
        )
    lines.append("    raise SystemExit(0)")
    if include_pass:
        lines.append("print('ARTIFACT_DIFF_CONTRACT=pass')")
    if base_case_count is not None:
        lines.append(f"print('ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={base_case_count}')")
    if base_cases is not None:
        lines.append("print('ARTIFACT_DIFF_CONTRACT_BASE_CASES=" + ",".join(base_cases) + "')")
    if repeat_case_count is not None:
        lines.append(f"print('ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={repeat_case_count}')")
    if repeat_cases is not None:
        lines.append("print('ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=" + ",".join(repeat_cases) + "')")
    if case_count is not None:
        lines.append(f"print('ARTIFACT_DIFF_CONTRACT_CASE_COUNT={case_count}')")
    if cases is not None:
        lines.append("print('ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join(cases) + "')")
    _write(path, "\n".join(lines) + "\n")


def _write_phase4_gate_evidence_checker_fixture(
    path: Path,
    *,
    include_check_pass: bool = True,
    target_count: str | None = str(EXPECTED_PHASE4_GATE_EVIDENCE_TARGET_COUNT),
    include_self_test_pass: bool = True,
    self_test_case_count: str | None = None,
    self_test_cases: list[str] | None = None,
) -> None:
    lines = ["#!/usr/bin/env python3", "import sys", "if '--self-test' in sys.argv:"]
    if include_self_test_pass:
        lines.append("    print('PHASE4_GATE_EVIDENCE_SELF_TEST=pass')")
    if self_test_case_count is not None:
        lines.append(f"    print('PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={self_test_case_count}')")
    if self_test_cases is not None:
        lines.append(
            "    print('PHASE4_GATE_EVIDENCE_SELF_TEST_CASES="
            + ",".join(self_test_cases)
            + "')"
        )
    lines.append("else:")
    if include_check_pass:
        lines.append("    print('PHASE4_GATE_EVIDENCE_CHECK=pass')")
    if target_count is not None:
        lines.append(f"    print('PHASE4_GATE_EVIDENCE_TARGET_COUNT={target_count}')")
    _write(path, "\n".join(lines) + "\n")


def _write_phase4_runtime_atomic64_packet_fixture(root: Path) -> None:
    phase4_build_sha = _git_blob_sha1((root / "zigux/tests/phase4_build.zig").read_bytes())
    validator_sha = _git_blob_sha1((root / "scripts/zigux/validate-phase4.py").read_bytes())
    matrix_sha = _git_blob_sha1((root / "Documentation/zigux/phase4-validation-matrix.md").read_bytes())
    phase9_build_sha = _git_blob_sha1((root / "zigux/tests/phase9_build.zig").read_bytes())
    manifest = {
        "phase4_build_blob_sha": phase4_build_sha,
        "phase4_validator_blob_sha": validator_sha,
        "phase4_validation_matrix_blob_sha": matrix_sha,
        "phase9_build_blob_sha": phase9_build_sha,
    }
    _write(
        root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
        json.dumps(manifest, indent=2) + "\n",
    )
    _write(
        root / "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
        "\n".join(
            [
                'const std = @import("std");',
                "",
                'test "fixture keeps current phase4 build, validator, matrix, and phase9 build pins" {',
                f"    // phase4 build pin {phase4_build_sha}",
                f"    // validator pin {validator_sha}",
                f"    // matrix pin {matrix_sha}",
                f"    // phase9 build pin {phase9_build_sha}",
                "}",
                "",
            ]
        ),
    )


def _write_phase4_fixture_docs(root: Path) -> None:
    _write(
        root / "Documentation/zigux/artifact-diff.md",
        "\n".join(
            [
                "# Artifact Diff Policy",
                "",
                "Current Phase 4 use",
                "- `scripts/zigux/artifact_diff.py`",
                "- `scripts/zigux/check-phase4-gate-evidence.py` and `Documentation/zigux/phase4-gate-evidence.md` keep the dedicated exact-readback companion packet explicit beside the validator-backed rollback surfaces.",
                "- `zigux/tests/atomic64_diff.zig`",
                "- `zigux/tests/runtime_atomic64_diff.zig`",
                "- `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`",
                "- `zigux/tests/bitmap_diff.zig`",
                "- `zigux/tests/phase4_bitmap_live_helper_replay.zig`",
                "- `zigux/tests/phase4_build.zig`",
                "- `scripts/zigux/validate-phase4.py`",
                "- `Documentation/zigux/phase4-validation-matrix.md`",
                "",
            ]
        ),
    )
    _write(
        root / "Documentation/zigux/phase4-gate-evidence.md",
        "\n".join(
            [
                "# Phase 4 Gate Evidence",
                "",
                "## Status",
                "- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`",
                "- `PHASE4_VALIDATOR_BLOB_SHA=placeholder`",
                "- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=14`",
                "- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES="
                + ",".join(EXPECTED_PHASE4_GATE_EVIDENCE_SELF_TEST_CASES)
                + "`",
                "- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
                "- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`",
                "- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`",
                "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=16`",
                "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=14`",
                "- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`",
                "- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false`",
                "",
                "## Exact Readback Evidence",
                "- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` stays in the packet.",
                "- `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` stays in the packet.",
                "",
                "## Current Conclusion",
                "- hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
                "",
            ]
        ),
    )
    _write(
        root / "Documentation/zigux/phase4-validation-matrix.md",
        "\n".join(
            [
                "# Phase 4 Validation Matrix",
                "",
                "atomic64_diff.zig",
                "runtime_atomic64_diff.zig",
                "phase4_runtime_atomic64_diff_manifest.json",
                "phase4_runtime_atomic64_diff_survey.zig",
                "bitmap_diff.zig",
                "phase4_bitmap_live_helper_replay.zig",
                "rollback owner",
                "Lab And CI Matrix",
                "threshold posture",
                "zig build test --build-file zigux/tests/phase4_build.zig",
                "Remaining Roadmap Gaps",
                "samples/zigux/kprobe_example.zig",
                "samples/kprobes/kprobe_example.c",
                "samples/zigux/test_fsmount.zig",
                "samples/vfs/test-fsmount.c",
                "hard perf thresholds and acceptable limits for the atomic64 and bitmap gates remain intentionally unapproved",
                "",
            ]
        ),
    )
    _write(
        root / "Documentation/zigux/README.md",
        "\n".join(
            [
                "Phase 4 notes",
                "validate-phase4.py",
                "phase4-gate-evidence.md",
                "phase4-validation-matrix.md",
                "atomic64_diff.zig",
                "runtime_atomic64_diff.zig",
                "phase4_runtime_atomic64_diff_survey.zig",
                "intentionally unapproved perf-threshold posture",
                "",
            ]
        ),
    )
    _write(
        root / "Documentation/zigux/review-checklist.md",
        "\n".join(
            [
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
                "",
            ]
        ),
    )
    _write(
        root / "scripts/zigux/README.md",
        "\n".join(
            [
                "validate-phase4.py",
                "atomic64_diff.zig",
                "runtime_atomic64_diff.zig",
                "phase4_runtime_atomic64_diff_survey.zig",
                "Phase 4 flow",
                "phase4_build.zig",
                "phase4-gate-evidence.md",
                "phase4-validation-matrix.md",
                "make -C zigux phase4-bitmap-live-helper-replay",
                "intentionally unapproved perf-threshold posture",
                "",
            ]
        ),
    )
    _write(
        root / "zigux/tests/README.md",
        "\n".join(
            [
                "zigux/tests/atomic64_diff.zig",
                "zigux/tests/runtime_atomic64_diff.zig",
                "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
                "zigux/tests/bitmap_diff.zig",
                "zigux/tests/phase4_build.zig",
                "scripts/zigux/validate-phase4.py",
                "",
            ]
        ),
    )


def _write_phase4_fixture_sources(root: Path) -> None:
    _write(root / "scripts/zigux/artifact_diff.py", "# placeholder\n")
    _write(root / "scripts/zigux/validate-phase4.py", "# placeholder\n")
    _write(
        root / "zigux/Makefile",
        "PHONY += phase4-validate phase4-test\nphase4-validate:\n\tscripts/zigux/validate-phase4.py\nphase4-test:\n\tzigux/tests/phase4_build.zig\n",
    )
    _write(
        root / ".github/workflows/zigux-bootstrap.yml",
        "python3 scripts/zigux/validate-phase4.py\npython3 scripts/zigux/validate-phase4.py --self-test\nzig build test --build-file zigux/tests/phase4_build.zig\n",
    )
    _write(root / "zigux/tests/atomic64_diff.zig", "// wrapper gate\n")
    _write(root / "zigux/tests/runtime_atomic64_diff.zig", "// runtime gate\n")
    _write(root / "zigux/tests/bitmap_diff.zig", "// bitmap gate\n")
    _write(root / "zigux/tests/phase4_bitmap_live_helper_replay.zig", "// helper replay gate\n")
    _write(root / "zigux/tests/phase9_build.zig", "// phase9 build gate\n")
    _write(
        root / "zigux/tests/phase4_build.zig",
        "\n".join(
            [
                "atomic64_diff.zig",
                "phase4_runtime_atomic64_diff_survey.zig",
                "bitmap_diff.zig",
                "phase4_bitmap_live_helper_replay.zig",
                "phase4-runtime-atomic64-diff-tests",
                "phase4-runtime-atomic64-diff-survey-tests",
                "phase4-bitmap-diff-tests",
                "phase4-bitmap-live-helper-replay-tests",
                "",
            ]
        ),
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_validator_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        _write_phase4_fixture_sources(root)
        _write_phase4_fixture_docs(root)
        _write_contract_checker_fixture(
            root / "scripts/zigux/check-artifact-diff-contract.py",
            base_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES)),
            base_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES,
            repeat_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES)),
            repeat_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES,
            case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES)),
            cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES,
            self_test_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES)),
            self_test_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES,
        )
        _write_phase4_gate_evidence_checker_fixture(
            root / "scripts/zigux/check-phase4-gate-evidence.py",
            self_test_case_count=str(len(EXPECTED_PHASE4_GATE_EVIDENCE_SELF_TEST_CASES)),
            self_test_cases=EXPECTED_PHASE4_GATE_EVIDENCE_SELF_TEST_CASES,
        )
        _write_phase4_runtime_atomic64_packet_fixture(root)

        assert _missing_files(root) == []
        assert validate_root(root) == []
        assert run_artifact_diff_contract_check(root) == []
        assert run_artifact_diff_contract_self_test_check(root) == []
        assert run_phase4_gate_evidence_check(root) == []
        assert run_phase4_gate_evidence_self_test_check(root) == []
        assert run_phase4_runtime_atomic64_packet_check(root) == []

        artifact_doc_path = root / "Documentation/zigux/artifact-diff.md"
        _write(
            artifact_doc_path,
            artifact_doc_path.read_text(encoding="utf-8").replace(
                "scripts/zigux/check-phase4-gate-evidence.py",
                "scripts/zigux/missing-phase4-gate-check.py",
                1,
            ),
        )
        assert validate_root(root) == [
            "doc:scripts/zigux/check-phase4-gate-evidence.py",
            "doc:exact_once:scripts/zigux/check-phase4-gate-evidence.py:0",
        ]

        _write_phase4_fixture_docs(root)
        _write(
            artifact_doc_path,
            artifact_doc_path.read_text(encoding="utf-8")
            + "- `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`\n",
        )
        assert validate_root(root) == [
            "doc:exact_once:zigux/tests/phase4_runtime_atomic64_diff_survey.zig:2"
        ]

        _write_phase4_fixture_docs(root)
        review_checklist_path = root / "Documentation/zigux/review-checklist.md"
        _write(
            review_checklist_path,
            review_checklist_path.read_text(encoding="utf-8").replace(
                "intentionally unapproved perf-threshold posture", "removed threshold note", 1
            ),
        )
        assert validate_root(root) == [
            "review_checklist:intentionally unapproved perf-threshold posture"
        ]

        _write_phase4_fixture_docs(root)
        script_readme_path = root / "scripts/zigux/README.md"
        _write(
            script_readme_path,
            script_readme_path.read_text(encoding="utf-8")
            + "make -C zigux phase4-perf-baseline-survey\n",
        )
        assert validate_root(root) == [
            "script_readme:forbidden:make -C zigux phase4-perf-baseline-survey:1",
            "script_readme:forbidden:phase4-perf-baseline-survey:1",
        ]

        _write_phase4_fixture_docs(root)
        gate_evidence_path = root / "Documentation/zigux/phase4-gate-evidence.md"
        _write(
            gate_evidence_path,
            gate_evidence_path.read_text(encoding="utf-8").replace(
                "- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=14`\n", "", 1
            ),
        )
        assert validate_root(root) == [
            "gate_evidence:PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=14"
        ]

        _write_phase4_fixture_docs(root)
        _write(
            gate_evidence_path,
            gate_evidence_path.read_text(encoding="utf-8").replace(
                "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=14`\n",
                "",
                1,
            ),
        )
        assert validate_root(root) == [
            "gate_evidence:PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=14"
        ]

        _write_phase4_fixture_docs(root)
        _write(
            gate_evidence_path,
            gate_evidence_path.read_text(encoding="utf-8").replace(
                "- hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.\n",
                "",
                1,
            ),
        )
        assert validate_root(root) == [
            "gate_evidence:hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved."
        ]

        _write_phase4_fixture_docs(root)
        manifest = json.loads(
            (root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        phase4_build_sha = _git_blob_sha1((root / "zigux/tests/phase4_build.zig").read_bytes())
        phase9_build_sha = _git_blob_sha1((root / "zigux/tests/phase9_build.zig").read_bytes())
        manifest["phase4_build_blob_sha"] = "1111111111111111111111111111111111111111"
        _write(
            root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
            json.dumps(manifest, indent=2) + "\n",
        )
        assert run_phase4_runtime_atomic64_packet_check(root) == [
            "phase4_runtime_atomic64_packet:unexpected_manifest_sha:phase4_build_blob_sha:"
            "1111111111111111111111111111111111111111:"
            f"{phase4_build_sha}"
        ]

        _write_phase4_runtime_atomic64_packet_fixture(root)
        survey_path = root / "zigux/tests/phase4_runtime_atomic64_diff_survey.zig"
        _write(
            survey_path,
            survey_path.read_text(encoding="utf-8").replace(
                phase4_build_sha, "1111111111111111111111111111111111111111", 1
            ),
        )
        assert run_phase4_runtime_atomic64_packet_check(root) == [
            "phase4_runtime_atomic64_packet:survey_sha_exact_count:"
            f"phase4_build_blob_sha:{phase4_build_sha}:0"
        ]

        _write_phase4_runtime_atomic64_packet_fixture(root)
        manifest = json.loads(
            (root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        manifest["phase9_build_blob_sha"] = "0000000000000000000000000000000000000000"
        _write(
            root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
            json.dumps(manifest, indent=2) + "\n",
        )
        assert run_phase4_runtime_atomic64_packet_check(root) == [
            "phase4_runtime_atomic64_packet:unexpected_manifest_sha:phase9_build_blob_sha:"
            "0000000000000000000000000000000000000000:"
            f"{phase9_build_sha}"
        ]

        _write_phase4_runtime_atomic64_packet_fixture(root)
        _write(
            survey_path,
            survey_path.read_text(encoding="utf-8").replace(
                phase9_build_sha, "2222222222222222222222222222222222222222", 1
            ),
        )
        assert run_phase4_runtime_atomic64_packet_check(root) == [
            "phase4_runtime_atomic64_packet:survey_sha_exact_count:"
            f"phase9_build_blob_sha:{phase9_build_sha}:0"
        ]

        _write_phase4_gate_evidence_checker_fixture(
            root / "scripts/zigux/check-phase4-gate-evidence.py",
            include_self_test_pass=False,
            self_test_case_count=str(len(EXPECTED_PHASE4_GATE_EVIDENCE_SELF_TEST_CASES)),
            self_test_cases=EXPECTED_PHASE4_GATE_EVIDENCE_SELF_TEST_CASES,
        )
        assert run_phase4_gate_evidence_self_test_check(root) == [
            "phase4_gate_evidence_self_test:missing_pass_marker"
        ]

        _write_phase4_gate_evidence_checker_fixture(
            root / "scripts/zigux/check-phase4-gate-evidence.py",
            self_test_case_count=None,
            self_test_cases=EXPECTED_PHASE4_GATE_EVIDENCE_SELF_TEST_CASES,
        )
        assert run_phase4_gate_evidence_self_test_check(root) == [
            "phase4_gate_evidence_self_test:missing_case_count_marker"
        ]

        _write_phase4_gate_evidence_checker_fixture(
            root / "scripts/zigux/check-phase4-gate-evidence.py",
            self_test_case_count="8",
            self_test_cases=EXPECTED_PHASE4_GATE_EVIDENCE_SELF_TEST_CASES,
        )
        assert run_phase4_gate_evidence_self_test_check(root) == [
            "phase4_gate_evidence_self_test:unexpected_case_count:8"
        ]

        _write_phase4_gate_evidence_checker_fixture(
            root / "scripts/zigux/check-phase4-gate-evidence.py",
            self_test_case_count=str(len(EXPECTED_PHASE4_GATE_EVIDENCE_SELF_TEST_CASES)),
            self_test_cases=None,
        )
        assert run_phase4_gate_evidence_self_test_check(root) == [
            "phase4_gate_evidence_self_test:missing_cases_marker"
        ]

        _write_phase4_gate_evidence_checker_fixture(
            root / "scripts/zigux/check-phase4-gate-evidence.py",
            self_test_case_count=str(len(EXPECTED_PHASE4_GATE_EVIDENCE_SELF_TEST_CASES)),
            self_test_cases=EXPECTED_PHASE4_GATE_EVIDENCE_SELF_TEST_CASES[1:],
        )
        assert run_phase4_gate_evidence_self_test_check(root) == [
            "phase4_gate_evidence_self_test:unexpected_cases:"
            + _expected_case_line(EXPECTED_PHASE4_GATE_EVIDENCE_SELF_TEST_CASES[1:])
        ]

        print("PHASE4_VALIDATE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 4 rollback-readiness packet.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated Phase 4 validator coverage in a temporary workspace.",
    )
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

    missing_markers = validate_root(ROOT)
    if missing_markers:
        print("PHASE4_VALIDATION=fail")
        print("MISSING_PHASE4_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE4_MARKERS_END")
        return 1

    for label, failures in [
        ("ARTIFACT_DIFF_CONTRACT_CHECK", run_artifact_diff_contract_check(ROOT)),
        ("ARTIFACT_DIFF_CONTRACT_SELF_TEST_CHECK", run_artifact_diff_contract_self_test_check(ROOT)),
        ("PHASE4_GATE_EVIDENCE_CHECK", run_phase4_gate_evidence_check(ROOT)),
        ("PHASE4_GATE_EVIDENCE_SELF_TEST_CHECK", run_phase4_gate_evidence_self_test_check(ROOT)),
        ("PHASE4_RUNTIME_ATOMIC64_PACKET_CHECK", run_phase4_runtime_atomic64_packet_check(ROOT)),
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
    print(
        "PHASE4_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_MAKE_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_DOC_MARKERS) + len(REQUIRED_PHASE4_GATE_EVIDENCE_MARKERS) + len(REQUIRED_TESTS_README_MARKERS) + len(REQUIRED_SCRIPT_README_MARKERS) + len(REQUIRED_DOC_README_MARKERS) + len(REQUIRED_REVIEW_CHECKLIST_MARKERS) + len(REQUIRED_PHASE4_MATRIX_MARKERS) + len(REQUIRED_PHASE4_BUILD_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
