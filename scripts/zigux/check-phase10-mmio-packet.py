#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

FILES = [
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md",
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "drivers/virtio/virtio_mmio.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "zigux/tests/phase10_build.zig",
]

SURVEY_NOTE_MARKERS = [
    "# Phase 10 Virtio MMIO Survey",
    "PHASE10_STATUS=parked",
    "drivers/virtio/virtio_mmio.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "interrupt-ack disposition review",
    "staged config-write planning",
    "config-write disposition reporting",
    "feature-negotiation deltas",
    "transport identity readback",
    "zigux/tests/phase10_build.zig",
    "zig test zigux/tests/phase10_virtio_mmio_survey.zig",
    "Documentation/zigux/freeze-map.md",
    "this survey stays inside `drivers/virtio/*.zig` and shared validation surfaces.",
    "this survey does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain study-only anchors.",
    "this survey also does not claim ownership of the freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`.",
]

COMPANION_MARKERS = [
    "# Phase 10 virtio MMIO Config-Write Disposition Companion",
    "PHASE10_STATUS=current_head_companion_landed",
    "PHASE10_FAMILY=virtio-mmio",
    "PHASE10_SURFACE=config-write-disposition-observation",
    "PHASE10_PROVENANCE_MODE=dated_master_readback",
    "surveyed against current `master` readback on `2026-05-19`",
    "Current `master` readback keeps this narrower MMIO packet explicit through:",
    "`drivers/virtio/virtio_mmio.zig` carries the richer config-write disposition observation helper",
    "`drivers/virtio/virtio_mmio_verify.zig` keeps the changed-byte-count, interrupt-ack-disposition, and queue-readiness wrapper proof explicit beside the helper",
    "`Documentation/zigux/phase10-virtio-mmio-survey.md` keeps the bounded transport-identity, queue-readiness, interrupt-ack-disposition, feature-negotiation, and config-write-disposition survey aligned with the same blocked lifecycle-and-IRQ boundary",
    "`zigux/tests/phase10_virtio_mmio.zig` keeps the helper-local probe-gating, queue-readiness, interrupt-ack-disposition, feature-negotiation, and config-write-disposition replays explicit",
    "`zigux/tests/phase10_virtio_mmio_survey.zig` rereads the parked survey note together with the shared `zigux/tests/phase10_build.zig` gate",
    "`zigux/tests/phase10_virtio_mmio_manifest.json` now rematerializes as the bounded MMIO manifest companion, keeping the lab gate, survey gate, config-write companion, and slice note explicit beside the helper-local packet",
    "`Documentation/zigux/phase10-virtio-mmio-slice.md` now materializes as the packet-local slice companion, keeping the helper, survey, manifest, and blocked transport boundary aligned beside the config-write detail surface",
]

SLICE_NOTE_MARKERS = [
    "# Phase 10 Virtio MMIO Slice",
    "scripts/zigux/check-phase10-mmio-packet.py",
    "`drivers/virtio/virtio_mmio.zig` aligned with `drivers/virtio/virtio_mmio_verify.zig`",
    "transport-identity readback, probe-preflight gating, selected-queue readiness, interrupt-ack disposition review, staged feature-word negotiation, planning-only config-write observation, and config-write disposition review",
    "interrupt-ack disposition stays bounded to pending, acknowledged, ignored, and remaining bits review, not live IRQ delivery parity",
    "the blocked `phase10-mmio-lifecycle-and-irq-paths` bucket remains outside this slice",
    "`Documentation/zigux/phase10-virtio-mmio-slice.md`",
]

MANIFEST_MARKERS = [
    '"lane_key": "P10-L11"',
    '"freeze_map": "Documentation/zigux/freeze-map.md"',
    '"freeze_boundary_status": "aligned"',
    '"freeze_status_change_claimed": false',
    '"risky_transport_posture": "blocked_on_risky_transport"',
    '"allowed_evidence_kinds": [',
    '"driver_local_lab_slices"',
    '"survey_manifests"',
    '"shared_validation_gates"',
    '"forbidden_transport_claims": [',
    '"queue_setup_reset_paths"',
    '"queue_reset_execution"',
    '"irq_parity"',
    '"dma_paths"',
    '"probe_remove_lifecycle"',
    '"freeze_restore_lifecycle"',
    '"architecture_council_reopen_required": true',
    '"architecture_council_reopen_attached": false',
    '"id": "phase10-mmio-transport-identity-helper"',
    '"id": "phase10-mmio-probe-preflight-helper"',
    '"id": "phase10-mmio-selected-queue-readiness-helper"',
    '"id": "phase10-mmio-interrupt-ack-disposition-helper"',
    '"id": "phase10-mmio-feature-negotiation-summary-helper"',
    '"id": "phase10-mmio-config-write-plan-freshness-helper"',
    '"id": "phase10-mmio-config-write-disposition-helper"',
    '"id": "phase10-mmio-verify-replay"',
    '"id": "phase10-virtio-mmio-lab-gate"',
    '"zigux_destination": "zigux/tests/phase10_virtio_mmio.zig"',
    '"id": "phase10-virtio-mmio-survey-gate"',
    '"zigux_destination": "zigux/tests/phase10_virtio_mmio_survey.zig"',
    '"id": "phase10-virtio-mmio-config-write-disposition-note"',
    '"zigux_destination": "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md"',
    '"id": "phase10-virtio-mmio-slice-note"',
    '"zigux_destination": "Documentation/zigux/phase10-virtio-mmio-slice.md"',
    '"status": "starter_landed"',
]

HELPER_MARKERS = [
    "pub const ConfigWritePlanFreshnessSummary = struct {",
    "pub const ConfigWriteDispositionSummary = struct {",
    "pub const FeatureNegotiationSummary = struct {",
    "pub const TransportIdentitySummary = struct {",
    "pub const ProbePreflightSummary = struct {",
    "pub const SelectedQueueReadinessSummary = struct {",
    "pub const InterruptAckDispositionSummary = struct {",
    "pending_config_write: ?ConfigWritePlanSummary = null,",
    "pub fn bumpConfigGeneration(self: *Self) void {",
    "available_for_disposition = availability == .fresh,",
    "pub fn configWritePlanFreshnessSummary(self: *const Self) ConfigWritePlanFreshnessSummary {",
    "pub fn configWriteDispositionSummary(self: *const Self) !ConfigWriteDispositionSummary {",
    "pub fn featureNegotiationSummary(self: *const Self) FeatureNegotiationSummary {",
    "pub fn transportIdentitySummary(self: *const Self) TransportIdentitySummary {",
    "pub fn probePreflightSummary(self: *const Self) ProbePreflightSummary {",
    "pub fn selectedQueueReadinessSummary(self: *const Self) !SelectedQueueReadinessSummary {",
    "pub fn interruptAckDispositionSummary(",
]

VERIFY_MARKERS = [
    "pub const TransportIdentitySummary = virtio_mmio.TransportIdentitySummary;",
    "pub const ProbePreflightSummary = virtio_mmio.ProbePreflightSummary;",
    "pub const SelectedQueueReadinessSummary = virtio_mmio.SelectedQueueReadinessSummary;",
    "pub const ConfigWritePlanFreshnessSummary = virtio_mmio.ConfigWritePlanFreshnessSummary;",
    "pub const ConfigWriteDispositionSummary = virtio_mmio.ConfigWriteDispositionSummary;",
    "pub const FeatureNegotiationSummary = virtio_mmio.FeatureNegotiationSummary;",
    "pub const InterruptAckDispositionSummary = virtio_mmio.InterruptAckDispositionSummary;",
    "pub fn summarizeFeatureNegotiation(device: *const virtio_mmio.VirtioMmioLab) FeatureNegotiationSummary {",
    "pub fn summarizeConfigWritePlanFreshness(device: *const virtio_mmio.VirtioMmioLab) ConfigWritePlanFreshnessSummary {",
    "pub fn summarizeConfigWriteDisposition(device: *const virtio_mmio.VirtioMmioLab) !ConfigWriteDispositionSummary {",
    "pub fn summarizeInterruptAckDisposition(",
    "pub fn changedByteCount(summary: ConfigWriteDispositionSummary) u3 {",
    "pub fn acknowledgedInterruptCount(summary: InterruptAckDispositionSummary) u6 {",
    "pub fn hasFreshConfigWritePlan(summary: ConfigWritePlanFreshnessSummary) bool {",
    'test "phase10 virtio mmio verify keeps probe wrapper transitions explicit" {',
    'test "phase10 virtio mmio verify keeps queue readiness wrapper below transport claims" {',
    'test "phase10 virtio mmio verify keeps feature negotiation wrapper drift explicit" {',
    'test "phase10 virtio mmio verify keeps config-write plan freshness below config application" {',
    'test "phase10 virtio mmio verify keeps stale config-write freshness visible but unavailable" {',
    'test "phase10 virtio mmio verify keeps interrupt-ack disposition below IRQ-delivery claims" {',
    'test "phase10 virtio mmio verify counts changed config bytes without mutating staged data" {',
]

HELPER_TEST_MARKERS = [
    'test "phase10 virtio mmio keeps probe gating anchored below transport-backed claims" {',
    'test "phase10 virtio mmio keeps selected queue readiness bounded to in-memory register state" {',
    'test "phase10 virtio mmio selected queue readiness keeps per-queue state isolated across selector changes" {',
    "_ = try device.writeRegister(.queue_num, 8);\n    summary = try device.selectedQueueReadinessSummary();\n    try std.testing.expect(summary.queue_size_programmed);\n    try std.testing.expect(!summary.queue_size_matches_advertised);\n    try std.testing.expect(!summary.queue_ready_for_handoff);",
    'test "phase10 virtio mmio records feature mismatches without claiming live negotiation" {',
    'test "phase10 virtio mmio probe preflight keeps queue-window and interrupt-ack blockers explicit" {',
    'test "phase10 virtio mmio keeps interrupt-ack disposition bounded to reviewable queue and config bits" {',
    'test "phase10 virtio mmio keeps config-write plan freshness bounded to staged review state" {',
    'test "phase10 virtio mmio keeps stale config-write plans unavailable after generation drift" {',
    'try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteDispositionSummary());',
    'test "phase10 virtio mmio keeps config-write disposition planning-only across restaging" {',
    'const no_op = try device.configWriteDispositionSummary();',
    'try std.testing.expectEqual(@as(u4, 0), no_op.changed_byte_mask);',
    'try std.testing.expect(!no_op.has_changes);',
    'try std.testing.expect(!summary.bounded_queue_register_window_ready);',
    'try std.testing.expect(!summary.interrupt_ack_ready);',
    'try std.testing.expect(summary.queue_ready_for_handoff);',
]

SURVEY_GATE_MARKERS = [
    'test "phase10 virtio mmio survey note keeps the direct lab gate, packet-local companions, manifest companion, and dedicated survey gate explicit beside the helper-local packet" {',
    'try expectContains(survey_note, "interrupt-ack disposition review");',
    'try expectContains(survey_note, "staged config-write planning");',
    'try expectContains(survey_note, "zigux/tests/phase10_virtio_mmio_survey.zig");',
    'try expectContains(survey_note, "zig test zigux/tests/phase10_virtio_mmio_survey.zig");',
    'try expectContains(build_file, "\\"phase10-virtio-mmio-survey-tests\\"");',
    'try expectContains(build_file, "phase10_virtio_mmio_survey_module");',
    'try expectContains(build_file, "run_phase10_virtio_mmio_survey_tests.step");',
    'test "phase10 virtio mmio survey packet keeps the config-write companion and slice note explicit" {',
    "`zigux/tests/phase10_virtio_mmio_manifest.json` now rematerializes as the bounded MMIO manifest companion",
    "`Documentation/zigux/phase10-virtio-mmio-slice.md` now materializes as the packet-local slice companion",
    "`previous_value` and `planned_value` so a reviewer can compare the staged write against the existing config bytes",
    "`changed_byte_mask` so byte-level deltas are visible without replaying the full word manually",
    "`has_changes` derived from the actual byte-delta mask rather than a blanket true result",
    "`error.ConfigWritePlanUnavailable` when no current staged plan is available",
    'try expectContains(slice_note, "# Phase 10 Virtio MMIO Slice");',
    'try expectContains(slice_note, "scripts/zigux/check-phase10-mmio-packet.py");',
    'try expectContains(slice_note, "planning-only config-write observation");',
    "the blocked `phase10-mmio-lifecycle-and-irq-paths` bucket remains outside this slice",
    'test "phase10 virtio mmio survey gate keeps survey-note lane identity, lane sequencing ownership, helper inventory, and risky transport posture explicit" {',
    'try expectContains(lane_sequencing_note, "MMIO lane `P10-L11` owns the bounded MMIO helper packet");',
    'try expectContains(manifest, "\\"lane_key\\": \\\"P10-L11\\\"");',
    'try expectContains(manifest, "\\"risky_transport_posture\\": \\\"blocked_on_risky_transport\\\"");',
    'try expectContains(manifest, "\\"id\\": \\\"phase10-mmio-interrupt-ack-disposition-helper\\\"");',
    'try expectContains(manifest, "\\"id\\": \\\"phase10-mmio-feature-negotiation-summary-helper\\\"");',
    'try expectContains(manifest, "\\"id\\": \\\"phase10-mmio-config-write-plan-freshness-helper\\\"");',
    'try expectContains(manifest, "\\"id\\": \\\"phase10-virtio-mmio-survey-gate\\\"");',
    'test "phase10 virtio mmio survey gate keeps helper-local queue isolation and probe blockers explicit" {',
    'try expectContains(helper_tests, "test \\\"phase10 virtio mmio selected queue readiness keeps per-queue state isolated across selector changes\\\" {");',
    'try expectContains(helper_tests, "test \\\"phase10 virtio mmio probe preflight keeps queue-window and interrupt-ack blockers explicit\\\" {");',
    'try expectContains(helper_tests, "try std.testing.expect(!summary.bounded_queue_register_window_ready);");',
    'try expectContains(helper_tests, "try std.testing.expect(!summary.interrupt_ack_ready);");',
    'try expectContains(helper_tests, "try std.testing.expect(summary.queue_ready_for_handoff);");',
    'test "phase10 virtio mmio survey note keeps risky transport work blocked" {',
    'try expectContains(survey_note, "transport-backed queue setup or queue reset execution");',
    'try expectContains(survey_note, "shared IRQ delivery parity");',
]

BUILD_MARKERS = [
    "../../drivers/virtio/virtio_mmio.zig",
    "../../drivers/virtio/virtio_mmio_verify.zig",
    '"phase10-virtio-mmio-tests"',
    '"phase10-virtio-mmio-verify-tests"',
    '"phase10-virtio-mmio-survey-tests"',
    "run_phase10_virtio_mmio_tests.step",
    "run_phase10_virtio_mmio_verify_tests.step",
    "run_phase10_virtio_mmio_survey_tests.step",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def validate(root: Path):
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers = []
    check_markers(missing_markers, "survey_note", read_text(root, "Documentation/zigux/phase10-virtio-mmio-survey.md"), SURVEY_NOTE_MARKERS)
    check_markers(missing_markers, "companion_note", read_text(root, "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md"), COMPANION_MARKERS)
    check_markers(missing_markers, "slice_note", read_text(root, "Documentation/zigux/phase10-virtio-mmio-slice.md"), SLICE_NOTE_MARKERS)
    check_markers(missing_markers, "manifest", read_text(root, "zigux/tests/phase10_virtio_mmio_manifest.json"), MANIFEST_MARKERS)
    check_markers(missing_markers, "helper", read_text(root, "drivers/virtio/virtio_mmio.zig"), HELPER_MARKERS)
    check_markers(missing_markers, "verify_helper", read_text(root, "drivers/virtio/virtio_mmio_verify.zig"), VERIFY_MARKERS)
    check_markers(missing_markers, "helper_tests", read_text(root, "zigux/tests/phase10_virtio_mmio.zig"), HELPER_TEST_MARKERS)
    check_markers(missing_markers, "survey_gate", read_text(root, "zigux/tests/phase10_virtio_mmio_survey.zig"), SURVEY_GATE_MARKERS)
    check_markers(missing_markers, "build_file", read_text(root, "zigux/tests/phase10_build.zig"), BUILD_MARKERS)
    return [], missing_markers


def write_fixture_files(root: Path) -> None:
    nl = "\n"
    files = {
        "Documentation/zigux/phase10-virtio-mmio-survey.md": nl.join(SURVEY_NOTE_MARKERS) + nl,
        "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md": nl.join(COMPANION_MARKERS) + nl,
        "Documentation/zigux/phase10-virtio-mmio-slice.md": nl.join(SLICE_NOTE_MARKERS) + nl,
        "drivers/virtio/virtio_mmio.zig": nl.join(HELPER_MARKERS) + nl,
        "drivers/virtio/virtio_mmio_verify.zig": nl.join(VERIFY_MARKERS) + nl,
        "zigux/tests/phase10_virtio_mmio.zig": nl.join(HELPER_TEST_MARKERS) + nl,
        "zigux/tests/phase10_virtio_mmio_manifest.json": nl.join(MANIFEST_MARKERS) + nl,
        "zigux/tests/phase10_virtio_mmio_survey.zig": nl.join(SURVEY_GATE_MARKERS) + nl,
        "zigux/tests/phase10_build.zig": nl.join(BUILD_MARKERS) + nl,
    }
    for rel_path, content in files.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def expect_missing_marker(root: Path, rel_path: str, old: str, new: str, expected: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"phase10-mmio-packet-self-test:unexpected_missing_files:{','.join(missing_files)}")
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"phase10-mmio-packet-self-test:expected={expected}:actual={actual}")
    path.write_text(original, encoding="utf-8")


def expect_missing_file(root: Path, rel_path: str) -> None:
    target = root / rel_path
    original = target.read_text(encoding="utf-8")
    target.unlink()
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(f"phase10-mmio-packet-self-test:unexpected_missing_markers:{','.join(missing_markers)}")
    if rel_path not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(f"phase10-mmio-packet-self-test:expected={rel_path}:actual={actual}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(original, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_mmio_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_files(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit("baseline_failed")

        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-mmio-survey.md", "Documentation/zigux/freeze-map.md", "Documentation/zigux/freeze-map-missing.md", "survey_note:Documentation/zigux/freeze-map.md")
        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-mmio-survey.md", "interrupt-ack disposition review", "interrupt-ack drift", "survey_note:interrupt-ack disposition review")
        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-mmio-survey.md", "staged config-write planning", "staged config-write drift", "survey_note:staged config-write planning")
        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-mmio-survey.md", "this survey does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain study-only anchors.", "this survey now reopens `kernel/workqueue.c`.", "survey_note:this survey does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain study-only anchors.")
        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md", "PHASE10_STATUS=current_head_companion_landed", "PHASE10_STATUS=missing", "companion_note:PHASE10_STATUS=current_head_companion_landed")
        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md", "PHASE10_FAMILY=virtio-mmio", "PHASE10_FAMILY=missing", "companion_note:PHASE10_FAMILY=virtio-mmio")
        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md", "PHASE10_SURFACE=config-write-disposition-observation", "PHASE10_SURFACE=missing", "companion_note:PHASE10_SURFACE=config-write-disposition-observation")
        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md", "PHASE10_PROVENANCE_MODE=dated_master_readback", "PHASE10_PROVENANCE_MODE=missing", "companion_note:PHASE10_PROVENANCE_MODE=dated_master_readback")
        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md", "`zigux/tests/phase10_virtio_mmio_manifest.json` now rematerializes as the bounded MMIO manifest companion, keeping the lab gate, survey gate, config-write companion, and slice note explicit beside the helper-local packet", "`zigux/tests/phase10_virtio_mmio_manifest_missing.json` now rematerializes as the bounded MMIO manifest companion, keeping the lab gate, survey gate, config-write companion, and slice note explicit beside the helper-local packet", "companion_note:`zigux/tests/phase10_virtio_mmio_manifest.json` now rematerializes as the bounded MMIO manifest companion, keeping the lab gate, survey gate, config-write companion, and slice note explicit beside the helper-local packet")
        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md", "`Documentation/zigux/phase10-virtio-mmio-slice.md` now materializes as the packet-local slice companion, keeping the helper, survey, manifest, and blocked transport boundary aligned beside the config-write detail surface", "`Documentation/zigux/phase10-virtio-mmio-slice-missing.md` now materializes as the packet-local slice companion", "companion_note:`Documentation/zigux/phase10-virtio-mmio-slice.md` now materializes as the packet-local slice companion, keeping the helper, survey, manifest, and blocked transport boundary aligned beside the config-write detail surface")
        expect_missing_marker(root, "Documentation/zigux/phase10-virtio-mmio-slice.md", "the blocked `phase10-mmio-lifecycle-and-irq-paths` bucket remains outside this slice", "the blocked `phase10-mmio-lifecycle-and-irq-paths` bucket moved inside this slice", "slice_note:the blocked `phase10-mmio-lifecycle-and-irq-paths` bucket remains outside this slice")
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"lane_key": "P10-L11"', '"lane_key": "P10-L10"', 'manifest:"lane_key": "P10-L11"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"freeze_map": "Documentation/zigux/freeze-map.md"', '"freeze_map": "Documentation/zigux/freeze-map-missing.md"', 'manifest:"freeze_map": "Documentation/zigux/freeze-map.md"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"freeze_boundary_status": "aligned"', '"freeze_boundary_status": "missing"', 'manifest:"freeze_boundary_status": "aligned"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"freeze_status_change_claimed": false', '"freeze_status_change_claimed": true', 'manifest:"freeze_status_change_claimed": false')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"risky_transport_posture": "blocked_on_risky_transport"', '"risky_transport_posture": "missing"', 'manifest:"risky_transport_posture": "blocked_on_risky_transport"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"allowed_evidence_kinds": [', '"allowed_evidence_kinds_missing": [', 'manifest:"allowed_evidence_kinds": [')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"driver_local_lab_slices"', '"driver_local_lab_slices_missing"', 'manifest:"driver_local_lab_slices"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"survey_manifests"', '"survey_manifests_missing"', 'manifest:"survey_manifests"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"shared_validation_gates"', '"shared_validation_gates_missing"', 'manifest:"shared_validation_gates"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"forbidden_transport_claims": [', '"forbidden_transport_claims_missing": [', 'manifest:"forbidden_transport_claims": [')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"queue_setup_reset_paths"', '"queue_setup_reset_paths_missing"', 'manifest:"queue_setup_reset_paths"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"queue_reset_execution"', '"queue_reset_execution_missing"', 'manifest:"queue_reset_execution"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"irq_parity"', '"irq_parity_missing"', 'manifest:"irq_parity"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"dma_paths"', '"dma_paths_missing"', 'manifest:"dma_paths"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"probe_remove_lifecycle"', '"probe_remove_lifecycle_missing"', 'manifest:"probe_remove_lifecycle"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"freeze_restore_lifecycle"', '"freeze_restore_lifecycle_missing"', 'manifest:"freeze_restore_lifecycle"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"architecture_council_reopen_required": true', '"architecture_council_reopen_required": false', 'manifest:"architecture_council_reopen_required": true')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"architecture_council_reopen_attached": false', '"architecture_council_reopen_attached": true', 'manifest:"architecture_council_reopen_attached": false')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"id": "phase10-mmio-transport-identity-helper"', '"id": "phase10-mmio-transport-identity-missing"', 'manifest:"id": "phase10-mmio-transport-identity-helper"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"id": "phase10-mmio-probe-preflight-helper"', '"id": "phase10-mmio-probe-preflight-missing"', 'manifest:"id": "phase10-mmio-probe-preflight-helper"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"id": "phase10-mmio-selected-queue-readiness-helper"', '"id": "phase10-mmio-selected-queue-readiness-missing"', 'manifest:"id": "phase10-mmio-selected-queue-readiness-helper"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"id": "phase10-mmio-interrupt-ack-disposition-helper"', '"id": "phase10-mmio-ack-missing"', 'manifest:"id": "phase10-mmio-interrupt-ack-disposition-helper"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"id": "phase10-mmio-feature-negotiation-summary-helper"', '"id": "phase10-mmio-feature-negotiation-missing"', 'manifest:"id": "phase10-mmio-feature-negotiation-summary-helper"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"id": "phase10-mmio-config-write-plan-freshness-helper"', '"id": "phase10-mmio-config-write-plan-freshness-missing"', 'manifest:"id": "phase10-mmio-config-write-plan-freshness-helper"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"id": "phase10-mmio-config-write-disposition-helper"', '"id": "phase10-mmio-config-write-disposition-missing"', 'manifest:"id": "phase10-mmio-config-write-disposition-helper"')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_manifest.json", '"id": "phase10-mmio-verify-replay"', '"id": "phase10-mmio-verify-missing"', 'manifest:"id": "phase10-mmio-verify-replay"')
        expect_missing_marker(root, "drivers/virtio/virtio_mmio.zig", "available_for_disposition = availability == .fresh,", "available_for_disposition = availability == .stale_generation,", "helper:available_for_disposition = availability == .fresh,")
        expect_missing_marker(root, "drivers/virtio/virtio_mmio.zig", "pub const ConfigWritePlanFreshnessSummary = struct {", "pub const ConfigWritePlanFreshnessMissing = struct {", "helper:pub const ConfigWritePlanFreshnessSummary = struct {")
        expect_missing_marker(root, "drivers/virtio/virtio_mmio.zig", "pub fn interruptAckDispositionSummary(", "pub fn interruptAckDispositionMissing(", "helper:pub fn interruptAckDispositionSummary(")
        expect_missing_marker(root, "drivers/virtio/virtio_mmio_verify.zig", "pub fn summarizeConfigWritePlanFreshness(device: *const virtio_mmio.VirtioMmioLab) ConfigWritePlanFreshnessSummary {", "pub fn summarizeConfigWritePlanFreshnessMissing(device: *const virtio_mmio.VirtioMmioLab) ConfigWritePlanFreshnessSummary {", "verify_helper:pub fn summarizeConfigWritePlanFreshness(device: *const virtio_mmio.VirtioMmioLab) ConfigWritePlanFreshnessSummary {")
        expect_missing_marker(root, "drivers/virtio/virtio_mmio_verify.zig", "pub fn summarizeInterruptAckDisposition(", "pub fn summarizeInterruptAckMissing(", "verify_helper:pub fn summarizeInterruptAckDisposition(")
        expect_missing_marker(root, "drivers/virtio/virtio_mmio_verify.zig", 'test "phase10 virtio mmio verify keeps feature negotiation wrapper drift explicit" {', 'test "phase10 virtio mmio verify keeps feature negotiation drift" {', 'verify_helper:test "phase10 virtio mmio verify keeps feature negotiation wrapper drift explicit" {')
        expect_missing_marker(root, "drivers/virtio/virtio_mmio_verify.zig", 'test "phase10 virtio mmio verify keeps stale config-write freshness visible but unavailable" {', 'test "phase10 virtio mmio verify keeps stale config-write drift" {', 'verify_helper:test "phase10 virtio mmio verify keeps stale config-write freshness visible but unavailable" {')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio.zig", 'test "phase10 virtio mmio keeps interrupt-ack disposition bounded to reviewable queue and config bits" {', 'test "phase10 virtio mmio keeps interrupt-ack drift" {', 'helper_tests:test "phase10 virtio mmio keeps interrupt-ack disposition bounded to reviewable queue and config bits" {')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio.zig", '_ = try device.writeRegister(.queue_num, 8);\n    summary = try device.selectedQueueReadinessSummary();\n    try std.testing.expect(summary.queue_size_programmed);\n    try std.testing.expect(!summary.queue_size_matches_advertised);\n    try std.testing.expect(!summary.queue_ready_for_handoff);', '_ = try device.writeRegister(.queue_num, 8);\n    summary = try device.selectedQueueReadinessSummary();\n    try std.testing.expect(summary.queue_size_programmed);\n    try std.testing.expect(summary.queue_size_matches_advertised);\n    try std.testing.expect(summary.queue_ready_for_handoff);', 'helper_tests:_ = try device.writeRegister(.queue_num, 8);\n    summary = try device.selectedQueueReadinessSummary();\n    try std.testing.expect(summary.queue_size_programmed);\n    try std.testing.expect(!summary.queue_size_matches_advertised);\n    try std.testing.expect(!summary.queue_ready_for_handoff);')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio.zig", 'test "phase10 virtio mmio keeps stale config-write plans unavailable after generation drift" {', 'test "phase10 virtio mmio keeps config-generation drift" {', 'helper_tests:test "phase10 virtio mmio keeps stale config-write plans unavailable after generation drift" {')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio.zig", 'test "phase10 virtio mmio keeps config-write plan freshness bounded to staged review state" {', 'test "phase10 virtio mmio keeps config-write plan drift" {', 'helper_tests:test "phase10 virtio mmio keeps config-write plan freshness bounded to staged review state" {')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio.zig", 'try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteDispositionSummary());', 'try std.testing.expect((try device.configWriteDispositionSummary()).has_changes);', 'helper_tests:try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteDispositionSummary());')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio.zig", 'const no_op = try device.configWriteDispositionSummary();', 'const no_op_missing = try device.configWriteDispositionSummary();', 'helper_tests:const no_op = try device.configWriteDispositionSummary();')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio.zig", 'try std.testing.expectEqual(@as(u4, 0), no_op.changed_byte_mask);', 'try std.testing.expectEqual(@as(u4, 1), no_op.changed_byte_mask);', 'helper_tests:try std.testing.expectEqual(@as(u4, 0), no_op.changed_byte_mask);')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio.zig", 'try std.testing.expect(!no_op.has_changes);', 'try std.testing.expect(no_op.has_changes);', 'helper_tests:try std.testing.expect(!no_op.has_changes);')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio.zig", 'test "phase10 virtio mmio selected queue readiness keeps per-queue state isolated across selector changes" {', 'test "phase10 virtio mmio selected queue readiness drifts across selector changes" {', 'helper_tests:test "phase10 virtio mmio selected queue readiness keeps per-queue state isolated across selector changes" {')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio.zig", 'try std.testing.expect(!summary.bounded_queue_register_window_ready);', 'try std.testing.expect(summary.bounded_queue_register_window_ready);', 'helper_tests:try std.testing.expect(!summary.bounded_queue_register_window_ready);')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_survey.zig", 'try expectContains(survey_note, "interrupt-ack disposition review");', 'try expectContains(survey_note, "interrupt-ack drift");', 'survey_gate:try expectContains(survey_note, "interrupt-ack disposition review");')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_survey.zig", 'try expectContains(survey_note, "staged config-write planning");', 'try expectContains(survey_note, "staged config-write drift");', 'survey_gate:try expectContains(survey_note, "staged config-write planning");')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_survey.zig", 'test "phase10 virtio mmio survey note keeps the direct lab gate, packet-local companions, manifest companion, and dedicated survey gate explicit beside the helper-local packet" {', 'test "phase10 virtio mmio survey note keeps the direct lab gate and dedicated survey gate explicit beside the helper-local packet" {', 'survey_gate:test "phase10 virtio mmio survey note keeps the direct lab gate, packet-local companions, manifest companion, and dedicated survey gate explicit beside the helper-local packet" {')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_survey.zig", 'test "phase10 virtio mmio survey packet keeps the config-write companion and slice note explicit" {', 'test "phase10 virtio mmio survey packet keeps only the config-write companion explicit" {', 'survey_gate:test "phase10 virtio mmio survey packet keeps the config-write companion and slice note explicit" {')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_survey.zig", "`zigux/tests/phase10_virtio_mmio_manifest.json` now rematerializes as the bounded MMIO manifest companion", "`zigux/tests/phase10_virtio_mmio_manifest_missing.json` now rematerializes as the bounded MMIO manifest companion", "survey_gate:`zigux/tests/phase10_virtio_mmio_manifest.json` now rematerializes as the bounded MMIO manifest companion")
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_survey.zig", "`Documentation/zigux/phase10-virtio-mmio-slice.md` now materializes as the packet-local slice companion", "`Documentation/zigux/phase10-virtio-mmio-slice-missing.md` now materializes as the packet-local slice companion", "survey_gate:`Documentation/zigux/phase10-virtio-mmio-slice.md` now materializes as the packet-local slice companion")
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_survey.zig", 'test "phase10 virtio mmio survey gate keeps survey-note lane identity, lane sequencing ownership, helper inventory, and risky transport posture explicit" {', 'test "phase10 virtio mmio survey gate keeps survey-note lane identity explicit" {', 'survey_gate:test "phase10 virtio mmio survey gate keeps survey-note lane identity, lane sequencing ownership, helper inventory, and risky transport posture explicit" {')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_survey.zig", 'try expectContains(lane_sequencing_note, "MMIO lane `P10-L11` owns the bounded MMIO helper packet");', 'try expectContains(lane_sequencing_note, "MMIO lane `P10-L10` owns the bounded MMIO helper packet");', 'survey_gate:try expectContains(lane_sequencing_note, "MMIO lane `P10-L11` owns the bounded MMIO helper packet");')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_survey.zig", 'try expectContains(manifest, "\\"lane_key\\": \\\"P10-L11\\\"");', 'try expectContains(manifest, "\\"lane_key\\": \\\"P10-L10\\\"");', 'survey_gate:try expectContains(manifest, "\\"lane_key\\": \\\"P10-L11\\\"");')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_survey.zig", 'try expectContains(manifest, "\\"risky_transport_posture\\": \\\"blocked_on_risky_transport\\\"");', 'try expectContains(manifest, "\\"risky_transport_posture\\": \\\"missing\\\"");', 'survey_gate:try expectContains(manifest, "\\"risky_transport_posture\\": \\\"blocked_on_risky_transport\\\"");')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_survey.zig", 'try expectContains(manifest, "\\"id\\": \\\"phase10-mmio-feature-negotiation-summary-helper\\\"");', 'try expectContains(manifest, "\\"id\\": \\\"phase10-mmio-feature-negotiation-missing\\\"");', 'survey_gate:try expectContains(manifest, "\\"id\\": \\\"phase10-mmio-feature-negotiation-summary-helper\\\"");')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_survey.zig", 'test "phase10 virtio mmio survey gate keeps helper-local queue isolation and probe blockers explicit" {', 'test "phase10 virtio mmio survey gate keeps helper-local queue isolation explicit" {', 'survey_gate:test "phase10 virtio mmio survey gate keeps helper-local queue isolation and probe blockers explicit" {')
        expect_missing_marker(root, "zigux/tests/phase10_virtio_mmio_survey.zig", 'try expectContains(helper_tests, "try std.testing.expect(!summary.interrupt_ack_ready);");', 'try expectContains(helper_tests, "try std.testing.expect(summary.interrupt_ack_ready);");', 'survey_gate:try expectContains(helper_tests, "try std.testing.expect(!summary.interrupt_ack_ready);");')
        expect_missing_marker(root, "zigux/tests/phase10_build.zig", "run_phase10_virtio_mmio_survey_tests.step", "run_phase10_virtio_mmio_survey_drift.step", "build_file:run_phase10_virtio_mmio_survey_tests.step")
        expect_missing_file(root, "Documentation/zigux/phase10-virtio-mmio-slice.md")

    print("PHASE10_MMIO_PACKET_SELF_TEST=pass")
    print("PHASE10_MMIO_PACKET_SELF_TEST_CASE_COUNT=68")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 10 virtio MMIO packet.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in synthetic drift tests for the packet checker.")
    parser.add_argument("--root", default=str(ROOT), help="Repository root to validate. Defaults to the checker's inferred repo root.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(Path(args.root))
    if missing_files:
        print("PHASE10_MMIO_PACKET=fail")
        print("MISSING_PHASE10_MMIO_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_MMIO_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_MMIO_PACKET=fail")
        print("MISSING_PHASE10_MMIO_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_MMIO_MARKERS_END")
        return 1

    print("PHASE10_MMIO_PACKET=pass")
    print(f"PHASE10_MMIO_REQUIRED_FILE_COUNT={len(FILES)}")
    print("PHASE10_MMIO_REQUIRED_MARKER_COUNT=" + str(len(SURVEY_NOTE_MARKERS) + len(COMPANION_MARKERS) + len(SLICE_NOTE_MARKERS) + len(MANIFEST_MARKERS) + len(HELPER_MARKERS) + len(VERIFY_MARKERS) + len(HELPER_TEST_MARKERS) + len(SURVEY_GATE_MARKERS) + len(BUILD_MARKERS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())