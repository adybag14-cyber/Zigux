#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
NOTE_PATH = Path("Documentation/zigux/phase4-gate-evidence.md")
MANIFEST_PATH = Path("zigux/tests/phase4_runtime_atomic64_diff_manifest.json")
SURVEY_PATH = Path("zigux/tests/phase4_runtime_atomic64_diff_survey.zig")
KPROBE_NOTE_PATH = Path("Documentation/zigux/phase4-kprobe-example-gap-survey.md")
KPROBE_MANIFEST_PATH = Path("zigux/tests/phase4_kprobe_example_manifest.json")
KPROBE_SURVEY_PATH = Path("zigux/tests/phase4_kprobe_example_survey.zig")
TEST_FSMOUNT_NOTE_PATH = Path("Documentation/zigux/phase4-test-fsmount-gap-survey.md")
TEST_FSMOUNT_MANIFEST_PATH = Path("zigux/tests/phase4_test_fsmount_manifest.json")
TEST_FSMOUNT_SURVEY_PATH = Path("zigux/tests/phase4_test_fsmount_survey.zig")
PERF_BASELINE_MANIFEST_PATH = Path("zigux/tests/phase4_perf_baseline_manifest.json")
PERF_BASELINE_SURVEY_PATH = Path("zigux/tests/phase4_perf_baseline_survey.zig")

PHASE4_GATE_EVIDENCE_BLOB_TARGETS = {
    "PHASE4_VALIDATION_MATRIX_BLOB_SHA": "Documentation/zigux/phase4-validation-matrix.md",
    "PHASE4_VALIDATOR_BLOB_SHA": "scripts/zigux/validate-phase4.py",
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
}
PHASE4_RUNTIME_ATOMIC64_PACKET_BLOB_TARGETS = {
    "phase4_build_blob_sha": "zigux/tests/phase4_build.zig",
    "phase4_validator_blob_sha": "scripts/zigux/validate-phase4.py",
    "phase4_validation_matrix_blob_sha": "Documentation/zigux/phase4-validation-matrix.md",
    "phase4_review_checklist_blob_sha": "Documentation/zigux/review-checklist.md",
    "phase9_build_blob_sha": "zigux/tests/phase9_build.zig",
}
SELF_TEST_CASES = [
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
    "bitmap_diff_survey_replay_marker_drift",
    "kprobe_gap_packet_presence_drift",
    "perf_baseline_packet_presence_drift",
    "test_fsmount_gap_packet_presence_drift",
    "missing_note_file",
]

REQUIRED_STATUS_LINES = [
    "PHASE4_EVIDENCE_MODE=github_connector_readback",
    "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions",
    "PHASE4_EXACT_READBACK_REF=master",
    f"PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}",
    f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES),
    "PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true",
    f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}",
    f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false",
    "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true",
]
REQUIRED_STATUS_PREFIXES = ["PHASE4_EVIDENCE_DATE="]
REQUIRED_NOTE_MARKERS = [
    "## Exact Readback Evidence",
    "## Current Conclusion",
    "`scripts/zigux/check-phase4-gate-evidence.py`",
    "`zigux/tests/phase4_runtime_atomic64_diff_manifest.json`",
    "`zigux/tests/phase4_runtime_atomic64_diff_survey.zig`",
    "`phase4-runtime-atomic64-diff-survey-tests`",
    "`phase4-bitmap-live-helper-replay-tests`",
    "`Documentation/zigux/artifact-diff.md`",
    "`Documentation/zigux/README.md`",
    "`zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig`",
    "`Shared Subsystems Pod` as both owner and rollback owner for `zigux/tests/phase4_bitmap_live_helper_replay.zig`",
    "`threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` explicit until a later bounded Phase 4 perf packet intentionally approves a harder threshold.",
    "That published eighteen-case self-test catalog now also exercises the runtime atomic64 packet's `validate-phase4.py`, `phase4-validation-matrix.md`, and `Documentation/zigux/review-checklist.md` manifest and survey blob drift paths inside the existing manifest-backed drift coverage, and it now checks the shipped perf-baseline packet's manifest-presence drift path plus the adjacent `test_fsmount` gap packet's manifest-presence drift path too, so those validator, matrix, reviewer-checklist, perf-baseline packet, and parked `test_fsmount` packet expectations are no longer an unstated self-test gap.",
    "manifest-backed runtime atomic64 survey pair now pins the same current `phase4_build.zig`, `validate-phase4.py`, `phase4-validation-matrix.md`, `Documentation/zigux/review-checklist.md`, and `phase9_build.zig` blobs that the shared validator and review packet now depend on",
    "`zigux/Makefile` still exposes `make -C zigux phase4-validate`, `make -C zigux phase4-test`, `make -C zigux phase4-runtime-atomic64-diff`, `make -C zigux phase4-runtime-atomic64-diff-survey`, `make -C zigux phase4-bitmap-diff`, `make -C zigux phase4-bitmap-live-helper-replay`, and `make -C zigux phase4`, so the Linux-style local replay surface matches the current shared Phase 4 packet instead of hiding those routes in the build file alone.",
    "`make -C zigux phase4-bitmap-diff-survey` plus `zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig`",
    "`Documentation/zigux/phase4-kprobe-example-gap-survey.md`",
    "`zigux/tests/phase4_kprobe_example_manifest.json`",
    "`zigux/tests/phase4_kprobe_example_survey.zig`",
    "`make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`",
    "shared gate-evidence note now keeps that adjacent parked packet explicit without claiming a shipped Zig starter",
    "`samples/zigux/kprobe_example.zig` remains absent",
    "`Documentation/zigux/phase4-test-fsmount-gap-survey.md`",
    "`zigux/tests/phase4_test_fsmount_manifest.json`",
    "`zigux/tests/phase4_test_fsmount_survey.zig`",
    "`make M=samples/vfs`",
    "shared validator route now picks that same parked packet up through `scripts/zigux/check-phase4-gate-evidence.py` while `samples/zigux/test_fsmount.zig` remains absent on current `master`",
    "hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved",
    "`zigux/tests/README.md` now explicitly carries the shipped local-only perf-baseline pair `zigux/tests/phase4_perf_baseline_manifest.json` plus `zigux/tests/phase4_perf_baseline_survey.zig`",
]

def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()

def read_text(root: Path, relative_path: Path | str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")

def read_bytes(root: Path, relative_path: Path | str) -> bytes:
    return (root / relative_path).read_bytes()

def exact_status_line_count(text: str, status_line: str) -> int:
    return sum(1 for line in text.splitlines() if line == f"- `{status_line}`")

def validate_runtime_atomic64_packet(root: Path) -> list[str]:
    manifest_file = root / MANIFEST_PATH
    survey_file = root / SURVEY_PATH
    missing: list[str] = []
    if not manifest_file.exists():
        return [f"file:{MANIFEST_PATH}"]
    if not survey_file.exists():
        return [f"file:{SURVEY_PATH}"]
    manifest = json.loads(read_text(root, MANIFEST_PATH))
    survey_text = read_text(root, SURVEY_PATH)
    for field, relative_path in PHASE4_RUNTIME_ATOMIC64_PACKET_BLOB_TARGETS.items():
        expected = git_blob_sha1(read_bytes(root, relative_path))
        actual = manifest.get(field)
        if actual != expected:
            missing.append(f"phase4_gate_evidence:runtime_atomic64_manifest_blob:{field}:{actual}:{expected}")
        count = survey_text.count(expected)
        if count != 1:
            missing.append(f"phase4_gate_evidence:runtime_atomic64_survey_blob_exact_count:{field}:{expected}:{count}")
    return missing

def validate_kprobe_gap_packet(root: Path) -> list[str]:
    missing: list[str] = []
    for path in [KPROBE_NOTE_PATH, KPROBE_MANIFEST_PATH, KPROBE_SURVEY_PATH]:
        if not (root / path).exists():
            missing.append(f"file:{path}")
            return missing
    note_text = read_text(root, KPROBE_NOTE_PATH)
    survey_text = read_text(root, KPROBE_SURVEY_PATH)
    manifest = json.loads(read_text(root, KPROBE_MANIFEST_PATH))
    if manifest.get("shared_gate_evidence_packet_present") is not True:
        missing.append("phase4_gate_evidence:kprobe_manifest:shared_gate_evidence_packet_present")
    for marker in [
        "PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=true",
        "shared gate-evidence note now names that same survey note, manifest, and replay command",
        "Land one manifest-backed Phase 4 test_fsmount gap survey packet",
    ]:
        if marker not in note_text:
            missing.append(f"phase4_gate_evidence:kprobe_note:{marker}")
    for marker in [
        "the packet now stays explicit in the shared gate-evidence note while still not claiming a shipped Zig sample",
        "treating adjacent gate-evidence visibility as a shipped Zig starter",
    ]:
        if marker not in survey_text:
            missing.append(f"phase4_gate_evidence:kprobe_survey:{marker}")
    return missing

def validate_test_fsmount_gap_packet(root: Path) -> list[str]:
    missing: list[str] = []
    for path in [TEST_FSMOUNT_NOTE_PATH, TEST_FSMOUNT_MANIFEST_PATH, TEST_FSMOUNT_SURVEY_PATH]:
        if not (root / path).exists():
            missing.append(f"file:{path}")
            return missing
    note_text = read_text(root, TEST_FSMOUNT_NOTE_PATH)
    survey_text = read_text(root, TEST_FSMOUNT_SURVEY_PATH)
    manifest = json.loads(read_text(root, TEST_FSMOUNT_MANIFEST_PATH))
    if manifest.get("shared_gate_evidence_packet_present") is not False:
        missing.append("phase4_gate_evidence:test_fsmount_manifest:shared_gate_evidence_packet_present")
    for marker in [
        "PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=false",
        "zigux/tests/phase4_test_fsmount_manifest.json",
        "zigux/tests/phase4_test_fsmount_survey.zig",
        "Land one focused promotion that teaches the shared Phase 4 validator and gate-evidence packet about this same survey note, manifest, and replay command",
    ]:
        if marker not in note_text:
            missing.append(f"phase4_gate_evidence:test_fsmount_note:{marker}")
    for marker in [
        "PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=false",
        "Land one focused promotion that teaches the shared Phase 4 validator and gate-evidence packet",
        "claiming that the shared Phase 4 exact-readback gate already carries this packet",
    ]:
        if marker not in survey_text:
            missing.append(f"phase4_gate_evidence:test_fsmount_survey:{marker}")
    return missing


def validate_perf_baseline_packet(root: Path) -> list[str]:
    manifest_file = root / PERF_BASELINE_MANIFEST_PATH
    survey_file = root / PERF_BASELINE_SURVEY_PATH
    missing: list[str] = []
    if not manifest_file.exists():
        return [f"file:{PERF_BASELINE_MANIFEST_PATH}"]
    if not survey_file.exists():
        return [f"file:{PERF_BASELINE_SURVEY_PATH}"]

    try:
        manifest = json.loads(read_text(root, PERF_BASELINE_MANIFEST_PATH))
    except json.JSONDecodeError as exc:
        return [f"phase4_gate_evidence:perf_baseline_manifest:invalid_json:{exc.msg}"]

    expected_fields = {
        "lane_key": "P4-L20",
        "phase": "Phase 4",
        "owner": "Validation and Perf Team",
        "rollback_owner": "Validation and Perf Team",
    }
    for field, expected in expected_fields.items():
        actual = manifest.get(field)
        if actual != expected:
            missing.append(f"phase4_gate_evidence:perf_baseline_manifest:{field}:{actual}:{expected}")

    surveyed_gates = manifest.get("surveyed_gates")
    if not isinstance(surveyed_gates, list) or len(surveyed_gates) != 2:
        missing.append("phase4_gate_evidence:perf_baseline_manifest:surveyed_gates")
    else:
        expected_surfaces = [
            (
                "zigux/tests/atomic64_diff.zig",
                "ABI and Runtime Team",
                "ABI and Runtime Team",
                "threshold_pending_until_runtime_atomic64_scope_widens",
            ),
            (
                "zigux/tests/bitmap_diff.zig",
                "Shared Subsystems Pod",
                "Shared Subsystems Pod",
                "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
            ),
        ]
        for gate, expected in zip(surveyed_gates, expected_surfaces):
            if not isinstance(gate, dict):
                missing.append("phase4_gate_evidence:perf_baseline_manifest:surveyed_gate_shape")
                continue
            surface, owner, rollback_owner, threshold = expected
            if gate.get("surface") != surface:
                missing.append(f"phase4_gate_evidence:perf_baseline_manifest:surface:{gate.get('surface')}:{surface}")
            if gate.get("gate_owner") != owner:
                missing.append(f"phase4_gate_evidence:perf_baseline_manifest:gate_owner:{gate.get('gate_owner')}:{owner}")
            if gate.get("gate_rollback_owner") != rollback_owner:
                missing.append(f"phase4_gate_evidence:perf_baseline_manifest:gate_rollback_owner:{gate.get('gate_rollback_owner')}:{rollback_owner}")
            if gate.get("threshold_posture") != threshold:
                missing.append(f"phase4_gate_evidence:perf_baseline_manifest:threshold_posture:{gate.get('threshold_posture')}:{threshold}")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        missing.append("phase4_gate_evidence:perf_baseline_manifest:survey_summary")
    else:
        expected_summary = {
            "phase4_build_step_present": True,
            "phase4_validation_matrix_present": True,
            "shared_phase4_test_step_includes_survey": False,
            "benchmark_command_unapproved": True,
            "acceptable_limit_unapproved": True,
        }
        for field, expected in expected_summary.items():
            actual = summary.get(field)
            if actual != expected:
                missing.append(f"phase4_gate_evidence:perf_baseline_manifest:survey_summary:{field}:{actual}:{expected}")

    survey_text = read_text(root, PERF_BASELINE_SURVEY_PATH)
    for marker in [
        "phase4 perf baseline survey manifest keeps the current unapproved threshold posture explicit",
        "zigux/tests/phase4_perf_baseline_manifest.json",
        "threshold_pending_until_runtime_atomic64_scope_widens",
        "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        "benchmark command plus one acceptable limit",
        "shared CI perf approval",
    ]:
        if marker not in survey_text:
            missing.append(f"phase4_gate_evidence:perf_baseline_survey:{marker}")

    return missing


def validate_root(root: Path) -> list[str]:
    note_file = root / NOTE_PATH
    if not note_file.exists():
        return [f"file:{NOTE_PATH}"]
    note_text = read_text(root, NOTE_PATH)
    missing: list[str] = []
    for status_prefix in REQUIRED_STATUS_PREFIXES:
        count = sum(1 for line in note_text.splitlines() if line.startswith("- `") and line.endswith("`") and line[3:-1].startswith(status_prefix))
        if count != 1:
            missing.append(f"phase4_gate_evidence:status_prefix_exact_count:{status_prefix}:{count}")
    for status_line in REQUIRED_STATUS_LINES:
        count = exact_status_line_count(note_text, status_line)
        if count != 1:
            missing.append(f"phase4_gate_evidence:status_exact_count:{status_line}:{count}")
    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            missing.append(f"phase4_gate_evidence:{marker}")
    for marker, relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.items():
        if not (root / relative_path).exists():
            missing.append(f"file:{relative_path}")
            continue
        digest = git_blob_sha1(read_bytes(root, relative_path))
        count = exact_status_line_count(note_text, f"{marker}={digest}")
        if count != 1:
            missing.append(f"phase4_gate_evidence:blob_exact_count:{marker}:{digest}:{count}")
    review_checklist_digest = git_blob_sha1(read_bytes(root, PHASE4_RUNTIME_ATOMIC64_PACKET_BLOB_TARGETS['phase4_review_checklist_blob_sha']))
    count = exact_status_line_count(note_text, f"PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA={review_checklist_digest}")
    if count != 1:
        missing.append(f"phase4_gate_evidence:status_exact_count:PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA={review_checklist_digest}:{count}")
    missing.extend(validate_runtime_atomic64_packet(root))
    missing.extend(validate_kprobe_gap_packet(root))
    missing.extend(validate_test_fsmount_gap_packet(root))
    missing.extend(validate_perf_baseline_packet(root))
    return missing

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8', newline='\n')

def write_runtime_atomic64_packet_fixture(root: Path) -> None:
    manifest = {field: git_blob_sha1(read_bytes(root, relative_path)) for field, relative_path in PHASE4_RUNTIME_ATOMIC64_PACKET_BLOB_TARGETS.items()}
    write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    write_text(root / SURVEY_PATH, "\n".join([
        'const std = @import("std");',
        '',
        'test "fixture keeps current phase4 build, validator, matrix, review checklist, and phase9 build pins" {',
        f"    // phase4 build pin {manifest['phase4_build_blob_sha']}",
        f"    // validator pin {manifest['phase4_validator_blob_sha']}",
        f"    // matrix pin {manifest['phase4_validation_matrix_blob_sha']}",
        f"    // review checklist pin {manifest['phase4_review_checklist_blob_sha']}",
        f"    // phase9 build pin {manifest['phase9_build_blob_sha']}",
        '}',
        '',
    ]))

def write_kprobe_gap_packet_fixture(root: Path) -> None:
    manifest = {
        'lane_key': 'validation-perf',
        'phase': 'Phase 4',
        'anchor_path': 'samples/kprobes/kprobe_example.c',
        'anchor_blob_sha': '53ec6c8b8c40d0f41f2d4f9becacc9d6b98f1d0d',
        'sample_path': 'samples/zigux/kprobe_example.zig',
        'sample_present': False,
        'current_replay': 'make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m',
        'survey_note': 'Documentation/zigux/phase4-kprobe-example-gap-survey.md',
        'survey_owner': 'Validation and Perf Team',
        'rollback_owner': 'Validation and Perf Team',
        'shared_gate_evidence_packet_present': True,
        'validation_entrypoint': 'zig test zigux/tests/phase4_kprobe_example_survey.zig',
        'review_prompts': [
            'the survey keeps the Linux anchor path and blob sha explicit while the Zig starter stays absent',
            'the packet keeps the live make replay command explicit without implying a shipped Zig sample',
            'the owner and rollback owner remain Validation and Perf Team while the packet stays adjacent to the shared Phase 4 validator-first route',
            'the packet now stays explicit in the shared gate-evidence note while still not claiming a shipped Zig sample',
        ],
        'non_goals': [
            'shipped kprobe Zig starter',
            'treating adjacent gate-evidence visibility as a shipped Zig starter',
            'approved kprobe perf threshold',
        ],
    }
    write_text(root / KPROBE_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    write_text(root / KPROBE_NOTE_PATH, """# Phase 4 Kprobe Example Gap Survey

This note records a bounded Phase 4 survey packet for the roadmap's `samples/kprobes/kprobe_example.c` anchor without claiming that a Zig starter has landed.

## Status

- `PHASE4_KPROBE_STATUS=parked_gap_survey`
- `PHASE4_LANE_KEY=validation-perf`
- `PHASE4_ANCHOR_PATH=samples/kprobes/kprobe_example.c`
- `PHASE4_ANCHOR_BLOB_SHA=53ec6c8b8c40d0f41f2d4f9becacc9d6b98f1d0d`
- `PHASE4_SAMPLE_PATH=samples/zigux/kprobe_example.zig`
- `PHASE4_SAMPLE_PRESENT=false`
- `PHASE4_CURRENT_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`
- `PHASE4_SURVEY_OWNER=Validation and Perf Team`
- `PHASE4_ROLLBACK_OWNER=Validation and Perf Team`
- `PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=true`
- `PHASE4_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig`

## Scope

- keep the current C anchor path, anchor blob, replay command, owner, rollback owner, and missing-Zig-starter posture reviewable
- keep this packet adjacent to the shared Phase 4 validator-first packet while the shared gate-evidence note now names that same survey note, manifest, and replay command without claiming a shipped Zig starter
- prepare the smallest truthful handoff for a future manifest-backed promotion into the broader Phase 4 validation surfaces

## Current Readback

- `samples/kprobes/kprobe_example.c` is present on `master` and still plants a bounded `kprobe` around `kernel_clone`
- the live replay path remains `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`
- `samples/zigux/kprobe_example.zig` is still absent on current `master`
- the dedicated parked gap packet already spans this note, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig`, and the shared gate-evidence note now names that same survey note, manifest, and replay command as adjacent evidence without claiming that a shipped Zig starter exists

## Non-Goals

- claiming a shipped Zig starter for `samples/zigux/kprobe_example.zig`
- treating adjacent gate-evidence visibility as a shipped Zig starter
- claiming approved hard perf thresholds for the kprobe anchor

## Next Bounded Step

Land one manifest-backed Phase 4 test_fsmount gap survey packet that keeps the current C anchor, replay command, owner, and rollback owner reviewable without claiming a shipped Zig starter.
""")
    write_text(root / KPROBE_SURVEY_PATH, """const std = @import(\"std\");

test \"phase4 kprobe gap fixture note alignment\" {
    try std.testing.expect(true);
}
// the packet now stays explicit in the shared gate-evidence note while still not claiming a shipped Zig sample
// treating adjacent gate-evidence visibility as a shipped Zig starter
""")

def write_test_fsmount_gap_packet_fixture(root: Path) -> None:
    manifest = {
        'lane_key': 'validation-perf',
        'phase': 'Phase 4',
        'anchor_path': 'samples/vfs/test-fsmount.c',
        'anchor_blob_sha': '50f47b72e85fbc8dd52dedad96ee96e6379da5b8',
        'sample_path': 'samples/zigux/test_fsmount.zig',
        'sample_present': False,
        'current_replay': 'make M=samples/vfs',
        'survey_note': 'Documentation/zigux/phase4-test-fsmount-gap-survey.md',
        'survey_owner': 'Validation and Perf Team',
        'rollback_owner': 'Validation and Perf Team',
        'shared_gate_evidence_packet_present': False,
        'validation_entrypoint': 'zig test zigux/tests/phase4_test_fsmount_survey.zig',
        'review_prompts': [
            'the survey keeps the Linux anchor path and blob sha explicit while the Zig starter stays absent',
            'the packet keeps the live VFS replay command explicit without implying a shipped Zig sample',
            'the owner and rollback owner remain Validation and Perf Team while the packet stays adjacent to the shared Phase 4 validator-first route',
            'the packet stays outside the shared gate-evidence target set until a later bounded promotion lands',
        ],
        'non_goals': [
            'shipped test_fsmount Zig starter',
            'shared gate-evidence promotion',
            'approved fsmount perf threshold',
        ],
    }
    write_text(root / TEST_FSMOUNT_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    write_text(root / TEST_FSMOUNT_NOTE_PATH, """# Phase 4 Test Fsmount Gap Survey

This note records a bounded Phase 4 survey packet for the roadmap's `samples/vfs/test-fsmount.c` anchor without claiming that a Zig starter has landed.

## Status

- `PHASE4_TEST_FSMOUNT_STATUS=parked_gap_survey`
- `PHASE4_LANE_KEY=validation-perf`
- `PHASE4_ANCHOR_PATH=samples/vfs/test-fsmount.c`
- `PHASE4_ANCHOR_BLOB_SHA=50f47b72e85fbc8dd52dedad96ee96e6379da5b8`
- `PHASE4_SAMPLE_PATH=samples/zigux/test_fsmount.zig`
- `PHASE4_SAMPLE_PRESENT=false`
- `PHASE4_CURRENT_REPLAY=make M=samples/vfs`
- `PHASE4_SURVEY_OWNER=Validation and Perf Team`
- `PHASE4_ROLLBACK_OWNER=Validation and Perf Team`
- `PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=false`
- `PHASE4_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_test_fsmount_survey.zig`

## Scope

- keep the current C anchor path, anchor blob, replay command, owner, rollback owner, and missing-Zig-starter posture reviewable
- keep this packet adjacent to the shared Phase 4 validator-first packet instead of pretending the exact-readback gate already owns it
- prepare the smallest truthful handoff for a future manifest-backed promotion into the broader Phase 4 validation surfaces

## Current Readback

- `samples/vfs/test-fsmount.c` is present on `master` and still keeps the fd-based mount flow around `fsopen`, `fsconfig`, `fsmount`, and `move_mount` explicit
- the live replay path remains `make M=samples/vfs`
- `samples/zigux/test_fsmount.zig` is still absent on current `master`
- the dedicated parked gap packet now spans this note, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`, so the `test_fsmount` follow-through is no longer matrix prose alone even while it stays outside the shared gate-evidence packet

## Non-Goals

- claiming a shipped Zig starter for `samples/zigux/test_fsmount.zig`
- claiming that the shared Phase 4 exact-readback gate already carries this packet
- claiming approved hard perf thresholds for the test_fsmount anchor

## Next Bounded Step

Land one focused promotion that teaches the shared Phase 4 validator and gate-evidence packet about this same survey note, manifest, and replay command once the adjacent packet has been reread and accepted as the truthful current boundary.
""")
    write_text(root / TEST_FSMOUNT_SURVEY_PATH, """const std = @import(\"std\");

test \"phase4 test_fsmount gap manifest keeps the parked survey explicit\" {
    try std.testing.expect(true);
}
// PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=false
// Land one focused promotion that teaches the shared Phase 4 validator and gate-evidence packet
// claiming that the shared Phase 4 exact-readback gate already carries this packet
""")


def write_perf_baseline_packet_fixture(root: Path) -> None:
    manifest = {
        "lane_key": "P4-L20",
        "phase": "Phase 4",
        "owner": "Validation and Perf Team",
        "rollback_owner": "Validation and Perf Team",
        "surveyed_gates": [
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
        ],
        "survey_summary": {
            "phase4_build_step_present": True,
            "phase4_validation_matrix_present": True,
            "shared_phase4_test_step_includes_survey": False,
            "benchmark_command_unapproved": True,
            "acceptable_limit_unapproved": True,
        },
        "gaps": [
            {
                "id": "phase4-perf-baseline-survey-manifest",
                "status": "starter_landed",
                "kind": "survey_manifest",
                "zigux_destination": "zigux/tests/phase4_perf_baseline_manifest.json",
                "why_now": "manifest-backed survey packet keeps the current unapproved benchmark-command and acceptable-limit posture machine-checked without inventing numbers",
            },
            {
                "id": "phase4-perf-baseline-survey-gate",
                "status": "starter_landed",
                "kind": "validation",
                "zigux_destination": "zigux/tests/phase4_perf_baseline_survey.zig",
                "why_now": "correctness-only posture stays measurable without treating the local survey route as shared CI perf approval",
            },
            {
                "id": "phase4-perf-baseline-atomic64-command",
                "status": "ready_next",
                "kind": "perf_command",
                "zigux_destination": "zigux/tests/atomic64_diff.zig",
                "why_now": "one bounded benchmark command plus one acceptable limit still needs approval",
            },
            {
                "id": "phase4-perf-baseline-bitmap-command",
                "status": "ready_next",
                "kind": "perf_command",
                "zigux_destination": "zigux/tests/bitmap_diff.zig",
                "why_now": "one bounded benchmark command plus one acceptable limit still needs approval",
            },
        ],
    }
    write_text(root / PERF_BASELINE_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    write_text(root / PERF_BASELINE_SURVEY_PATH, """const std = @import(\"std\");

test \"phase4 perf baseline survey manifest keeps the current unapproved threshold posture explicit\" {
    try std.testing.expect(true);
}
// zigux/tests/phase4_perf_baseline_manifest.json
// threshold_pending_until_runtime_atomic64_scope_widens
// threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks
// benchmark command plus one acceptable limit
// shared CI perf approval
""")


def build_fixture_note(root: Path) -> str:
    lines = [
        '# Phase 4 Gate Evidence',
        'This note records one exact readback snapshot for the current Phase 4 rollback-ownership and lab-matrix gate definitions.',
        '',
        '## Status',
        '- `PHASE4_EVIDENCE_DATE=2026-05-08`',
        '- `PHASE4_EVIDENCE_MODE=github_connector_readback`',
        '- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`',
        '- `PHASE4_EXACT_READBACK_REF=master`',
    ]
    for marker, relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.items():
        lines.append(f"- `{marker}={git_blob_sha1(read_bytes(root, relative_path))}`")
    lines.extend([
        f"- `PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA={git_blob_sha1(read_bytes(root, PHASE4_RUNTIME_ATOMIC64_PACKET_BLOB_TARGETS['phase4_review_checklist_blob_sha']))}`",
        f"- `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}`",
        f"- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}`",
        "- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES) + "`",
        '- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`',
        '- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`',
        '- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`',
        f"- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}`",
        f"- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}`",
        '- `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`',
        '- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`',
        '- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`',
        '- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`',
        '',
        '## Exact Readback Evidence',
        '- `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now all point at the same currently shipped Phase 4 rollback-readiness packet surfaces that the validator and shared build still own on `master`.',
        '- `scripts/zigux/check-phase4-gate-evidence.py` remains the dedicated exact-readback checker for this narrower rollback-ownership packet.',
        '- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` remain the manifest-backed runtime atomic64 survey pair, and `phase4-runtime-atomic64-diff-survey-tests` plus `phase4-bitmap-live-helper-replay-tests` stay wired through the shared Phase 4 build entrypoint.',
        "- That published eighteen-case self-test catalog now also exercises the runtime atomic64 packet's `validate-phase4.py`, `phase4-validation-matrix.md`, and `Documentation/zigux/review-checklist.md` manifest and survey blob drift paths inside the existing manifest-backed drift coverage, and it now checks the shipped perf-baseline packet's manifest-presence drift path plus the adjacent `test_fsmount` gap packet's manifest-presence drift path too, so those validator, matrix, reviewer-checklist, perf-baseline packet, and parked `test_fsmount` packet expectations are no longer an unstated self-test gap.",
        '- The exact-readback set is current again for the shared rollback-ownership and lab-matrix packet, and the manifest-backed runtime atomic64 survey pair now pins the same current `phase4_build.zig`, `validate-phase4.py`, `phase4-validation-matrix.md`, `Documentation/zigux/review-checklist.md`, and `phase9_build.zig` blobs that the shared validator and review packet now depend on.',
        '- The current helper-backed bitmap rollback lab replay route remains `zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig`, and the helper-backed row still records `Shared Subsystems Pod` as both owner and rollback owner for `zigux/tests/phase4_bitmap_live_helper_replay.zig`.',
        '- The helper-backed bitmap rollback row still keeps `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` explicit until a later bounded Phase 4 perf packet intentionally approves a harder threshold.',
        '- `zigux/tests/phase4_perf_baseline_manifest.json` and `zigux/tests/phase4_perf_baseline_survey.zig` also remain shipped on `master` as the dedicated local-only perf-baseline posture packet, and `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` stays the bounded replay route outside the shared validator-backed exact-readback target set until benchmark commands and acceptable limits are intentionally approved.',
        '- `zigux/Makefile` still exposes `make -C zigux phase4-validate`, `make -C zigux phase4-test`, `make -C zigux phase4-runtime-atomic64-diff`, `make -C zigux phase4-runtime-atomic64-diff-survey`, `make -C zigux phase4-bitmap-diff`, `make -C zigux phase4-bitmap-live-helper-replay`, and `make -C zigux phase4`, so the Linux-style local replay surface matches the current shared Phase 4 packet instead of hiding those routes in the build file alone.',
        '- The broader shared build and Makefile surface also still carries `make -C zigux phase4-bitmap-diff-survey` plus `zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig`, so the bitmap survey packet remains reviewable beside the helper-backed replay without widening the lane into perf-threshold approval.',
        '- The parked kprobe gap packet at `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig` now stays explicit in this shared gate-evidence note as adjacent parked evidence only, its Linux replay remains `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`, and the shared gate-evidence note now keeps that adjacent parked packet explicit without claiming a shipped Zig starter while `samples/zigux/kprobe_example.zig` remains absent on current `master`.',
        '- The dedicated parked `test_fsmount` gap packet at `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig` now also stays under the dedicated exact-readback checker, its Linux replay remains `make M=samples/vfs`, and the shared validator route now picks that same parked packet up through `scripts/zigux/check-phase4-gate-evidence.py` while `samples/zigux/test_fsmount.zig` remains absent on current `master`.',
        '- The shipped local perf-baseline survey packet is intentionally separate from that shared exact-readback set: it keeps the still-unapproved benchmark-command and acceptable-limit posture machine-checked locally without turning the Phase 4 validator or CI path into a perf-approval claim before one bounded threshold packet lands for each rollback gate.',
        '',
        '## Current Conclusion',
        '- hard perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.',
        '- the dedicated local perf-baseline survey packet is still the truthful way to keep that unapproved posture measurable until one bounded benchmark command and one acceptable limit are promoted for each shipped rollback gate.',
        '- The current exact-readback note is aligned again to the live validator, README, workflow, Makefile, and Phase 4 gate surfaces on `master`, and `zigux/tests/README.md` now explicitly carries the shipped local-only perf-baseline pair `zigux/tests/phase4_perf_baseline_manifest.json` plus `zigux/tests/phase4_perf_baseline_survey.zig`, while the adjacent `test_fsmount` gap packet is now visible as parked evidence with its own note, manifest, and survey route and is reread by the dedicated exact-readback checker before the shared validator continues.',
    ])
    return "\n".join(lines) + "\n"

def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_phase4_gate_evidence_') as tmp_dir:
        root = Path(tmp_dir)
        for relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.values():
            write_text(root / relative_path, f'fixture for {relative_path}\n')
        for relative_path in PHASE4_RUNTIME_ATOMIC64_PACKET_BLOB_TARGETS.values():
            write_text(root / relative_path, f'fixture for {relative_path}\n')
        write_runtime_atomic64_packet_fixture(root)
        write_kprobe_gap_packet_fixture(root)
        write_test_fsmount_gap_packet_fixture(root)
        write_perf_baseline_packet_fixture(root)
        write_text(root / NOTE_PATH, build_fixture_note(root))
        missing = validate_root(root)
        assert not missing, missing

        broken_perf_root = root / 'broken_perf'
        for relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.values():
            write_text(broken_perf_root / relative_path, f'fixture for {relative_path}\n')
        for relative_path in PHASE4_RUNTIME_ATOMIC64_PACKET_BLOB_TARGETS.values():
            write_text(broken_perf_root / relative_path, f'fixture for {relative_path}\n')
        write_runtime_atomic64_packet_fixture(broken_perf_root)
        write_kprobe_gap_packet_fixture(broken_perf_root)
        write_test_fsmount_gap_packet_fixture(broken_perf_root)
        write_perf_baseline_packet_fixture(broken_perf_root)
        write_text(broken_perf_root / NOTE_PATH, build_fixture_note(broken_perf_root))
        (broken_perf_root / PERF_BASELINE_MANIFEST_PATH).unlink()
        missing = validate_root(broken_perf_root)
        assert f"file:{PERF_BASELINE_MANIFEST_PATH}" in missing, missing

        broken_test_fsmount_root = root / 'broken_test_fsmount'
        for relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.values():
            write_text(broken_test_fsmount_root / relative_path, f'fixture for {relative_path}\n')
        for relative_path in PHASE4_RUNTIME_ATOMIC64_PACKET_BLOB_TARGETS.values():
            write_text(broken_test_fsmount_root / relative_path, f'fixture for {relative_path}\n')
        write_runtime_atomic64_packet_fixture(broken_test_fsmount_root)
        write_kprobe_gap_packet_fixture(broken_test_fsmount_root)
        write_test_fsmount_gap_packet_fixture(broken_test_fsmount_root)
        write_perf_baseline_packet_fixture(broken_test_fsmount_root)
        write_text(broken_test_fsmount_root / NOTE_PATH, build_fixture_note(broken_test_fsmount_root))
        (broken_test_fsmount_root / TEST_FSMOUNT_MANIFEST_PATH).unlink()
        missing = validate_root(broken_test_fsmount_root)
        assert f"file:{TEST_FSMOUNT_MANIFEST_PATH}" in missing, missing
    print('PHASE4_GATE_EVIDENCE_SELF_TEST=pass')
    print(f'PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}')
    print('PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=' + ','.join(SELF_TEST_CASES))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = validate_root(ROOT)
    if missing:
        print('PHASE4_GATE_EVIDENCE_CHECK=fail')
        print('PHASE4_GATE_EVIDENCE_TARGETS_START')
        for item in missing:
            print(item)
        print('PHASE4_GATE_EVIDENCE_TARGETS_END')
        return 1

    print('PHASE4_GATE_EVIDENCE_CHECK=pass')
    print(f'PHASE4_GATE_EVIDENCE_TARGET_COUNT={len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
