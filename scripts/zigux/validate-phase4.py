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
    "- deterministic survey entrypoint: `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py` must keep the helper self-test catalog, the contract summary catalog, and the repeat-case packet aligned with this note and the shared validator packet",
    "- review rule: any change to the helper's emitted `ARTIFACT_DIFF=*`, `MODE=*`, `EXPECTED=*`, `ACTUAL=*`, `SHA256=*`, `EXPECTED_EXISTS=*`, `ACTUAL_EXISTS=*`, `EXPECTED_JSON_ERROR=*`, or `ACTUAL_JSON_ERROR=*` lines must update this note in the same change so the published host-side artifact packet stays reviewable",
    "- boundary: keep this note scoped to the shared host-side diff helper; Phase 4 gate ownership for `zigux/tests/*.zig` still belongs in `Documentation/zigux/phase4-validation-matrix.md`",
    "- deterministic helper contract: `ARTIFACT_DIFF_RESULT_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL[,SHA256|EXPECTED_EXISTS|ACTUAL_EXISTS|EXPECTED_JSON_ERROR|ACTUAL_JSON_ERROR]`",
    "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_TEXT` must prove both the stable text pass shape and the direct text mismatch fail shape",
    "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_JSON` must prove canonical JSON equivalence while `ARTIFACT_DIFF_SELF_TEST_JSON_INVALID` proves malformed JSON fails without inventing digest or exists markers",
    "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_SHA256` must prove both the shared digest pass line and the exact expected-vs-actual digest drift lines",
    "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_MISSING` must prove missing-path failures emit only the EXISTS markers",
    "- deterministic helper catalog: `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_SELF_TEST_CASES` must stay aligned with the helper's published `--self-test` packet",
    "- deterministic checker catalog: `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_BASE_CASES`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASES`, `ARTIFACT_DIFF_CONTRACT_CASE_COUNT`, and `ARTIFACT_DIFF_CONTRACT_CASES` must stay aligned with the published contract replay packet",
    "- deterministic checker self-test catalog: `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES` must stay aligned with the isolated stale-catalog and review-note drift coverage",
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

PHASE4_PERF_BASELINE_EXPECTED_STRINGS = {
    "lane_key": "P4-L20",
    "phase": "Phase 4",
    "owner": "Validation and Perf Team",
    "rollback_owner": "Validation and Perf Team",
}

PHASE4_PERF_BASELINE_SURVEYED_GATES = [
    {
        "surface": "zigux/tests/atomic64_diff.zig",
        "gate_owner": "ABI and Runtime Team",
        "gate_rollback_owner": "ABI and Runtime Team",
        "threshold_posture": "threshold_pending_until_runtime_atomic64_scope_widens",
    },
    {
        "surface": "zigux/tests/bitmap_diff.zig",
        "gate_owner": "Shared Subsystems Pod",
        "gate_rollback_owner": "Shared Subsystems Pod",
        "threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
    },
]

PHASE4_PERF_BASELINE_SUMMARY_FIELDS = {
    "phase4_build_step_present": True,
    "phase4_validation_matrix_present": True,
    "shared_phase4_test_step_includes_survey": False,
    "benchmark_command_unapproved": False,
    "acceptable_limit_unapproved": False,
    "atomic64_benchmark_command_approved": True,
    "atomic64_acceptable_limit_approved": True,
    "bitmap_benchmark_command_approved": True,
    "bitmap_acceptable_limit_approved": True,
}

PHASE4_PERF_BASELINE_COMMAND_EVIDENCE = {
    "atomic64": {
        "evidence_status": "benchmark_command_approved",
        "benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
        "acceptable_limit_status": "approved_local_only",
        "acceptable_limit_metric": "median_elapsed_ns",
        "acceptable_limit_iterations": 4,
        "acceptable_limit_sample_count": 7,
        "acceptable_limit_max_elapsed_ns": 8192,
        "deterministic_replays": [
            {
                "iterations": 1,
                "checksum": 3626254113632800175,
                "final_counter": 130322557735600377,
            },
            {
                "iterations": 4,
                "checksum": 9210681150676220922,
                "final_counter": 130322557735600376,
            },
        ],
    },
    "bitmap": {
        "evidence_status": "benchmark_command_approved",
        "benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
        "acceptable_limit_status": "approved_local_only",
        "acceptable_limit_metric": "median_elapsed_ns",
        "acceptable_limit_iterations": 4,
        "acceptable_limit_sample_count": 7,
        "acceptable_limit_max_elapsed_ns": 131072,
        "deterministic_replays": [
            {
                "iterations": 1,
                "checksum": 5216946504564592253,
                "final_first_set": 0,
                "final_first_zero": 109,
                "final_weight": 1005,
                "final_nth_seven": 123,
            },
            {
                "iterations": 4,
                "checksum": 7942141539243507472,
                "final_first_set": 0,
                "final_first_zero": 109,
                "final_weight": 1005,
                "final_nth_seven": 123,
            },
        ],
    },
}

PHASE4_PERF_BASELINE_REQUIRED_GAPS = {
    "phase4-perf-baseline-survey-manifest": {
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase4_perf_baseline_manifest.json",
        "why_markers": [
            "manifest-backed survey packet",
            "acceptable limits for both landed rollback gates",
        ],
    },
    "phase4-perf-baseline-survey-gate": {
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase4_perf_baseline_survey.zig",
        "why_markers": [
            "correctness-only posture",
            "bitmap acceptable-limit edge",
        ],
    },
    "phase4-perf-baseline-atomic64-command-evidence": {
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase4_perf_baseline_manifest.json",
        "why_markers": [
            "exact-pins",
            "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
            "runThresholdReplay(1)",
            "3626254113632800175",
            "130322557735600377",
            "runThresholdReplay(4)",
            "9210681150676220922",
            "130322557735600376",
        ],
    },
    "phase4-perf-baseline-atomic64-command": {
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/atomic64_diff.zig",
        "benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
        "why_markers": [
            "approved for local Phase 4 perf review",
            "shared CI perf approval",
        ],
    },
    "phase4-perf-baseline-atomic64-acceptable-limit": {
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/atomic64_diff.zig",
        "why_markers": [
            "8192",
            "seven monotonic samples",
            "attached Zig toolchain",
        ],
    },
    "phase4-perf-baseline-bitmap-command-evidence": {
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase4_perf_baseline_manifest.json",
        "why_markers": [
            "exact-pins",
            "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
            "runThresholdReplay(1)",
            "5216946504564592253",
            "final first-set `0`",
            "final first-zero `109`",
            "final weight `1005`",
            "final nth-seven `123`",
            "runThresholdReplay(4)",
            "7942141539243507472",
        ],
    },
    "phase4-perf-baseline-bitmap-command": {
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/bitmap_diff.zig",
        "benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
        "why_markers": [
            "approved for local Phase 4 perf review",
            "acceptable limit now stays explicitly local-only",
        ],
    },
    "phase4-perf-baseline-bitmap-acceptable-limit": {
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/bitmap_diff.zig",
        "why_markers": [
            "131072",
            "79135",
            "121289",
            "shared CI perf coverage",
        ],
    },
    "phase4-perf-baseline-shared-promotion-decision": {
        "status": "ready_next",
        "zigux_destination": "Documentation/zigux/phase4-validation-matrix.md",
        "why_markers": [
            "approved local benchmark commands",
            "approved local-only acceptable limits",
            "keep those limits local-only or intentionally promote a broader shared CI perf-coverage claim",
            "without widening the current validator-first packet by accident",
        ],
    },
}

PHASE4_PERF_BASELINE_SURVEY_MARKERS = [
    'test "phase4 perf baseline survey manifest keeps the current benchmark-command posture explicit"',
    "P4-L20",
    "Validation and Perf Team",
    "phase4-perf-baseline-survey-manifest",
    "phase4-perf-baseline-survey-gate",
    "phase4-perf-baseline-atomic64-command-evidence",
    "phase4-perf-baseline-atomic64-command",
    "phase4-perf-baseline-atomic64-acceptable-limit",
    "phase4-perf-baseline-bitmap-command-evidence",
    "phase4-perf-baseline-bitmap-command",
    "phase4-perf-baseline-bitmap-acceptable-limit",
    "phase4-perf-baseline-shared-promotion-decision",
    "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
    "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
    "approved_local_only",
    "8192",
    "131072",
    "79135",
    "121289",
    "shared CI perf coverage",
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
    "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_re…2364 tokens truncated…TOMIC64_MANIFEST_SHA_TARGETS.items():
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


def run_phase4_perf_baseline_packet_check(root: Path) -> list[str]:
    manifest = json.loads(
        (root / "zigux/tests/phase4_perf_baseline_manifest.json").read_text(encoding="utf-8")
    )
    survey = (root / "zigux/tests/phase4_perf_baseline_survey.zig").read_text(encoding="utf-8")
    problems: list[str] = []

    for field, expected in PHASE4_PERF_BASELINE_EXPECTED_STRINGS.items():
        if manifest.get(field) != expected:
            problems.append(f"perf_baseline_manifest:{field}:{manifest.get(field)}:{expected}")

    surveyed_gates = manifest.get("surveyed_gates")
    if not isinstance(surveyed_gates, list):
        problems.append(f"perf_baseline_manifest:surveyed_gates:{type(surveyed_gates).__name__}:list")
    elif len(surveyed_gates) != len(PHASE4_PERF_BASELINE_SURVEYED_GATES):
        problems.append(
            f"perf_baseline_manifest:surveyed_gates:length:{len(surveyed_gates)}:{len(PHASE4_PERF_BASELINE_SURVEYED_GATES)}"
        )
    else:
        for index, expected_gate in enumerate(PHASE4_PERF_BASELINE_SURVEYED_GATES):
            gate = surveyed_gates[index]
            if not isinstance(gate, dict):
                problems.append(
                    f"perf_baseline_manifest:surveyed_gates:{index}:{type(gate).__name__}:dict"
                )
                continue
            for field, expected in expected_gate.items():
                actual = gate.get(field)
                if actual != expected:
                    problems.append(
                        f"perf_baseline_manifest_surveyed_gate:{index}:{field}:{actual}:{expected}"
                    )

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        problems.append(f"perf_baseline_manifest:survey_summary:{type(summary).__name__}:dict")
    else:
        for field, expected in PHASE4_PERF_BASELINE_SUMMARY_FIELDS.items():
            actual = summary.get(field)
            if actual != expected:
                problems.append(f"perf_baseline_manifest_summary:{field}:{actual}:{expected}")

    command_evidence = manifest.get("command_evidence")
    if not isinstance(command_evidence, dict):
        problems.append(f"perf_baseline_manifest:command_evidence:{type(command_evidence).__name__}:dict")
    else:
        for family, expected_fields in PHASE4_PERF_BASELINE_COMMAND_EVIDENCE.items():
            actual_fields = command_evidence.get(family)
            if not isinstance(actual_fields, dict):
                problems.append(
                    f"perf_baseline_manifest_command:{family}:{type(actual_fields).__name__}:dict"
                )
                continue
            for field, expected in expected_fields.items():
                actual = actual_fields.get(field)
                if actual != expected:
                    problems.append(
                        f"perf_baseline_manifest_command:{family}:{field}:{actual}:{expected}"
                    )

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        problems.append(f"perf_baseline_manifest:gaps:{type(gaps).__name__}:list")
    else:
        if len(gaps) != len(PHASE4_PERF_BASELINE_REQUIRED_GAPS):
            problems.append(
                f"perf_baseline_manifest:gaps:length:{len(gaps)}:{len(PHASE4_PERF_BASELINE_REQUIRED_GAPS)}"
            )
        starter_landed_count = sum(1 for gap in gaps if isinstance(gap, dict) and gap.get("status") == "starter_landed")
        ready_next_count = sum(1 for gap in gaps if isinstance(gap, dict) and gap.get("status") == "ready_next")
        if starter_landed_count != 8:
            problems.append(f"perf_baseline_manifest:gaps:starter_landed:{starter_landed_count}:8")
        if ready_next_count != 1:
            problems.append(f"perf_baseline_manifest:gaps:ready_next:{ready_next_count}:1")
        gaps_by_id = {
            gap.get("id"): gap
            for gap in gaps
            if isinstance(gap, dict) and isinstance(gap.get("id"), str)
        }
        for gap_id, expected in PHASE4_PERF_BASELINE_REQUIRED_GAPS.items():
            gap = gaps_by_id.get(gap_id)
            if gap is None:
                problems.append(f"perf_baseline_gap:id:missing:{gap_id}")
                continue
            if gap.get("status") != expected["status"]:
                problems.append(
                    f"perf_baseline_gap:{gap_id}:status:{gap.get('status')}:{expected['status']}"
                )
            if gap.get("zigux_destination") != expected["zigux_destination"]:
                problems.append(
                    "perf_baseline_gap:"
                    f"{gap_id}:zigux_destination:{gap.get('zigux_destination')}:{expected['zigux_destination']}"
                )
            expected_command = expected.get("benchmark_command")
            actual_command = gap.get("benchmark_command")
            if actual_command != expected_command:
                problems.append(
                    f"perf_baseline_gap:{gap_id}:benchmark_command:{actual_command}:{expected_command}"
                )
            why_now = gap.get("why_now")
            if not isinstance(why_now, str):
                problems.append(f"perf_baseline_gap:{gap_id}:why_now:{type(why_now).__name__}:str")
                continue
            for marker in expected["why_markers"]:
                if marker not in why_now:
                    problems.append(f"perf_baseline_gap_marker:{gap_id}:{marker}")

    for marker in PHASE4_PERF_BASELINE_SURVEY_MARKERS:
        if marker not in survey:
            problems.append(f"perf_baseline_survey:{marker}")

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
    _write(root / "Documentation/zigux/phase4-gate-evidence.md", "phase4 gate evidence fixture\n")
    _write(root / "zigux/tests/phase4_build.zig", "\n".join(REQUIRED_PHASE4_BUILD_MARKERS + [""]))
    _write(root / "zigux/tests/phase9_build.zig", "// phase9 build\n")

    phase4_perf_baseline_manifest = {
        **PHASE4_PERF_BASELINE_EXPECTED_STRINGS,
        "surveyed_gates": PHASE4_PERF_BASELINE_SURVEYED_GATES,
        "survey_summary": PHASE4_PERF_BASELINE_SUMMARY_FIELDS,
        "command_evidence": PHASE4_PERF_BASELINE_COMMAND_EVIDENCE,
        "gaps": [
            {
                "id": gap_id,
                "status": expected["status"],
                "kind": "perf_policy" if gap_id == "phase4-perf-baseline-shared-promotion-decision" else "survey_manifest",
                "zigux_destination": expected["zigux_destination"],
                **(
                    {"benchmark_command": expected["benchmark_command"]}
                    if "benchmark_command" in expected
                    else {}
                ),
                "why_now": " ".join(expected["why_markers"]),
            }
            for gap_id, expected in PHASE4_PERF_BASELINE_REQUIRED_GAPS.items()
        ],
    }
    _write(
        root / "zigux/tests/phase4_perf_baseline_manifest.json",
        json.dumps(phase4_perf_baseline_manifest, indent=2) + "\n",
    )
    _write(
        root / "zigux/tests/phase4_perf_baseline_survey.zig",
        "\n".join(PHASE4_PERF_BASELINE_SURVEY_MARKERS + [""]),
    )

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
        assert run_phase4_perf_baseline_packet_check(root) == []

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

        bad_root3 = Path(tmp_dir) / "bad3"
        build_fixture_tree(bad_root3)
        perf_manifest_path = bad_root3 / "zigux/tests/phase4_perf_baseline_manifest.json"
        perf_manifest = json.loads(perf_manifest_path.read_text(encoding="utf-8"))
        perf_manifest["survey_summary"]["bitmap_acceptable_limit_approved"] = False
        perf_manifest_path.write_text(json.dumps(perf_manifest, indent=2) + "\n", encoding="utf-8")
        assert run_phase4_perf_baseline_packet_check(bad_root3) == [
            "perf_baseline_manifest_summary:bitmap_acceptable_limit_approved:False:True"
        ]

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
        ("PHASE4_PERF_BASELINE_PACKET_CHECK", run_phase4_perf_baseline_packet_check(ROOT)),
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
