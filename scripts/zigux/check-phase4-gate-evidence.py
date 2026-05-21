#!/usr/bin/env python3
"""Guard the broader Phase 4 gate-evidence packet."""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-gate-evidence.md")
MATRIX = Path("Documentation/zigux/phase4-validation-matrix.md")
DOCS_README = Path("Documentation/zigux/README.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
VALIDATOR = Path("scripts/zigux/validate-phase4.py")
ARTIFACT_DIFF_HELPER = Path("scripts/zigux/artifact_diff.py")
ATOMIC64_MANIFEST = Path("zigux/tests/phase4_runtime_atomic64_diff_manifest.json")
BITMAP_SURVEY = Path("zigux/tests/phase4_bitmap_diff_survey.zig")
PERF_SURVEY = Path("zigux/tests/phase4_perf_baseline_survey.zig")
KPROBE_MANIFEST = Path("zigux/tests/phase4_kprobe_example_manifest.json")
TEST_FSMOUNT_SURVEY = Path("zigux/tests/phase4_test_fsmount_survey.zig")
PHASE9_BUILD = Path("zigux/tests/phase9_build.zig")
SELF = Path("scripts/zigux/check-phase4-gate-evidence.py")

EXPECTED_TARGET_COUNT = 19
EXPECTED_SELF_TEST_CASE_COUNT = 43
SELF_TEST_CASES = [
    "baseline_round_trip",
    "shipped_target_count_drift",
    "missing_exact_readback_heading",
    "forbidden_gate_evidence_checker_self_pin",
    "validator_blob_pin_drift",
    "phase4_build_manifest_blob_pin_drift",
    "phase4_build_survey_blob_pin_drift",
    "phase9_build_manifest_blob_pin_drift",
    "phase9_build_survey_blob_pin_drift",
    "doc_readme_blob_pin_drift",
    "script_readme_blob_pin_drift",
    "tests_readme_blob_pin_drift",
    "gate_evidence_self_test_case_count_drift",
    "gate_evidence_self_test_cases_drift",
    "shared_validator_reruns_gate_evidence_check_drift",
    "shared_validator_reruns_gate_evidence_self_test_drift",
    "shared_validator_expected_target_count_drift",
    "shared_validator_expected_self_test_case_count_drift",
    "runtime_atomic64_survey_packet_presence_drift",
    "bitmap_diff_survey_replay_marker_drift",
    "kprobe_gap_packet_presence_drift",
    "kprobe_owner_drift",
    "kprobe_validation_entrypoint_drift",
    "kprobe_next_step_drift",
    "perf_baseline_packet_presence_drift",
    "perf_baseline_note_split_marker_drift",
    "perf_baseline_owner_drift",
    "perf_baseline_shared_promotion_status_drift",
    "test_fsmount_gap_packet_presence_drift",
    "test_fsmount_threshold_posture_drift",
    "test_fsmount_owner_drift",
    "test_fsmount_validation_entrypoint_drift",
    "test_fsmount_linux_style_wrapper_drift",
    "test_fsmount_next_step_drift",
    "missing_validator_file",
    "missing_phase4_build_file",
    "missing_artifact_diff_helper_file",
    "missing_atomic64_manifest_file",
    "missing_bitmap_survey_file",
    "missing_perf_survey_file",
    "missing_kprobe_manifest_file",
    "missing_test_fsmount_survey_file",
    "missing_note_file",
]

NOTE_MARKERS = (
    "# Phase 4 Gate Evidence",
    "## Status",
    "`PHASE4_VALIDATION_MATRIX_BLOB_SHA=0c243dd80d8ff192d43c3f2db0ca36a2f8e5f77c`",
    "`PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=c1fa46fad53adc7327a03fbe12d3510e854e8bfa`",
    "`PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=5173368ba7f69587f6839931b380f1e77c456933`",
    "`PHASE4_ARTIFACT_DIFF_HELPER_BLOB_SHA=4dc6294c98aea9475d4d5965ac541cab9a7dc725`",
    "`PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=92696cb02fc915fec0f5f1c4c2768a99cf99c9bf`",
    "`PHASE4_MAKEFILE_BLOB_SHA=2123cbb48f7bb32293c1bb3dead619e6d437923b`",
    "`PHASE4_WORKFLOW_BLOB_SHA=d33dbde416395f8d7cd0e79da73d90b6e5dea3bb`",
    "`PHASE4_DOC_README_BLOB_SHA=c8ce5d87ce4a86e6808435533da42f954ebc27cb`",
    "`PHASE4_SCRIPT_README_BLOB_SHA=83126c399d73992e4aabbd11d8c57326ad3ae31b`",
    "`PHASE4_TESTS_README_BLOB_SHA=4df2358985dca0abf52dbf08258841a77cf02b91`",
    "`PHASE4_VALIDATOR_BLOB_SHA=4ef6d3c50ee6111e6855ff05fe92928c5700097b`",
    "`PHASE4_ATOMIC64_DIFF_BLOB_SHA=e84bf84b5e24428d596fe25502512fa24ce28b51`",
    "`PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=9ad41de72613cd72273b41c9cf2a64a0c46962df`",
    "`PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=0c7e843708eefefd688d4909110b81bf3782176c`",
    "`PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=8ac70b09fb17b97f0c067547f2ad8b3855c4a908`",
    "`PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=3f484f5d95b544f533ec03d0ddfc45ea40e7daba`",
    "`PHASE4_PHASE9_BUILD_BLOB_SHA=2ac6379e587fe059115df6a12c879e6d84590a66`",
    "`PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_BLOB_SHA=76c83983235d4701fca5b3eb26aadd063b303525`",
    "`PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19`",
    "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=43`",
    "`PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
    "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`",
    "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`",
    "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`",
    "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=43`",
    "`PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
    "`PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`",
    "`PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`",
    "`PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`",
    "## Exact Readback Evidence",
    "`scripts/zigux/check-phase4-gate-evidence.py`",
    "`phase4-runtime-atomic64-diff-survey-tests`",
    "`make -C zigux phase4-runtime-atomic64-diff-survey`",
    "two `inc_not_zero` checks",
    "three `dec_if_positive` checks",
    "PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
)

MATRIX_MARKERS = (
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-remaining-gap-matrix.py",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`",
    "kprobe owner: `Validation and Perf Team`",
    "local-only benchmark commands and acceptable limits are approved today",
    "perf baseline owner: `Validation and Perf Team`",
    "shared CI perf promotion pending",
    "current measurable status: absent on current `master`",
    "test_fsmount threshold posture: reviewability_only_no_perf_threshold",
    "test_fsmount validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
    "test_fsmount dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`",
    "test_fsmount owner: `Validation and Perf Team`",
    "next bounded evidence step: keep the dedicated parked survey packet",
)

WORKFLOW_MARKERS = (
    "- name: Validate Phase 4 rollback routes",
    "run: make -C zigux phase4-validate",
    "- name: Run Phase 4 rollback tests",
    "run: make -C zigux phase4-test",
    "- name: Self-test current Phase 4 artifact-diff helper",
    "run: python3 scripts/zigux/artifact_diff.py --self-test",
    "- name: Self-test current Phase 4 artifact-diff contract checker",
    "run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
    "- name: Check current Phase 4 artifact-diff contract packet",
    "run: python3 scripts/zigux/check-artifact-diff-contract.py",
    "- name: Self-test current Phase 4 artifact-diff determinism checker",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "- name: Check current Phase 4 artifact-diff determinism packet",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "- name: Self-test current Phase 4 artifact-diff validator replay checker",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
    "- name: Check current Phase 4 artifact-diff validator replay packet",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
)

CHECKLIST_MARKERS = (
    "keep the directly readable local-only perf packet explicit",
    "keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "keep the repo-reality warning explicit for the broader Phase 4 validator, build, and bitmap-diff companions still needing raw-fallback proof or fresh authenticated blob capture",
    "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence",
    "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval",
)

TESTS_README_MARKERS = (
    "Keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, and `scripts/zigux/check-phase4-workflow-route-counts.py` keep the current helper-contract, validator-replay, shared rollback-owner reminder, local-only perf-governance, recovered remaining-gap, and route-inventory packet explicit on current `master`",
    "keep the current governance split explicit here too: the direct-readback shared handoff stays narrower than the broader recovered note companions, the Validation and Perf Team remains the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod remain the coordination owners for that policy call, and the dedicated perf-baseline survey must stay local-only until a later bounded lane intentionally widens that posture",
)

COUNT_MARKERS = (
    ("PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT", EXPECTED_TARGET_COUNT),
    ("PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT", EXPECTED_SELF_TEST_CASE_COUNT),
    ("PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT", EXPECTED_TARGET_COUNT),
    ("PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT", EXPECTED_SELF_TEST_CASE_COUNT),
)

MUTATIONS = [
    ("shipped_target_count_drift", "`PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19`", "`PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=18`", NOTE),
    ("missing_exact_readback_heading", "## Exact Readback Evidence", "## Evidence", NOTE),
    ("validator_blob_pin_drift", "`PHASE4_VALIDATOR_BLOB_SHA=4ef6d3c50ee6111e6855ff05fe92928c5700097b`", "`PHASE4_VALIDATOR_BLOB_SHA=deadbeef`", NOTE),
    ("phase4_build_manifest_blob_pin_drift", "`PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_BLOB_SHA=76c83983235d4701fca5b3eb26aadd063b303525`", "`PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_BLOB_SHA=deadbeef`", NOTE),
    ("phase4_build_survey_blob_pin_drift", "`PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=8ac70b09fb17b97f0c067547f2ad8b3855c4a908`", "`PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=deadbeef`", NOTE),
    ("phase9_build_manifest_blob_pin_drift", "`PHASE4_PHASE9_BUILD_BLOB_SHA=2ac6379e587fe059115df6a12c879e6d84590a66`", "`PHASE4_PHASE9_BUILD_BLOB_SHA=deadbeef`", NOTE),
    ("phase9_build_survey_blob_pin_drift", "`phase4-runtime-atomic64-diff-survey-tests`", "`phase9-runtime-atomic64-diff-survey-tests`", NOTE),
    ("doc_readme_blob_pin_drift", "`PHASE4_DOC_README_BLOB_SHA=c8ce5d87ce4a86e6808435533da42f954ebc27cb`", "`PHASE4_DOC_README_BLOB_SHA=deadbeef`", NOTE),
    ("script_readme_blob_pin_drift", "`PHASE4_SCRIPT_README_BLOB_SHA=83126c399d73992e4aabbd11d8c57326ad3ae31b`", "`PHASE4_SCRIPT_README_BLOB_SHA=deadbeef`", NOTE),
    ("tests_readme_blob_pin_drift", "`PHASE4_TESTS_README_BLOB_SHA=4df2358985dca0abf52dbf08258841a77cf02b91`", "`PHASE4_TESTS_README_BLOB_SHA=deadbeef`", NOTE),
    ("gate_evidence_self_test_case_count_drift", "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=43`", "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=42`", NOTE),
    ("shared_validator_reruns_gate_evidence_check_drift", "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`", "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=false`", NOTE),
    ("shared_validator_reruns_gate_evidence_self_test_drift", "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`", "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=false`", NOTE),
    ("shared_validator_expected_target_count_drift", "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`", "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=18`", NOTE),
    ("shared_validator_expected_self_test_case_count_drift", "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=43`", "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=42`", NOTE),
    ("runtime_atomic64_survey_packet_presence_drift", "`PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`", "`PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=false`", NOTE),
    ("bitmap_diff_survey_replay_marker_drift", "zigux/tests/phase4_perf_baseline_survey.zig", "zigux/tests/phase4_perf_survey.zig", MATRIX),
    ("kprobe_gap_packet_presence_drift", "`PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`", "`PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false`", NOTE),
    ("kprobe_owner_drift", "kprobe owner: `Validation and Perf Team`", "kprobe owner: `Shared Subsystems Pod`", MATRIX),
    ("kprobe_validation_entrypoint_drift", "validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`", "validation entrypoint: `zig test zigux/tests/kprobe_example_survey.zig`", MATRIX),
    ("kprobe_next_step_drift", "next bounded evidence step: keep the dedicated parked survey packet", "next bounded evidence step: revisit later", MATRIX),
    ("perf_baseline_packet_presence_drift", "`PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`", "`PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false`", NOTE),
    ("perf_baseline_note_split_marker_drift", "local-only benchmark commands and acceptable limits are approved today", "local-only benchmark commands are approved today", MATRIX),
    ("perf_baseline_owner_drift", "perf baseline owner: `Validation and Perf Team`", "perf baseline owner: `Shared Subsystems Pod`", MATRIX),
    ("perf_baseline_shared_promotion_status_drift", "shared CI perf promotion pending", "shared CI perf promotion landed", MATRIX),
    ("test_fsmount_gap_packet_presence_drift", "`PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`", "`PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`", NOTE),
    ("test_fsmount_threshold_posture_drift", "test_fsmount threshold posture: reviewability_only_no_perf_threshold", "test_fsmount threshold posture: landed_perf_threshold", MATRIX),
    ("test_fsmount_owner_drift", "test_fsmount owner: `Validation and Perf Team`", "test_fsmount owner: `Shared Subsystems Pod`", MATRIX),
    ("test_fsmount_validation_entrypoint_drift", "test_fsmount validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`", "test_fsmount validation entrypoint: `zig test zigux/tests/phase4_test_fsmount_survey.zig`", MATRIX),
    ("test_fsmount_linux_style_wrapper_drift", "test_fsmount dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`", "test_fsmount dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount`", MATRIX),
    ("test_fsmount_next_step_drift", "current measurable status: absent on current `master`", "current measurable status: landed on current `master`", MATRIX),
]

MISSING_FILE_CASES = [
    ("missing_validator_file", VALIDATOR),
    ("missing_phase4_build_file", MAKEFILE),
    ("missing_artifact_diff_helper_file", ARTIFACT_DIFF_HELPER),
    ("missing_atomic64_manifest_file", ATOMIC64_MANIFEST),
    ("missing_bitmap_survey_file", BITMAP_SURVEY),
    ("missing_perf_survey_file", PERF_SURVEY),
    ("missing_kprobe_manifest_file", KPROBE_MANIFEST),
    ("missing_test_fsmount_survey_file", TEST_FSMOUNT_SURVEY),
    ("missing_note_file", NOTE),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixture self-test")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)


def require_markers(text: str, markers: tuple[str, ...], label: str, missing: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def require_exact_value(text: str, marker_label: str, expected: int, label: str, missing: list[str]) -> None:
    matches = re.findall(rf"`{re.escape(marker_label)}=(\d+)`", text)
    if not matches:
        missing.append(f"{label}:missing:{marker_label}")
        return
    if any(int(value) != expected for value in matches):
        missing.append(f"{label}:{marker_label}:expected={expected}:actual={matches}")


def required_files() -> tuple[Path, ...]:
    return (
        NOTE,
        MATRIX,
        DOCS_README,
        SCRIPTS_README,
        TESTS_README,
        REVIEW_CHECKLIST,
        WORKFLOW,
        MAKEFILE,
        VALIDATOR,
        ARTIFACT_DIFF_HELPER,
        ATOMIC64_MANIFEST,
        BITMAP_SURVEY,
        PERF_SURVEY,
        KPROBE_MANIFEST,
        TEST_FSMOUNT_SURVEY,
        PHASE9_BUILD,
        SELF,
    )


def build_fixture_tree(root: Path) -> None:
    note_lines = [
        "# Phase 4 Gate Evidence",
        "",
        "## Status",
        "  * `PHASE4_VALIDATION_MATRIX_BLOB_SHA=0c243dd80d8ff192d43c3f2db0ca36a2f8e5f77c`",
        "  * `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=c1fa46fad53adc7327a03fbe12d3510e854e8bfa`",
        "  * `PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=5173368ba7f69587f6839931b380f1e77c456933`",
        "  * `PHASE4_ARTIFACT_DIFF_HELPER_BLOB_SHA=4dc6294c98aea9475d4d5965ac541cab9a7dc725`",
        "  * `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=92696cb02fc915fec0f5f1c4c2768a99cf99c9bf`",
        "  * `PHASE4_MAKEFILE_BLOB_SHA=2123cbb48f7bb32293c1bb3dead619e6d437923b`",
        "  * `PHASE4_WORKFLOW_BLOB_SHA=d33dbde416395f8d7cd0e79da73d90b6e5dea3bb`",
        "  * `PHASE4_DOC_README_BLOB_SHA=c8ce5d87ce4a86e6808435533da42f954ebc27cb`",
        "  * `PHASE4_SCRIPT_README_BLOB_SHA=83126c399d73992e4aabbd11d8c57326ad3ae31b`",
        "  * `PHASE4_TESTS_README_BLOB_SHA=4df2358985dca0abf52dbf08258841a77cf02b91`",
        "  * `PHASE4_VALIDATOR_BLOB_SHA=4ef6d3c50ee6111e6855ff05fe92928c5700097b`",
        "  * `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=placeholder`",
        "  * `PHASE4_ATOMIC64_DIFF_BLOB_SHA=e84bf84b5e24428d596fe25502512fa24ce28b51`",
        "  * `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=9ad41de72613cd72273b41c9cf2a64a0c46962df`",
        "  * `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=0c7e843708eefefd688d4909110b81bf3782176c`",
        "  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=8ac70b09fb17b97f0c067547f2ad8b3855c4a908`",
        "  * `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=3f484f5d95b544f533ec03d0ddfc45ea40e7daba`",
        "  * `PHASE4_PHASE9_BUILD_BLOB_SHA=2ac6379e587fe059115df6a12c879e6d84590a66`",
        "  * `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_BLOB_SHA=76c83983235d4701fca5b3eb26aadd063b303525`",
        "  * `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19`",
        "  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=43`",
        "  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES) + "`",
        "  * `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
        "  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`",
        "  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`",
        "  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`",
        "  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=43`",
        "  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
        "  * `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`",
        "  * `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`",
        "  * `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`",
        "",
        "## Exact Readback Evidence",
        "  * `scripts/zigux/check-phase4-gate-evidence.py` now exact-pins the current broader packet instead of leaving its own checker blob implicit.",
        "  * The runtime atomic64 handoff remains reviewable through `phase4-runtime-atomic64-diff-survey-tests`, `make -C zigux phase4-runtime-atomic64-diff-survey`, two `inc_not_zero` checks, and three `dec_if_positive` checks.",
        "  * The adjacent local-only perf packet remains explicit through `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and the shared posture that local-only benchmark commands and acceptable limits are approved today while shared CI perf promotion pending remains unchanged.",
        "  * The parked starter-gap packet keeps `PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix` explicit beside the current `make -C zigux phase4-kprobe-example-survey` and `make -C zigux phase4-test-fsmount-survey` wrappers.",
        "",
    ]
    write_text(root / NOTE, "\n".join(note_lines))
    write_text(root / MATRIX, "\n".join(MATRIX_MARKERS) + "\n")
    write_text(root / DOCS_README, "sample docs readme\n")
    write_text(root / SCRIPTS_README, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root / TESTS_README, "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root / REVIEW_CHECKLIST, "\n".join(CHECKLIST_MARKERS) + "\n")
    write_text(root / WORKFLOW, "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(root / MAKEFILE, "phase4-validate:\nphase4-test-fsmount-survey:\nphase4-kprobe-example-survey:\n")
    for rel in required_files():
        if rel in {NOTE, MATRIX, DOCS_README, SCRIPTS_README, TESTS_README, REVIEW_CHECKLIST, WORKFLOW, MAKEFILE}:
            continue
        write_text(root / rel, "placeholder\n")


def validate_root(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in required_files():
        if not (root / rel).is_file():
            missing.append(f"file:{rel.as_posix()}")
    if missing:
        return missing

    note_text = read_text(root / NOTE)
    require_markers(note_text, NOTE_MARKERS, "note", missing)
    if note_text.count("PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=") != 1:
        missing.append("note:PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=count")
    if note_text.count("PHASE4_VALIDATOR_BLOB_SHA=") != 1:
        missing.append("note:PHASE4_VALIDATOR_BLOB_SHA=count")
    require_markers(note_text, ("`PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES) + "`",), "note", missing)
    for marker_label, expected in COUNT_MARKERS:
        require_exact_value(note_text, marker_label, expected, "note", missing)

    require_markers(read_text(root / MATRIX), MATRIX_MARKERS, "matrix", missing)
    require_markers(read_text(root / DOCS_README), ("sample docs readme",), "docs_readme", missing)
    require_markers(read_text(root / SCRIPTS_README), SCRIPTS_README_MARKERS, "scripts_readme", missing)
    require_markers(read_text(root / TESTS_README), TESTS_README_MARKERS, "tests_readme", missing)
    require_markers(read_text(root / REVIEW_CHECKLIST), CHECKLIST_MARKERS, "checklist", missing)
    require_markers(read_text(root / WORKFLOW), WORKFLOW_MARKERS, "workflow", missing)
    return missing


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-gate-evidence-") as tmp:
        root = Path(tmp)
        build_fixture_tree(root)
        if validate_root(root):
            raise AssertionError("baseline fixture failed")
        cases += 1

        def expect_failure(case_name: str, mutator) -> None:
            nonlocal cases
            build_fixture_tree(root)
            mutator(root)
            if not validate_root(root):
                raise AssertionError(f"expected validation failure for {case_name}")
            cases += 1

        expect_failure("forbidden_gate_evidence_checker_self_pin", lambda r: write_text(r / NOTE, read_text(r / NOTE) + "  * `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=duplicate`\n"))
        expect_failure("gate_evidence_self_test_cases_drift", lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), ",".join(SELF_TEST_CASES), ",".join(SELF_TEST_CASES[:-1]))))
        for case_name, old, new, target in MUTATIONS:
            expect_failure(case_name, lambda r, o=old, n=new, t=target: write_text(r / t, replace_once(read_text(r / t), o, n)))
        for case_name, rel in MISSING_FILE_CASES:
            expect_failure(case_name, lambda r, path=rel: (r / path).unlink())

        if cases != EXPECTED_SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {EXPECTED_SELF_TEST_CASE_COUNT} self-test cases, saw {cases}")


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        print(f"phase4 gate evidence self-test: PASS ({EXPECTED_SELF_TEST_CASE_COUNT} cases)")
        return 0
    failures = validate_root(Path(args.root).resolve())
    if failures:
        for failure in failures:
            print(f"phase4 gate evidence check failed: {failure}")
        return 1
    print("phase4 gate evidence check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())