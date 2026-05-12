#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path(__file__).resolve().parent

FILES = [
    "scripts/zigux/check-phase10-mmio-packet.py",
    "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_driver_id.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "drivers/virtio/virtio_mmio.zig",
    "drivers/virtio/virtio_ring_verify.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
]

MARKERS = {
    "scripts/zigux/check-phase10-mmio-freeze-boundary.py": [
        'FREEZE_BOUNDARY_CHECK = "python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py"',
        '"phase10-mmio-lifecycle-and-irq-paths"',
        '"drivers/virtio/virtio_mmio_verify.zig"',
        '"closure_manifest:exact_checks:freeze_boundary_count"',
    ],
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
        "Documentation/zigux/phase10-closure-evidence.md",
        "drivers/virtio/virtio_mmio_verify.zig",
        "zigux/tests/phase10_virtio_mmio.zig",
        "zigux/tests/phase10_virtio_input_probe_preflight.zig",
        "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
        "zigux/tests/phase10_virtio_input_registration_preflight.zig",
        "zigux/tests/phase10_virtio_input_teardown_observation.zig",
        "zigux/tests/phase10_virtio_input_status_drain.zig",
        "make -C zigux phase10-test",
    ],
    "Documentation/zigux/review-checklist.md": [
        "Documentation/zigux/phase10-closure-evidence.md",
        "scripts/zigux/check-phase10-mmio-packet.py",
        "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
        "drivers/virtio/virtio_mmio.zig",
        "drivers/virtio/virtio_mmio_verify.zig",
        "zigux/tests/phase10_virtio_mmio_manifest.json",
        "make -C zigux phase10-test",
        "make -C zigux phase10",
    ],
    "Documentation/zigux/phase10-closure-evidence.md": [
        "Documentation/zigux/review-checklist.md",
        "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
        "drivers/virtio/virtio_mmio_verify.zig",
        "zigux/tests/phase10_virtio_mmio.zig",
        "zigux/tests/phase10_virtio_input_probe_preflight.zig",
        "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
        "zigux/tests/phase10_virtio_input_registration_preflight.zig",
        "zigux/tests/phase10_virtio_input_teardown_observation.zig",
        "zigux/tests/phase10_virtio_input_status_drain.zig",
        "input registration lifecycle parity",
    ],
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": [
        "`P10-L10` MMIO lane owns MMIO helper footing, the risky-transport freeze boundary, and MMIO-local transport posture evidence:",
        "Documentation/zigux/phase10-virtio-mmio-survey.md",
        "zigux/tests/phase10_virtio_mmio_manifest.json",
        "scripts/zigux/check-phase10-mmio-packet.py",
        "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
        "drivers/virtio/virtio_mmio_verify.zig",
        "zigux/tests/phase10_virtio_input_probe_preflight.zig",
        "selected-queue readiness",
    ],
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": [
        "Documentation/zigux/phase10-closure-evidence.md",
        "scripts/zigux/check-phase10-mmio-packet.py",
        "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
        "drivers/virtio/virtio_mmio_verify.zig",
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
        "zigux/tests/phase10_virtio_mmio_manifest.json",
        "zigux/tests/phase10_virtio_mmio_survey.zig",
        "zigux/tests/phase10_virtio_input_probe_preflight.zig",
        "make -C zigux phase10-test",
    ],
    "scripts/zigux/README.md": [
        "check-phase10-mmio-packet.py",
        "check-phase10-mmio-freeze-boundary.py",
        "phase10_virtio_mmio.zig",
        "phase10_virtio_mmio_survey.zig",
        "drivers/virtio/virtio_mmio_verify.zig",
        "phase10_virtio_input_probe_preflight.zig",
        "phase10_virtio_input_queue_callback_preflight.zig",
        "phase10_virtio_input_registration_preflight.zig",
        "phase10_virtio_input_teardown_observation.zig",
        "phase10_virtio_input_status_drain.zig",
        "the virtio mmio packet plus the focused mmio-verify replay",
        "make -C zigux phase10",
    ],
    "zigux/tests/README.md": [
        "phase10_virtio_mmio.zig",
        "phase10_virtio_mmio_survey.zig",
        "phase10_virtio_mmio_manifest.json",
        "phase10_virtio_input_probe_preflight.zig",
    ],
    "zigux/tests/phase10_closure_manifest.json": [
        "zigux/tests/phase10_virtio_core_reset_queue.zig",
        "zigux/tests/phase10_virtio_driver_id.zig",
        "zigux/tests/phase10_virtio_input_probe_preflight.zig",
        "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
        "zigux/tests/phase10_virtio_input_registration_preflight.zig",
        "zigux/tests/phase10_virtio_input_teardown_observation.zig",
        "zigux/tests/phase10_virtio_input_status_drain.zig",
        "drivers/virtio/virtio_mmio_verify.zig",
        "scripts/zigux/check-phase10-mmio-packet.py",
        "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
        "phase10-mmio-lifecycle-and-irq-paths",
    ],
    "zigux/tests/phase10_virtio_core_reset_queue.zig": [
        'test "phase10 virtio core blocks fresh queue registration once reset is required" {',
    ],
    "zigux/tests/phase10_virtio_driver_id.zig": [
        'test "phase10 virtio driver id helper records bounded registration identity strings" {',
    ],
    "zigux/tests/phase10_virtio_input_probe_preflight.zig": [
        'test "phase10 virtio input probe preflight keeps identity visible before queue setup" {',
    ],
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig": [
        'test "phase10 virtio input queue callback preflight reports queue and ready blockers and resets cleanly" {',
    ],
    "zigux/tests/phase10_virtio_input_registration_preflight.zig": [
        'test "phase10 virtio input registration preflight fails closed on incomplete identity before registration handoff" {',
    ],
    "zigux/tests/phase10_virtio_input_teardown_observation.zig": [
        'test "phase10 virtio input teardown observation captures reset-local cleanup cues without widening into remove lifecycle" {',
    ],
    "zigux/tests/phase10_virtio_input_status_drain.zig": [
        'test "phase10 virtio input drains queued status completions without touching suppressed multitouch counters" {',
    ],
    "zigux/tests/phase10_build.zig": [
        "phase10_virtio_mmio_module",
        "../../drivers/virtio/virtio_mmio_verify.zig",
        "phase10_virtio_mmio_survey_module",
        '"phase10-virtio-mmio-tests"',
        '"phase10-virtio-mmio-verify-tests"',
        '"phase10-virtio-mmio-survey-tests"',
        "run_phase10_virtio_mmio_tests.step",
        "run_phase10_virtio_mmio_verify_tests.step",
        "run_phase10_virtio_mmio_survey_tests.step",
    ],
    "zigux/Makefile": [
        "phase10-test:",
        "scripts/zigux/check-phase10-mmio-packet.py --self-test",
        "scripts/zigux/check-phase10-mmio-packet.py",
        "scripts/zigux/check-phase10-mmio-freeze-boundary.py --self-test",
        "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
        "$(ZIG) build test --build-file zigux/tests/phase10_build.zig",
    ],
    "drivers/virtio/virtio_mmio.zig": [
        "pub const ConfigWritePlanSummary = struct {",
        "pub const ConfigWriteDispositionSummary = struct {",
        "pub const FeatureNegotiationSummary = struct {",
        "pub const TransportIdentitySummary = struct {",
        "pub const SelectedQueueReadinessSummary = struct {",
        "pub const ConfiguredQueueCoverageSummary = struct {",
        "pending_config_write: ?ConfigWritePlanSummary = null,",
        "pub fn planConfigWriteOffset(self: *Self, offset: u32, planned_value: u32) !ConfigWritePlanSummary {",
        "self.pending_config_write = plan;",
        "pub fn configWriteDispositionSummary(self: *const Self) !ConfigWriteDispositionSummary {",
        "pub fn featureNegotiationSummary(self: *const Self) FeatureNegotiationSummary {",
        "pub fn transportIdentitySummary(self: *const Self) TransportIdentitySummary {",
        "pub fn selectedQueueReadinessSummary(self: *const Self) !SelectedQueueReadinessSummary {",
        "pub fn configuredQueueCoverageSummary(self: *const Self) ConfiguredQueueCoverageSummary {",
        "pub fn probePreflightSummary(self: *const Self) ProbePreflightSummary {",
        "self.pending_config_write = null;",
        'test "phase10 virtio mmio config-generation bumps clear stale planned config writes" {',
    ],
    "drivers/virtio/virtio_mmio_verify.zig": [
        'test "virtio mmio wrapper-facing probe preflight keeps bounded blockers visible" {',
        'test "virtio mmio wrapper-facing config review stays scoped to the current generation" {',
        'test "virtio mmio wrapper-facing queue coverage review stays within configured queues" {',
        'test "virtio mmio wrapper-facing queue handoff review stays selected-queue local" {',
        "var summary = device.configuredQueueCoverageSummary();",
        "try std.testing.expect(!summary.ready_for_probe_handoff);",
        "try std.testing.expectEqual(@as(u32, 1), disposition.config_generation);",
        "device.bumpConfigGeneration();",
        "try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteDispositionSummary());",
        "try std.testing.expectEqual(@as(usize, 3), summary.handoff_ready_queue_count);",
        "try std.testing.expect(summary.all_configured_queues_ready_for_handoff);",
        "try std.testing.expect(summary.queue_ready_for_handoff);",
    ],
    "zigux/tests/phase10_virtio_mmio.zig": [
        'test "phase10 virtio mmio plans a bounded config-word write without mutating config space" {',
        'test "phase10 virtio mmio summarizes a planned config-word write disposition without mutating config space" {',
        'test "phase10 virtio mmio summarizes bounded feature negotiation before lifecycle work" {',
        'test "phase10 virtio mmio summarizes transport identity before lifecycle work" {',
        'test "phase10 virtio mmio summarizes bounded probe preflight readiness before lifecycle work" {',
        'test "phase10 virtio mmio keeps the legacy probe preflight path ready when transport identity stays aligned" {',
        'test "phase10 virtio mmio marks probe preflight incomplete when identity presence falls away" {',
        'test "phase10 virtio mmio marks probe preflight incomplete when transport identity drifts" {',
        'test "phase10 virtio mmio summarizes selected-queue readiness before queue handoff" {',
        'test "phase10 virtio mmio summarizes configured-queue coverage across the staged queue window" {',
        "var summary = device.configuredQueueCoverageSummary();",
        "try std.testing.expectEqual(@as(usize, 3), summary.handoff_ready_queue_count);",
        "try std.testing.expect(summary.all_configured_queues_ready_for_handoff);",
    ],
    "zigux/tests/phase10_virtio_mmio_survey.zig": [
        'test "phase10 virtio mmio survey manifest records the landed identity-backed packet" {',
        'try std.testing.expectEqualStrings("P10-L10", manifest.lane_key);',
        'try std.testing.expectEqual(@as(usize, 15), manifest.survey_summary.preexisting_phase10_test_files);',
        'try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);',
        'try std.testing.expectEqualStrings("drivers/virtio/*.zig", manifest.roadmap_destinations[0]);',
        'try std.testing.expectEqualStrings("zigux/kernel/", manifest.roadmap_destinations[1]);',
        'try std.testing.expectEqualStrings("zigux/helpers/", manifest.roadmap_destinations[2]);',
        'try std.testing.expectEqualStrings("blocked_on_risky_transport", manifest.risky_transport_posture);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase10_virtio_input_probe_preflight.zig") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase10_virtio_input_registration_preflight.zig") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase10_virtio_input_teardown_observation.zig") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase10_virtio_input_status_drain.zig") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, slice_note, "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, slice_note, "zigux/tests/phase10_virtio_input_registration_preflight.zig") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, slice_note, "zigux/tests/phase10_virtio_input_teardown_observation.zig") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/virtio_ring_verify.zig") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/virtio_input_verify.zig") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "transport-identity summary") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "consumes that identity snapshot") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "selected-queue readiness summary") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "configured-queue coverage summary") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "probe-preflight summary flips from ready to blocked") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, build_file, "../../drivers/virtio/virtio_mmio_verify.zig") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, build_file, "phase10-virtio-mmio-verify-tests") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, build_file, "run_phase10_virtio_mmio_verify_tests.step") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, slice_note, "configured-queue coverage summary") != null);',
        'try std.testing.expect(manifest.survey_summary.preexisting_virtio_mmio_verify_present);',
        'var saw_mmio_configured_queue_coverage = false;',
        'if (std.mem.eql(u8, gap.id, "phase10-mmio-configured-queue-coverage-helper")) {',
        'try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "configured, programmed, ready, and handoff-ready queue counts") != null);',
        'try std.testing.expect(saw_mmio_configured_queue_coverage);',
        'try std.testing.expect(starter_landed_count >= 18);',
    ],
    "Documentation/zigux/phase10-virtio-mmio-slice.md": [
        "one explicit transport-identity summary",
        "one bounded config-write disposition summary",
        "one bounded probe-preflight summary",
        "one bounded selected-queue readiness summary",
        "one bounded configured-queue coverage summary",
        "drivers/virtio/virtio_ring_verify.zig",
        "drivers/virtio/virtio_input_verify.zig",
        "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
        "zigux/tests/phase10_virtio_input_registration_preflight.zig",
        "zigux/tests/phase10_virtio_input_teardown_observation.zig",
        "zigux/tests/phase10_virtio_input_status_drain.zig",
        "zig test zigux/tests/phase10_virtio_mmio.zig",
        "zig test zigux/tests/phase10_virtio_mmio_survey.zig",
    ],
    "Documentation/zigux/phase10-virtio-mmio-survey.md": [
        "PHASE10_STATUS=parked",
        "PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport",
        "fifteen dedicated Phase 10 virtio test or survey files under `zigux/tests/`",
        "phase10-mmio-transport-identity-helper",
        "phase10-mmio-config-write-disposition-helper",
        "phase10-mmio-probe-preflight-helper",
        "phase10-mmio-selected-queue-readiness-helper",
        "phase10-mmio-lifecycle-and-irq-paths",
        "drivers/virtio/virtio_ring_verify.zig",
        "drivers/virtio/virtio_input_verify.zig",
        "zigux/tests/phase10_virtio_input_probe_preflight.zig",
        "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
        "zigux/tests/phase10_virtio_input_registration_preflight.zig",
        "zigux/tests/phase10_virtio_input_teardown_observation.zig",
        "zigux/tests/phase10_virtio_input_status_drain.zig",
        "transport-identity summary",
        "consumes that identity snapshot",
        "selected-queue readiness summary",
        "configured-queue coverage summary",
        "generation-scoped config-review posture",
        "probe-preflight summary flips from ready to blocked",
        "queue-ready-for-handoff posture",
        "zig test zigux/tests/phase10_virtio_mmio.zig",
    ],
}

MANIFEST_SCALARS = {
    "lane_key": "P10-L10",
    "phase": "Phase 10",
    "surveyed_commit": "84f90e23ad1c28ae345905d5293a8c5395f37d43",
    "anchor": "drivers/virtio/virtio_mmio.c",
    "freeze_map": "Documentation/zigux/freeze-map.md",
    "freeze_boundary_status": "aligned",
    "freeze_status_change_claimed": False,
    "risky_transport_posture": "blocked_on_risky_transport",
    "architecture_council_reopen_required": True,
    "architecture_council_reopen_attached": False,
}

EXPECTED_ROADMAP_DESTINATIONS = ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"]
EXPECTED_ALLOWED_EVIDENCE_KINDS = [
    "driver_local_lab_slices",
    "survey_manifests",
    "shared_validation_gates",
]
EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS = [
    "queue_setup_reset_paths",
    "irq_parity",
    "dma_paths",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
]
EXPECTED_SUMMARY = {
    "virtio_mmio_c_lines": 829,
    "preexisting_phase10_test_files": 15,
    "preexisting_virtio_mmio_verify_present": True,
}
EXPECTED_GAPS = {
    "phase10-build-gate": "starter_landed",
    "phase10-virtio-core-lab-starter": "starter_landed",
    "phase10-virtio-ring-survey-gate": "starter_landed",
    "phase10-virtio-ring-lab-helper": "starter_landed",
    "phase10-virtio-ring-slice-note": "starter_landed",
    "phase10-virtio-mmio-survey-gate": "starter_landed",
    "phase10-virtio-mmio-survey-note": "starter_landed",
    "phase10-mmio-register-window-helper": "starter_landed",
    "phase10-mmio-queue-size-helper": "starter_landed",
    "phase10-virtio-mmio-slice-note": "starter_landed",
    "phase10-mmio-feature-word-selector-helper": "starter_landed",
    "phase10-mmio-feature-negotiation-summary-helper": "starter_landed",
    "phase10-mmio-config-window-helper": "starter_landed",
    "phase10-mmio-config-write-plan-helper": "starter_landed",
    "phase10-mmio-transport-identity-helper": "starter_landed",
    "phase10-mmio-probe-preflight-helper": "starter_landed",
    "phase10-mmio-config-write-disposition-helper": "starter_landed",
    "phase10-mmio-selected-queue-readiness-helper": "starter_landed",
    "phase10-mmio-configured-queue-coverage-helper": "starter_landed",
    "phase10-mmio-lifecycle-and-irq-paths": "blocked_on_risky_transport",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    for rel_path, markers in MARKERS.items():
        text = read_text(root, rel_path)
        label = Path(rel_path).name
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{label}:{marker}")

    manifest = json.loads(read_text(root, "zigux/tests/phase10_virtio_mmio_manifest.json"))
    for key, value in MANIFEST_SCALARS.items():
        if manifest.get(key) != value:
            missing_markers.append(f"manifest:{key}={manifest.get(key)!r}")
    if manifest.get("roadmap_destinations") != EXPECTED_ROADMAP_DESTINATIONS:
        missing_markers.append("manifest:roadmap_destinations")
    if manifest.get("allowed_evidence_kinds") != EXPECTED_ALLOWED_EVIDENCE_KINDS:
        missing_markers.append("manifest:allowed_evidence_kinds")
    if manifest.get("forbidden_transport_claims") != EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS:
        missing_markers.append("manifest:forbidden_transport_claims")

    summary = manifest.get("survey_summary", {})
    for key, value in EXPECTED_SUMMARY.items():
        if summary.get(key) != value:
            missing_markers.append(f"manifest:survey_summary:{key}={summary.get(key)!r}")

    gaps = manifest.get("gaps", [])
    if len(gaps) != len(EXPECTED_GAPS):
        missing_markers.append(f"manifest:gaps={len(gaps)}")
    gap_index = {gap.get("id"): gap for gap in gaps if isinstance(gap, dict)}
    for gap_id, status in EXPECTED_GAPS.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            missing_markers.append(f"manifest:missing_gap:{gap_id}")
            continue
        if gap.get("status") != status:
            missing_markers.append(f"manifest:gap_status:{gap_id}={gap.get('status')!r}")

    return missing_files, missing_markers


def write_fixture(root: Path, rel_path: str, content: str) -> None:
    target = root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_fixture() -> dict[str, str]:
    fixture: dict[str, str] = {
        "scripts/zigux/check-phase10-mmio-packet.py": "# synthetic fixture for self-test\n",
        "drivers/virtio/virtio_ring_verify.zig": 'test "virtio ring verify fixture" {}\n',
        "drivers/virtio/virtio_input_verify.zig": 'test "virtio input verify fixture" {}\n',
    }
    for rel_path, markers in MARKERS.items():
        if rel_path in fixture or rel_path == "zigux/tests/phase10_virtio_mmio_manifest.json":
            continue
        fixture[rel_path] = "\n".join(markers) + "\n"
    fixture["zigux/tests/phase10_virtio_mmio_manifest.json"] = json.dumps(
        {
            "lane_key": "P10-L10",
            "phase": "Phase 10",
            "surveyed_commit": "84f90e23ad1c28ae345905d5293a8c5395f37d43",
            "anchor": "drivers/virtio/virtio_mmio.c",
            "freeze_map": "Documentation/zigux/freeze-map.md",
            "freeze_boundary_status": "aligned",
            "freeze_status_change_claimed": False,
            "risky_transport_posture": "blocked_on_risky_transport",
            "architecture_council_reopen_required": True,
            "architecture_council_reopen_attached": False,
            "roadmap_destinations": EXPECTED_ROADMAP_DESTINATIONS,
            "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
            "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
            "survey_summary": {
                "virtio_mmio_c_lines": 829,
                "preexisting_phase10_test_files": 15,
                "preexisting_virtio_mmio_verify_present": True,
            },
            "gaps": [
                {"id": gap_id, "status": status}
                for gap_id, status in EXPECTED_GAPS.items()
            ],
        },
        indent=2,
    ) + "\n"
    return fixture


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_mmio_packet_") as tmp_dir:
        root = Path(tmp_dir)
        fixture = build_fixture()
        for rel_path, content in fixture.items():
            write_fixture(root, rel_path, content)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-mmio-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"markers={','.join(missing_markers) or 'none'}"
            )

        case_count = 0

        def run_missing_case(rel_path: str, old: str, new: str, expected: str) -> None:
            nonlocal case_count
            path = root / rel_path
            original = path.read_text(encoding="utf-8")
            path.write_text(original.replace(old, new, 1), encoding="utf-8")
            _, markers = validate(root)
            if expected not in markers:
                raise SystemExit(f"phase10-mmio-self-test:expected_marker_missing:{expected}")
            path.write_text(original, encoding="utf-8")
            case_count += 1

        def run_manifest_case() -> None:
            nonlocal case_count
            manifest_path = root / "zigux/tests/phase10_virtio_mmio_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for gap in manifest["gaps"]:
                if gap["id"] == "phase10-mmio-configured-queue-coverage-helper":
                    gap["status"] = "ready_next"
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            _, markers = validate(root)
            expected = "manifest:gap_status:phase10-mmio-configured-queue-coverage-helper='ready_next'"
            if expected not in markers:
                raise SystemExit(f"phase10-mmio-self-test:expected_marker_missing:{expected}")
            case_count += 1

        drift_cases = [
            (
                "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
                'FREEZE_BOUNDARY_CHECK = "python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py"',
                'FREEZE_BOUNDARY_CHECK = "python3 scripts/zigux/check-phase10-mmio-freeze-boundary-drift.py"',
                'check-phase10-mmio-freeze-boundary.py:FREEZE_BOUNDARY_CHECK = "python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py"',
            ),
            (
                "Documentation/zigux/review-checklist.md",
                "drivers/virtio/virtio_mmio_verify.zig",
                "drivers/virtio/virtio_mmio_verify_drift.zig",
                "review-checklist.md:drivers/virtio/virtio_mmio_verify.zig",
            ),
            (
                "zigux/tests/phase10_closure_manifest.json",
                "zigux/tests/phase10_virtio_input_status_drain.zig",
                "zigux/tests/phase10_virtio_input_status_only_drain.zig",
                "phase10_closure_manifest.json:zigux/tests/phase10_virtio_input_status_drain.zig",
            ),
            (
                "zigux/tests/phase10_virtio_core_reset_queue.zig",
                'test "phase10 virtio core blocks fresh queue registration once reset is required" {',
                'test "phase10 virtio core reset replay drift" {',
                'phase10_virtio_core_reset_queue.zig:test "phase10 virtio core blocks fresh queue registration once reset is required" {',
            ),
            (
                "zigux/tests/phase10_virtio_input_probe_preflight.zig",
                'test "phase10 virtio input probe preflight keeps identity visible before queue setup" {',
                'test "phase10 virtio input probe preflight drift" {',
                'phase10_virtio_input_probe_preflight.zig:test "phase10 virtio input probe preflight keeps identity visible before queue setup" {',
            ),
            (
                "Documentation/zigux/phase10-virtio-mmio-survey.md",
                "generation-scoped config-review posture",
                "generation-scoped config drift posture",
                "phase10-virtio-mmio-survey.md:generation-scoped config-review posture",
            ),
        ]

        for rel_path, old, new, expected in drift_cases:
            run_missing_case(rel_path, old, new, expected)

        run_manifest_case()

    print("PHASE10_MMIO_PACKET_SELF_TEST=pass")
    print(f"PHASE10_MMIO_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 10 virtio_mmio packet.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in drift checks against a synthetic fixture tree.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
