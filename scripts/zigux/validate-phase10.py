#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")

FILES = [
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase10-virtio-ring-slice.md",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
    "Documentation/zigux/phase10-virtio-input-slice.md",
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_input.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "drivers/virtio/virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
]

MAKE_MARKERS = [
    "PHONY += phase10-validate phase10-test phase10",
    "phase10-validate:",
    "scripts/zigux/validate-phase10.py --self-test",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "phase10-test:",
    "$(ZIG) build test --build-file zigux/tests/phase10_build.zig --summary all",
    "phase10: phase10-validate phase10-test",
]

WORKFLOW_MARKERS = [
    "Self-test Phase 10 shared validator",
    "python3 scripts/zigux/validate-phase10.py --self-test",
    "Validate Phase 10 closure evidence",
    "make -C zigux phase10-validate",
    "Run Phase 10 virtio helper tests",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
]

SCRIPT_README_MARKERS = [
    "validate-phase10.py",
    "Phase 10 flow",
    "make -C zigux phase10-validate",
    "Phase 10 ring-plus-input-plus-MMIO lab packet",
    "phase10_build.zig",
    "phase10_virtio_ring_manifest.json",
    "phase10_virtio_ring_reset_reuse.zig",
    "phase10_virtio_input_manifest.json",
    "phase10_virtio_mmio_manifest.json",
    "phase10-virtio-ring-slice.md",
    "phase10-virtio-input-slice.md",
    "phase10-virtio-input-survey.md",
    "ring manifest-backed packet",
    "ring reset-reuse replay",
    "blocked registration-lifecycle contract",
    "shared validation surface",
    "bounded MMIO interrupt-ack rung",
    "probe-preflight helper",
    "eleven shared test entrypoints",
]

FORBIDDEN_SCRIPT_README_MARKERS = [
    "ABS_MT_SLOT remains the single ready-next helper step",
]

TESTS_README_MARKERS = [
    "scripts/zigux/validate-phase10.py",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "registration-preflight helper",
    "queue-callback preflight helper",
    "registration-lifecycle blocker",
    "four lane survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
]

FORBIDDEN_TESTS_README_MARKERS = [
    "three lane survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
    "three manifest-backed survey records",
]

DOC_README_MARKERS = [
    "python3 scripts/zigux/validate-phase10.py",
    "make -C zigux phase10-validate",
    "phase10-closure-evidence.md",
    "same nine published Phase 10 docs named by the shared closure packet",
    "phase10-virtio-core-survey.md",
    "phase10-virtio-ring-slice.md",
    "phase10-virtio-mmio-slice.md",
    "phase10-virtio-input-slice.md",
    "phase10-virtio-input-survey.md",
    "registration-preflight helper",
    "queue-callback preflight helper",
    "landed probe-preflight helper",
    "registration-lifecycle plus MMIO lifecycle blockers",
]

RING_SLICE_MARKERS = [
    "notify-prepare accounting with rollover flushing",
    "queue-reset guard and drained-queue reset bookkeeping",
    "Do not reopen `virtio_ring.zig` for more speculative in-memory queue work",
]

RING_SURVEY_MARKERS = [
    "phase10-mmio-config-write-helper",
    "no smaller ready transport follow-up remains ahead of the still-blocked lifecycle and IRQ packet",
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
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "phase10-virtio-input-probe-preflight-helper",
    "phase10-virtio-input-registration-lifecycle",
]

MODULE_SLICE_MARKERS = [
    "queue-callback preflight helper",
    "input core capability registration",
]

MMIO_SLICE_MARKERS = [
    "PHASE10_SLICE=virtio-mmio-interrupt-ack-helper",
    "in-memory config-write planning",
    "phase10-mmio-lifecycle-and-irq-paths",
]

MMIO_SURVEY_MARKERS = [
    "phase10-mmio-config-write-helper",
    "phase10-mmio-lifecycle-and-irq-paths",
    "config-write planning helper",
]

RING_HELPER_MARKERS = [
    "pub fn pollUsedBuffers(",
    "pub fn enableCallbackDelayed(",
    "pub fn resetGuardSummary(",
    "pub fn resetQueue(",
    "pub fn recoverBrokenQueue(",
]

MMIO_HELPER_MARKERS = [
    "pub const ConfigWritePlanSummary = struct {",
    "pub fn planConfigWrite(",
    "pub fn snapshotConfigWindow(",
    "pub fn acknowledgeInterrupt(self: *Self, bits: u32) !InterruptAckSummary {",
]

RING_TEST_MARKERS = [
    'test "phase10 virtio ring delays callbacks until most outstanding buffers are consumed" {',
    'test "phase10 virtio ring reset rejects queues with unpublished or unpolled work" {',
    'test "phase10 virtio ring reset clears drained queue bookkeeping without dropping queue shape" {',
]

RING_RESET_REUSE_TEST_MARKERS = [
    'test "phase10 virtio ring drained reset clears the broken flag so the queue can be reused" {',
]

RING_SURVEY_TEST_MARKERS = [
    'test "phase10 virtio ring survey manifest records the live queue-discipline packet and parked MMIO blocker after landed interrupt-ack" {',
    'try std.testing.expectEqual(@as(usize, 40), manifest.surveyed_commit.len);',
    'try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
    'if (std.mem.eql(u8, gap.id, "phase10-mmio-config-write-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-mmio-lifecycle-and-irq-paths")) {',
]

MMIO_TEST_MARKERS = [
    'test "phase10 virtio mmio plans bounded config-window writes without side effects" {',
    'test "phase10 virtio mmio acknowledges only pending bounded interrupt bits" {',
]

MMIO_SURVEY_TEST_MARKERS = [
    'test "phase10 virtio mmio survey manifest records the landed config-write rung and remaining transport gap" {',
    'try std.testing.expectEqualStrings("P10-L18", manifest.lane_key);',
    'try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
    'if (std.mem.eql(u8, gap.id, "phase10-mmio-config-write-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-mmio-lifecycle-and-irq-paths")) {',
]

HELPER_MARKERS = [
    "pub const MultitouchSlotPlanSummary = struct {",
    "pub const TeardownPlanSummary = struct {",
    "pub const RegistrationPreflightSummary = struct {",
    "pub const QueueCallbackPreflightSummary = struct {",
    "pub fn capabilitySetupSummary(self: *const Self) !CapabilitySetupSummary {",
    "pub fn multitouchSlotPlanSummary(self: *const Self) !MultitouchSlotPlanSummary {",
    "pub fn teardownPlanSummary(self: *const Self) TeardownPlanSummary {",
    "pub fn registrationPreflightSummary(self: *const Self) !RegistrationPreflightSummary {",
    "pub fn queueCallbackPreflightSummary(self: *const Self) !QueueCallbackPreflightSummary {",
    "pub fn sendStatus(self: *Self, event_type: u16, code: u16, value: i32) !StatusSendSummary {",
    "pub fn reset(self: *Self) void {",
]

TEST_MARKERS = [
    'test "phase10 virtio input stages capability setup from config bitmaps and ABS metadata" {',
    'test "phase10 virtio input plans multitouch slots from ABS_MT_SLOT metadata" {',
    'test "phase10 virtio input teardown summary keeps reset cleanup and identity preservation explicit" {',
    'test "phase10 virtio input records registration preflight once identity and capability intent are staged" {',
    'test "phase10 virtio input registration preflight infers multitouch slot intent from staged ABS_MT_SLOT metadata" {',
    'test "phase10 virtio input records queue-callback preflight once registration and queue intent are staged" {',
    'test "phase10 virtio input records probe preflight once registration and queue provisioning converge" {',
    'test "phase10 virtio input reset clears queue plan and returns to default bus identity" {',
]

SURVEY_TEST_MARKERS = [
    'test "phase10 virtio input survey manifest records the live starter and remaining gap" {',
    'try std.testing.expectEqualStrings("P10-L13", manifest.lane_key);',
    'try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
    'try std.testing.expectEqual(@as(usize, 1), blocked_count);',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-teardown-observation-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-registration-preflight-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-queue-callback-preflight-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-probe-preflight-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-registration-lifecycle")) {',
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_manifest(root: Path, rel_path: str) -> dict[str, object]:
    return json.loads(read_text(root, rel_path))


def find_gap(manifest: dict[str, object], gap_id: str) -> dict[str, object] | None:
    for gap in manifest.get("gaps", []):
        if isinstance(gap, dict) and gap.get("id") == gap_id:
            return gap
    return None


def required_marker_count() -> int:
    return (
        len(MAKE_MARKERS)
        + len(WORKFLOW_MARKERS)
        + len(SCRIPT_README_MARKERS)
        + len(TESTS_README_MARKERS)
        + len(DOC_README_MARKERS)
        + len(RING_SLICE_MARKERS)
        + len(RING_SURVEY_MARKERS)
        + len(SLICE_MARKERS)
        + len(SURVEY_MARKERS)
        + len(MODULE_SLICE_MARKERS)
        + len(MMIO_SLICE_MARKERS)
        + len(MMIO_SURVEY_MARKERS)
        + len(RING_HELPER_MARKERS)
        + len(HELPER_MARKERS)
        + len(MMIO_HELPER_MARKERS)
        + len(RING_TEST_MARKERS)
        + len(RING_RESET_REUSE_TEST_MARKERS)
        + len(RING_SURVEY_TEST_MARKERS)
        + len(TEST_MARKERS)
        + len(MMIO_TEST_MARKERS)
        + len(SURVEY_TEST_MARKERS)
        + len(MMIO_SURVEY_TEST_MARKERS)
        + len(FORBIDDEN_SCRIPT_README_MARKERS)
        + len(FORBIDDEN_TESTS_README_MARKERS)
    )


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []
    for name, source, markers in [
        ("make", read_text(root, "zigux/Makefile"), MAKE_MARKERS),
        ("workflow", read_text(root, ".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS),
        ("script_readme", read_text(root, "scripts/zigux/README.md"), SCRIPT_README_MARKERS),
        ("tests_readme", read_text(root, "zigux/tests/README.md"), TESTS_README_MARKERS),
        ("doc_readme", read_text(root, "Documentation/zigux/README.md"), DOC_README_MARKERS),
        ("ring_slice_doc", read_text(root, "Documentation/zigux/phase10-virtio-ring-slice.md"), RING_SLICE_MARKERS),
        ("ring_survey_doc", read_text(root, "Documentation/zigux/phase10-virtio-ring-survey.md"), RING_SURVEY_MARKERS),
        ("slice_doc", read_text(root, "Documentation/zigux/phase10-virtio-input-slice.md"), SLICE_MARKERS),
        ("survey_doc", read_text(root, "Documentation/zigux/phase10-virtio-input-survey.md"), SURVEY_MARKERS),
        ("module_slice", read_text(root, "Documentation/zigux/phase10-virtio-input-module-slice.md"), MODULE_SLICE_MARKERS),
        ("mmio_slice_doc", read_text(root, "Documentation/zigux/phase10-virtio-mmio-slice.md"), MMIO_SLICE_MARKERS),
        ("mmio_survey_doc", read_text(root, "Documentation/zigux/phase10-virtio-mmio-survey.md"), MMIO_SURVEY_MARKERS),
        ("ring_helper", read_text(root, "drivers/virtio/virtio_ring.zig"), RING_HELPER_MARKERS),
        ("helper", read_text(root, "drivers/virtio/virtio_input.zig"), HELPER_MARKERS),
        ("mmio_helper", read_text(root, "drivers/virtio/virtio_mmio.zig"), MMIO_HELPER_MARKERS),
        ("ring_tests", read_text(root, "zigux/tests/phase10_virtio_ring.zig"), RING_TEST_MARKERS),
        ("ring_reset_reuse_tests", read_text(root, "zigux/tests/phase10_virtio_ring_reset_reuse.zig"), RING_RESET_REUSE_TEST_MARKERS),
        ("ring_survey_tests", read_text(root, "zigux/tests/phase10_virtio_ring_survey.zig"), RING_SURVEY_TEST_MARKERS),
        ("tests", read_text(root, "zigux/tests/phase10_virtio_input.zig"), TEST_MARKERS),
        ("mmio_tests", read_text(root, "zigux/tests/phase10_virtio_mmio.zig"), MMIO_TEST_MARKERS),
        ("survey_test", read_text(root, "zigux/tests/phase10_virtio_input_survey.zig"), SURVEY_TEST_MARKERS),
        ("mmio_survey_test", read_text(root, "zigux/tests/phase10_virtio_mmio_survey.zig"), MMIO_SURVEY_TEST_MARKERS),
    ]:
        for marker in markers:
            if marker not in source:
                missing.append(f"{name}:{marker}")

    for name, source, markers in [
        ("script_readme", read_text(root, "scripts/zigux/README.md"), FORBIDDEN_SCRIPT_README_MARKERS),
        ("tests_readme", read_text(root, "zigux/tests/README.md"), FORBIDDEN_TESTS_README_MARKERS),
    ]:
        for marker in markers:
            if marker in source:
                missing.append(f"{name}:stale_marker:{marker}")

    ring_manifest = load_manifest(root, "zigux/tests/phase10_virtio_ring_manifest.json")
    if ring_manifest.get("lane_key") != "P10-L08":
        missing.append("ring_manifest:lane_key=P10-L08")
    if ring_manifest.get("phase") != "Phase 10":
        missing.append("ring_manifest:phase=Phase 10")
    if ring_manifest.get("anchor") != "drivers/virtio/virtio_ring.c":
        missing.append("ring_manifest:anchor=drivers/virtio/virtio_ring.c")
    if not HEX40.fullmatch(str(ring_manifest.get("surveyed_commit", ""))):
        missing.append("ring_manifest:surveyed_commit")

    if ring_manifest.get("roadmap_destinations") != ["drivers/virtio/*.zig", "zigux/helpers/"]:
        missing.append("ring_manifest:roadmap_destinations")

    ring_survey_summary = ring_manifest.get("survey_summary")
    if not isinstance(ring_survey_summary, dict):
        missing.append("ring_manifest:survey_summary")
    else:
        if ring_survey_summary.get("preexisting_virtio_core_zig_present") is not True:
            missing.append("ring_manifest:preexisting_virtio_core_zig_present")
        if ring_survey_summary.get("preexisting_phase10_build_present") is not True:
            missing.append("ring_manifest:preexisting_phase10_build_present")
        if ring_survey_summary.get("preexisting_virtio_ring_zig_present") is not True:
            missing.append("ring_manifest:preexisting_virtio_ring_zig_present")
        if ring_survey_summary.get("preexisting_virtio_ring_reset_reuse_test_present") is not True:
            missing.append("ring_manifest:preexisting_virtio_ring_reset_reuse_test_present")
        if ring_survey_summary.get("preexisting_virtio_ring_doc_present") is not True:
            missing.append("ring_manifest:preexisting_virtio_ring_doc_present")

    ring_gaps = ring_manifest.get("gaps")
    if not isinstance(ring_gaps, list) or len(ring_gaps) < 20:
        missing.append("ring_manifest:gaps")
    else:
        starter_count = 0
        ready_count = 0
        blocked_count = 0
        for gap in ring_gaps:
            if not isinstance(gap, dict):
                missing.append("ring_manifest:gap_object")
                continue
            status = gap.get("status")
            if status == "starter_landed":
                starter_count += 1
            elif status == "ready_next":
                ready_count += 1
            elif status == "blocked_on_risky_transport":
                blocked_count += 1
        if ready_count != 0:
            missing.append(f"ring_manifest:ready_next_count={ready_count}")
        if blocked_count != 1:
            missing.append(f"ring_manifest:blocked_count={blocked_count}")
        if starter_count < 20:
            missing.append(f"ring_manifest:starter_count={starter_count}")

        expected_ring_statuses = {
            "phase10-virtio-ring-survey-gate": "starter_landed",
            "phase10-virtio-ring-survey-note": "starter_landed",
            "phase10-virtqueue-shape-helper": "starter_landed",
            "phase10-used-buffer-polling-helper": "starter_landed",
            "phase10-callback-enable-prepare-helper": "starter_landed",
            "phase10-callback-delay-helper": "starter_landed",
            "phase10-notify-prepare-helper": "starter_landed",
            "phase10-queue-reset-guard-helper": "starter_landed",
            "phase10-queue-reset-helper": "starter_landed",
            "phase10-mmio-config-write-helper": "starter_landed",
            "phase10-mmio-lifecycle-and-irq-paths": "blocked_on_risky_transport",
            "phase10-virtio-ring-slice-note": "starter_landed",
        }
        for gap_id, status in expected_ring_statuses.items():
            gap = find_gap(ring_manifest, gap_id)
            if gap is None:
                missing.append(f"ring_manifest:gap:{gap_id}")
                continue
            if gap.get("status") != status:
                missing.append(f"ring_manifest:gap_status:{gap_id}={gap.get('status')}")

        notify_prepare_gap = find_gap(ring_manifest, "phase10-notify-prepare-helper")
        if notify_prepare_gap is not None:
            why_now = str(notify_prepare_gap.get("why_now", ""))
            if "num_added" not in why_now:
                missing.append("ring_manifest:notify_prepare_gap:num_added")
            if "16-bit counter" not in why_now:
                missing.append("ring_manifest:notify_prepare_gap:16_bit_counter")

        reset_guard_gap = find_gap(ring_manifest, "phase10-queue-reset-guard-helper")
        if reset_guard_gap is not None:
            why_now = str(reset_guard_gap.get("why_now", ""))
            if "unpublished chains" not in why_now:
                missing.append("ring_manifest:reset_guard_gap:unpublished_chains")
            if "follow-up poll debt" not in why_now:
                missing.append("ring_manifest:reset_guard_gap:follow_up_poll_debt")

        reset_gap = find_gap(ring_manifest, "phase10-queue-reset-helper")
        if reset_gap is not None:
            why_now = str(reset_gap.get("why_now", ""))
            if "drained-queue reset helper" not in why_now:
                missing.append("ring_manifest:reset_gap:drained_queue_reset_helper")
            if "queue shape metadata" not in why_now:
                missing.append("ring_manifest:reset_gap:queue_shape_metadata")

        blocked_ring_gap = find_gap(ring_manifest, "phase10-mmio-lifecycle-and-irq-paths")
        if blocked_ring_gap is not None:
            why_now = str(blocked_ring_gap.get("why_now", ""))
            if "interrupt acknowledgement" not in why_now:
                missing.append("ring_manifest:blocked_gap:interrupt_acknowledgement")
            if "probe or remove lifecycle" not in why_now:
                missing.append("ring_manifest:blocked_gap:probe_or_remove_lifecycle")

    manifest = load_manifest(root, "zigux/tests/phase10_virtio_input_manifest.json")
    if manifest.get("lane_key") != "P10-L13":
        missing.append("manifest:lane_key=P10-L13")
    if manifest.get("phase") != "Phase 10":
        missing.append("manifest:phase=Phase 10")
    if manifest.get("anchor") != "drivers/virtio/virtio_input.c":
        missing.append("manifest:anchor=drivers/virtio/virtio_input.c")
    if not HEX40.fullmatch(str(manifest.get("surveyed_commit", ""))):
        missing.append("manifest:surveyed_commit")

    if manifest.get("roadmap_destinations") != ["drivers/virtio/*.zig", "zigux/helpers/"]:
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
    if not isinstance(gaps, list) or len(gaps) < 13:
        missing.append("manifest:gaps")
    else:
        expected_statuses = {
            "phase10-virtio-input-lab-helper": "starter_landed",
            "phase10-virtio-input-lab-gate": "starter_landed",
            "phase10-virtio-input-survey-gate": "starter_landed",
            "phase10-virtio-input-capability-setup-helper": "starter_landed",
            "phase10-virtio-input-multitouch-slot-helper": "starter_landed",
            "phase10-virtio-input-teardown-observation-helper": "starter_landed",
            "phase10-virtio-input-registration-preflight-helper": "starter_landed",
            "phase10-virtio-input-queue-callback-preflight-helper": "starter_landed",
            "phase10-virtio-input-probe-preflight-helper": "starter_landed",
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
        if starter_count < 9:
            missing.append(f"manifest:starter_count={starter_count}")
        for gap_id, status in expected_statuses.items():
            gap = find_gap(manifest, gap_id)
            if gap is None:
                missing.append(f"manifest:gap:{gap_id}")
                continue
            if gap.get("status") != status:
                missing.append(f"manifest:gap_status:{gap_id}={gap.get('status')}")

        capability_gap = find_gap(manifest, "phase10-virtio-input-capability-setup-helper")
        if capability_gap is not None:
            why_now = str(capability_gap.get("why_now", ""))
            if "bitmap" not in why_now:
                missing.append("manifest:capability_gap:bitmap")
            if "ABS metadata" not in why_now:
                missing.append("manifest:capability_gap:ABS_metadata")

        registration_preflight_gap = find_gap(manifest, "phase10-virtio-input-registration-preflight-helper")
        if registration_preflight_gap is not None:
            why_now = str(registration_preflight_gap.get("why_now", ""))
            if "registration intent" not in why_now:
                missing.append("manifest:registration_preflight_gap:registration_intent")
            if "input_register_device()" not in why_now:
                missing.append("manifest:registration_preflight_gap:input_register_device()")

        ready_gap = find_gap(manifest, "phase10-virtio-input-queue-callback-preflight-helper")
        if ready_gap is not None:
            why_now = str(ready_gap.get("why_now", ""))
            if "registration intent is staged" not in why_now:
                missing.append("manifest:ready_gap:registration_intent_is_staged")
            if "event queue is filled" not in why_now:
                missing.append("manifest:ready_gap:event_queue_is_filled")
            if "status queue is configured" not in why_now:
                missing.append("manifest:ready_gap:status_queue_is_configured")
            if "device is ready" not in why_now:
                missing.append("manifest:ready_gap:device_is_ready")

        probe_gap = find_gap(manifest, "phase10-virtio-input-probe-preflight-helper")
        if probe_gap is not None:
            why_now = str(probe_gap.get("why_now", ""))
            if "registration intent" not in why_now:
                missing.append("manifest:probe_gap:registration_intent")
            if "queue provisioning" not in why_now:
                missing.append("manifest:probe_gap:queue_provisioning")
            if "ready-state gating" not in why_now:
                missing.append("manifest:probe_gap:ready_state_gating")
            if "transport-backed probe handoff" not in why_now:
                missing.append("manifest:probe_gap:transport_backed_probe_handoff")

        blocked_gap = find_gap(manifest, "phase10-virtio-input-registration-lifecycle")
        if blocked_gap is not None:
            why_now = str(blocked_gap.get("why_now", ""))
            if "freeze or restore" not in why_now:
                missing.append("manifest:blocked_gap:freeze_or_restore")
            if "transport-backed queue callbacks" not in why_now:
                missing.append("manifest:blocked_gap:transport_callbacks")

    mmio_manifest = load_manifest(root, "zigux/tests/phase10_virtio_mmio_manifest.json")
    if mmio_manifest.get("lane_key") != "P10-L18":
        missing.append("mmio_manifest:lane_key=P10-L18")
    if mmio_manifest.get("phase") != "Phase 10":
        missing.append("mmio_manifest:phase=Phase 10")
    if mmio_manifest.get("anchor") != "drivers/virtio/virtio_mmio.c":
        missing.append("mmio_manifest:anchor=drivers/virtio/virtio_mmio.c")
    if not HEX40.fullmatch(str(mmio_manifest.get("surveyed_commit", ""))):
        missing.append("mmio_manifest:surveyed_commit")

    if mmio_manifest.get("roadmap_destinations") != ["drivers/virtio/*.zig", "zigux/helpers/"]:
        missing.append("mmio_manifest:roadmap_destinations")

    mmio_survey_summary = mmio_manifest.get("survey_summary")
    if not isinstance(mmio_survey_summary, dict):
        missing.append("mmio_manifest:survey_summary")
    else:
        if mmio_survey_summary.get("preexisting_virtio_ring_zig_present") is not True:
            missing.append("mmio_manifest:preexisting_virtio_ring_zig_present")
        if mmio_survey_summary.get("preexisting_virtio_input_zig_present") is not True:
            missing.append("mmio_manifest:preexisting_virtio_input_zig_present")
        if mmio_survey_summary.get("preexisting_virtio_mmio_zig_present") is not True:
            missing.append("mmio_manifest:preexisting_virtio_mmio_zig_present")

    mmio_gaps = mmio_manifest.get("gaps")
    if not isinstance(mmio_gaps, list) or len(mmio_gaps) < 18:
        missing.append("mmio_manifest:gaps")
    else:
        starter_count = 0
        ready_count = 0
        blocked_count = 0
        for gap in mmio_gaps:
            if not isinstance(gap, dict):
                missing.append("mmio_manifest:gap_object")
                continue
            status = gap.get("status")
            if status == "starter_landed":
                starter_count += 1
            elif status == "ready_next":
                ready_count += 1
            elif status == "blocked_on_risky_transport":
                blocked_count += 1
        if ready_count != 0:
            missing.append(f"mmio_manifest:ready_next_count={ready_count}")
        if blocked_count != 1:
            missing.append(f"mmio_manifest:blocked_count={blocked_count}")
        if starter_count < 17:
            missing.append(f"mmio_manifest:starter_count={starter_count}")

        expected_mmio_statuses = {
            "phase10-virtio-mmio-survey-gate": "starter_landed",
            "phase10-virtio-mmio-slice-note": "starter_landed",
            "phase10-mmio-register-window-helper": "starter_landed",
            "phase10-mmio-queue-register-helper": "starter_landed",
            "phase10-mmio-queue-notify-helper": "starter_landed",
            "phase10-mmio-queue-address-helper": "starter_landed",
            "phase10-mmio-config-window-helper": "starter_landed",
            "phase10-mmio-config-write-helper": "starter_landed",
            "phase10-mmio-interrupt-ack-helper": "starter_landed",
            "phase10-mmio-lifecycle-and-irq-paths": "blocked_on_risky_transport",
        }
        for gap_id, status in expected_mmio_statuses.items():
            gap = find_gap(mmio_manifest, gap_id)
            if gap is None:
                missing.append(f"mmio_manifest:gap:{gap_id}")
                continue
            if gap.get("status") != status:
                missing.append(f"mmio_manifest:gap_status:{gap_id}={gap.get('status')}")

        config_write_gap = find_gap(mmio_manifest, "phase10-mmio-config-write-helper")
        if config_write_gap is not None:
            why_now = str(config_write_gap.get("why_now", ""))
            if "config-write planning helper" not in why_now:
                missing.append("mmio_manifest:config_write_gap:planning_helper")
            if "byte, halfword, and word" not in why_now:
                missing.append("mmio_manifest:config_write_gap:byte_halfword_word")

        interrupt_ack_gap = find_gap(mmio_manifest, "phase10-mmio-interrupt-ack-helper")
        if interrupt_ack_gap is not None:
            why_now = str(interrupt_ack_gap.get("why_now", ""))
            if "interrupt-status acknowledge bookkeeping" not in why_now:
                missing.append("mmio_manifest:interrupt_ack_gap:acknowledge_bookkeeping")
            if "queue and config interrupt bits" not in why_now:
                missing.append("mmio_manifest:interrupt_ack_gap:queue_and_config_bits")

        blocked_mmio_gap = find_gap(mmio_manifest, "phase10-mmio-lifecycle-and-irq-paths")
        if blocked_mmio_gap is not None:
            why_now = str(blocked_mmio_gap.get("why_now", ""))
            if "interrupt acknowledgement" not in why_now:
                missing.append("mmio_manifest:blocked_gap:interrupt_acknowledgement")
            if "queue notify side effects" not in why_now:
                missing.append("mmio_manifest:blocked_gap:queue_notify_side_effects")

    return [], missing


def clone_fixture_root(destination_root: Path) -> None:
    for rel_path in FILES:
        source = ROOT / rel_path
        target = destination_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase10-self-test:{label}:unexpected_missing_files:{','.join(missing_files)}"
        )
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase10-self-test:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_selftest_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        makefile_path = tmp_root / "zigux/Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_self_test_hook",
            tmp_root,
            "make:scripts/zigux/validate-phase10.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Self-test Phase 10 shared validator\n"
                "        run: python3 scripts/zigux/validate-phase10.py --self-test\n\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "workflow_self_test_step",
            tmp_root,
            "workflow:Self-test Phase 10 shared validator",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        ring_manifest_path = tmp_root / "zigux/tests/phase10_virtio_ring_manifest.json"
        original_ring_manifest = ring_manifest_path.read_text(encoding="utf-8")
        ring_manifest_path.write_text(
            original_ring_manifest.replace(
                "\"phase10-queue-reset-helper\"",
                "\"phase10-queue-reset-helper-drift\"",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ring_manifest_reset_gap_id",
            tmp_root,
            "ring_manifest:gap:phase10-queue-reset-helper",
        )
        ring_manifest_path.write_text(original_ring_manifest, encoding="utf-8")

        ring_reset_reuse_path = tmp_root / "zigux/tests/phase10_virtio_ring_reset_reuse.zig"
        original_ring_reset_reuse = ring_reset_reuse_path.read_text(encoding="utf-8")
        ring_reset_reuse_path.write_text(
            original_ring_reset_reuse.replace(
                'test "phase10 virtio ring drained reset clears the broken flag so the queue can be reused" {\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ring_reset_reuse_test",
            tmp_root,
            'ring_reset_reuse_tests:test "phase10 virtio ring drained reset clears the broken flag so the queue can be reused" {',
        )
        ring_reset_reuse_path.write_text(original_ring_reset_reuse, encoding="utf-8")

        ring_survey_path = tmp_root / "Documentation/zigux/phase10-virtio-ring-survey.md"
        original_ring_survey = ring_survey_path.read_text(encoding="utf-8")
        ring_survey_path.write_text(
            original_ring_survey.replace(
                "phase10-mmio-config-write-helper",
                "phase10-mmio-configwrite-helper-drift",
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ring_survey_config_write_marker",
            tmp_root,
            "ring_survey_doc:phase10-mmio-config-write-helper",
        )
        ring_survey_path.write_text(original_ring_survey, encoding="utf-8")

        input_manifest_path = tmp_root / "zigux/tests/phase10_virtio_input_manifest.json"
        original_input_manifest = input_manifest_path.read_text(encoding="utf-8")
        input_manifest_path.write_text(
            original_input_manifest.replace(
                "\"phase10-virtio-input-registration-preflight-helper\"",
                "\"phase10-virtio-input-registration-preflight-drift\"",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "input_manifest_gap_id",
            tmp_root,
            "manifest:gap:phase10-virtio-input-registration-preflight-helper",
        )
        input_manifest_path.write_text(original_input_manifest, encoding="utf-8")

        input_manifest_path.write_text(
            original_input_manifest.replace(
                "\"phase10-virtio-input-queue-callback-preflight-helper\",\n      \"status\": \"starter_landed\"",
                "\"phase10-virtio-input-queue-callback-preflight-helper\",\n      \"status\": \"ready_next\"",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "input_manifest_ready_next_regression",
            tmp_root,
            "manifest:ready_next_count=1",
        )
        input_manifest_path.write_text(original_input_manifest, encoding="utf-8")

        input_manifest_path.write_text(
            original_input_manifest.replace(
                "\"phase10-virtio-input-probe-preflight-helper\"",
                "\"phase10-virtio-input-probe-preflight-helper-drift\"",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "input_manifest_probe_preflight_gap_id",
            tmp_root,
            "manifest:gap:phase10-virtio-input-probe-preflight-helper",
        )
        input_manifest_path.write_text(original_input_manifest, encoding="utf-8")

        mmio_manifest_path = tmp_root / "zigux/tests/phase10_virtio_mmio_manifest.json"
        original_mmio_manifest = mmio_manifest_path.read_text(encoding="utf-8")
        mmio_manifest_path.write_text(
            original_mmio_manifest.replace(
                "\"phase10-mmio-lifecycle-and-irq-paths\"",
                "\"phase10-mmio-lifecycle-and-irq-paths-drift\"",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "mmio_manifest_blocked_gap_id",
            tmp_root,
            "mmio_manifest:gap:phase10-mmio-lifecycle-and-irq-paths",
        )
        mmio_manifest_path.write_text(original_mmio_manifest, encoding="utf-8")

        mmio_manifest_path.write_text(
            original_mmio_manifest.replace(
                "\"phase10-mmio-interrupt-ack-helper\"",
                "\"phase10-mmio-interrupt-ack-helper-drift\"",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "mmio_manifest_interrupt_ack_gap_id",
            tmp_root,
            "mmio_manifest:gap:phase10-mmio-interrupt-ack-helper",
        )
        mmio_manifest_path.write_text(original_mmio_manifest, encoding="utf-8")

        mmio_manifest_path.write_text(
            original_mmio_manifest.replace(
                "\"phase10-mmio-interrupt-ack-helper\",\n      \"status\": \"starter_landed\"",
                "\"phase10-mmio-interrupt-ack-helper\",\n      \"status\": \"ready_next\"",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "mmio_manifest_ready_next_regression",
            tmp_root,
            "mmio_manifest:ready_next_count=1",
        )
        mmio_manifest_path.write_text(original_mmio_manifest, encoding="utf-8")

        scripts_readme_path = tmp_root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "`zigux/tests/phase10_virtio_ring_manifest.json`, ",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_phase10_ring_manifest_entry",
            tmp_root,
            "script_readme:phase10_virtio_ring_manifest.json",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "the landed probe-preflight helper, ",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_probe_preflight_entry",
            tmp_root,
            "script_readme:probe-preflight helper",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "the eleven shared test entrypoints",
                "the nine shared test entrypoints",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_phase10_test_count",
            tmp_root,
            "script_readme:eleven shared test entrypoints",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        tests_readme_path = tmp_root / "zigux/tests/README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- `zigux/tests/phase10_virtio_ring_reset_reuse.zig`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_phase10_ring_reset_reuse_entry",
            tmp_root,
            "tests_readme:zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme + "\nABS_MT_SLOT remains the single ready-next helper step\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_stale_ready_next_marker",
            tmp_root,
            "script_readme:stale_marker:ABS_MT_SLOT remains the single ready-next helper step",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme + "\nthree manifest-backed survey records\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_stale_manifest_count_marker",
            tmp_root,
            "tests_readme:stale_marker:three manifest-backed survey records",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        input_test_path = tmp_root / "zigux/tests/phase10_virtio_input.zig"
        original_input_test = input_test_path.read_text(encoding="utf-8")
        input_test_path.write_text(
            original_input_test.replace(
                'test "phase10 virtio input records probe preflight once registration and queue provisioning converge" {\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "input_probe_preflight_test",
            tmp_root,
            'tests:test "phase10 virtio input records probe preflight once registration and queue provisioning converge" {',
        )
        input_test_path.write_text(original_input_test, encoding="utf-8")

        input_survey_test_path = tmp_root / "zigux/tests/phase10_virtio_input_survey.zig"
        original_input_survey_test = input_survey_test_path.read_text(encoding="utf-8")
        input_survey_test_path.write_text(
            original_input_survey_test.replace(
                'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-probe-preflight-helper")) {',
                'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-probe-preflight-helper-drift")) {',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "input_probe_preflight_survey_test",
            tmp_root,
            'survey_test:if (std.mem.eql(u8, gap.id, "phase10-virtio-input-probe-preflight-helper")) {',
        )
        input_survey_test_path.write_text(original_input_survey_test, encoding="utf-8")

        mmio_test_path = tmp_root / "zigux/tests/phase10_virtio_mmio.zig"
        original_mmio_test = mmio_test_path.read_text(encoding="utf-8")
        mmio_test_path.write_text(
            original_mmio_test.replace(
                'test "phase10 virtio mmio acknowledges only pending bounded interrupt bits" {\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "mmio_interrupt_ack_test",
            tmp_root,
            'mmio_tests:test "phase10 virtio mmio acknowledges only pending bounded interrupt bits" {',
        )
        mmio_test_path.write_text(original_mmio_test, encoding="utf-8")

        doc_readme_path = tmp_root / "Documentation/zigux/README.md"
        original_doc_readme = doc_readme_path.read_text(encoding="utf-8")
        doc_readme_path.write_text(
            original_doc_readme.replace(
                "same nine published Phase 10 docs named by the shared closure packet",
                "same published Phase 10 docs",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "doc_readme_phase10_packet_note",
            tmp_root,
            "doc_readme:same nine published Phase 10 docs named by the shared closure packet",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

    print("PHASE10_VALIDATOR_SELF_TEST=pass")
    print("PHASE10_VALIDATOR_SELF_TEST_CASE_COUNT=21")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 10 virtio lab review packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in validator drift checks against a temporary Phase 10 fixture tree.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_VALIDATION=fail")
        print("MISSING_PHASE10_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_FILES_END")
        return 1
    if missing_markers:
        print("PHASE10_VALIDATION=fail")
        print("MISSING_PHASE10_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_MARKERS_END")
        return 1

    print("PHASE10_VALIDATION=pass")
    print(f"PHASE10_REQUIRED_FILE_COUNT={len(FILES)}")
    print(f"PHASE10_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
