#!/usr/bin/env python3
"""Validate the current Phase 4 exact-readback evidence note."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
GATE_EVIDENCE_REL = Path("Documentation/zigux/phase4-gate-evidence.md")
EXPECTED_SHIPPED_TARGET_COUNT = 19
EXPECTED_SELF_TEST_CASE_COUNT = 33
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
    "missing_note_file",
]
SELF_TEST_CASES_LINE = (
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES)
)

REQUIRED_STATUS_MARKERS = [
    "PHASE4_EVIDENCE_DATE=",
    "PHASE4_EVIDENCE_MODE=github_connector_readback",
    "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions",
    "PHASE4_EXACT_READBACK_REF=master",
    "PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=",
    "PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true",
]

EXACT_STATUS_LINES = [
    "PHASE4_EXACT_READBACK_REF=master",
    f"PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}",
    f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}",
    SELF_TEST_CASES_LINE,
    "PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true",
    f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}",
    (
        "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="
        f"{EXPECTED_SELF_TEST_CASE_COUNT}"
    ),
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true",
]

REQUIRED_PROSE_MARKERS = [
    "## Exact Readback Evidence",
    "## Current Conclusion",
    "`scripts/zigux/check-phase4-gate-evidence.py` remains the dedicated exact-readback checker for this narrower rollback-ownership packet.",
    "`zigux/tests/phase4_perf_baseline_manifest.json` and `zigux/tests/phase4_perf_baseline_survey.zig` also remain shipped on `master` as the dedicated local-only perf-baseline posture packet",
    "shared CI perf coverage stays out of scope.",
    "Validation and Perf Team stays named as the decision owner",
    "phase4-bitmap-live-helper-replay-tests",
    "shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
    "the parked kprobe gap packet at `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig` now also stays under the dedicated exact-readback checker",
]

REQUIRED_SELF_TEST_CASE_MARKERS = [
    "baseline_round_trip",
    "shipped_target_count_drift",
    "validator_blob_pin_drift",
    "phase4_build_manifest_blob_pin_drift",
    "phase4_build_survey_blob_pin_drift",
    "doc_readme_blob_pin_drift",
    "script_readme_blob_pin_drift",
    "tests_readme_blob_pin_drift",
    "runtime_atomic64_survey_packet_presence_drift",
    "kprobe_owner_drift",
    "kprobe_validation_entrypoint_drift",
    "kprobe_next_step_drift",
    "test_fsmount_threshold_posture_drift",
    "test_fsmount_owner_drift",
    "test_fsmount_validation_entrypoint_drift",
    "test_fsmount_linux_style_wrapper_drift",
    "test_fsmount_next_step_drift",
    "missing_note_file",
]

BLOB_TARGETS = {
    "PHASE4_VALIDATION_MATRIX_BLOB_SHA": "Documentation/zigux/phase4-validation-matrix.md",
    "PHASE4_VALIDATOR_BLOB_SHA": "scripts/zigux/validate-phase4.py",
    "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA": "scripts/zigux/check-phase4-gate-evidence.py",
    "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA": "scripts/zigux/check-phase4-workflow-route-counts.py",
    "PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA": "Documentation/zigux/artifact-diff.md",
    "PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA": "scripts/zigux/check-artifact-diff-contract.py",
    "PHASE4_BUILD_BLOB_SHA": "zigux/tests/phase4_build.zig",
    "PHASE4_MAKEFILE_BLOB_SHA": "zigux/Makefile",
    "PHASE4_WORKFLOW_BLOB_SHA": ".github/workflows/zigux-bootstrap.yml",
    "PHASE4_DOC_README_BLOB_SHA": "Documentation/zigux/README.md",
    "PHASE4_SCRIPT_README_BLOB_SHA": "scripts/zigux/README.md",
    "PHASE4_TESTS_README_BLOB_SHA": "zigux/tests/README.md",
    "PHASE4_ATOMIC64_DIFF_BLOB_SHA": "zigux/tests/atomic64_diff.zig",
    "PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA": "zigux/tests/runtime_atomic64_diff.zig",
    "PHASE4_BITMAP_DIFF_BLOB_SHA": "zigux/tests/bitmap_diff.zig",
    "PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA": "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA": "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA": "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA": "Documentation/zigux/review-checklist.md",
}

if EXPECTED_SHIPPED_TARGET_COUNT != len(BLOB_TARGETS):
    raise AssertionError(
        "phase4 gate-evidence shipped target count drifted: "
        f"{EXPECTED_SHIPPED_TARGET_COUNT} != {len(BLOB_TARGETS)}"
    )

KPROBE_NOTE_REL = Path("Documentation/zigux/phase4-kprobe-example-gap-survey.md")
KPROBE_MANIFEST_REL = Path("zigux/tests/phase4_kprobe_example_manifest.json")
KPROBE_SURVEY_REL = Path("zigux/tests/phase4_kprobe_example_survey.zig")

KPROBE_NOTE_MARKERS = [
    "PHASE4_KPROBE_STATUS=parked_gap_packet_landed",
    "PHASE4_KPROBE_C_ANCHOR=samples/kprobes/kprobe_example.c",
    "PHASE4_KPROBE_CURRENT_LINUX_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-example-survey",
    "PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig",
    "PHASE4_KPROBE_OWNER=Validation and Perf Team",
    "PHASE4_KPROBE_ROLLBACK_OWNER=Validation and Perf Team",
    "Current `master` still does not ship `samples/zigux/kprobe_example.zig`.",
]

KPROBE_MANIFEST_EXPECTATIONS = {
    "lane_key": "P4-L19",
    "phase": "Phase 4",
    "c_anchor": "samples/kprobes/kprobe_example.c",
    "current_linux_replay": "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "dedicated_local_survey_wrapper": "make -C zigux phase4-kprobe-example-survey",
    "validation_entrypoint": "zig test zigux/tests/phase4_kprobe_example_survey.zig",
    "owner": "Validation and Perf Team",
    "rollback_owner": "Validation and Perf Team",
    "current_measurable_status": "absent_on_current_master_but_reviewable_through_the_dedicated_gap_packet_without_claiming_a_shipped_zig_starter",
    "reversible_delivery_evidence": "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, the local survey wrapper, the direct validation entrypoint, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface",
    "next_bounded_evidence_step": "keep the dedicated parked survey packet adjacent to the shared Phase 4 validation packet until a later bounded lane intentionally promotes the validator surface or lands the Zig starter",
}

KPROBE_SURVEY_MARKERS = [
    'test "phase4 kprobe survey keeps the parked gap packet explicit" {',
    'test "phase4 kprobe survey keeps reversible-delivery evidence explicit" {',
    'test "phase4 kprobe survey keeps the bounded next step explicit" {',
    '\\\"dedicated_local_survey_wrapper\\\": \\\"make -C zigux phase4-kprobe-example-survey\\\"',
    '\\\"validation_entrypoint\\\": \\\"zig test zigux/tests/phase4_kprobe_example_survey.zig\\\"',
    '\\\"owner\\\": \\\"Validation and Perf Team\\\"',
]

TEST_FSMOUNT_NOTE_REL = Path("Documentation/zigux/phase4-test-fsmount-gap-survey.md")
TEST_FSMOUNT_MANIFEST_REL = Path("zigux/tests/phase4_test_fsmount_manifest.json")
TEST_FSMOUNT_SURVEY_REL = Path("zigux/tests/phase4_test_fsmount_survey.zig")

TEST_FSMOUNT_NOTE_MARKERS = [
    "PHASE4_TEST_FSMOUNT_STATUS=parked_gap_packet_landed",
    "PHASE4_TEST_FSMOUNT_C_ANCHOR=samples/vfs/test-fsmount.c",
    "PHASE4_TEST_FSMOUNT_CURRENT_LINUX_REPLAY=make M=samples/vfs",
    "PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey",
    "PHASE4_TEST_FSMOUNT_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_OWNER=Validation and Perf Team",
    "PHASE4_TEST_FSMOUNT_ROLLBACK_OWNER=Validation and Perf Team",
    "PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold",
    "Current `master` still does not ship `samples/zigux/test_fsmount.zig`.",
    "reviewability-only no-perf-threshold posture",
]

TEST_FSMOUNT_MANIFEST_EXPECTATIONS = {
    "lane_key": "P4-L19",
    "phase": "Phase 4",
    "c_anchor": "samples/vfs/test-fsmount.c",
    "current_linux_replay": "make M=samples/vfs",
    "dedicated_local_survey_wrapper": "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "dedicated_linux_style_survey_wrapper": "make -C zigux phase4-test-fsmount-survey",
    "validation_entrypoint": "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "owner": "Validation and Perf Team",
    "rollback_owner": "Validation and Perf Team",
    "current_measurable_status": "absent_on_current_master_but_reviewable_through_the_dedicated_gap_packet_without_claiming_a_shipped_zig_starter",
    "threshold_posture": "reviewability_only_no_perf_threshold",
    "reversible_delivery_evidence": "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit bootstrap-CI posture, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface",
    "next_bounded_evidence_step": "keep the dedicated parked survey packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper until a later bounded lane intentionally promotes the validator surface or lands the Zig starter",
}

TEST_FSMOUNT_SURVEY_MARKERS = [
    'test "phase4 test_fsmount survey keeps the parked gap packet explicit" {',
    'test "phase4 test_fsmount survey keeps threshold posture explicit" {',
    'test "phase4 test_fsmount survey keeps reversible-delivery evidence explicit" {',
    'test "phase4 test_fsmount survey keeps the bounded next step explicit" {',
    '\\\"dedicated_linux_style_survey_wrapper\\\": \\\"make -C zigux phase4-test-fsmount-survey\\\"',
    '\\\"threshold_posture\\\": \\\"reviewability_only_no_perf_threshold\\\"',
    '\\\"owner\\\": \\\"Validation and Perf Team\\\"',
]


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def exact_status_line_count(text: str, status_line: str) -> int:
    return sum(1 for line in text.splitlines() if line == f"- `{status_line}`")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing marker: {old}")
    return text.replace(old, new, 1)


def validate_kprobe_packet(root: Path) -> list[str]:
    failures: list[str] = []
    note_path = root / KPROBE_NOTE_REL
    manifest_path = root / KPROBE_MANIFEST_REL
    survey_path = root / KPROBE_SURVEY_REL
    for path in (note_path, manifest_path, survey_path):
        if not path.exists():
            failures.append(f"file:{path.relative_to(root).as_posix()}")
    if failures:
        return failures

    note = read_text(note_path)
    manifest = json.loads(read_text(manifest_path))
    survey = read_text(survey_path)

    for marker in KPROBE_NOTE_MARKERS:
        if marker not in note:
            failures.append(f"kprobe_note:{marker}")

    for key, expected in KPROBE_MANIFEST_EXPECTATIONS.items():
        actual = manifest.get(key)
        if actual != expected:
            failures.append(f"kprobe_manifest:{key}:{actual}:{expected}")

    for marker in KPROBE_SURVEY_MARKERS:
        if marker not in survey:
            failures.append(f"kprobe_survey:{marker}")

    return failures


def validate_test_fsmount_packet(root: Path) -> list[str]:
    failures: list[str] = []
    note_path = root / TEST_FSMOUNT_NOTE_REL
    manifest_path = root / TEST_FSMOUNT_MANIFEST_REL
    survey_path = root / TEST_FSMOUNT_SURVEY_REL
    for path in (note_path, manifest_path, survey_path):
        if not path.exists():
            failures.append(f"file:{path.relative_to(root).as_posix()}")
    if failures:
        return failures

    note = read_text(note_path)
    manifest = json.loads(read_text(manifest_path))
    survey = read_text(survey_path)

    for marker in TEST_FSMOUNT_NOTE_MARKERS:
        if marker not in note:
            failures.append(f"test_fsmount_note:{marker}")

    for key, expected in TEST_FSMOUNT_MANIFEST_EXPECTATIONS.items():
        actual = manifest.get(key)
        if actual != expected:
            failures.append(f"test_fsmount_manifest:{key}:{actual}:{expected}")

    for marker in TEST_FSMOUNT_SURVEY_MARKERS:
        if marker not in survey:
            failures.append(f"test_fsmount_survey:{marker}")

    return failures


def validate_root(root: Path) -> list[str]:
    gate_evidence_path = root / GATE_EVIDENCE_REL
    if not gate_evidence_path.exists():
        return [f"file:{GATE_EVIDENCE_REL.as_posix()}"]

    text = read_text(gate_evidence_path)
    failures: list[str] = []

    for marker in REQUIRED_STATUS_MARKERS:
        if marker not in text:
            failures.append(f"missing_status_marker:{marker}")

    for status_line in EXACT_STATUS_LINES:
        count = exact_status_line_count(text, status_line)
        if count != 1:
            failures.append(f"status_exact_count:{status_line}:{count}")

    for marker in REQUIRED_PROSE_MARKERS:
        if marker not in text:
            failures.append(f"missing_prose_marker:{marker}")

    for marker in REQUIRED_SELF_TEST_CASE_MARKERS:
        if marker not in text:
            failures.append(f"missing_self_test_case:{marker}")

    for key, relative_path in BLOB_TARGETS.items():
        target = root / relative_path
        if not target.exists():
            failures.append(f"file:{relative_path}")
            continue
        digest = git_blob_sha1(target.read_bytes())
        marker = f"- `{key}={digest}`"
        if marker not in text:
            failures.append(f"blob_pin_mismatch:{key}:{digest}")

    failures.extend(validate_kprobe_packet(root))
    failures.extend(validate_test_fsmount_packet(root))
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    for relative_path in BLOB_TARGETS.values():
        write_text(root / relative_path, f"fixture for {relative_path}\n")

    blob_pin_lines = [
        f"- `{key}={git_blob_sha1((root / relative_path).read_bytes())}`"
        for key, relative_path in BLOB_TARGETS.items()
    ]

    gate_evidence = "\n".join(
        [
            "# Phase 4 Gate Evidence",
            "",
            "## Status",
            "- `PHASE4_EVIDENCE_DATE=2026-05-11`",
            "- `PHASE4_EVIDENCE_MODE=github_connector_readback`",
            "- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`",
            "- `PHASE4_EXACT_READBACK_REF=master`",
            *blob_pin_lines,
            f"- `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}`",
            f"- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}`",
            f"- `{SELF_TEST_CASES_LINE}`",
            "- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
            "- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`",
            "- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`",
            f"- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}`",
            (
                "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="
                f"{EXPECTED_SELF_TEST_CASE_COUNT}`"
            ),
            "- `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
            "- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`",
            "- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`",
            "- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`",
            "",
            "## Exact Readback Evidence",
            "- `scripts/zigux/check-phase4-gate-evidence.py` remains the dedicated exact-readback checker for this narrower rollback-ownership packet.",
            "- `zigux/tests/phase4_perf_baseline_manifest.json` and `zigux/tests/phase4_perf_baseline_survey.zig` also remain shipped on `master` as the dedicated local-only perf-baseline posture packet while shared CI perf coverage stays out of scope.",
            "- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` remain the manifest-backed runtime atomic64 survey pair, and `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`, `phase4-runtime-atomic64-diff-survey-tests`, and `phase4-bitmap-live-helper-replay-tests` stay wired through the shared Phase 4 build entrypoint.",
            "- the parked kprobe gap packet at `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig` now also stays under the dedicated exact-readback checker so the current C anchor, direct validation entrypoint, local survey wrapper, owner, rollback owner, and absent-starter boundary fail closed together.",
            "",
            "## Current Conclusion",
            "- shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
            "- `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `Documentation/zigux/phase4-validation-matrix.md` now all mirror that local-only split and the current decision-owner packet: the Validation and Perf Team stays named as the decision owner for any broader shared-CI perf promotion, while the ABI and Runtime Team plus Shared Subsystems Pod stay named as the coordination owners for that policy call.",
        ]
    )
    write_text(root / GATE_EVIDENCE_REL, gate_evidence + "\n")

    write_text(
        root / KPROBE_NOTE_REL,
        """# Phase 4 kprobe_example Gap Survey

## Status
- `PHASE4_KPROBE_STATUS=parked_gap_packet_landed`
- `PHASE4_KPROBE_LANE_KEY=P4-L19`
- `PHASE4_KPROBE_PHASE=Phase 4`
- `PHASE4_KPROBE_C_ANCHOR=samples/kprobes/kprobe_example.c`
- `PHASE4_KPROBE_CURRENT_LINUX_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`
- `PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-example-survey`
- `PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig`
- `PHASE4_KPROBE_OWNER=Validation and Perf Team`
- `PHASE4_KPROBE_ROLLBACK_OWNER=Validation and Perf Team`
- `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, the local survey wrapper, the direct validation entrypoint, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface`

Current `master` still does not ship `samples/zigux/kprobe_example.zig`.
""",
    )

    write_text(
        root / KPROBE_MANIFEST_REL,
        json.dumps(KPROBE_MANIFEST_EXPECTATIONS, indent=2) + "\n",
    )

    write_text(
        root / KPROBE_SURVEY_REL,
        """const std = @import(\"std\");

test \"phase4 kprobe survey keeps the parked gap packet explicit\" {
    _ = std.testing.allocator;
    _ = \"\\\"dedicated_local_survey_wrapper\\\": \\\"make -C zigux phase4-kprobe-example-survey\\\"\";
    _ = \"\\\"validation_entrypoint\\\": \\\"zig test zigux/tests/phase4_kprobe_example_survey.zig\\\"\";
    _ = \"\\\"owner\\\": \\\"Validation and Perf Team\\\"\";
}

test \"phase4 kprobe survey keeps reversible-delivery evidence explicit\" {
    _ = std.testing.allocator;
}

test \"phase4 kprobe survey keeps the bounded next step explicit\" {
    _ = std.testing.allocator;
}
""",
    )

    write_text(
        root / TEST_FSMOUNT_NOTE_REL,
        """# Phase 4 test_fsmount Gap Survey

## Status
- `PHASE4_TEST_FSMOUNT_STATUS=parked_gap_packet_landed`
- `PHASE4_TEST_FSMOUNT_LANE_KEY=P4-L19`
- `PHASE4_TEST_FSMOUNT_PHASE=Phase 4`
- `PHASE4_TEST_FSMOUNT_C_ANCHOR=samples/vfs/test-fsmount.c`
- `PHASE4_TEST_FSMOUNT_CURRENT_LINUX_REPLAY=make M=samples/vfs`
- `PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
- `PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey`
- `PHASE4_TEST_FSMOUNT_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
- `PHASE4_TEST_FSMOUNT_OWNER=Validation and Perf Team`
- `PHASE4_TEST_FSMOUNT_ROLLBACK_OWNER=Validation and Perf Team`
- `PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold`
- `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit bootstrap-CI posture, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface`

Current `master` still does not ship `samples/zigux/test_fsmount.zig`.
This dedicated packet keeps the reviewability-only no-perf-threshold posture explicit.
""",
    )

    write_text(
        root / TEST_FSMOUNT_MANIFEST_REL,
        json.dumps(TEST_FSMOUNT_MANIFEST_EXPECTATIONS, indent=2) + "\n",
    )

    write_text(
        root / TEST_FSMOUNT_SURVEY_REL,
        """const std = @import(\"std\");

test \"phase4 test_fsmount survey keeps the parked gap packet explicit\" {
    _ = std.testing.allocator;
    _ = \"\\\"dedicated_linux_style_survey_wrapper\\\": \\\"make -C zigux phase4-test-fsmount-survey\\\"\";
    _ = \"\\\"threshold_posture\\\": \\\"reviewability_only_no_perf_threshold\\\"\";
    _ = \"\\\"owner\\\": \\\"Validation and Perf Team\\\"\";
}

test \"phase4 test_fsmount survey keeps threshold posture explicit\" {
    _ = std.testing.allocator;
}

test \"phase4 test_fsmount survey keeps reversible-delivery evidence explicit\" {
    _ = std.testing.allocator;
}

test \"phase4 test_fsmount survey keeps the bounded next step explicit\" {
    _ = std.testing.allocator;
}
""",
    )


def expect_failure(
    root: Path,
    gate_evidence_path: Path,
    description: str,
    *,
    exact_failure: str | None = None,
    prefix_failure: str | None = None,
) -> bool:
    failures = validate_root(root)
    if exact_failure is not None and exact_failure not in failures:
        print("PHASE4_GATE_EVIDENCE_SELF_TEST=fail")
        print(f"expected {description} failure: {exact_failure}")
        print("\n".join(failures))
        return False
    if prefix_failure is not None and not any(
        entry.startswith(prefix_failure) for entry in failures
    ):
        print("PHASE4_GATE_EVIDENCE_SELF_TEST=fail")
        print(f"expected {description} failure prefix: {prefix_failure}")
        print("\n".join(failures))
        return False
    return True


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_gate_evidence_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)
        gate_evidence_path = root / GATE_EVIDENCE_REL
        original_note = read_text(gate_evidence_path)

        failures = validate_root(root)
        if failures:
            print("PHASE4_GATE_EVIDENCE_SELF_TEST=fail")
            print("\n".join(failures))
            return 1
        case_count += 1

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                f"PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}",
                f"PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT - 1}",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "shipped target count drift",
            exact_failure=(
                "status_exact_count:"
                f"PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}:0"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(original_note, "## Exact Readback Evidence", "## Readback Evidence"),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "exact readback heading drift",
            exact_failure="missing_prose_marker:## Exact Readback Evidence",
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        validator_path = root / "scripts/zigux/validate-phase4.py"
        original_validator = read_text(validator_path)
        validator_path.write_text("drifted validator fixture\n", encoding="utf-8")
        if not expect_failure(
            root,
            gate_evidence_path,
            "validator blob pin drift",
            prefix_failure="blob_pin_mismatch:PHASE4_VALIDATOR_BLOB_SHA:",
        ):
            return 1
        case_count += 1
        validator_path.write_text(original_validator, encoding="utf-8")

        manifest_path = root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json"
        original_manifest = read_text(manifest_path)
        manifest_path.write_text("manifest drift\n", encoding="utf-8")
        if not expect_failure(
            root,
            gate_evidence_path,
            "runtime manifest blob drift",
            prefix_failure="blob_pin_mismatch:PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA:",
        ):
            return 1
        case_count += 1
        manifest_path.write_text(original_manifest, encoding="utf-8")

        survey_path = root / "zigux/tests/phase4_runtime_atomic64_diff_survey.zig"
        original_survey = read_text(survey_path)
        survey_path.write_text("survey drift\n", encoding="utf-8")
        if not expect_failure(
            root,
            gate_evidence_path,
            "runtime survey blob drift",
            prefix_failure="blob_pin_mismatch:PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA:",
        ):
            return 1
        case_count += 1
        survey_path.write_text(original_survey, encoding="utf-8")

        build_path = root / "zigux/tests/phase4_build.zig"
        original_build = read_text(build_path)
        build_path.write_text("phase4 build drift\n", encoding="utf-8")
        if not expect_failure(
            root,
            gate_evidence_path,
            "phase4 build blob drift",
            prefix_failure="blob_pin_mismatch:PHASE4_BUILD_BLOB_SHA:",
        ):
            return 1
        case_count += 1
        build_path.write_text(original_build, encoding="utf-8")

        checklist_path = root / "Documentation/zigux/review-checklist.md"
        original_checklist = read_text(checklist_path)
        checklist_path.write_text("review checklist drift\n", encoding="utf-8")
        if not expect_failure(
            root,
            gate_evidence_path,
            "review checklist blob drift",
            prefix_failure="blob_pin_mismatch:PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA:",
        ):
            return 1
        case_count += 1
        checklist_path.write_text(original_checklist, encoding="utf-8")

        doc_readme_path = root / "Documentation/zigux/README.md"
        original_doc_readme = read_text(doc_readme_path)
        doc_readme_path.write_text("docs root drift\n", encoding="utf-8")
        if not expect_failure(
            root,
            gate_evidence_path,
            "docs-root README blob drift",
            prefix_failure="blob_pin_mismatch:PHASE4_DOC_README_BLOB_SHA:",
        ):
            return 1
        case_count += 1
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        script_readme_path = root / "scripts/zigux/README.md"
        original_script_readme = read_text(script_readme_path)
        script_readme_path.write_text("scripts root drift\n", encoding="utf-8")
        if not expect_failure(
            root,
            gate_evidence_path,
            "scripts-root README blob drift",
            prefix_failure="blob_pin_mismatch:PHASE4_SCRIPT_README_BLOB_SHA:",
        ):
            return 1
        case_count += 1
        script_readme_path.write_text(original_script_readme, encoding="utf-8")

        tests_readme_path = root / "zigux/tests/README.md"
        original_tests_readme = read_text(tests_readme_path)
        tests_readme_path.write_text("tests root drift\n", encoding="utf-8")
        if not expect_failure(
            root,
            gate_evidence_path,
            "tests-root README blob drift",
            prefix_failure="blob_pin_mismatch:PHASE4_TESTS_README_BLOB_SHA:",
        ):
            return 1
        case_count += 1
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}",
                f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT - 1}",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "self-test count drift",
            exact_failure=(
                "status_exact_count:"
                f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}:0"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                SELF_TEST_CASES_LINE,
                SELF_TEST_CASES_LINE.replace(
                    "missing_note_file", "missing_note_file_drifted", 1
                ),
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "self-test case catalog drift",
            exact_failure=f"status_exact_count:{SELF_TEST_CASES_LINE}:0",
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true",
                "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=false",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "shared validator rerun self-test drift",
            exact_failure=(
                "status_exact_count:PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true:0"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}",
                f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT - 1}",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "shared validator expected target count drift",
            exact_failure=(
                "status_exact_count:"
                f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}:0"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                (
                    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="
                    f"{EXPECTED_SELF_TEST_CASE_COUNT}"
                ),
                (
                    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="
                    f"{EXPECTED_SELF_TEST_CASE_COUNT - 1}"
                ),
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "shared validator expected self-test count drift",
            exact_failure=(
                "status_exact_count:"
                "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="
                f"{EXPECTED_SELF_TEST_CASE_COUNT}:0"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true",
                "PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=false",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "runtime atomic64 survey packet presence drift",
            exact_failure=(
                "status_exact_count:PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true:0"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "phase4-bitmap-live-helper-replay-tests",
                "phase4-bitmap-live-helper-replay-drift",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "bitmap replay marker drift",
            exact_failure="missing_prose_marker:phase4-bitmap-live-helper-replay-tests",
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true",
                "PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "kprobe packet presence drift",
            exact_failure="status_exact_count:PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true:0",
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        kprobe_note_path = root / KPROBE_NOTE_REL
        original_kprobe_note = read_text(kprobe_note_path)
        kprobe_note_path.write_text(
            replace_once(
                original_kprobe_note,
                "PHASE4_KPROBE_OWNER=Validation and Perf Team",
                "PHASE4_KPROBE_OWNER=Tooling and Validation Team",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "kprobe owner drift",
            exact_failure="kprobe_note:PHASE4_KPROBE_OWNER=Validation and Perf Team",
        ):
            return 1
        case_count += 1
        kprobe_note_path.write_text(original_kprobe_note, encoding="utf-8")

        kprobe_manifest_path = root / KPROBE_MANIFEST_REL
        original_kprobe_manifest = json.loads(read_text(kprobe_manifest_path))
        drifted_kprobe_manifest = dict(original_kprobe_manifest)
        drifted_kprobe_manifest["validation_entrypoint"] = "zig build broken-entrypoint"
        kprobe_manifest_path.write_text(
            json.dumps(drifted_kprobe_manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "kprobe validation entrypoint drift",
            prefix_failure="kprobe_manifest:validation_entrypoint:",
        ):
            return 1
        case_count += 1
        kprobe_manifest_path.write_text(
            json.dumps(original_kprobe_manifest, indent=2) + "\n",
            encoding="utf-8",
        )

        kprobe_survey_path = root / KPROBE_SURVEY_REL
        original_kprobe_survey = read_text(kprobe_survey_path)
        kprobe_survey_path.write_text(
            replace_once(
                original_kprobe_survey,
                'test "phase4 kprobe survey keeps the bounded next step explicit" {',
                'test "phase4 kprobe survey drifted next step" {',
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "kprobe next-step drift",
            exact_failure=(
                'kprobe_survey:test "phase4 kprobe survey keeps the bounded next step explicit" {'
            ),
        ):
            return 1
        case_count += 1
        kprobe_survey_path.write_text(original_kprobe_survey, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true",
                "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "perf baseline packet presence drift",
            exact_failure=(
                "status_exact_count:PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true:0"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "shared CI perf coverage stays out of scope.",
                "shared CI perf coverage is promoted here.",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "perf baseline split-marker drift",
            exact_failure="missing_prose_marker:shared CI perf coverage stays out of scope.",
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "Validation and Perf Team stays named as the decision owner",
                "Tooling and Validation Team stays named as the decision owner",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "perf baseline owner drift",
            exact_failure=(
                "missing_prose_marker:Validation and Perf Team stays named as the decision owner"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
                "shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates are promoted.",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "shared perf promotion status drift",
            exact_failure=(
                "missing_prose_marker:shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved."
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true",
                "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "test_fsmount packet presence drift",
            exact_failure=(
                "status_exact_count:PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true:0"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        test_fsmount_note_path = root / TEST_FSMOUNT_NOTE_REL
        original_test_fsmount_note = read_text(test_fsmount_note_path)
        test_fsmount_note_path.write_text(
            replace_once(
                original_test_fsmount_note,
                "PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold",
                "PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=shared_ci_perf_promoted",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "test_fsmount threshold posture drift",
            exact_failure=(
                "test_fsmount_note:PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE="
                "reviewability_only_no_perf_threshold"
            ),
        ):
            return 1
        case_count += 1
        test_fsmount_note_path.write_text(original_test_fsmount_note, encoding="utf-8")

        test_fsmount_manifest_path = root / TEST_FSMOUNT_MANIFEST_REL
        original_test_fsmount_manifest = json.loads(
            read_text(test_fsmount_manifest_path)
        )
        drifted_manifest = dict(original_test_fsmount_manifest)
        drifted_manifest["owner"] = "Tooling and Validation Team"
        test_fsmount_manifest_path.write_text(
            json.dumps(drifted_manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "test_fsmount owner drift",
            prefix_failure="test_fsmount_manifest:owner:",
        ):
            return 1
        case_count += 1
        test_fsmount_manifest_path.write_text(
            json.dumps(original_test_fsmount_manifest, indent=2) + "\n",
            encoding="utf-8",
        )

        drifted_manifest = dict(original_test_fsmount_manifest)
        drifted_manifest["validation_entrypoint"] = "zig build broken-test-fsmount-entrypoint"
        test_fsmount_manifest_path.write_text(
            json.dumps(drifted_manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "test_fsmount validation entrypoint drift",
            prefix_failure="test_fsmount_manifest:validation_entrypoint:",
        ):
            return 1
        case_count += 1
        test_fsmount_manifest_path.write_text(
            json.dumps(original_test_fsmount_manifest, indent=2) + "\n",
            encoding="utf-8",
        )

        drifted_manifest = dict(original_test_fsmount_manifest)
        drifted_manifest["dedicated_linux_style_survey_wrapper"] = "make -C zigux broken-phase4-test-fsmount-survey"
        test_fsmount_manifest_path.write_text(
            json.dumps(drifted_manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "test_fsmount linux-style wrapper drift",
            prefix_failure="test_fsmount_manifest:dedicated_linux_style_survey_wrapper:",
        ):
            return 1
        case_count += 1
        test_fsmount_manifest_path.write_text(
            json.dumps(original_test_fsmount_manifest, indent=2) + "\n",
            encoding="utf-8",
        )

        drifted_manifest = dict(original_test_fsmount_manifest)
        drifted_manifest["next_bounded_evidence_step"] = "drifted next bounded evidence step"
        test_fsmount_manifest_path.write_text(
            json.dumps(drifted_manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "test_fsmount next-step drift",
            prefix_failure="test_fsmount_manifest:next_bounded_evidence_step:",
        ):
            return 1
        case_count += 1
        test_fsmount_manifest_path.write_text(
            json.dumps(original_test_fsmount_manifest, indent=2) + "\n",
            encoding="utf-8",
        )

        gate_evidence_path.unlink()
        if not expect_failure(
            root,
            gate_evidence_path,
            "missing note",
            exact_failure=f"file:{GATE_EVIDENCE_REL.as_posix()}",
        ):
            return 1
        case_count += 1

    if case_count != EXPECTED_SELF_TEST_CASE_COUNT:
        print("PHASE4_GATE_EVIDENCE_SELF_TEST=fail")
        print(
            "unexpected self-test case count "
            f"{case_count} != {EXPECTED_SELF_TEST_CASE_COUNT}"
        )
        return 1

    print("PHASE4_GATE_EVIDENCE_SELF_TEST=pass")
    print(f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 4 gate-evidence note."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in coverage checks in a temporary workspace.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate_root(ROOT)
    if failures:
        print("PHASE4_GATE_EVIDENCE_CHECK=fail")
        print("MISSING_PHASE4_GATE_EVIDENCE_MARKERS_START")
        for item in failures:
            print(item)
        print("MISSING_PHASE4_GATE_EVIDENCE_MARKERS_END")
        return 1

    print("PHASE4_GATE_EVIDENCE_CHECK=pass")
    print(f"PHASE4_GATE_EVIDENCE_BLOB_PIN_COUNT={len(BLOB_TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
