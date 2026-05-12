#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")

FILES = [
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase10-virtio-input-slice.md",
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
]

MAKE_MARKERS = [
    "PHONY += phase10-validate phase10-test phase10",
    "phase10-validate:",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "phase10-test:",
    "$(ZIG) build test --build-file zigux/tests/phase10_build.zig --summary all",
    "phase10: phase10-validate phase10-test",
]

BUILD_MARKERS = [
    "phase10_virtio_input_probe_preflight_module",
    "phase10_virtio_input_queue_callback_preflight_module",
    "phase10_virtio_input_status_drain_module",
    "phase10_virtio_input_verify_module",
    '"phase10-virtio-input-probe-preflight-tests"',
    '"phase10-virtio-input-queue-callback-preflight-tests"',
    '"phase10-virtio-input-status-drain-tests"',
    '"phase10-virtio-input-verify-tests"',
]

WORKFLOW_MARKERS = [
    "Validate Phase 10 closure evidence",
    "make -C zigux phase10-validate",
    "Run Phase 10 virtio helper tests",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
]

SCRIPT_README_MARKERS = [
    "validate-phase10.py",
    "Phase 10 flow",
    "make -C zigux phase10-validate",
    "phase10_virtio_input_manifest.json",
    "phase10-virtio-input-slice.md",
    "phase10-virtio-input-survey.md",
    "blocked registration-lifecycle contract",
    "queue-callback preflight helper is landed",
    "drivers/virtio/virtio_input_verify.zig",
    "phase10_virtio_input_probe_preflight.zig",
    "phase10_virtio_input_queue_callback_preflight.zig",
    "phase10_virtio_input_registration_preflight.zig",
    "phase10_virtio_input_teardown_observation.zig",
]

FORBIDDEN_SCRIPT_README_MARKERS = [
    "ABS_MT_SLOT remains the single ready-next helper step",
]

TESTS_README_MARKERS = [
    "scripts/zigux/validate-phase10.py",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "registration-preflight helper",
    "queue-callback preflight helper",
    "registration-lifecycle blocker",
    "four lane survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
    "phase10_virtio_input_probe_preflight.zig",
    "phase10_virtio_input_queue_callback_preflight.zig",
    "phase10_virtio_input_registration_preflight.zig",
    "phase10_virtio_input_teardown_observation.zig",
    "phase10_virtio_input_status_drain.zig",
]

FORBIDDEN_TESTS_README_MARKERS = [
    "three lane survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
    "three manifest-backed survey records",
]

DOC_README_MARKERS = [
    "python3 scripts/zigux/validate-phase10.py",
    "make -C zigux phase10-validate",
    "phase10-virtio-input-slice.md",
    "phase10-virtio-input-survey.md",
    "registration-preflight helper",
    "queue-callback preflight helper",
    "registration-lifecycle blocker",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
]

FORBIDDEN_DOC_README_MARKERS = [
    "there is still no dedicated shared `validate-phase10.py`, `check-phase10-harness-coverage.py`, or `phase10-validate` target on `master`",
]

SLICE_MARKERS = [
    "python3 scripts/zigux/validate-phase10.py",
    "make -C zigux phase10-validate",
    "queue-callback preflight helper",
    "input-device registration work",
]

SURVEY_MARKERS = [
    "python3 scripts/zigux/validate-phase10.py",
    "make -C zigux phase10-validate",
    "phase10-virtio-input-registration-preflight-replay",
    "phase10-virtio-input-teardown-observation-replay",
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "phase10-virtio-input-registration-lifecycle",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
]

MODULE_SLICE_MARKERS = [
    "queue-callback preflight helper",
    "input core capability registration",
]

HELPER_MARKERS = [
    "pub const MultitouchSlotPlanSummary = struct {",
    "pub const TeardownPlanSummary = struct {",
    "pub const QueueCallbackPreflightSummary = struct {",
    "pub fn capabilitySetupSummary(self: *const Self) !CapabilitySetupSummary {",
    "pub fn multitouchSlotPlanSummary(self: *const Self) !MultitouchSlotPlanSummary {",
    "pub fn teardownPlanSummary(self: *const Self) TeardownPlanSummary {",
    "pub fn queueCallbackPreflightSummary(self: *const Self) !QueueCallbackPreflightSummary {",
    "pub fn sendStatus(self: *Self, event_type: u16, code: u16, value: i32) !StatusSendSummary {",
    "pub fn reset(self: *Self) void {",
]

VERIFY_MARKERS = [
    'test "virtio input wrapper-facing queue preflight advances in bounded order" {',
    'test "virtio input wrapper-facing probe preflight stops before registration lifecycle claims" {',
    'test "virtio input registration preflight keeps wrapper prerequisites ahead of registration claims" {',
]

PROBE_PREFLIGHT_HELPER_MARKERS = [
    "pub const ProbePreflightBlocker = enum {",
    "registration_preflight_ready: bool,",
    "pub fn summarize(device: *const virtio_input.VirtioInputLab) ProbePreflightSummary {",
]

TEST_MARKERS = [
    'test "phase10 virtio input stages capability setup from config bitmaps and ABS metadata" {',
    'test "phase10 virtio input plans multitouch slots from ABS_MT_SLOT metadata" {',
    'test "phase10 virtio input teardown summary keeps reset cleanup and identity preservation explicit" {',
    'test "phase10 virtio input records queue-callback preflight once registration and queue intent are staged" {',
    'test "phase10 virtio input reset clears queue plan and returns to default bus identity" {',
]

PROBE_PREFLIGHT_TEST_MARKERS = [
    'test "phase10 virtio input probe preflight keeps identity visible before queue setup" {',
    'test "phase10 virtio input probe preflight reports the next bounded blocker before handoff" {',
    "summary.registration_preflight_ready",
    "summary.ready_for_probe_handoff",
]

QUEUE_CALLBACK_PREFLIGHT_TEST_MARKERS = [
    'test "phase10 virtio input queue callback preflight reports queue and ready blockers and resets cleanly" {',
    "QueueCallbackPreflightBlocker.event_queue_unconfigured",
    "QueueCallbackPreflightBlocker.device_not_ready",
    "ready_for_queue_callbacks",
]

SURVEY_TEST_MARKERS = [
    'test "phase10 virtio input survey manifest records the live starter and remaining gap" {',
    'try std.testing.expectEqualStrings("P10-L13", manifest.lane_key);',
    'try std.testing.expect(starter_landed_count >= 16);',
    'try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
    'try std.testing.expectEqual(@as(usize, 1), blocked_count);',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-verify-replay")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-queue-callback-preflight-replay")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-probe-preflight-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-registration-preflight-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-queue-callback-preflight-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-status-drain-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-teardown-observation-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-wrapper-ownership-note")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-registration-lifecycle")) {',
]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_manifest(path: str) -> dict[str, object]:
    return json.loads(text(path))


def find_gap(manifest: dict[str, object], gap_id: str) -> dict[str, object] | None:
    for gap in manifest.get("gaps", []):
        if isinstance(gap, dict) and gap.get("id") == gap_id:
            return gap
    return None


missing_files = [path for path in FILES if not (ROOT / path).exists()]
if missing_files:
    print("PHASE10_VALIDATION=fail")
    print("MISSING_PHASE10_FILES_START")
    for path in missing_files:
        print(path)
    print("MISSING_PHASE10_FILES_END")
    sys.exit(1)

missing: list[str] = []
for name, source, markers in [
    ("make", text("zigux/Makefile"), MAKE_MARKERS),
    ("build_file", text("zigux/tests/phase10_build.zig"), BUILD_MARKERS),
    ("workflow", text(".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS),
    ("script_readme", text("scripts/zigux/README.md"), SCRIPT_README_MARKERS),
    ("tests_readme", text("zigux/tests/README.md"), TESTS_README_MARKERS),
    ("doc_readme", text("Documentation/zigux/README.md"), DOC_README_MARKERS),
    ("slice_doc", text("Documentation/zigux/phase10-virtio-input-slice.md"), SLICE_MARKERS),
    ("survey_doc", text("Documentation/zigux/phase10-virtio-input-survey.md"), SURVEY_MARKERS),
    ("module_slice", text("Documentation/zigux/phase10-virtio-input-module-slice.md"), MODULE_SLICE_MARKERS),
    ("helper", text("drivers/virtio/virtio_input.zig"), HELPER_MARKERS),
    ("verify", text("drivers/virtio/virtio_input_verify.zig"), VERIFY_MARKERS),
    (
        "probe_preflight_helper",
        text("drivers/virtio/virtio_input_probe_preflight.zig"),
        PROBE_PREFLIGHT_HELPER_MARKERS,
    ),
    ("tests", text("zigux/tests/phase10_virtio_input.zig"), TEST_MARKERS),
    (
        "probe_preflight_test",
        text("zigux/tests/phase10_virtio_input_probe_preflight.zig"),
        PROBE_PREFLIGHT_TEST_MARKERS,
    ),
    (
        "queue_callback_preflight_test",
        text("zigux/tests/phase10_virtio_input_queue_callback_preflight.zig"),
        QUEUE_CALLBACK_PREFLIGHT_TEST_MARKERS,
    ),
    ("survey_test", text("zigux/tests/phase10_virtio_input_survey.zig"), SURVEY_TEST_MARKERS),
]:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")

for name, source, markers in [
    ("script_readme", text("scripts/zigux/README.md"), FORBIDDEN_SCRIPT_README_MARKERS),
    ("tests_readme", text("zigux/tests/README.md"), FORBIDDEN_TESTS_README_MARKERS),
    ("doc_readme", text("Documentation/zigux/README.md"), FORBIDDEN_DOC_README_MARKERS),
]:
    for marker in markers:
        if marker in source:
            missing.append(f"{name}:stale_marker:{marker}")

manifest = load_manifest("zigux/tests/phase10_virtio_input_manifest.json")
if manifest.get("lane_key") != "P10-L13":
    missing.append("manifest:lane_key=P10-L13")
if manifest.get("phase") != "Phase 10":
    missing.append("manifest:phase=Phase 10")
if manifest.get("anchor") != "drivers/virtio/virtio_input.c":
    missing.append("manifest:anchor=drivers/virtio/virtio_input.c")
if not HEX40.fullmatch(str(manifest.get("surveyed_commit", ""))):
    missing.append("manifest:surveyed_commit")

if manifest.get("roadmap_destinations") != ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"]:
    missing.append("manifest:roadmap_destinations")

survey_summary = manifest.get("survey_summary")
if not isinstance(survey_summary, dict):
    missing.append("manifest:survey_summary")
else:
    if survey_summary.get("preexisting_virtio_input_zig_present") is not True:
        missing.append("manifest:preexisting_virtio_input_zig_present")
    if survey_summary.get("preexisting_virtio_input_test_present") is not True:
        missing.append("manifest:preexisting_virtio_input_test_present")
    if survey_summary.get("preexisting_virtio_input_slice_note_present") is not True:
        missing.append("manifest:preexisting_virtio_input_slice_note_present")
    if survey_summary.get("preexisting_virtio_input_module_note_present") is not True:
        missing.append("manifest:preexisting_virtio_input_module_note_present")

gaps = manifest.get("gaps")
if not isinstance(gaps, list) or len(gaps) < 19:
    missing.append("manifest:gaps")
else:
    expected_statuses = {
        "phase10-virtio-input-lab-helper": "starter_landed",
        "phase10-virtio-input-lab-gate": "starter_landed",
        "phase10-virtio-input-verify-replay": "starter_landed",
        "phase10-virtio-input-queue-callback-preflight-replay": "starter_landed",
        "phase10-virtio-input-registration-preflight-replay": "starter_landed",
        "phase10-virtio-input-teardown-observation-replay": "starter_landed",
        "phase10-virtio-input-survey-gate": "starter_landed",
        "phase10-virtio-input-capability-setup-helper": "starter_landed",
        "phase10-virtio-input-multitouch-slot-helper": "starter_landed",
        "phase10-virtio-input-probe-preflight-helper": "starter_landed",
        "phase10-virtio-input-registration-preflight-helper": "starter_landed",
        "phase10-virtio-input-queue-callback-preflight-helper": "starter_landed",
        "phase10-virtio-input-status-drain-helper": "starter_landed",
        "phase10-virtio-input-teardown-observation-helper": "starter_landed",
        "phase10-virtio-input-wrapper-ownership-note": "starter_landed",
        "phase10-virtio-input-registration-lifecycle": "blocked_on_risky_transport",
    }
    starter_count = 0
    ready_count = 0
    blocked_count = 0
    for gap in gaps:
        if not isinstance(gap, dict):
            missing.append("manifest:gap_object")
            continue
        status = gap.get("status")
        if status == "starter_landed":
            starter_count += 1
        elif status == "ready_next":
            ready_count += 1
        elif status == "blocked_on_risky_transport":
            blocked_count += 1
    if ready_count != 0:
        missing.append(f"manifest:ready_next_count={ready_count}")
    if blocked_count != 1:
        missing.append(f"manifest:blocked_count={blocked_count}")
    if starter_count < 20:
        missing.append(f"manifest:starter_count={starter_count}")

    for gap_id, status in expected_statuses.items():
        gap = find_gap(manifest, gap_id)
        if gap is None:
            missing.append(f"manifest:gap:{gap_id}")
            continue
        if gap.get("status") != status:
            missing.append(f"manifest:gap_status:{gap_id}={gap.get('status')}")

    registration_preflight_replay_gap = find_gap(
        manifest,
        "phase10-virtio-input-registration-preflight-replay",
    )
    if registration_preflight_replay_gap is not None:
        why_now = str(registration_preflight_replay_gap.get("why_now", ""))
        if "dedicated registration-preflight replay" not in why_now:
            missing.append("manifest:registration_preflight_replay_gap:dedicated_registration_preflight_replay")
        if "capability-setup" not in why_now:
            missing.append("manifest:registration_preflight_replay_gap:capability_setup")
        if "multitouch-slot blockers" not in why_now:
            missing.append("manifest:registration_preflight_replay_gap:multitouch_slot_blockers")
        if "input_register_device() handoff" not in why_now:
            missing.append("manifest:registration_preflight_replay_gap:input_register_device_handoff")

    teardown_observation_replay_gap = find_gap(
        manifest,
        "phase10-virtio-input-teardown-observation-replay",
    )
    if teardown_observation_replay_gap is not None:
        why_now = str(teardown_observation_replay_gap.get("why_now", ""))
        if "dedicated teardown-observation replay" not in why_now:
            missing.append("manifest:teardown_observation_replay_gap:dedicated_teardown_observation_replay")
        if "identity preservation plus runtime- and capability-state cleanup explicit" not in why_now:
            missing.append("manifest:teardown_observation_replay_gap:identity_and_cleanup")
        if "remove, freeze, or restore work" not in why_now:
            missing.append("manifest:teardown_observation_replay_gap:remove_freeze_restore")

    landed_preflight_gap = find_gap(manifest, "phase10-virtio-input-registration-preflight-helper")
    if landed_preflight_gap is not None:
        why_now = str(landed_preflight_gap.get("why_now", ""))
        if "registration-preflight summary" not in why_now:
            missing.append("manifest:registration_preflight_gap:registration_preflight_summary")
        if "capability-setup" not in why_now:
            missing.append("manifest:registration_preflight_gap:capability_setup")
        if "multitouch-slot blockers" not in why_now:
            missing.append("manifest:registration_preflight_gap:multitouch_slot_blockers")
        if "input_register_device()" not in why_now:
            missing.append("manifest:registration_preflight_gap:input_register_device()")

    queue_callback_gap = find_gap(manifest, "phase10-virtio-input-queue-callback-preflight-helper")
    if queue_callback_gap is not None:
        why_now = str(queue_callback_gap.get("why_now", ""))
        if "queue-callback preflight summary" not in why_now:
            missing.append("manifest:queue_callback_gap:queue_callback_preflight_summary")
        if "event and status queue configuration" not in why_now:
            missing.append("manifest:queue_callback_gap:event_and_status_queue_configuration")
        if "event-buffer fill state" not in why_now:
            missing.append("manifest:queue_callback_gap:event_buffer_fill_state")
        if "transport-backed callback handoff" not in why_now:
            missing.append("manifest:queue_callback_gap:transport_backed_callback_handoff")

    blocked_gap = find_gap(manifest, "phase10-virtio-input-registration-lifecycle")
    if blocked_gap is not None:
        why_now = str(blocked_gap.get("why_now", ""))
        if "input_register_device()" not in why_now:
            missing.append("manifest:blocked_gap:input_register_device()")
        if "freeze or restore" not in why_now:
            missing.append("manifest:blocked_gap:freeze_or_restore")
        if "probe-preflight" not in why_now:
            missing.append("manifest:blocked_gap:probe_preflight")
        if "status-drain helpers landed" not in why_now:
            missing.append("manifest:blocked_gap:status_drain_helpers_landed")

if missing:
    print("PHASE10_VALIDATION=fail")
    print("MISSING_PHASE10_MARKERS_START")
    for item in missing:
        print(item)
    print("MISSING_PHASE10_MARKERS_END")
    sys.exit(1)

print("PHASE10_VALIDATION=pass")
print(f"PHASE10_REQUIRED_FILE_COUNT={len(FILES)}")
print(
    "PHASE10_REQUIRED_MARKER_COUNT="
    f"{len(MAKE_MARKERS) + len(BUILD_MARKERS) + len(WORKFLOW_MARKERS) + len(SCRIPT_README_MARKERS) + len(TESTS_README_MARKERS) + len(DOC_README_MARKERS) + len(FORBIDDEN_DOC_README_MARKERS) + len(SLICE_MARKERS) + len(SURVEY_MARKERS) + len(MODULE_SLICE_MARKERS) + len(HELPER_MARKERS) + len(VERIFY_MARKERS) + len(PROBE_PREFLIGHT_HELPER_MARKERS) + len(TEST_MARKERS) + len(PROBE_PREFLIGHT_TEST_MARKERS) + len(QUEUE_CALLBACK_PREFLIGHT_TEST_MARKERS) + len(SURVEY_TEST_MARKERS)}"
)
