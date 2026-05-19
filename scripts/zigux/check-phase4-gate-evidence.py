#!/usr/bin/env python3
"""Guard the broader Phase 4 gate-evidence packet."""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-gate-evidence.md")
MATRIX = Path("Documentation/zigux/phase4-validation-matrix.md")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")
REVERSIBLE_NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
SEQUENCING_NOTE = Path("Documentation/zigux/phase4-validation-lane-sequencing.md")
ARTIFACT_DIFF_NOTE = Path("Documentation/zigux/artifact-diff.md")
ARTIFACT_DIFF_HELPER = Path("scripts/zigux/artifact_diff.py")
ARTIFACT_DIFF_CONTRACT = Path("scripts/zigux/check-artifact-diff-contract.py")
ARTIFACT_DIFF_DETERMINISM = Path("scripts/zigux/check-phase4-artifact-diff-determinism.py")
VALIDATOR = Path("scripts/zigux/validate-phase4.py")
PHASE4_BUILD = Path("zigux/tests/phase4_build.zig")
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

EXPECTED_TARGET_COUNT = 19
EXPECTED_SELF_TEST_CASE_COUNT = 42
SELF_TEST_CASES = [
    "baseline_round_trip",
    "shipped_target_count_drift",
    "missing_exact_readback_heading",
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
    "`PHASE4_VALIDATOR_BLOB_SHA=dea77e6385618147aba44d3714f73b6c5249e942`",
    "`PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=95471df68eea2537ea547394d0311c2939ae0d33`",
    "`PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=ef333c03fa97927b2be0152b613fab727bb89a11`",
    "`PHASE4_DOC_README_BLOB_SHA=ac515e3ed47c771b0947fde4200a90b9a1952c99`",
    "`PHASE4_SCRIPT_README_BLOB_SHA=4b22006c7278280203a23e6ec568cf8f47b62c7e`",
    "`PHASE4_TESTS_README_BLOB_SHA=107d5d300f43fb5c9b0c7f9439601af3507a59ff`",
    "`PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=6e486e059c0d1caa9599c5ac54936f7c52ac8e9a`",
    "`PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=65c2ceed2512dcec8f86cbe3c47831c30f5547d3`",
    "`PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19`",
    "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=42`",
    "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES) + "`",
    "`PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
    "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`",
    "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`",
    "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`",
    "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=42`",
    "`PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
    "`PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`",
    "`PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`",
    "`PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`",
    "## Exact Readback Evidence",
    "Use `Documentation/zigux/phase4-reversible-delivery-evidence.md` as the narrower direct-readback handoff while `scripts/zigux/check-phase4-gate-evidence.py` continues to guard this broader rollback-ownership note",
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
    "### `scripts/zigux/check-phase4-gate-evidence.py`",
    "### `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "### `zigux/tests/phase4_perf_baseline_survey.zig`",
    "validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`",
    "Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners",
    "dedicated local checker: `python3 scripts/zigux/check-phase4-perf-baseline-packet.py --self-test` then `python3 scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "local-only benchmark commands and acceptable limits are approved today",
    "shared CI perf promotion pending",
    "current measurable status: absent on current `master`",
    "test_fsmount threshold posture: reviewability_only_no_perf_threshold",
    "test_fsmount validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
    "test_fsmount dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`",
    "next bounded evidence step: keep the dedicated parked survey packet",
)

MAKEFILE_MARKERS = (
    "phase4-validate:",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-remaining-gap-matrix.py",
    "phase4-kprobe-example-survey:",
    "phase4-test-fsmount-survey:",
    "phase4-perf-baseline-survey:",
)

WORKFLOW_MARKERS = (
    "- name: Validate Phase 4 rollback routes",
    "run: make -C zigux phase4-validate",
    "- name: Run Phase 4 rollback tests",
    "run: make -C zigux phase4-test",
)

CHECKLIST_MARKERS = (
    "keep the directly readable local-only perf packet explicit",
    "keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "keep the repo-reality warning explicit for the missing broader Phase 4 validator, build, and bitmap-diff companions",
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixture self-test")
    return parser.parse_args()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing required file: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_markers(text: str, markers: tuple[str, ...], label: str, missing: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def require_exact_value(text: str, label: str, marker_label: str, expected: int, missing: list[str]) -> None:
    matches = re.findall(rf"`{re.escape(marker_label)}=(\d+)`", text)
    if not matches:
        missing.append(f"{label}:missing:{marker_label}")
        return
    if any(int(value) != expected for value in matches):
        missing.append(f"{label}:{marker_label}:expected={expected}:actual={matches}")


def require_file_set(root: Path, missing: list[str]) -> None:
    for rel in (
        NOTE,
        MATRIX,
        MAKEFILE,
        WORKFLOW,
        REVIEW_CHECKLIST,
        TESTS_README,
        REVERSIBLE_NOTE,
        SEQUENCING_NOTE,
        ARTIFACT_DIFF_NOTE,
        ARTIFACT_DIFF_HELPER,
        ARTIFACT_DIFF_CONTRACT,
        ARTIFACT_DIFF_DETERMINISM,
        VALIDATOR,
        PHASE4_BUILD,
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
    ):
        if not (root / rel).is_file():
            missing.append(f"file:{rel.as_posix()}")


def validate_root(root: Path) -> list[str]:
    missing: list[str] = []
    require_file_set(root, missing)
    if missing:
        return missing

    note_text = read_text(root / NOTE)
    matrix_text = read_text(root / MATRIX)
    makefile_text = read_text(root / MAKEFILE)
    workflow_text = read_text(root / WORKFLOW)
    checklist_text = read_text(root / REVIEW_CHECKLIST)
    tests_readme_text = read_text(root / TESTS_README)

    require_markers(note_text, NOTE_MARKERS, "note", missing)
    require_markers(matrix_text, MATRIX_MARKERS, "matrix", missing)
    require_markers(makefile_text, MAKEFILE_MARKERS, "makefile", missing)
    require_markers(workflow_text, WORKFLOW_MARKERS, "workflow", missing)
    require_markers(checklist_text, CHECKLIST_MARKERS, "checklist", missing)
    require_markers(tests_readme_text, TESTS_README_MARKERS, "tests_readme", missing)

    require_exact_value(
        note_text,
        "note",
        "PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT",
        EXPECTED_TARGET_COUNT,
        missing,
    )
    require_exact_value(
        note_text,
        "note",
        "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT",
        EXPECTED_SELF_TEST_CASE_COUNT,
        missing,
    )
    require_exact_value(
        note_text,
        "note",
        "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT",
        EXPECTED_TARGET_COUNT,
        missing,
    )
    require_exact_value(
        note_text,
        "note",
        "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT",
        EXPECTED_SELF_TEST_CASE_COUNT,
        missing,
    )

    return missing


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)


def build_fixture_tree(root: Path) -> None:
    write_text(
        root / NOTE,
        "\n".join(
            [
                "# Phase 4 Gate Evidence",
                "",
                "## Status",
                "  * `PHASE4_VALIDATOR_BLOB_SHA=dea77e6385618147aba44d3714f73b6c5249e942`",
                "  * `PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=95471df68eea2537ea547394d0311c2939ae0d33`",
                "  * `PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=ef333c03fa97927b2be0152b613fab727bb89a11`",
                "  * `PHASE4_DOC_README_BLOB_SHA=ac515e3ed47c771b0947fde4200a90b9a1952c99`",
                "  * `PHASE4_SCRIPT_README_BLOB_SHA=4b22006c7278280203a23e6ec568cf8f47b62c7e`",
                "  * `PHASE4_TESTS_README_BLOB_SHA=107d5d300f43fb5c9b0c7f9439601af3507a59ff`",
                "  * `PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=6e486e059c0d1caa9599c5ac54936f7c52ac8e9a`",
                "  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=65c2ceed2512dcec8f86cbe3c47831c30f5547d3`",
                "  * `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19`",
                "  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=42`",
                "  * `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES) + "`",
                "  * `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
                "  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`",
                "  * `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`",
                "  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`",
                "  * `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=42`",
                "  * `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
                "  * `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`",
                "  * `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`",
                "  * `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`",
                "",
                "## Exact Readback Evidence",
                "Use `Documentation/zigux/phase4-reversible-delivery-evidence.md` as the narrower direct-readback handoff while `scripts/zigux/check-phase4-gate-evidence.py` continues to guard this broader rollback-ownership note and `scripts/zigux/check-phase4-perf-baseline-packet.py` keeps the adjacent local-only perf packet exact.",
                "That narrower handoff still keeps the parked kprobe packet's shared matrix anchor explicit as `PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix`.",
                "",
            ]
        ),
    )
    write_text(
        root / MATRIX,
        "\n".join(
            [
                "# Phase 4 Validation Matrix",
                "  * current repo reality:",
                "    * `scripts/zigux/check-phase4-gate-evidence.py`",
                "    * `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
                "    * `scripts/zigux/check-phase4-workflow-route-counts.py`",
                "    * `scripts/zigux/check-phase4-perf-baseline-packet.py`",
                "    * `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`",
                "    * `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`",
                "    * `zigux/tests/phase4_bitmap_diff_manifest.json`",
                "    * `zigux/tests/phase4_bitmap_diff_survey.zig`",
                "    * `zigux/tests/phase4_bitmap_live_helper_replay.zig`",
                "    * `zigux/tests/phase4_perf_baseline_manifest.json`",
                "    * `zigux/tests/phase4_perf_baseline_survey.zig`",
                "### `scripts/zigux/check-phase4-gate-evidence.py`",
                "### `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
                "### `zigux/tests/phase4_perf_baseline_survey.zig`",
                "validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`",
                "Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners so the validator-first packet does not widen by accident.",
                "dedicated local checker: `python3 scripts/zigux/check-phase4-perf-baseline-packet.py --self-test` then `python3 scripts/zigux/check-phase4-perf-baseline-packet.py`; this checker keeps the dedicated perf-baseline packet local-only and self-tested without promoting it into the shared workflow or the shared `phase4-test` route while shared CI perf promotion stays pending",
                "local-only benchmark commands and acceptable limits are approved today",
                "shared CI perf promotion pending",
                "current measurable status: absent on current `master`",
                "test_fsmount threshold posture: reviewability_only_no_perf_threshold",
                "test_fsmount validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
                "test_fsmount dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`",
                "next bounded evidence step: keep the dedicated parked survey packet",
                "",
            ]
        ),
    )
    write_text(
        root / MAKEFILE,
        "\n".join(
            [
                "phase4-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-remaining-gap-matrix.py",
                "phase4-kprobe-example-survey:",
                "phase4-test-fsmount-survey:",
                "phase4-perf-baseline-survey:",
                "",
            ]
        ),
    )
    write_text(
        root / WORKFLOW,
        "\n".join(
            [
                "      - name: Validate Phase 4 rollback routes",
                "        run: make -C zigux phase4-validate",
                "      - name: Run Phase 4 rollback tests",
                "        run: make -C zigux phase4-test",
                "",
            ]
        ),
    )
    write_text(
        root / REVIEW_CHECKLIST,
        "\n".join(
            [
                "# Review Checklist",
                "keep the directly readable local-only perf packet explicit",
                "keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
                "keep the repo-reality warning explicit for the missing broader Phase 4 validator, build, and bitmap-diff companions",
                "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence",
                "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
                "keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
                "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval",
                "",
            ]
        ),
    )
    write_text(
        root / TESTS_README,
        "\n".join(
            [
                "# zigux/tests",
                "Keep the current bounded Phase 4 reminder packet explicit through `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and `zigux/tests/README.md`.",
                "Keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py` so the tests-root summary records the narrower current-head repo-reality packet instead of leaving those returned checker surfaces in the missing bucket.",
                "Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`",
                "Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`",
                "current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone",
                "",
            ]
        ),
    )
    write_text(root / REVERSIBLE_NOTE, "# reversible handoff\n")
    write_text(root / SEQUENCING_NOTE, "# sequencing note\n")
    write_text(root / ARTIFACT_DIFF_NOTE, "# artifact diff note\n")
    write_text(root / ARTIFACT_DIFF_HELPER, "# artifact diff helper\n")
    write_text(root / ARTIFACT_DIFF_CONTRACT, "# artifact diff contract\n")
    write_text(root / ARTIFACT_DIFF_DETERMINISM, "# artifact diff determinism\n")
    write_text(root / VALIDATOR, "# phase4 validator\n")
    write_text(root / PHASE4_BUILD, "// phase4 build\n")
    write_text(root / ATOMIC64_MANIFEST, "{}\n")
    write_text(root / ATOMIC64_SURVEY, "// atomic64 survey\n")
    write_text(root / BITMAP_MANIFEST, "{}\n")
    write_text(root / BITMAP_SURVEY, "// bitmap survey\n")
    write_text(root / BITMAP_HELPER_REPLAY, "// bitmap helper replay\n")
    write_text(root / PERF_MANIFEST, "{}\n")
    write_text(root / PERF_SURVEY, "// perf survey\n")
    write_text(root / KPROBE_NOTE, "# kprobe gap note\n")
    write_text(root / KPROBE_MANIFEST, "{}\n")
    write_text(root / KPROBE_SURVEY, "// kprobe survey\n")
    write_text(root / TEST_FSMOUNT_NOTE, "# test_fsmount gap note\n")
    write_text(root / TEST_FSMOUNT_MANIFEST, "{}\n")
    write_text(root / TEST_FSMOUNT_SURVEY, "// test_fsmount survey\n")
    write_text(root / SELF, "# self placeholder\n")


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-gate-evidence-") as tmp:
        root = Path(tmp)
        build_fixture_tree(root)

        failures = validate_root(root)
        if failures:
            raise AssertionError(f"baseline fixture failed: {failures}")
        cases += 1

        def expect_failure(mutator) -> None:
            nonlocal cases
            build_fixture_tree(root)
            mutator(root)
            if not validate_root(root):
                raise AssertionError("expected validation failure")
            cases += 1

        expect_failure(lambda r: (r / NOTE).unlink())
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19`", "`PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=18`")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "## Exact Readback Evidence", "## Evidence")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "dea77e6385618147aba44d3714f73b6c5249e942", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "6e486e059c0d1caa9599c5ac54936f7c52ac8e9a", "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "65c2ceed2512dcec8f86cbe3c47831c30f5547d3", "cccccccccccccccccccccccccccccccccccccccc")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "ac515e3ed47c771b0947fde4200a90b9a1952c99", "dddddddddddddddddddddddddddddddddddddddd")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "4b22006c7278280203a23e6ec568cf8f47b62c7e", "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "107d5d300f43fb5c9b0c7f9439601af3507a59ff", "ffffffffffffffffffffffffffffffffffffffff")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=42`", "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=41`")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), ",".join(SELF_TEST_CASES), ",".join(SELF_TEST_CASES[:-1]))))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`", "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=false`")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`", "`PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=false`")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`", "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=18`")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=42`", "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=41`")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`", "`PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=false`")))
        expect_failure(lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "zigux/tests/phase4_runtime_atomic64_diff_manifest.json", "zigux/tests/runtime_atomic64_diff_manifest.json")))
        expect_failure(lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "zigux/tests/phase4_runtime_atomic64_diff_survey.zig", "zigux/tests/runtime_atomic64_diff_survey.zig")))
        expect_failure(lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "zigux/tests/phase4_bitmap_diff_manifest.json", "zigux/tests/bitmap_diff_manifest.json")))
        expect_failure(lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "zigux/tests/phase4_bitmap_diff_survey.zig", "zigux/tests/phase4_bitmap_survey.zig")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`", "`PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false`")))
        expect_failure(lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`", "validation entrypoint: `zig test zigux/tests/kprobe_example_survey.zig`")))
        expect_failure(lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "next bounded evidence step: keep the dedicated parked survey packet", "next bounded evidence step: revisit later")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`", "`PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false`")))
        expect_failure(lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "local-only benchmark commands and acceptable limits are approved today", "local-only benchmark commands are approved today")))
        expect_failure(lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "shared CI perf promotion pending", "shared CI perf promotion landed")))
        expect_failure(lambda r: write_text(r / NOTE, replace_once(read_text(r / NOTE), "`PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`", "`PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`")))
        expect_failure(lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "test_fsmount threshold posture: reviewability_only_no_perf_threshold", "test_fsmount threshold posture: landed_perf_threshold")))
        expect_failure(lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "test_fsmount validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`", "test_fsmount validation entrypoint: `zig test zigux/tests/phase4_test_fsmount_survey.zig`")))
        expect_failure(lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "test_fsmount dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`", "test_fsmount dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount`")))
        expect_failure(lambda r: write_text(r / MATRIX, replace_once(read_text(r / MATRIX), "current measurable status: absent on current `master`", "current measurable status: landed on current `master`")))
        expect_failure(lambda r: (r / VALIDATOR).unlink())
        expect_failure(lambda r: (r / PHASE4_BUILD).unlink())
        expect_failure(lambda r: (r / ARTIFACT_DIFF_HELPER).unlink())
        expect_failure(lambda r: (r / ATOMIC64_MANIFEST).unlink())
        expect_failure(lambda r: (r / BITMAP_SURVEY).unlink())
        expect_failure(lambda r: (r / PERF_SURVEY).unlink())
        expect_failure(lambda r: (r / KPROBE_MANIFEST).unlink())
        expect_failure(lambda r: (r / TEST_FSMOUNT_SURVEY).unlink())
        expect_failure(lambda r: write_text(r / TESTS_README, replace_once(read_text(r / TESTS_README), "Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`", "Current direct-readback perf checker: `scripts/zigux/check-phase4-perf-baseline.py`")))
        expect_failure(lambda r: write_text(r / TESTS_README, replace_once(read_text(r / TESTS_README), "Keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py`", "Keep the broader packet explicit through shared notes only")))

        if cases != EXPECTED_SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {EXPECTED_SELF_TEST_CASE_COUNT} self-test cases, saw {cases}")


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        print(f"phase4 gate evidence self-test: PASS ({EXPECTED_SELF_TEST_CASE_COUNT} cases)")
        return 0

    root = Path(args.root).resolve()
    failures = validate_root(root)
    if failures:
        for failure in failures:
            print(f"phase4 gate evidence check failed: {failure}")
        return 1

    print("phase4 gate evidence check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
