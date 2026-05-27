#!/usr/bin/env python3
"""Guard the broader Phase 4 gate-evidence packet."""

from __future__ import annotations

import argparse
import json
import hashlib
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
ARTIFACT_DIFF_DOC = Path("Documentation/zigux/artifact-diff.md")
ARTIFACT_DIFF_HELPER = Path("scripts/zigux/artifact_diff.py")
ARTIFACT_DIFF_CONTRACT_CHECKER = Path("scripts/zigux/check-artifact-diff-contract.py")
WORKFLOW_ROUTE_CHECKER = Path("scripts/zigux/check-phase4-workflow-route-counts.py")
ATOMIC64_DIFF = Path("zigux/tests/atomic64_diff.zig")
RUNTIME_ATOMIC64_DIFF = Path("zigux/tests/runtime_atomic64_diff.zig")
ATOMIC64_MANIFEST = Path("zigux/tests/phase4_runtime_atomic64_diff_manifest.json")
RUNTIME_ATOMIC64_SURVEY = Path("zigux/tests/phase4_runtime_atomic64_diff_survey.zig")
BITMAP_MANIFEST = Path("zigux/tests/phase4_bitmap_diff_manifest.json")
BITMAP_SURVEY = Path("zigux/tests/phase4_bitmap_diff_survey.zig")
PERF_SURVEY = Path("zigux/tests/phase4_perf_baseline_survey.zig")
KPROBE_MANIFEST = Path("zigux/tests/phase4_kprobe_example_manifest.json")
TEST_FSMOUNT_SURVEY = Path("zigux/tests/phase4_test_fsmount_survey.zig")
PHASE4_BUILD = Path("zigux/tests/phase4_build.zig")
PHASE9_BUILD = Path("zigux/tests/phase9_build.zig")
REVERSIBLE_DELIVERY_EVIDENCE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
SELF = Path("scripts/zigux/check-phase4-gate-evidence.py")

EXPECTED_TARGET_COUNT = 19
EXPECTED_SELF_TEST_CASE_COUNT = 45

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
    "bitmap_manifest_gate_evidence_blob_drift",
    "workflow_route_checker_matrix_presence_drift",
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
    "missing_workflow_route_checker_file",
    "missing_atomic64_manifest_file",
    "missing_bitmap_manifest_file",
    "missing_perf_survey_file",
    "missing_kprobe_manifest_file",
    "missing_test_fsmount_survey_file",
    "missing_note_file",
]

BLOB_TARGETS = (
    ("PHASE4_VALIDATION_MATRIX_BLOB_SHA", MATRIX),
    ("PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA", WORKFLOW_ROUTE_CHECKER),
    ("PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA", ARTIFACT_DIFF_DOC),
    ("PHASE4_ARTIFACT_DIFF_HELPER_BLOB_SHA", ARTIFACT_DIFF_HELPER),
    ("PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA", ARTIFACT_DIFF_CONTRACT_CHECKER),
    ("PHASE4_MAKEFILE_BLOB_SHA", MAKEFILE),
    ("PHASE4_WORKFLOW_BLOB_SHA", WORKFLOW),
    ("PHASE4_DOC_README_BLOB_SHA", DOCS_README),
    ("PHASE4_SCRIPT_README_BLOB_SHA", SCRIPTS_README),
    ("PHASE4_TESTS_README_BLOB_SHA", TESTS_README),
    ("PHASE4_VALIDATOR_BLOB_SHA", VALIDATOR),
    ("PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA", SELF),
    ("PHASE4_ATOMIC64_DIFF_BLOB_SHA", ATOMIC64_DIFF),
    ("PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA", RUNTIME_ATOMIC64_DIFF),
    ("PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA", ATOMIC64_MANIFEST),
    ("PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA", RUNTIME_ATOMIC64_SURVEY),
    ("PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA", REVIEW_CHECKLIST),
    ("PHASE4_PHASE9_BUILD_BLOB_SHA", PHASE9_BUILD),
    ("PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_BLOB_SHA", REVERSIBLE_DELIVERY_EVIDENCE),
)

NOTE_MARKERS = (
    "# Phase 4 Gate Evidence",
    "## Status",
    "`PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19`",
    "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=45`",
    "`PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
    "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`",
    "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`",
    "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`",
    "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=45`",
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
    "scripts/zigux/check-phase4-workflow-route-counts.py",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "explicit local lab replay marker: `make -C zigux phase4-kprobe-example-survey`",
    "dedicated local survey wrapper: `make -C zigux phase4-kprobe-example-survey`",
    "validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`",
    "survey owner: `Validation and Perf Team`",
    "rollback owner: `Validation and Perf Team`",
    "local-only benchmark commands and acceptable limits are approved today",
    "gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
    "shared CI perf promotion pending",
    "current measurable status: absent on current `master`",
    "reviewability-only no-perf-threshold posture",
    "validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
    "dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`",
    "survey owner: `Validation and Perf Team`",
    "rollback owner: `Validation and Perf Team`",
    "Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners",
    "next bounded evidence step: keep the dedicated parked survey packet",
)

TEST_FSMOUNT_SURVEY_MARKERS = (
    '"PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig"',
)

DOCS_README_MARKERS = (
    "Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "the current docs-root Phase 4 reminder packet should stay parked on the directly readable helper, the returned contract checker, the determinism and validator-replay checkers, the shared repo-reality and pin guards, the dedicated local-only perf packet, the recovered broader note-and-checker companions, and the roadmap-backed atomic64 differential pair",
    "keep the current governance split explicit here too: the direct-readback shared handoff stays narrower than the broader recovered note companions, the Validation and Perf Team remains the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod remain the coordination owners for that policy call, and the dedicated perf-baseline survey must stay local-only until a later bounded lane intentionally widens that posture",
    "current `master` keeps the broader Phase 4 packet in a split-readback state rather than the missing bucket:",
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
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/atomic64_diff.zig`, and `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain the current reminder-surface companions for that active Phase 4 rollback-readiness and perf-governance packet",
    "keep the current governance split explicit here too: the direct-readback shared handoff stays narrower than the broader recovered note companions, the Validation and Perf Team remains the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod remain the coordination owners for that policy call, and the dedicated perf-baseline survey must stay local-only until a later bounded lane intentionally widens that posture",
)

COUNT_MARKERS = (
    ("PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT", EXPECTED_TARGET_COUNT),
    ("PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT", EXPECTED_SELF_TEST_CASE_COUNT),
    ("PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT", EXPECTED_TARGET_COUNT),
    ("PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT", EXPECTED_SELF_TEST_CASE_COUNT),
)

MISSING_FILE_CASES = (
    ("missing_validator_file", VALIDATOR),
    ("missing_phase4_build_file", PHASE4_BUILD),
    ("missing_artifact_diff_helper_file", ARTIFACT_DIFF_HELPER),
    ("missing_workflow_route_checker_file", WORKFLOW_ROUTE_CHECKER),
    ("missing_atomic64_manifest_file", ATOMIC64_MANIFEST),
    ("missing_bitmap_manifest_file", BITMAP_MANIFEST),
    ("missing_perf_survey_file", PERF_SURVEY),
    ("missing_kprobe_manifest_file", KPROBE_MANIFEST),
    ("missing_test_fsmount_survey_file", TEST_FSMOUNT_SURVEY),
    ("missing_note_file", NOTE),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(old)
    return text.replace(old, new, 1)


def require_markers(text: str, markers: tuple[str, ...], label: str, missing: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def extract_note_values(text: str, marker_label: str) -> list[str]:
    needle = f"`{marker_label}="
    values: list[str] = []
    start = 0
    while True:
        idx = text.find(needle, start)
        if idx == -1:
            return values
        value_start = idx + len(needle)
        value_end = text.find("`", value_start)
        if value_end == -1:
            return values
        values.append(text[value_start:value_end])
        start = value_end + 1


def require_exact_value(text: str, marker_label: str, expected: int, label: str, missing: list[str]) -> None:
    matches = extract_note_values(text, marker_label)
    if not matches:
        missing.append(f"{label}:missing:{marker_label}")
        return
    parsed = [int(value) for value in matches]
    if any(value != expected for value in parsed):
        missing.append(f"{label}:{marker_label}:expected={expected}:actual={matches}")


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def require_blob_pins(root: Path, note_text: str, missing: list[str]) -> None:
    for marker_label, rel in BLOB_TARGETS:
        matches = extract_note_values(note_text, marker_label)
        if len(matches) != 1:
            missing.append(f"note:{marker_label}:count={len(matches)}")
            continue
        actual = git_blob_sha(root / rel)
        if matches[0] != actual:
            missing.append(f"note:{marker_label}:expected={actual}:actual={matches[0]}")


def require_bitmap_manifest_alignment(root: Path, missing: list[str]) -> None:
    manifest = json.loads(read_text(root / BITMAP_MANIFEST))
    expected_note_path = NOTE.as_posix()
    expected_note_blob = git_blob_sha(root / NOTE)
    if manifest.get("shared_gate_evidence_path") != expected_note_path:
        missing.append(
            "bitmap_manifest:shared_gate_evidence_path:"
            f"expected={expected_note_path}:actual={manifest.get('shared_gate_evidence_path')}"
        )
    if manifest.get("gate_evidence_path") != expected_note_path:
        missing.append(
            "bitmap_manifest:gate_evidence_path:"
            f"expected={expected_note_path}:actual={manifest.get('gate_evidence_path')}"
        )
    if manifest.get("gate_evidence_blob_sha") != expected_note_blob:
        missing.append(
            "bitmap_manifest:gate_evidence_blob_sha:"
            f"expected={expected_note_blob}:actual={manifest.get('gate_evidence_blob_sha')}"
        )


def require_atomic64_manifest_alignment(root: Path, missing: list[str]) -> None:
    manifest = json.loads(read_text(root / ATOMIC64_MANIFEST))
    expected_note_path = NOTE.as_posix()
    expected_phase4_build_blob = git_blob_sha(root / PHASE4_BUILD)
    if manifest.get("phase4_gate_evidence_path") != expected_note_path:
        missing.append(
            "atomic64_manifest:phase4_gate_evidence_path:"
            f"expected={expected_note_path}:actual={manifest.get('phase4_gate_evidence_path')}"
        )
    if manifest.get("phase4_build_blob_sha") != expected_phase4_build_blob:
        missing.append(
            "atomic64_manifest:phase4_build_blob_sha:"
            f"expected={expected_phase4_build_blob}:actual={manifest.get('phase4_build_blob_sha')}"
        )


def required_files() -> tuple[Path, ...]:
    return (
        NOTE, MATRIX, DOCS_README, SCRIPTS_README, TESTS_README, REVIEW_CHECKLIST,
        WORKFLOW, MAKEFILE, VALIDATOR, ARTIFACT_DIFF_DOC, ARTIFACT_DIFF_HELPER,
        ARTIFACT_DIFF_CONTRACT_CHECKER, WORKFLOW_ROUTE_CHECKER, ATOMIC64_DIFF,
        RUNTIME_ATOMIC64_DIFF, ATOMIC64_MANIFEST, RUNTIME_ATOMIC64_SURVEY,
        BITMAP_MANIFEST,
        BITMAP_SURVEY, PERF_SURVEY, KPROBE_MANIFEST, TEST_FSMOUNT_SURVEY,
        PHASE4_BUILD, PHASE9_BUILD, REVERSIBLE_DELIVERY_EVIDENCE, SELF,
    )


def build_fixture_tree(root: Path) -> None:
    fixtures = {
        MATRIX.as_posix(): "\n".join([
            "scripts/zigux/check-phase4-gate-evidence.py",
            "scripts/zigux/check-phase4-remaining-gap-matrix.py",
            "scripts/zigux/check-phase4-workflow-route-counts.py",
            "zigux/tests/phase4_perf_baseline_manifest.json",
            "zigux/tests/phase4_perf_baseline_survey.zig",
            "explicit local lab replay marker: `make -C zigux phase4-kprobe-example-survey`",
            "dedicated local survey wrapper: `make -C zigux phase4-kprobe-example-survey`",
            "validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`",
            "survey owner: `Validation and Perf Team`",
            "rollback owner: `Validation and Perf Team`",
            "local-only benchmark commands and acceptable limits are approved today",
            "gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
            "shared CI perf promotion pending",
            "current measurable status: absent on current `master`",
            "reviewability-only no-perf-threshold posture",
            "validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
            "dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`",
            "survey owner: `Validation and Perf Team`",
            "rollback owner: `Validation and Perf Team`",
            "Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners",
            "next bounded evidence step: keep the dedicated parked survey packet",
            "",
        ]),
        DOCS_README.as_posix(): "\n".join(DOCS_README_MARKERS) + "\n",
        SCRIPTS_README.as_posix(): "\n".join(SCRIPTS_README_MARKERS) + "\n",
        TESTS_README.as_posix(): "\n".join(TESTS_README_MARKERS) + "\n",
        REVIEW_CHECKLIST.as_posix(): "\n".join(CHECKLIST_MARKERS) + "\n",
        WORKFLOW.as_posix(): "\n".join(WORKFLOW_MARKERS) + "\n",
        MAKEFILE.as_posix(): "phase4-validate:\nphase4-test-fsmount-survey:\nphase4-kprobe-example-survey:\n",
        VALIDATOR.as_posix(): "validator placeholder\n",
        ARTIFACT_DIFF_DOC.as_posix(): "artifact diff doc placeholder\n",
        ARTIFACT_DIFF_HELPER.as_posix(): "artifact diff helper placeholder\n",
        ARTIFACT_DIFF_CONTRACT_CHECKER.as_posix(): "artifact diff contract checker placeholder\n",
        WORKFLOW_ROUTE_CHECKER.as_posix(): "workflow route checker placeholder\n",
        ATOMIC64_DIFF.as_posix(): "atomic64 diff placeholder\n",
        RUNTIME_ATOMIC64_DIFF.as_posix(): "runtime atomic64 diff placeholder\n",
        ATOMIC64_MANIFEST.as_posix(): "{\n  \"phase4_gate_evidence_path\": \"Documentation/zigux/phase4-gate-evidence.md\",\n  \"phase4_build_blob_sha\": \"__PHASE4_BUILD_BLOB_SHA__\"\n}\n",
        RUNTIME_ATOMIC64_SURVEY.as_posix(): "runtime atomic64 survey placeholder\n",
        BITMAP_MANIFEST.as_posix(): "{\n  \"shared_gate_evidence_path\": \"Documentation/zigux/phase4-gate-evidence.md\",\n  \"gate_evidence_path\": \"Documentation/zigux/phase4-gate-evidence.md\",\n  \"gate_evidence_blob_sha\": \"__GATE_EVIDENCE_BLOB_SHA__\"\n}\n",
        BITMAP_SURVEY.as_posix(): "bitmap survey placeholder\n",
        PERF_SURVEY.as_posix(): "perf survey placeholder\n",
        KPROBE_MANIFEST.as_posix(): "kprobe manifest placeholder\n",
        TEST_FSMOUNT_SURVEY.as_posix(): '"PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig"\n',
        PHASE4_BUILD.as_posix(): "phase4 build placeholder\n",
        PHASE9_BUILD.as_posix(): "phase9 build placeholder\n",
        REVERSIBLE_DELIVERY_EVIDENCE.as_posix(): "reversible delivery evidence placeholder\n",
        SELF.as_posix(): "fixture gate evidence checker\n",
    }
    for rel, content in fixtures.items():
        write_text(root / rel, content)
    fixtures[ATOMIC64_MANIFEST.as_posix()] = fixtures[ATOMIC64_MANIFEST.as_posix()].replace(
        "__PHASE4_BUILD_BLOB_SHA__",
        git_blob_sha(root / PHASE4_BUILD),
    )
    write_text(root / ATOMIC64_MANIFEST, fixtures[ATOMIC64_MANIFEST.as_posix()])
    note_lines = ["# Phase 4 Gate Evidence", "", "## Status"]
    for marker_label, rel in BLOB_TARGETS:
        note_lines.append(f"  * `{marker_label}={git_blob_sha(root / rel)}`")
    note_lines.extend([
        f"  * `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={EXPECTED_TARGET_COUNT}`",
        f"  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}`",
        "  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES) + "`",
        "  * `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
        "  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`",
        "  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`",
        f"  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={EXPECTED_TARGET_COUNT}`",
        f"  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}`",
        "  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
        "  * `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`",
        "  * `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`",
        "  * `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`",
        "",
        "## Exact Readback Evidence",
        "  * `scripts/zigux/check-phase4-gate-evidence.py` now recomputes the broader packet blob pins from live file contents so stale readback evidence fails closed.",
        "  * The runtime atomic64 handoff remains reviewable through `phase4-runtime-atomic64-diff-survey-tests`, `make -C zigux phase4-runtime-atomic64-diff-survey`, two `inc_not_zero` checks, and three `dec_if_positive` checks.",
        "  * The adjacent local-only perf packet remains explicit through `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and the shared posture that local-only benchmark commands and acceptable limits are approved today while shared CI perf promotion pending remains unchanged.",
        "  * The parked starter-gap packet keeps `PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix` explicit beside the current `make -C zigux phase4-kprobe-example-survey` and `make -C zigux phase4-test-fsmount-survey` wrappers.",
        "",
    ])
    write_text(root / NOTE, "\n".join(note_lines))
    fixtures[BITMAP_MANIFEST.as_posix()] = fixtures[BITMAP_MANIFEST.as_posix()].replace(
        "__GATE_EVIDENCE_BLOB_SHA__",
        git_blob_sha(root / NOTE),
    )
    write_text(root / BITMAP_MANIFEST, fixtures[BITMAP_MANIFEST.as_posix()])


def validate_root(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in required_files():
        if not (root / rel).is_file():
            missing.append(f"file:{rel.as_posix()}")
    if missing:
        return missing
    note_text = read_text(root / NOTE)
    require_markers(note_text, NOTE_MARKERS, "note", missing)
    require_markers(note_text, ("`PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES) + "`",), "note", missing)
    require_blob_pins(root, note_text, missing)
    require_atomic64_manifest_alignment(root, missing)
    require_bitmap_manifest_alignment(root, missing)
    for marker_label, expected in COUNT_MARKERS:
        require_exact_value(note_text, marker_label, expected, "note", missing)
    require_markers(read_text(root / MATRIX), MATRIX_MARKERS, "matrix", missing)
    require_markers(read_text(root / TEST_FSMOUNT_SURVEY), TEST_FSMOUNT_SURVEY_MARKERS, "test_fsmount_survey", missing)
    require_markers(read_text(root / DOCS_README), DOCS_README_MARKERS, "docs_readme", missing)
    require_markers(read_text(root / SCRIPTS_README), SCRIPTS_README_MARKERS, "scripts_readme", missing)
    require_markers(read_text(root / TESTS_README), TESTS_README_MARKERS, "tests_readme", missing)
    require_markers(read_text(root / REVIEW_CHECKLIST), CHECKLIST_MARKERS, "checklist", missing)
    require_markers(read_text(root / WORKFLOW), WORKFLOW_MARKERS, "workflow", missing)
    return missing


def mutate_file(root: Path, rel: Path) -> None:
    write_text(root / rel, read_text(root / rel) + "drift\n")


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-gate-evidence-") as tmp:
        root = Path(tmp)
        build_fixture_tree(root)
        if validate_root(root):
            raise AssertionError("baseline fixture failed")
        cases += 1
        mutators = {
            "shipped_target_count_drift": lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19`", "`PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=18`")),
            "missing_exact_readback_heading": lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "## Exact Readback Evidence", "## Evidence")),
            "forbidden_gate_evidence_checker_self_pin": lambda r: write_text(r / NOTE, read_text(r / NOTE) + "  * `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=duplicate`\n"),
            "validator_blob_pin_drift": lambda r: mutate_file(r, VALIDATOR),
            "phase4_build_manifest_blob_pin_drift": lambda r: write_text(
                r / ATOMIC64_MANIFEST,
                replace_once(
                    read_text(r / ATOMIC64_MANIFEST),
                    git_blob_sha(r / PHASE4_BUILD),
                    "0000000000000000000000000000000000000000",
                ),
            ),
            "phase4_build_survey_blob_pin_drift": lambda r: mutate_file(r, RUNTIME_ATOMIC64_SURVEY),
            "phase9_build_manifest_blob_pin_drift": lambda r: mutate_file(r, PHASE9_BUILD),
            "phase9_build_survey_blob_pin_drift": lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "phase4-runtime-atomic64-diff-survey-tests", "phase9-runtime-atomic64-diff-survey-tests")),
            "doc_readme_blob_pin_drift": lambda r: write_text(r / DOCS_README, replace_once(read_text(r / DOCS_README), DOCS_README_MARKERS[0], "Phase 4 notes - `Documentation/zigux/phase4-legacy-note.md`")),
            "script_readme_blob_pin_drift": lambda r: mutate_file(r, SCRIPTS_README),
            "tests_readme_blob_pin_drift": lambda r: mutate_file(r, TESTS_README),
            "gate_evidence_self_test_case_count_drift": lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=45`", "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=44`")),
            "gate_evidence_self_test_cases_drift": lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), ",".join(SELF_TEST_CASES), ",".join(SELF_TEST_CASES[:-1]))),
            "shared_validator_reruns_gate_evidence_check_drift": lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`", "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=false`")),
            "shared_validator_reruns_gate_evidence_self_test_drift": lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`", "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=false`")),
            "shared_validator_expected_target_count_drift": lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`", "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=18`")),
            "shared_validator_expected_self_test_case_count_drift": lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=45`", "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=44`")),
            "runtime_atomic64_survey_packet_presence_drift": lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`", "`PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=false`")),
            "bitmap_manifest_gate_evidence_blob_drift": lambda r: write_text(r / BITMAP_MANIFEST, replace_once(read_text(r / BITMAP_MANIFEST), git_blob_sha(r / NOTE), "0000000000000000000000000000000000000000")),
            "workflow_route_checker_matrix_presence_drift": lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "scripts/zigux/check-phase4-workflow-route-counts.py\n", "")),
            "kprobe_gap_packet_presence_drift": lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`", "`PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false`")),
            "kprobe_owner_drift": lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "survey owner: `Validation and Perf Team`", "survey owner: `Shared Subsystems Pod`")),
            "kprobe_validation_entrypoint_drift": lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`", "validation entrypoint: `zig test zigux/tests/kprobe_example_survey.zig`")),
            "kprobe_next_step_drift": lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "next bounded evidence step: keep the dedicated parked survey packet", "next bounded evidence step: revisit later")),
            "perf_baseline_packet_presence_drift": lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`", "`PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false`")),
            "perf_baseline_note_split_marker_drift": lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "local-only benchmark commands and acceptable limits are approved today", "local-only benchmark commands are approved today")),
            "perf_baseline_owner_drift": lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`", "gate owners: `ABI and Replay Team` and `Shared Subsystems Pod`")),
            "perf_baseline_shared_promotion_status_drift": lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "shared CI perf promotion pending", "shared CI perf promotion landed")),
            "test_fsmount_gap_packet_presence_drift": lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`", "`PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`")),
            "test_fsmount_threshold_posture_drift": lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "reviewability-only no-perf-threshold posture", "landed perf-threshold posture")),
            "test_fsmount_owner_drift": lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`\nsurvey owner: `Validation and Perf Team`", "dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`\nsurvey owner: `Shared Subsystems Pod`")),
            "test_fsmount_validation_entrypoint_drift": lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`", "validation entrypoint: `zig test zigux/tests/phase4_test_fsmount_survey.zig`")),
            "test_fsmount_linux_style_wrapper_drift": lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`", "dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount`")),
            "test_fsmount_next_step_drift": lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "current measurable status: absent on current `master`", "current measurable status: landed on current `master`")),
        }
        for case_name in SELF_TEST_CASES[1:]:
            build_fixture_tree(root)
            if case_name in mutators:
                mutators[case_name](root)
            else:
                matched = False
                for known_name, rel in MISSING_FILE_CASES:
                    if case_name == known_name:
                        (root / rel).unlink()
                        matched = True
                        break
                if not matched:
                    raise AssertionError(case_name)
            if not validate_root(root):
                raise AssertionError(case_name)
            cases += 1
        if cases != EXPECTED_SELF_TEST_CASE_COUNT:
            raise AssertionError(cases)


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