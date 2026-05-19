#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path(__file__).resolve().parent

FILES = [
    "Documentation/zigux/phase10-virtio-input-slice.md",
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_build.zig",
]

SLICE_MARKERS = [
    "# Phase 10 Virtio Input Slice",
    "scripts/zigux/check-phase10-input-packet.py",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "queued status completions are reclaimed only in memory",
    "teardown-reset parity explicit across reset",
]

MODULE_MARKERS = [
    "# Phase 10 Virtio Input Module Slice",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "queued status completions reclaimable in memory",
    "wrapper-facing verify coverage still proves queue-callback ordering, registration prerequisites, and teardown-reset parity across reset without widening into transport-backed queue execution or freeze, restore, or remove lifecycle claims",
    "registration lifecycle closure, freeze, restore, remove, and broader transport-backed lifecycle work remain outside this module slice",
]

SURVEY_NOTE_MARKERS = [
    "# Phase 10 Virtio Input Survey",
    "PHASE10_STATUS=parked",
    "PHASE10_LANE_KEY=P10-L13",
    "PHASE10_SURVEYED_COMMIT=",
    "PHASE10_DUAL_IMPLEMENTATION_POSTURE=blocked_on_risky_transport",
    "roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`",
    "drivers/virtio/virtio_input_verify.zig",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "Current `master` keeps this input lane reviewable through the bounded helper packet:",
    "Do not claim a transport-backed Phase 10 input compile or lifecycle replay from this survey until the risky transport bridge itself changes.",
    "wrapper-facing teardown-reset verify parity stays explicit across reset",
]

MANIFEST_MARKERS = [
    '"lane_key": "P10-L13"',
    '"surveyed_commit": "',
    '"roadmap_destinations": [',
    '"drivers/virtio/*.zig"',
    '"zigux/kernel/"',
    '"zigux/helpers/"',
    '"risky_transport_posture": "blocked_on_risky_transport"',
    '"id": "phase10-virtio-input-survey-gate"',
    '"zigux_destination": "zigux/tests/phase10_virtio_input_survey.zig"',
    '"id": "phase10-virtio-input-verify-replay"',
    '"zigux_destination": "drivers/virtio/virtio_input_verify.zig"',
    "teardown-reset parity across reset explicit without widening into transport-backed queue execution or freeze, restore, or remove lifecycle claims",
    '"id": "phase10-virtio-input-queue-callback-preflight-helper"',
    '"zigux_destination": "drivers/virtio/virtio_input_queue_callback_preflight.zig"',
    '"id": "phase10-virtio-input-registration-preflight-helper"',
    '"zigux_destination": "drivers/virtio/virtio_input_registration_preflight.zig"',
    '"id": "phase10-virtio-input-status-drain-helper"',
    '"zigux_destination": "drivers/virtio/virtio_input_status_drain.zig"',
    '"id": "phase10-virtio-input-teardown-observation-helper"',
    '"zigux_destination": "drivers/virtio/virtio_input_teardown_observation.zig"',
    '"id": "phase10-virtio-input-registration-lifecycle"',
    '"status": "blocked_on_risky_transport"',
]

INPUT_HELPER_MARKERS = [
    "pub const QueuePlanSummary = struct {",
    "pub const StatusDrainSummary = struct {",
    "pub const RegistrationPreflightSummary = struct {",
    "pub const QueueCallbackPreflightSummary = struct {",
    "pub const ProbePreflightSummary = struct {",
    "pub const TeardownObservationSummary = struct {",
    "pub fn fillEventBuffers(self: *Self) !QueuePlanSummary {",
    "pub fn queueCallbackPreflightSummary(self: *const Self) QueueCallbackPreflightSummary {",
    "pub fn registrationPreflightSummary(self: *const Self) RegistrationPreflightSummary {",
    "pub fn probePreflightSummary(self: *const Self) ProbePreflightSummary {",
    "pub fn teardownObservationSummary(self: *const Self) TeardownObservationSummary {",
    "pub fn drainStatusQueue(self: *Self, completed_count: usize) !StatusDrainSummary {",
]

PROBE_HELPER_MARKERS = [
    "pub const ProbePreflightSummary = virtio_input.ProbePreflightSummary;",
    "pub const ProbePreflightBlocker = virtio_input.ProbePreflightBlocker;",
    "pub fn summarize(device: *const virtio_input.VirtioInputLab) ProbePreflightSummary {",
    "pub fn blockerTag(blocker: ProbePreflightBlocker) []const u8 {",
]

QUEUE_CALLBACK_HELPER_MARKERS = [
    "pub const QueueCallbackPreflightSummary = virtio_input.QueueCallbackPreflightSummary;",
    "pub const QueueCallbackPreflightBlocker = virtio_input.QueueCallbackPreflightBlocker;",
    "pub fn summarize(device: *const virtio_input.VirtioInputLab) QueueCallbackPreflightSummary {",
    "return device.queueCallbackPreflightSummary();",
    "pub fn blockerTag(blocker: QueueCallbackPreflightBlocker) []const u8 {",
]

REGISTRATION_HELPER_MARKERS = [
    "pub const RegistrationPreflightSummary = virtio_input.RegistrationPreflightSummary;",
    "pub const RegistrationBlocker = virtio_input.RegistrationBlocker;",
    "pub fn summarize(device: *const virtio_input.VirtioInputLab) RegistrationPreflightSummary {",
    "pub fn blockerTag(blocker: RegistrationBlocker) []const u8 {",
    "pub fn queuePlanReady(summary: RegistrationPreflightSummary) bool {",
    "return summary.queue_plan_ready;",
    "pub fn capabilitySetupReady(summary: RegistrationPreflightSummary) bool {",
    "return summary.capability_setup_ready;",
    "pub fn multitouchSlotsReady(summary: RegistrationPreflightSummary) bool {",
    "return summary.multitouch_slots_ready;",
    "pub fn waitingOnCapabilitySetup(summary: RegistrationPreflightSummary) bool {",
    "return summary.blocker == .capability_setup_incomplete;",
    "pub fn waitingOnMultitouchSlots(summary: RegistrationPreflightSummary) bool {",
    "return summary.blocker == .multitouch_slots_unplanned;",
    "pub fn readyForRegistration(summary: RegistrationPreflightSummary) bool {",
    "return summary.ready_for_registration;",
]

STATUS_DRAIN_HELPER_MARKERS = [
    "pub const StatusDrainSummary = virtio_input.StatusDrainSummary;",
    "pub fn summarize(",
    "return device.drainStatusQueue(completed_count);",
]

TEARDOWN_HELPER_MARKERS = [
    "pub const TeardownObservationSummary = virtio_input.TeardownObservationSummary;",
    "pub fn summarize(device: *const virtio_input.VirtioInputLab) TeardownObservationSummary {",
    "pub fn runtimeStateArmed(summary: TeardownObservationSummary) bool {",
    "pub fn capabilityStateArmed(summary: TeardownObservationSummary) bool {",
    "pub fn preservesIdentity(summary: TeardownObservationSummary) bool {",
]

VERIFY_HELPER_MARKERS = [
    'test "phase10 virtio input verify keeps wrapper-facing queue preflight ordering explicit" {',
    'test "phase10 virtio input verify keeps wrapper prerequisites ahead of registration claims" {',
    'test "phase10 virtio input verify keeps teardown wrapper parity explicit across reset" {',
]

BUILD_MARKERS = [
    "virtio_input_verify_module",
    "phase10_virtio_input_module",
    "phase10_virtio_input_probe_preflight_module",
    "phase10_virtio_input_queue_callback_preflight_module",
    "phase10_virtio_input_registration_preflight_module",
    "phase10_virtio_input_status_drain_module",
    "phase10_virtio_input_teardown_observation_module",
    "phase10_virtio_input_survey_module",
    '"phase10-virtio-input-tests"',
    '"phase10-virtio-input-probe-preflight-tests"',
    '"phase10-virtio-input-queue-callback-preflight-tests"',
    '"phase10-virtio-input-registration-preflight-tests"',
    '"phase10-virtio-input-status-drain-tests"',
    '"phase10-virtio-input-teardown-observation-tests"',
    '"phase10-virtio-input-survey-tests"',
    '"phase10-virtio-input-verify-tests"',
]

SURVEY_GATE_MARKERS = [
    'test "phase10 virtio input survey note keeps the restored verifier, teardown parity, and queue callback packet explicit" {',
    'test "phase10 virtio input manifest keeps the restored replay ids and blocked lifecycle posture explicit" {',
    'test "phase10 virtio input slice companions keep the replay inventory and blocked lifecycle boundary explicit" {',
    "PHASE10_STATUS=parked",
    "PHASE10_LANE_KEY=P10-L13",
    "roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    '"id": "phase10-virtio-input-survey-gate"',
    '"status": "blocked_on_risky_transport"',
    "the dedicated status-drain helper plus replay",
    "teardown-reset parity across reset",
]

TEST_MARKERS = {
    "zigux/tests/phase10_virtio_input.zig": [
        'test "phase10 virtio input descriptor and identity snapshot stay lab-only and bounded" {',
        'test "phase10 virtio input queue planning caps and refills event buffers" {',
    ],
    "zigux/tests/phase10_virtio_input_probe_preflight.zig": [
        'test "phase10 virtio input probe preflight helper keeps blocker tags and ready transition reviewable" {',
    ],
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig": [
        'test "phase10 virtio input queue callback preflight tracks queue and ready-state gating" {',
    ],
    "zigux/tests/phase10_virtio_input_registration_preflight.zig": [
        'test "phase10 virtio input registration preflight helper exposes blocker tags and ready transition" {',
    ],
    "zigux/tests/phase10_virtio_input_status_drain.zig": [
        'test "phase10 virtio input status drain preserves suppressed timestamp counts while draining queued statuses" {',
    ],
    "zigux/tests/phase10_virtio_input_teardown_observation.zig": [
        'test "phase10 virtio input teardown observation keeps identity while resettable runtime state stays explicit" {',
    ],
}

MANIFEST_SURVEYED_COMMIT_MARKER = '"surveyed_commit": "'
SURVEY_NOTE_COMMIT_MARKER = "PHASE10_SURVEYED_COMMIT="
CLOSURE_MANIFEST_PATH = "zigux/tests/phase10_closure_manifest.json"
CLOSURE_INPUT_MANIFEST_PATH = "zigux/tests/phase10_virtio_input_manifest.json"
CLOSURE_READY_FOLLOWUP = "phase10-virtio-input-registration-lifecycle"
CLOSURE_INPUT_HELPER_IDS = [
    "phase10-virtio-input-capability-setup-helper",
    "phase10-virtio-input-multitouch-slot-helper",
    "phase10-virtio-input-probe-preflight-helper",
    "phase10-virtio-input-teardown-observation-helper",
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "phase10-virtio-input-status-drain-helper",
]
CLOSURE_INPUT_REPLAY_FILES = [
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
]
CLOSURE_LAB_VALIDATION_EVIDENCE = [
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "scripts/zigux/check-phase10-input-packet.py",
    "zigux/tests/phase10_build.zig",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def read_json(root: Path, rel_path: str) -> dict:
    return json.loads(read_text(root, rel_path))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def extract_manifest_surveyed_commit(manifest: str) -> str | None:
    start = manifest.find(MANIFEST_SURVEYED_COMMIT_MARKER)
    if start == -1:
        return None
    start += len(MANIFEST_SURVEYED_COMMIT_MARKER)
    end = manifest.find('"', start)
    if end == -1:
        return None
    return manifest[start:end]


def extract_survey_note_commit(survey_note: str) -> str | None:
    start = survey_note.find(SURVEY_NOTE_COMMIT_MARKER)
    if start == -1:
        return None
    start += len(SURVEY_NOTE_COMMIT_MARKER)
    end = survey_note.find("\n", start)
    if end == -1:
        end = len(survey_note)
    commit = survey_note[start:end].strip()
    return commit or None


def check_surveyed_commit_alignment(missing: list[str], survey_note: str, manifest: str) -> None:
    manifest_commit = extract_manifest_surveyed_commit(manifest)
    if manifest_commit is None:
        missing.append('manifest:"surveyed_commit": "')
        return

    note_commit = extract_survey_note_commit(survey_note)
    if note_commit is None:
        missing.append("survey_note:PHASE10_SURVEYED_COMMIT=")
        return

    if note_commit != manifest_commit:
        missing.append("survey_note:surveyed_commit_alignment")


def check_closure_manifest_alignment(missing: list[str], root: Path, manifest_text: str) -> None:
    manifest = json.loads(manifest_text)
    closure = read_json(root, CLOSURE_MANIFEST_PATH)

    lane_key = manifest.get("lane_key")
    surveyed_commit = manifest.get("surveyed_commit")
    gaps = manifest.get("gaps", [])
    starter_landed = {
        gap.get("id")
        for gap in gaps
        if gap.get("status") == "starter_landed" and isinstance(gap.get("id"), str)
    }
    blocked = {
        gap.get("id")
        for gap in gaps
        if gap.get("status") == "blocked_on_risky_transport" and isinstance(gap.get("id"), str)
    }

    provenance = closure.get("survey_provenance", {})
    lane_keys = provenance.get("lane_keys", {})
    surveyed_commits = provenance.get("surveyed_commits", {})
    if lane_keys.get("input") != lane_key:
        missing.append("closure_manifest:survey_provenance.input_lane_key")
    if surveyed_commits.get("input") != surveyed_commit:
        missing.append("closure_manifest:survey_provenance.input_surveyed_commit")

    ready_followups = closure.get("ready_transport_followups", {})
    ready_followup = ready_followups.get(CLOSURE_INPUT_MANIFEST_PATH)
    if ready_followup != CLOSURE_READY_FOLLOWUP:
        missing.append("closure_manifest:ready_transport_followups.input")
    if ready_followup not in blocked:
        missing.append("closure_manifest:ready_transport_followups.input_blocked_status")

    landed_helpers = closure.get("landed_input_helper_evidence", {}).get(CLOSURE_INPUT_MANIFEST_PATH)
    if not isinstance(landed_helpers, list):
        missing.append("closure_manifest:landed_input_helper_evidence")
        landed_helper_set: set[str] = set()
    else:
        landed_helper_set = {item for item in landed_helpers if isinstance(item, str)}
    for helper_id in CLOSURE_INPUT_HELPER_IDS:
        if helper_id not in starter_landed:
            missing.append(f"manifest:starter_landed:{helper_id}")
        if helper_id not in landed_helper_set:
            missing.append(f"closure_manifest:landed_input_helper:{helper_id}")

    focused_harness = closure.get("focused_harness_replays", {})
    tests = closure.get("tests", [])
    test_set = {item for item in tests if isinstance(item, str)}
    for path in CLOSURE_INPUT_REPLAY_FILES:
        labels = focused_harness.get(path)
        if not isinstance(labels, list) or not labels:
            missing.append(f"closure_manifest:focused_harness_replays:{path}")
        elif not all(isinstance(label, str) and label.strip() for label in labels):
            missing.append(f"closure_manifest:focused_harness_replays:{path}:blank_label")
        if path not in test_set:
            missing.append(f"closure_manifest:tests:{path}")

    evidence = (
        closure.get("roadmap_parity_scoreboard", {})
        .get("lab_only_driver_validation", {})
        .get("evidence", [])
    )
    if not isinstance(evidence, list):
        missing.append("closure_manifest:lab_only_driver_validation.evidence")
        evidence_set: set[str] = set()
    else:
        evidence_set = {item for item in evidence if isinstance(item, str)}
    for item in CLOSURE_LAB_VALIDATION_EVIDENCE:
        if item not in evidence_set:
            missing.append(f"closure_manifest:lab_only_driver_validation:{item}")


def required_marker_count() -> int:
    return (
        len(SLICE_MARKERS)
        + len(MODULE_MARKERS)
        + len(SURVEY_NOTE_MARKERS)
        + len(MANIFEST_MARKERS)
        + len(INPUT_HELPER_MARKERS)
        + len(PROBE_HELPER_MARKERS)
        + len(QUEUE_CALLBACK_HELPER_MARKERS)
        + len(REGISTRATION_HELPER_MARKERS)
        + len(STATUS_DRAIN_HELPER_MARKERS)
        + len(TEARDOWN_HELPER_MARKERS)
        + len(VERIFY_HELPER_MARKERS)
        + len(BUILD_MARKERS)
        + len(SURVEY_GATE_MARKERS)
        + sum(len(markers) for markers in TEST_MARKERS.values())
        + 4
        + len(CLOSURE_INPUT_HELPER_IDS)
        + (2 * len(CLOSURE_INPUT_REPLAY_FILES))
        + len(CLOSURE_LAB_VALIDATION_EVIDENCE)
    )


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    slice_note = read_text(root, "Documentation/zigux/phase10-virtio-input-slice.md")
    module_note = read_text(root, "Documentation/zigux/phase10-virtio-input-module-slice.md")
    survey_note = read_text(root, "Documentation/zigux/phase10-virtio-input-survey.md")
    manifest = read_text(root, "zigux/tests/phase10_virtio_input_manifest.json")

    check_markers(missing_markers, "slice_note", slice_note, SLICE_MARKERS)
    check_markers(missing_markers, "module_note", module_note, MODULE_MARKERS)
    check_markers(missing_markers, "survey_note", survey_note, SURVEY_NOTE_MARKERS)
    check_markers(missing_markers, "manifest", manifest, MANIFEST_MARKERS)
    check_surveyed_commit_alignment(missing_markers, survey_note, manifest)
    check_closure_manifest_alignment(missing_markers, root, manifest)
    check_markers(missing_markers, "input_helper", read_text(root, "drivers/virtio/virtio_input.zig"), INPUT_HELPER_MARKERS)
    check_markers(missing_markers, "probe_helper", read_text(root, "drivers/virtio/virtio_input_probe_preflight.zig"), PROBE_HELPER_MARKERS)
    check_markers(missing_markers, "queue_callback_helper", read_text(root, "drivers/virtio/virtio_input_queue_callback_preflight.zig"), QUEUE_CALLBACK_HELPER_MARKERS)
    check_markers(missing_markers, "registration_helper", read_text(root, "drivers/virtio/virtio_input_registration_preflight.zig"), REGISTRATION_HELPER_MARKERS)
    check_markers(missing_markers, "status_drain_helper", read_text(root, "drivers/virtio/virtio_input_status_drain.zig"), STATUS_DRAIN_HELPER_MARKERS)
    check_markers(missing_markers, "teardown_helper", read_text(root, "drivers/virtio/virtio_input_teardown_observation.zig"), TEARDOWN_HELPER_MARKERS)
    check_markers(missing_markers, "verify_helper", read_text(root, "drivers/virtio/virtio_input_verify.zig"), VERIFY_HELPER_MARKERS)
    check_markers(missing_markers, "phase10_build", read_text(root, "zigux/tests/phase10_build.zig"), BUILD_MARKERS)
    check_markers(missing_markers, "survey_gate", read_text(root, "zigux/tests/phase10_virtio_input_survey.zig"), SURVEY_GATE_MARKERS)
    for rel_path, markers in TEST_MARKERS.items():
        check_markers(missing_markers, Path(rel_path).name, read_text(root, rel_path), markers)

    return [], missing_markers


def write_fixture(root: Path) -> None:
    manifest_commit = "7361ac51374149a96b7a7a2c6ea3c995d8cc1231"
    input_manifest = {
        "lane_key": "P10-L13",
        "surveyed_commit": manifest_commit,
        "roadmap_destinations": ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"],
        "risky_transport_posture": "blocked_on_risky_transport",
        "allowed_evidence_kinds": ["driver_local_lab_slices", "survey_manifests", "shared_validation_gates"],
        "gaps": [
            {"id": "phase10-virtio-input-survey-gate", "status": "starter_landed", "zigux_destination": "zigux/tests/phase10_virtio_input_survey.zig", "why_now": "survey gate"},
            {"id": "phase10-virtio-input-verify-replay", "status": "starter_landed", "zigux_destination": "drivers/virtio/virtio_input_verify.zig", "why_now": "teardown-reset parity across reset explicit without widening into transport-backed queue execution or freeze, restore, or remove lifecycle claims"},
            {"id": "phase10-virtio-input-capability-setup-helper", "status": "starter_landed", "zigux_destination": "drivers/virtio/virtio_input.zig", "why_now": "helper"},
            {"id": "phase10-virtio-input-multitouch-slot-helper", "status": "starter_landed", "zigux_destination": "drivers/virtio/virtio_input.zig", "why_now": "helper"},
            {"id": "phase10-virtio-input-probe-preflight-helper", "status": "starter_landed", "zigux_destination": "drivers/virtio/virtio_input_probe_preflight.zig", "why_now": "helper"},
            {"id": "phase10-virtio-input-queue-callback-preflight-helper", "status": "starter_landed", "zigux_destination": "drivers/virtio/virtio_input_queue_callback_preflight.zig", "why_now": "helper"},
            {"id": "phase10-virtio-input-registration-preflight-helper", "status": "starter_landed", "zigux_destination": "drivers/virtio/virtio_input_registration_preflight.zig", "why_now": "helper"},
            {"id": "phase10-virtio-input-status-drain-helper", "status": "starter_landed", "zigux_destination": "drivers/virtio/virtio_input_status_drain.zig", "why_now": "helper"},
            {"id": "phase10-virtio-input-teardown-observation-helper", "status": "starter_landed", "zigux_destination": "drivers/virtio/virtio_input_teardown_observation.zig", "why_now": "helper"},
            {"id": "phase10-virtio-input-registration-lifecycle", "status": "blocked_on_risky_transport", "zigux_destination": "zigux/tests/phase10_virtio_input.zig", "why_now": "blocked"},
        ],
    }
    closure_manifest = {
        "survey_provenance": {"lane_keys": {"input": "P10-L13"}, "surveyed_commits": {"input": manifest_commit}},
        "ready_transport_followups": {CLOSURE_INPUT_MANIFEST_PATH: CLOSURE_READY_FOLLOWUP},
        "landed_input_helper_evidence": {CLOSURE_INPUT_MANIFEST_PATH: list(CLOSURE_INPUT_HELPER_IDS)},
        "focused_harness_replays": {path: [f"{Path(path).stem} replay"] for path in CLOSURE_INPUT_REPLAY_FILES},
        "tests": sorted(set(list(TEST_MARKERS.keys()) + CLOSURE_INPUT_REPLAY_FILES + ["zigux/tests/phase10_virtio_input_survey.zig"])),
        "roadmap_parity_scoreboard": {"lab_only_driver_validation": {"evidence": list(CLOSURE_LAB_VALIDATION_EVIDENCE)}},
    }

    fixture_contents = {
        "Documentation/zigux/phase10-virtio-input-slice.md": "\n".join(SLICE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-input-module-slice.md": "\n".join(MODULE_MARKERS + ["queued status completions are only reclaimed in memory"]) + "\n",
        "Documentation/zigux/phase10-virtio-input-survey.md": "\n".join([marker if marker != "PHASE10_SURVEYED_COMMIT=" else f"PHASE10_SURVEYED_COMMIT={manifest_commit}" for marker in SURVEY_NOTE_MARKERS]) + "\n",
        "drivers/virtio/virtio_input.zig": "\n".join(INPUT_HELPER_MARKERS) + "\n",
        "drivers/virtio/virtio_input_probe_preflight.zig": "\n".join(PROBE_HELPER_MARKERS) + "\n",
        "drivers/virtio/virtio_input_queue_callback_preflight.zig": "\n".join(QUEUE_CALLBACK_HELPER_MARKERS) + "\n",
        "drivers/virtio/virtio_input_registration_preflight.zig": "\n".join(REGISTRATION_HELPER_MARKERS) + "\n",
        "drivers/virtio/virtio_input_status_drain.zig": "\n".join(STATUS_DRAIN_HELPER_MARKERS) + "\n",
        "drivers/virtio/virtio_input_teardown_observation.zig": "\n".join(TEARDOWN_HELPER_MARKERS) + "\n",
        "drivers/virtio/virtio_input_verify.zig": "\n".join(VERIFY_HELPER_MARKERS) + "\n",
        "zigux/tests/phase10_build.zig": "\n".join(BUILD_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_input_survey.zig": "\n".join(SURVEY_GATE_MARKERS) + "\n",
    }
    for rel_path, markers in TEST_MARKERS.items():
        fixture_contents[rel_path] = "\n".join(markers) + "\n"

    for rel_path, content in fixture_contents.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    write_json(root / "zigux/tests/phase10_virtio_input_manifest.json", input_manifest)
    write_json(root / CLOSURE_MANIFEST_PATH, closure_manifest)


def expect_missing_marker(root: Path, rel_path: str, old: str, new: str, expected: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"unexpected_missing_files:{','.join(missing_files)}")
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"expected={expected}:actual={actual}")
    path.write_text(original, encoding="utf-8")


def expect_json_missing_marker(root: Path, rel_path: str, mutate, expected: str) -> None:
    path = root / rel_path
    original = read_json(root, rel_path)
    mutated = mutate(json.loads(json.dumps(original)))
    write_json(path, mutated)
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"unexpected_missing_files:{','.join(missing_files)}")
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"expected={expected}:actual={actual}")
    write_json(path, original)


def expect_missing_file(root: Path, rel_path: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.unlink()
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(f"unexpected_missing_markers:{','.join(missing_markers)}")
    if rel_path not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(f"expected={rel_path}:actual={actual}")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_input_live_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        text_cases = [
            (
                "Documentation/zigux/phase10-virtio-input-slice.md",
                "drivers/virtio/virtio_input_queue_callback_preflight.zig",
                "drivers/virtio/virtio_input_queue_callback_preflight_missing.zig",
                "slice_note:drivers/virtio/virtio_input_queue_callback_preflight.zig",
            ),
            (
                "Documentation/zigux/phase10-virtio-input-module-slice.md",
                "zigux/tests/phase10_virtio_input_survey.zig",
                "zigux/tests/phase10_virtio_input_survey_missing.zig",
                "module_note:zigux/tests/phase10_virtio_input_survey.zig",
            ),
            (
                "Documentation/zigux/phase10-virtio-input-survey.md",
                "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
                "zigux/tests/phase10_virtio_input_queue_callback_preflight_missing.zig",
                "survey_note:zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
            ),
            (
                "Documentation/zigux/phase10-virtio-input-survey.md",
                "PHASE10_SURVEYED_COMMIT=7361ac51374149a96b7a7a2c6ea3c995d8cc1231",
                "PHASE10_SURVEYED_COMMIT=deadbeef",
                "survey_note:surveyed_commit_alignment",
            ),
            (
                "Documentation/zigux/phase10-virtio-input-module-slice.md",
                "zigux/tests/phase10_virtio_input_manifest.json",
                "zigux/tests/phase10_virtio_input_manifest_missing.json",
                "module_note:zigux/tests/phase10_virtio_input_manifest.json",
            ),
            (
                "zigux/tests/phase10_build.zig",
                '"phase10-virtio-input-verify-tests"',
                '"phase10-virtio-input-verify-drift"',
                'phase10_build:"phase10-virtio-input-verify-tests"',
            ),
            (
                "drivers/virtio/virtio_input_registration_preflight.zig",
                "pub fn readyForRegistration(summary: RegistrationPreflightSummary) bool {",
                "pub fn readyForRegistrationDrift(summary: RegistrationPreflightSummary) bool {",
                "registration_helper:pub fn readyForRegistration(summary: RegistrationPreflightSummary) bool {",
            ),
        ]
        for rel_path, old, new, expected in text_cases:
            expect_missing_marker(root, rel_path, old, new, expected)

        expect_json_missing_marker(
            root,
            "zigux/tests/phase10_virtio_input_manifest.json",
            lambda data: {**data, "roadmap_destinations": ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/runtime/"]},
            'manifest:"zigux/helpers/"',
        )
        expect_json_missing_marker(
            root,
            CLOSURE_MANIFEST_PATH,
            lambda data: {**data, "survey_provenance": {**data["survey_provenance"], "lane_keys": {**data["survey_provenance"]["lane_keys"], "input": "P10-L99"}}},
            "closure_manifest:survey_provenance.input_lane_key",
        )
        expect_json_missing_marker(
            root,
            CLOSURE_MANIFEST_PATH,
            lambda data: {**data, "survey_provenance": {**data["survey_provenance"], "surveyed_commits": {**data["survey_provenance"]["surveyed_commits"], "input": "deadbeef"}}},
            "closure_manifest:survey_provenance.input_surveyed_commit",
        )
        expect_json_missing_marker(
            root,
            CLOSURE_MANIFEST_PATH,
            lambda data: {**data, "ready_transport_followups": {**data["ready_transport_followups"], CLOSURE_INPUT_MANIFEST_PATH: "phase10-virtio-input-registration-preflight-helper"}},
            "closure_manifest:ready_transport_followups.input",
        )
        expect_json_missing_marker(
            root,
            CLOSURE_MANIFEST_PATH,
            lambda data: {**data, "landed_input_helper_evidence": {CLOSURE_INPUT_MANIFEST_PATH: [item for item in data["landed_input_helper_evidence"][CLOSURE_INPUT_MANIFEST_PATH] if item != "phase10-virtio-input-status-drain-helper"]}},
            "closure_manifest:landed_input_helper:phase10-virtio-input-status-drain-helper",
        )
        expect_json_missing_marker(
            root,
            CLOSURE_MANIFEST_PATH,
            lambda data: {**data, "focused_harness_replays": {**data["focused_harness_replays"], "zigux/tests/phase10_virtio_input_status_drain.zig": []}},
            "closure_manifest:focused_harness_replays:zigux/tests/phase10_virtio_input_status_drain.zig",
        )
        expect_json_missing_marker(
            root,
            CLOSURE_MANIFEST_PATH,
            lambda data: {**data, "tests": [item for item in data["tests"] if item != "zigux/tests/phase10_virtio_input_teardown_observation.zig"]},
            "closure_manifest:tests:zigux/tests/phase10_virtio_input_teardown_observation.zig",
        )
        expect_json_missing_marker(
            root,
            CLOSURE_MANIFEST_PATH,
            lambda data: {**data, "roadmap_parity_scoreboard": {"lab_only_driver_validation": {"evidence": [item for item in data["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] if item != "scripts/zigux/check-phase10-input-packet.py"]}}},
            "closure_manifest:lab_only_driver_validation:scripts/zigux/check-phase10-input-packet.py",
        )

        expect_missing_file(root, "Documentation/zigux/phase10-virtio-input-survey.md")
        expect_missing_file(root, "zigux/tests/phase10_virtio_input_survey.zig")

    print("PHASE10_INPUT_LIVE_PACKET_SELF_TEST=pass")
    print("PHASE10_INPUT_LIVE_PACKET_SELF_TEST_CASE_COUNT=17")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the live Phase 10 virtio input packet and its shared closure-manifest alignment.")
    parser.add_argument("--self-test", action="store_true", help="run the checker's built-in synthetic drift tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_INPUT_LIVE_PACKET=fail")
        print("MISSING_PHASE10_INPUT_LIVE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_INPUT_LIVE_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_INPUT_LIVE_PACKET=fail")
        print("MISSING_PHASE10_INPUT_LIVE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_INPUT_LIVE_MARKERS_END")
        return 1

    print("PHASE10_INPUT_LIVE_PACKET=pass")
    print(f"PHASE10_INPUT_LIVE_REQUIRED_FILE_COUNT={len(FILES)}")
    print(f"PHASE10_INPUT_LIVE_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())