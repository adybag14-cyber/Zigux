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
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
REVERSIBLE_NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
SEQUENCING_NOTE = Path("Documentation/zigux/phase4-validation-lane-sequencing.md")
ARTIFACT_DIFF_NOTE = Path("Documentation/zigux/artifact-diff.md")
ARTIFACT_DIFF_HELPER = Path("scripts/zigux/artifact_diff.py")
ARTIFACT_DIFF_CONTRACT = Path("scripts/zigux/check-artifact-diff-contract.py")
ARTIFACT_DIFF_DETERMINISM = Path("scripts/zigux/check-phase4-artifact-diff-determinism.py")
VALIDATOR = Path("scripts/zigux/validate-phase4.py")
PHASE4_BUILD = Path("zigux/tests/phase4_build.zig")
ATOMIC64_DIFF = Path("zigux/tests/atomic64_diff.zig")
ATOMIC64_MANIFEST = Path("zigux/tests/phase4_runtime_atomic64_diff_manifest.json")
ATOMIC64_SURVEY = Path("zigux/tests/phase4_runtime_atomic64_diff_survey.zig")
BITMAP_MANIFEST = Path("zigux/tests/phase4_bitmap_diff_manifest.json")
BITMAP_SURVEY = Path("zigux/tests/phase4_bitmap_diff_survey.zig")
BITMAP_HELPER_REPLAY = Path("zigux/tests/phase4_bitmap_live_helper_replay.zig")
PERF_MANIFEST = Path("zigux/tests/phase4_perf_baseline_manifest.json")
PERF_SURVEY = Path("zigux/tests/phase4_perf_baseline_survey.zig")
KPROBE_NOTE = Path("Documentation/zigux/phase4-kprobe-example-gap-survey.md")
KPROBE_MANIFEST = Path("zigux/tests/phase4_kprobe_example_manifest.json")
KPROBE_SURVEY = Path("zigux/tests/phase4_kprobe_example_survey.zig")
TEST_FSMOUNT_NOTE = Path("Documentation/zigux/phase4-test-fsmount-gap-survey.md")
TEST_FSMOUNT_MANIFEST = Path("zigux/tests/phase4_test_fsmount_manifest.json")
TEST_FSMOUNT_SURVEY = Path("zigux/tests/phase4_test_fsmount_survey.zig")
SELF = Path("scripts/zigux/check-phase4-gate-evidence.py")

EXPECTED_TARGET_COUNT = 15
EXPECTED_SELF_TEST_CASE_COUNT = 47
SELF_TEST_CASES = [
    "baseline_round_trip",
    "shipped_target_count_drift",
    "missing_exact_readback_heading",
    "forbidden_gate_evidence_checker_self_pin",
    "phase4_build_manifest_blob_pin_drift",
    "makefile_blob_pin_drift",
    "phase9_build_survey_blob_pin_drift",
    "doc_readme_blob_pin_drift",
    "script_readme_blob_pin_drift",
    "tests_readme_blob_pin_drift",
    "atomic64_diff_blob_pin_drift",
    "review_checklist_blob_pin_drift",
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
    "missing_doc_readme_file",
    "missing_script_readme_file",
    "missing_atomic64_diff_file",
    "missing_note_file",
]

UPDATED_WORKFLOW_SENTENCE = (
    "The current bootstrap workflow still routes Phase 4 through "
    "`make -C zigux phase4-validate` and `make -C zigux phase4-test` "
    "before the direct artifact-diff helper and checker reruns."
)

NOTE_MARKERS = (
    "# Phase 4 Gate Evidence",
    "`PHASE4_VALIDATION_MATRIX_BLOB_SHA=0c243dd80d8ff192d43c3f2db0ca36a2f8e5f77c`",
    "`PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=c1fa46fad53adc7327a03fbe12d3510e854e8bfa`",
    "`PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA=5173368ba7f69587f6839931b380f1e77c456933`",
    "`PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=92696cb02fc915fec0f5f1c4c2768a99cf99c9bf`",
    "`PHASE4_MAKEFILE_BLOB_SHA=2123cbb48f7bb32293c1bb3dead619e6d437923b`",
    "`PHASE4_WORKFLOW_BLOB_SHA=a4aad5b4904fb2d68f63921dc7693eea94f80780`",
    "`PHASE4_DOC_README_BLOB_SHA=faa69f9fca3e5d8cf328a904dc8cbc618ba0d017`",
    "`PHASE4_SCRIPT_README_BLOB_SHA=2908674dd61bbceb0b7a7474627dd4235e500ed0`",
    "`PHASE4_TESTS_README_BLOB_SHA=157b874862299ac71c80b51aa3da1b5a9e7cb3d4`",
    "`PHASE4_ATOMIC64_DIFF_BLOB_SHA=e84bf84b5e24428d596fe25502512fa24ce28b51`",
    "`PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=9ad41de72613cd72273b41c9cf2a64a0c46962df`",
    "`PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=a28a7393df1b270de8c80c57c30287d548bd0c4e`",
    "`PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=fa4ab6b736a3eba358630a9913b447f77569ab29`",
    "`PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=41557595b640e28985629285d40f7ad16e52340f`",
    "`PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=15`",
    "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=47`",
    "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES) + "`",
    "`PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
    "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`",
    "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`",
    "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=15`",
    "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=47`",
    "`PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
    "`PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`",
    "`PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`",
    "`PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`",
    "## Exact Readback Evidence",
    "`scripts/zigux/check-phase4-gate-evidence.py` stays explicit as the broader packet checker, but this note intentionally does not exact-pin that checker's own blob because any checker edit would invalidate a self-recorded blob immediately.",
    "Use `Documentation/zigux/phase4-reversible-delivery-evidence.md` as the narrower direct-readback handoff while `scripts/zigux/check-phase4-gate-evidence.py` continues to guard this broader rollback-ownership note",
    UPDATED_WORKFLOW_SENTENCE,
    "Keep `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` explicit as public-raw returned current-`master` companions while exact authenticated blob-pin refresh remains pending for that broader branch of the packet.",
    "PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
)

MATRIX_MARKERS = (
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-remaining-gap-matrix.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/phase4_bitmap_diff_manifest.json",
    "zigux/tests/phase4_bitmap_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`",
    "kprobe owner: `Validation and Perf Team`",
    "Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners",
    "dedicated local checker: `python3 scripts/zigux/check-phase4-perf-baseline-packet.py --self-test` then `python3 scripts/zigux/check-phase4-perf-baseline-packet.py`",
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
    "- name: Self-test current Phase 4 repo-reality warning checker",
    "run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
    "- name: Check current Phase 4 repo-reality warning packet",
    "run: python3 scripts/zigux/check-phase4-repo-reality-warning.py",
    "- name: Self-test current Phase 4 reversible-delivery pin checker",
    "run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test",
    "- name: Check current Phase 4 reversible-delivery pin packet",
    "run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "- name: Self-test current Phase 4 tests README checker",
    "run: python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test",
    "- name: Check current Phase 4 tests README packet",
    "run: python3 scripts/zigux/check-phase4-tests-readme-packet.py",
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
    "Keep the current bounded Phase 4 reminder packet explicit through `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and `zigux/tests/README.md`.",
    "Keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`",
    "current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md`",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, and `scripts/zigux/check-phase4-workflow-route-counts.py` keep the current helper-contract, validator-replay, shared rollback-owner reminder, local-only perf-governance, recovered remaining-gap, and route-inventory packet explicit on current `master`",
    "keep the current governance split explicit here too: the direct-readback shared handoff stays narrower than the broader recovered note companions, the Validation and Perf Team remains the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod remain the coordination owners for that policy call, and the dedicated perf-baseline survey must stay local-only until a later bounded lane intentionally widens that posture",
    "current `master` keeps the broader Phase 4 validator, build, and bitmap replay companions in a split-readback state rather than the missing bucket: `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap in authenticated contents reads in this runtime, but public raw fallback rereads return those files on current `master`, so keep them explicit as now-returned companions while exact authenticated blob-pin refresh remains pending",
)

COUNT_MARKERS = (
    ("PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT", EXPECTED_TARGET_COUNT),
    ("PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT", EXPECTED_SELF_TEST_CASE_COUNT),
    ("PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT", EXPECTED_TARGET_COUNT),
    ("PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT", EXPECTED_SELF_TEST_CASE_COUNT),
)

MUTATIONS: list[tuple[str, str, str, Path | None]] = [
    ("shipped_target_count_drift", "`PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=15`", "`PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=14`", NOTE),
    ("missing_exact_readback_heading", "## Exact Readback Evidence", "## Evidence", NOTE),
    ("phase4_build_manifest_blob_pin_drift", "a28a7393df1b270de8c80c57c30287d548bd0c4e", "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", NOTE),
    ("makefile_blob_pin_drift", "`PHASE4_MAKEFILE_BLOB_SHA=2123cbb48f7bb32293c1bb3dead619e6d437923b`", "`PHASE4_MAKEFILE_BLOB_SHA=3333333333333333333333333333333333333333`", NOTE),
    ("phase9_build_survey_blob_pin_drift", "`PHASE4_WORKFLOW_BLOB_SHA=a4aad5b4904fb2d68f63921dc7693eea94f80780`", "`PHASE4_WORKFLOW_BLOB_SHA=2222222222222222222222222222222222222222`", NOTE),
    ("doc_readme_blob_pin_drift", "faa69f9fca3e5d8cf328a904dc8cbc618ba0d017", "dddddddddddddddddddddddddddddddddddddddd", NOTE),
    ("script_readme_blob_pin_drift", SCRIPTS_README_MARKERS[1], "scripts README drift", SCRIPTS_README),
    ("tests_readme_blob_pin_drift", "157b874862299ac71c80b51aa3da1b5a9e7cb3d4", "ffffffffffffffffffffffffffffffffffffffff", NOTE),
    ("atomic64_diff_blob_pin_drift", "e84bf84b5e24428d596fe25502512fa24ce28b51", "9999999999999999999999999999999999999999", NOTE),
    ("review_checklist_blob_pin_drift", "41557595b640e28985629285d40f7ad16e52340f", "8888888888888888888888888888888888888888", NOTE),
    ("gate_evidence_self_test_case_count_drift", "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=47`", "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=46`", NOTE),
    ("shared_validator_reruns_gate_evidence_check_drift", "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`", "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=false`", NOTE),
    ("shared_validator_reruns_gate_evidence_self_test_drift", "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`", "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=false`", NOTE),
    ("shared_validator_expected_target_count_drift", "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=15`", "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=14`", NOTE),
    ("shared_validator_expected_self_test_case_count_drift", "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=47`", "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=46`", NOTE),
    ("runtime_atomic64_survey_packet_presence_drift", "`PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`", "`PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=false`", NOTE),
    ("bitmap_diff_survey_replay_marker_drift", "zigux/tests/phase4_bitmap_diff_survey.zig", "zigux/tests/phase4_bitmap_survey.zig", MATRIX),
    ("kprobe_gap_packet_presence_drift", "`PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`", "`PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false`", NOTE),
    ("kprobe_owner_drift", "kprobe owner: `Validation and Perf Team`", "kprobe owner: `Tooling and Validation Team`", MATRIX),
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

MISSING_FILE_CASES: list[tuple[str, Path]] = [
    ("missing_validator_file", VALIDATOR),
    ("missing_phase4_build_file", PHASE4_BUILD),
    ("missing_artifact_diff_helper_file", ARTIFACT_DIFF_HELPER),
    ("missing_atomic64_manifest_file", ATOMIC64_MANIFEST),
    ("missing_bitmap_survey_file", BITMAP_SURVEY),
    ("missing_perf_survey_file", PERF_SURVEY),
    ("missing_kprobe_manifest_file", KPROBE_MANIFEST),
    ("missing_test_fsmount_survey_file", TEST_FSMOUNT_SURVEY),
    ("missing_doc_readme_file", DOCS_README),
    ("missing_script_readme_file", SCRIPTS_README),
    ("missing_atomic64_diff_file", ATOMIC64_DIFF),
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
        MAKEFILE,
        WORKFLOW,
        REVIEW_CHECKLIST,
        SCRIPTS_README,
        TESTS_README,
        REVERSIBLE_NOTE,
        SEQUENCING_NOTE,
        ARTIFACT_DIFF_NOTE,
        ARTIFACT_DIFF_HELPER,
        ARTIFACT_DIFF_CONTRACT,
        ARTIFACT_DIFF_DETERMINISM,
        VALIDATOR,
        PHASE4_BUILD,
        ATOMIC64_DIFF,
        ATOMIC64_MANIFEST,
        ATOMIC64_SURVEY,
        BITMAP_MANIFEST,
        BITMAP_SURVEY,
        BITMAP_HELPER_REPLAY,
        PERF_MANIFEST,
        PERF_SURVEY,
        KPROBE_NOTE,
        KPROBE_MANIFEST,
        KPROBE_SURVEY,
        TEST_FSMOUNT_NOTE,
        TEST_FSMOUNT_MANIFEST,
        TEST_FSMOUNT_SURVEY,
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
        "  * `PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA=92696cb02fc915fec0f5f1c4c2768a99cf99c9bf`",
        "  * `PHASE4_MAKEFILE_BLOB_SHA=2123cbb48f7bb32293c1bb3dead619e6d437923b`",
        "  * `PHASE4_WORKFLOW_BLOB_SHA=a4aad5b4904fb2d68f63921dc7693eea94f80780`",
        "  * `PHASE4_DOC_README_BLOB_SHA=faa69f9fca3e5d8cf328a904dc8cbc618ba0d017`",
        "  * `PHASE4_SCRIPT_README_BLOB_SHA=2908674dd61bbceb0b7a7474627dd4235e500ed0`",
        "  * `PHASE4_TESTS_README_BLOB_SHA=157b874862299ac71c80b51aa3da1b5a9e7cb3d4`",
        "  * `PHASE4_ATOMIC64_DIFF_BLOB_SHA=e84bf84b5e24428d596fe25502512fa24ce28b51`",
        "  * `PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=9ad41de72613cd72273b41c9cf2a64a0c46962df`",
        "  * `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=a28a7393df1b270de8c80c57c30287d548bd0c4e`",
        "  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=fa4ab6b736a3eba358630a9913b447f77569ab29`",
        "  * `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=41557595b640e28985629285d40f7ad16e52340f`",
        "  * `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=15`",
        "  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=47`",
        "  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES) + "`",
        "  * `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
        "  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`",
        "  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`",
        "  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=15`",
        "  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=47`",
        "  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
        "  * `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`",
        "  * `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`",
        "  * `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`",
        "",
        "## Exact Readback Evidence",
        "  * `scripts/zigux/check-phase4-gate-evidence.py` stays explicit as the broader packet checker, but this note intentionally does not exact-pin that checker's own blob because any checker edit would invalidate a self-recorded blob immediately.",
        "  * Use `Documentation/zigux/phase4-reversible-delivery-evidence.md` as the narrower direct-readback handoff while `scripts/zigux/check-phase4-gate-evidence.py` continues to guard this broader rollback-ownership note and `scripts/zigux/check-phase4-perf-baseline-packet.py` keeps the adjacent local-only perf packet exact.",
        "  * " + UPDATED_WORKFLOW_SENTENCE,
        "  * Keep `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` explicit as public-raw returned current-`master` companions while exact authenticated blob-pin refresh remains pending for that broader branch of the packet.",
        "  * That narrower handoff still keeps the parked kprobe packet's shared matrix anchor explicit as `PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix`.",
        "",
    ]
    write_text(root / NOTE, "\n".join(note_lines))
    write_text(root / MATRIX, "\n".join(MATRIX_MARKERS) + "\n")
    write_text(root / MAKEFILE, "phase4-validate:\n\tscripts/zigux/check-phase4-gate-evidence.py\n\tscripts/zigux/check-phase4-remaining-gap-matrix.py\nphase4-kprobe-example-survey:\nphase4-test-fsmount-survey:\nphase4-perf-baseline-survey:\n")
    write_text(root / WORKFLOW, "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(root / REVIEW_CHECKLIST, "\n".join(CHECKLIST_MARKERS) + "\n")
    write_text(root / SCRIPTS_README, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root / TESTS_README, "\n".join(TESTS_README_MARKERS) + "\n")
    for rel in required_files():
        if rel in {NOTE, MATRIX, MAKEFILE, WORKFLOW, REVIEW_CHECKLIST, SCRIPTS_README, TESTS_README}:
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
    if "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=" in note_text:
        missing.append("note:forbidden:PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=")
    for marker_label, expected in COUNT_MARKERS:
        require_exact_value(note_text, marker_label, expected, "note", missing)

    require_markers(read_text(root / MATRIX), MATRIX_MARKERS, "matrix", missing)
    require_markers(read_text(root / MAKEFILE), ("phase4-validate:", "phase4-kprobe-example-survey:", "phase4-test-fsmount-survey:", "phase4-perf-baseline-survey:"), "makefile", missing)
    require_markers(read_text(root / WORKFLOW), WORKFLOW_MARKERS, "workflow", missing)
    require_markers(read_text(root / REVIEW_CHECKLIST), CHECKLIST_MARKERS, "checklist", missing)
    require_markers(read_text(root / SCRIPTS_README), SCRIPTS_README_MARKERS, "scripts_readme", missing)
    require_markers(read_text(root / TESTS_README), TESTS_README_MARKERS, "tests_readme", missing)
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

        expect_failure("forbidden_gate_evidence_checker_self_pin", lambda r: write_text(r / NOTE, read_text(r / NOTE) + "  * `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=deadbeef`\n"))
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