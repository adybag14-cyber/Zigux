#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

MANIFEST_PATH = "zigux/tests/phase10_virtio_ring_manifest.json"
EXPECTED_FREEZE_BOUNDARY_OWNER = "P10-L11"
EXPECTED_MANIFEST_FIELDS = {
    "freeze_status_change_claimed": False,
    "risky_transport_posture": "blocked_on_risky_transport",
    "allowed_evidence_kinds": [
        "driver_local_lab_slices",
        "survey_manifests",
        "shared_validation_gates",
    ],
    "forbidden_transport_claims": [
        "queue_setup_reset_paths",
        "irq_parity",
        "dma_paths",
        "input_registration_lifecycle",
        "probe_remove_lifecycle",
    ],
    "architecture_council_reopen_required": True,
    "architecture_council_reopen_attached": False,
}
EXPECTED_GAP_METADATA = {
    "phase10-build-gate": {
        "kind": "validation",
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase10_build.zig",
    },
    "phase10-virtio-core-lab-starter": {
        "kind": "lab_driver_starter",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio.zig",
    },
    "phase10-virtio-ring-survey-gate": {
        "kind": "validation",
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase10_virtio_ring_survey.zig",
    },
    "phase10-virtio-ring-survey-note": {
        "kind": "documentation",
        "status": "starter_landed",
        "zigux_destination": "Documentation/zigux/phase10-virtio-ring-survey.md",
    },
    "phase10-virtqueue-shape-helper": {
        "kind": "queue_wrapper",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-used-buffer-polling-helper": {
        "kind": "queue_wrapper",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-callback-enable-helper": {
        "kind": "queue_wrapper",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-callback-delay-helper": {
        "kind": "queue_wrapper",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-notify-prepare-helper": {
        "kind": "queue_wrapper",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-notification-data-summary-helper": {
        "kind": "queue_wrapper",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-broken-queue-poll-guard": {
        "kind": "queue_wrapper",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-queue-publish-readiness-helper": {
        "kind": "queue_wrapper",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_ring_publish_readiness.zig",
    },
    "phase10-queue-reset-helper": {
        "kind": "queue_wrapper",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-queue-reset-readiness-helper": {
        "kind": "queue_wrapper",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-ring-publish-readiness-replay": {
        "kind": "validation",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_ring_publish_readiness.zig",
    },
    "phase10-ring-verify-replay": {
        "kind": "validation",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_ring_verify.zig",
    },
    "phase10-virtio-ring-slice-note": {
        "kind": "documentation",
        "status": "starter_landed",
        "zigux_destination": "Documentation/zigux/phase10-virtio-ring-slice.md",
    },
    "phase10-ring-lab-driver-bridge": {
        "kind": "roadmap_gap",
        "status": "blocked_on_risky_transport",
        "zigux_destination": "drivers/virtio/virtio_mmio.zig",
    },
}

REQUIRED_MARKERS = {
    "Documentation/zigux/phase10-virtio-ring-survey.md": [
        "`phase10-virtio-ring-survey-gate`",
        "`zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`",
        "`zigux/tests/phase10_virtio_ring_survey.zig`",
        "`drivers/virtio/virtio_ring_publish_readiness.zig`",
        "`phase10-queue-publish-readiness-helper`",
        "public current-`master` readback rematerializes the broader replay `zigux/tests/phase10_virtio_ring.zig` even though exact direct-path contents reads in this lane still do not",
        "the blocked `phase10-ring-lab-driver-bridge` remains owned by the adjacent `P10-L11` MMIO packet",
    ],
    "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md": [
        "current packet lane on master: `P10-L10`",
        "adjacent freeze-boundary owner: `P10-L11`",
        "public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` even though exact direct-path contents reads in this lane still leave that broader replay outside the queue-local helper ladder",
        "the dedicated ring survey replay `zigux/tests/phase10_virtio_ring_survey.zig` stays part of the same directly readable ring packet",
        "the smallest same-lane follow-through is reminder-surface, checker, or manifest truthfulness work",
    ],
    "Documentation/zigux/phase10-virtio-ring-slice.md": [
        "`drivers/virtio/virtio_ring_publish_readiness.zig`",
        "`zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`",
        "`zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`",
        "`zigux/tests/phase10_virtio_ring_survey.zig`",
        "the publish-readiness wrapper-facing replay",
        "`phase10-queue-publish-readiness-helper`",
        "public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` but it still remains outside exact direct-path current-head evidence in this slice",
        "the notification-data replay and the dedicated survey gate are now landed review surfaces inside this slice",
    ],
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": [
        "ring lane `P10-L10` owns the queue-local wrapper packet",
        "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md",
        "queue-local wrapper reviewability does not drift into MMIO-owned blocked transport claims",
    ],
    "drivers/virtio/virtio_ring.zig": [
        "pub const QueueShapeSummary = struct {",
        "pub const NotificationDataSummary = struct {",
        "pub fn notificationSummary(self: *const Self, queue_index: u16) !QueueNotificationSummary {",
        "pub fn enableCallback(self: *Self, queue_index: u16) !CallbackEnableSummary {",
        "pub fn enableCallbackDelayed(self: *Self, queue_index: u16) !DelayedCallbackSummary {",
        "pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {",
    ],
    "drivers/virtio/virtio_ring_verify.zig": [
        "pub fn summarizeNotificationState(",
        "pub fn summarizeNotificationData(",
        "pub fn summarizeDelayedCallback(",
        "pub fn summarizeResetReadiness(",
        'test "phase10 virtio ring verify keeps notification-state wrapper explicit across publish kick and used replay" {',
        'test "phase10 virtio ring verify keeps notification-data next-avail state reviewable across split packed and reset replay" {',
        'test "phase10 virtio ring verify keeps reset-readiness blockers ordered through queue-local replay" {',
    ],
    "drivers/virtio/virtio_ring_publish_readiness.zig": [
        "pub const QueuePublishReadinessSummary = virtio_ring.QueuePublishReadinessSummary;",
        "pub fn summarizePublishReadiness(",
        "pub fn queueCanPublish(summary: QueuePublishReadinessSummary) bool {",
        "pub fn queueHasPublishCapacity(summary: QueuePublishReadinessSummary) bool {",
        'test "phase10 virtio ring publish-readiness wrapper keeps empty queues publishable" {',
        'test "phase10 virtio ring publish-readiness wrapper blocks full queues until used chains return capacity" {',
        'test "phase10 virtio ring publish-readiness wrapper regains publish capacity before used buffers are polled" {',
        'test "phase10 virtio ring publish-readiness wrapper keeps broken queues fenced even when slots remain" {',
        'test "phase10 virtio ring publish-readiness wrapper falls back to queue-full after a broken full queue is cleared" {',
    ],
    "zigux/tests/phase10_build.zig": [
        '.root_source_file = b.path("phase10_virtio_ring_notification_data_readiness.zig"),',
        '.root_source_file = b.path("../../drivers/virtio/virtio_ring_publish_readiness.zig"),',
        '.root_source_file = b.path("phase10_virtio_ring_survey.zig"),',
        '.name = "phase10-virtio-ring-notification-data-readiness-tests",',
        '.name = "phase10-virtio-ring-publish-readiness-tests",',
        '.name = "phase10-virtio-ring-verify-tests",',
        '.name = "phase10-virtio-ring-prepare-kick-idempotent-tests",',
        '.name = "phase10-virtio-ring-reset-reuse-tests",',
        '.name = "phase10-virtio-ring-broken-queue-queue-discipline-tests",',
        '.name = "phase10-virtio-ring-delayed-callback-budget-tests",',
        '.name = "phase10-virtio-ring-survey-tests",',
        "test_step.dependOn(&run_phase10_virtio_ring_notification_data_readiness_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_publish_readiness_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_survey_tests.step);",
        "Run the live Phase 10 virtio core, input, ring, and MMIO lab validation tests",
    ],
    MANIFEST_PATH: [
        '"lane_key": "P10-L10"',
        '"preexisting_phase10_test_files": 3,',
        '"freeze_status_change_claimed": false,',
        '"risky_transport_posture": "blocked_on_risky_transport",',
        '"allowed_evidence_kinds": [',
        '"driver_local_lab_slices",',
        '"shared_validation_gates"',
        '"forbidden_transport_claims": [',
        '"queue_setup_reset_paths",',
        '"probe_remove_lifecycle"',
        '"architecture_council_reopen_required": true,',
        '"architecture_council_reopen_attached": false,',
        '"id": "phase10-virtio-ring-survey-gate"',
        '"id": "phase10-queue-publish-readiness-helper"',
        '"id": "phase10-queue-reset-helper"',
        '"id": "phase10-queue-reset-readiness-helper"',
        '"id": "phase10-ring-publish-readiness-replay"',
        '"status": "starter_landed"',
        '"id": "phase10-ring-verify-replay"',
        '"id": "phase10-ring-lab-driver-bridge"',
        '"status": "blocked_on_risky_transport"',
    ],
    "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig": [
        'test "phase10 virtio ring notification-data replay keeps split and packed next-avail state explicit" {',
        "const split_summary = try ring.notificationDataSummary(1);",
        "const packed_summary = try ring.notificationDataSummary(2);",
        'test "phase10 virtio ring reset-readiness replay orders blockers before a clean queue reset" {',
        "const reset = try ring.resetQueue(5);",
    ],
    "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig": [
        'test "phase10 virtio ring repeated prepareKick stays idle until new descriptors are published" {',
        "kick_summary = try ring.prepareKick(1);",
        "try std.testing.expect(!kick_summary.needs_kick);",
    ],
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig": [
        'test "phase10 virtio ring reset reuse stays blocked until queue-local reset prerequisites clear and then replays from a clean queue state" {',
        "const reset = try ring.resetQueue(2);",
        "const kick_after_reset = try ring.prepareKick(2);",
    ],
    "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig": [
        'test "phase10 virtio ring broken-queue coverage kicks published work before used accounting and keeps notification history visible" {',
        "try std.testing.expectError(error.QueueResetWhileBroken, ring.resetQueue(3));",
        "const cleared_summary = try ring.clearBroken(3);",
    ],
    "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig": [
        'test "phase10 virtio ring delayed callback budget stays bounded to queue-local replay state" {',
        "try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);",
        "try std.testing.expect(summary.should_poll);",
        "try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(7));",
    ],
    "zigux/tests/phase10_virtio_ring_survey.zig": [
        'try expectContains(survey_note, "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig");',
        'try expectContains(slice_note, "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig");',
        'try expectContains(slice_note, "the notification-data replay and the dedicated survey gate are now landed review surfaces inside this slice");',
        'test "phase10 virtio ring freeze-boundary note keeps risky transport work blocked" {',
        'test "phase10 virtio ring lane sequencing keeps P10-L10 queue ownership explicit beside P10-L11" {',
        "const lane_note = try readRepoRelative(",
        'try expectContains(lane_note, "ring lane `P10-L10` owns the queue-local wrapper packet");',
        'try expectContains(lane_note, "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md");',
        '"queue-local wrapper reviewability does not drift into MMIO-owned blocked transport claims",',
    ],
}

FORBIDDEN_MARKERS = {
    "Documentation/zigux/phase10-virtio-ring-survey.md": [
        "the broader replay `zigux/tests/phase10_virtio_ring.zig` still does not materialize on current `master`",
        "the broader replay `zigux/tests/phase10_virtio_ring.zig`, the focused queue-local replays",
        "the broader ring replay, the queue-local ring helper ladder, the wrapper-facing verify replay",
    ],
    "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md": [
        "the broader ring replay now rematerializes",
        "`zigux/tests/phase10_virtio_ring.zig` joins direct current-head evidence beside the queue-local helper ladder",
        "the broader ring replay `zigux/tests/phase10_virtio_ring.zig` still remains a direct-readback gap beside the queue-local helper ladder",
    ],
    "Documentation/zigux/phase10-virtio-ring-slice.md": [
        "the broader ring replay and the dedicated survey gate are now landed review surfaces inside this slice",
        "the dedicated survey gate is now a landed review surface inside this slice",
        "Fresh direct readback on current `master` now materializes `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`",
        "the broader ring replay still remains outside direct current-head evidence in this slice",
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate_manifest_fields(root: Path) -> list[str]:
    manifest_path = root / MANIFEST_PATH
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    problems: list[str] = []

    for field_name, expected_value in EXPECTED_MANIFEST_FIELDS.items():
        actual_value = manifest.get(field_name)
        if actual_value != expected_value:
            problems.append(f"{MANIFEST_PATH}:{field_name}:{actual_value}")

    freeze_boundary_owner = manifest.get("freeze_boundary_owner_lane")
    if freeze_boundary_owner != EXPECTED_FREEZE_BOUNDARY_OWNER:
        problems.append(
            f"{MANIFEST_PATH}:freeze_boundary_owner_lane:{freeze_boundary_owner}"
        )

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        problems.append(f"{MANIFEST_PATH}:gaps:not_a_list")
        return problems

    gap_by_id = {}
    for gap in gaps:
        if isinstance(gap, dict):
            gap_id = gap.get("id")
            if isinstance(gap_id, str):
                gap_by_id[gap_id] = gap

    for gap_id, expected_fields in EXPECTED_GAP_METADATA.items():
        gap = gap_by_id.get(gap_id)
        if gap is None:
            problems.append(f"{MANIFEST_PATH}:gap_missing:{gap_id}")
            continue
        for field_name, expected_value in expected_fields.items():
            actual_value = gap.get(field_name)
            if actual_value != expected_value:
                problems.append(
                    f"{MANIFEST_PATH}:gap:{gap_id}:{field_name}:{actual_value}"
                )

    return problems


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in REQUIRED_MARKERS if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    problems: list[str] = []
    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                problems.append(f"{rel_path}:{marker}")

    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker in text:
                problems.append(f"{rel_path}:forbidden:{marker}")

    problems.extend(validate_manifest_fields(root))
    return [], problems


def fixture_manifest() -> dict[str, object]:
    return {
        "lane_key": "P10-L10",
        "phase": "Phase 10",
        "surveyed_commit": "fixture",
        "anchor": "drivers/virtio/virtio_ring.c",
        "roadmap_destinations": [
            "drivers/virtio/*.zig",
            "zigux/kernel/",
            "zigux/helpers/",
        ],
        "freeze_map": "Documentation/zigux/freeze-map.md",
        "freeze_boundary_status": "aligned",
        "freeze_status_change_claimed": False,
        "risky_transport_posture": "blocked_on_risky_transport",
        "allowed_evidence_kinds": [
            "driver_local_lab_slices",
            "survey_manifests",
            "shared_validation_gates",
        ],
        "forbidden_transport_claims": [
            "queue_setup_reset_paths",
            "irq_parity",
            "dma_paths",
            "input_registration_lifecycle",
            "probe_remove_lifecycle",
        ],
        "architecture_council_reopen_required": True,
        "architecture_council_reopen_attached": False,
        "freeze_boundary_owner_lane": EXPECTED_FREEZE_BOUNDARY_OWNER,
        "study_only_anchors": [
            "kernel/workqueue.c",
            "kernel/trace/ring_buffer.c",
        ],
        "freeze_in_c_anchors": [
            "kernel/sched/core.c",
            "mm/page_alloc.c",
            "kernel/rcu/tree.c",
            "net/core/skbuff.c",
        ],
        "survey_summary": {
            "virtio_ring_c_lines": 3940,
            "preexisting_phase10_test_files": 3,
            "preexisting_virtio_core_zig_present": True,
            "preexisting_phase10_build_present": True,
            "preexisting_phase10_core_doc_present": False,
            "preexisting_virtio_ring_zig_present": True,
            "preexisting_virtio_ring_doc_present": True,
            "preexisting_ring_verify_present": True,
            "preexisting_ring_publish_readiness_present": True,
        },
        "gaps": [
            {"id": "phase10-build-gate", "status": "starter_landed", "kind": "validation", "zigux_destination": "zigux/tests/phase10_build.zig"},
            {"id": "phase10-virtio-core-lab-starter", "status": "starter_landed", "kind": "lab_driver_starter", "zigux_destination": "drivers/virtio/virtio.zig"},
            {"id": "phase10-virtio-ring-survey-gate", "status": "starter_landed", "kind": "validation", "zigux_destination": "zigux/tests/phase10_virtio_ring_survey.zig"},
            {"id": "phase10-virtio-ring-survey-note", "status": "starter_landed", "kind": "documentation", "zigux_destination": "Documentation/zigux/phase10-virtio-ring-survey.md"},
            {"id": "phase10-virtqueue-shape-helper", "status": "starter_landed", "kind": "queue_wrapper", "zigux_destination": "drivers/virtio/virtio_ring.zig"},
            {"id": "phase10-used-buffer-polling-helper", "status": "starter_landed", "kind": "queue_wrapper", "zigux_destination": "drivers/virtio/virtio_ring.zig"},
            {"id": "phase10-callback-enable-helper", "status": "starter_landed", "kind": "queue_wrapper", "zigux_destination": "drivers/virtio/virtio_ring.zig"},
            {"id": "phase10-callback-delay-helper", "status": "starter_landed", "kind": "queue_wrapper", "zigux_destination": "drivers/virtio/virtio_ring.zig"},
            {"id": "phase10-notify-prepare-helper", "status": "starter_landed", "kind": "queue_wrapper", "zigux_destination": "drivers/virtio/virtio_ring.zig"},
            {"id": "phase10-notification-data-summary-helper", "status": "starter_landed", "kind": "queue_wrapper", "zigux_destination": "drivers/virtio/virtio_ring.zig"},
            {"id": "phase10-broken-queue-poll-guard", "status": "starter_landed", "kind": "queue_wrapper", "zigux_destination": "drivers/virtio/virtio_ring.zig"},
            {"id": "phase10-queue-publish-readiness-helper", "status": "starter_landed", "kind": "queue_wrapper", "zigux_destination": "drivers/virtio/virtio_ring_publish_readiness.zig"},
            {"id": "phase10-queue-reset-helper", "status": "starter_landed", "kind": "queue_wrapper", "zigux_destination": "drivers/virtio/virtio_ring.zig"},
            {"id": "phase10-queue-reset-readiness-helper", "status": "starter_landed", "kind": "queue_wrapper", "zigux_destination": "drivers/virtio/virtio_ring.zig"},
            {"id": "phase10-ring-publish-readiness-replay", "status": "starter_landed", "kind": "validation", "zigux_destination": "drivers/virtio/virtio_ring_publish_readiness.zig"},
            {"id": "phase10-ring-verify-replay", "status": "starter_landed", "kind": "validation", "zigux_destination": "drivers/virtio/virtio_ring_verify.zig"},
            {"id": "phase10-virtio-ring-slice-note", "status": "starter_landed", "kind": "documentation", "zigux_destination": "Documentation/zigux/phase10-virtio-ring-slice.md"},
            {"id": "phase10-ring-lab-driver-bridge", "status": "blocked_on_risky_transport", "kind": "roadmap_gap", "zigux_destination": "drivers/virtio/virtio_mmio.zig"},
        ],
    }


def write_fixture(root: Path) -> None:
    for rel_path, markers in REQUIRED_MARKERS.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if rel_path == MANIFEST_PATH:
            target.write_text(json.dumps(fixture_manifest(), indent=2) + "\n", encoding="utf-8")
        else:
            target.write_text("\n".join(markers) + "\n", encoding="utf-8")


def expect_missing_marker(root: Path, rel_path: str, marker: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(marker, "__removed__", 1), encoding="utf-8")
    _, problems = validate(root)
    expected = f"{rel_path}:{marker}"
    if expected not in problems:
        actual = ",".join(problems) if problems else "none"
        raise SystemExit(f"phase10-ring-self-test:expected={expected}:actual={actual}")
    path.write_text(original, encoding="utf-8")


def expect_forbidden_marker(root: Path, rel_path: str, marker: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original + marker + "\n", encoding="utf-8")
    _, problems = validate(root)
    expected = f"{rel_path}:forbidden:{marker}"
    if expected not in problems:
        actual = ",".join(problems) if problems else "none"
        raise SystemExit(f"phase10-ring-self-test:expected={expected}:actual={actual}")
    path.write_text(original, encoding="utf-8")


def expect_missing_file(root: Path, rel_path: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.unlink()
    missing_files, problems = validate(root)
    if problems:
        actual = ",".join(problems)
        raise SystemExit(f"phase10-ring-self-test:unexpected_problems={actual}")
    if rel_path not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(f"phase10-ring-self-test:expected={rel_path}:actual={actual}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(original, encoding="utf-8")


def expect_manifest_field_drift(root: Path, old: str, new: str, expected: str) -> None:
    path = root / MANIFEST_PATH
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    _, problems = validate(root)
    if expected not in problems:
        actual = ",".join(problems) if problems else "none"
        raise SystemExit(f"phase10-ring-self-test:expected={expected}:actual={actual}")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_ring_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, problems = validate(root)
        if missing_files or problems:
            raise SystemExit(
                "phase10-ring-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"problems={','.join(problems) or 'none'}"
            )

        cases = [
            ("Documentation/zigux/phase10-virtio-ring-survey.md", "`zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`"),
            ("Documentation/zigux/phase10-virtio-ring-survey.md", "`drivers/virtio/virtio_ring_publish_readiness.zig`"),
            ("Documentation/zigux/phase10-virtio-ring-survey.md", "public current-`master` readback rematerializes the broader replay `zigux/tests/phase10_virtio_ring.zig` even though exact direct-path contents reads in this lane still do not"),
            ("Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md", "public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` even though exact direct-path contents reads in this lane still leave that broader replay outside the queue-local helper ladder"),
            ("Documentation/zigux/phase10-virtio-ring-slice.md", "`drivers/virtio/virtio_ring_publish_readiness.zig`"),
            ("Documentation/zigux/phase10-virtio-ring-slice.md", "`zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`"),
            ("Documentation/zigux/phase10-virtio-ring-slice.md", "the notification-data replay and the dedicated survey gate are now landed review surfaces inside this slice"),
            ("Documentation/zigux/phase10-virtio-ring-slice.md", "public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` but it still remains outside exact direct-path current-head evidence in this slice"),
            ("Documentation/zigux/phase10-virtio-driver-lane-sequencing.md", "ring lane `P10-L10` owns the queue-local wrapper packet"),
            ("Documentation/zigux/phase10-virtio-driver-lane-sequencing.md", "queue-local wrapper reviewability does not drift into MMIO-owned blocked transport claims"),
            ("drivers/virtio/virtio_ring.zig", "pub fn enableCallback(self: *Self, queue_index: u16) !CallbackEnableSummary {"),
            ("drivers/virtio/virtio_ring_verify.zig", "pub fn summarizeNotificationState("),
            ("drivers/virtio/virtio_ring_verify.zig", 'test "phase10 virtio ring verify keeps notification-state wrapper explicit across publish kick and used replay" {'),
            ("drivers/virtio/virtio_ring_publish_readiness.zig", "pub fn summarizePublishReadiness("),
            ("drivers/virtio/virtio_ring_publish_readiness.zig", 'test "phase10 virtio ring publish-readiness wrapper keeps broken queues fenced even when slots remain" {'),
            ("drivers/virtio/virtio_ring_publish_readiness.zig", 'test "phase10 virtio ring publish-readiness wrapper regains publish capacity before used buffers are polled" {'),
            ("drivers/virtio/virtio_ring_publish_readiness.zig", 'test "phase10 virtio ring publish-readiness wrapper falls back to queue-full after a broken full queue is cleared" {'),
            ("zigux/tests/phase10_build.zig", '.root_source_file = b.path("../../drivers/virtio/virtio_ring_publish_readiness.zig"),'),
            ("zigux/tests/phase10_build.zig", '.name = "phase10-virtio-ring-publish-readiness-tests",'),
            ("zigux/tests/phase10_build.zig", '.name = "phase10-virtio-ring-notification-data-readiness-tests",'),
            ("zigux/tests/phase10_build.zig", "test_step.dependOn(&run_phase10_virtio_ring_publish_readiness_tests.step);"),
            ("zigux/tests/phase10_build.zig", "test_step.dependOn(&run_phase10_virtio_ring_notification_data_readiness_tests.step);"),
            ("zigux/tests/phase10_virtio_ring_notification_data_readiness.zig", "const packed_summary = try ring.notificationDataSummary(2);"),
            ("zigux/tests/phase10_virtio_ring_survey.zig", 'try expectContains(survey_note, "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig");'),
            ("zigux/tests/phase10_virtio_ring_survey.zig", 'try expectContains(slice_note, "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig");'),
            ("zigux/tests/phase10_virtio_ring_survey.zig", 'try expectContains(slice_note, "the notification-data replay and the dedicated survey gate are now landed review surfaces inside this slice");'),
            ("zigux/tests/phase10_virtio_ring_survey.zig", 'test "phase10 virtio ring lane sequencing keeps P10-L10 queue ownership explicit beside P10-L11" {'),
            ("zigux/tests/phase10_virtio_ring_survey.zig", 'try expectContains(lane_note, "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md");'),
            ("zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig", "try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(7));"),
        ]
        for rel_path, marker in cases:
            expect_missing_marker(root, rel_path, marker)

        forbidden_cases = [
            ("Documentation/zigux/phase10-virtio-ring-survey.md", "the broader replay `zigux/tests/phase10_virtio_ring.zig` still does not materialize on current `master`"),
            ("Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md", "the broader ring replay now rematerializes"),
            ("Documentation/zigux/phase10-virtio-ring-slice.md", "the broader ring replay and the dedicated survey gate are now landed review surfaces inside this slice"),
            ("Documentation/zigux/phase10-virtio-ring-slice.md", "the dedicated survey gate is now a landed review surface inside this slice"),
        ]
        for rel_path, marker in forbidden_cases:
            expect_forbidden_marker(root, rel_path, marker)

        manifest_field_cases = [
            ('"freeze_status_change_claimed": false', '"freeze_status_change_claimed": true', f"{MANIFEST_PATH}:freeze_status_change_claimed:True"),
            ('"risky_transport_posture": "blocked_on_risky_transport"', '"risky_transport_posture": "starter_landed"', f"{MANIFEST_PATH}:risky_transport_posture:starter_landed"),
            ('"allowed_evidence_kinds": [\n    "driver_local_lab_slices",\n    "survey_manifests",\n    "shared_validation_gates"\n  ]', '"allowed_evidence_kinds": [\n    "driver_local_lab_slices"\n  ]', f"{MANIFEST_PATH}:allowed_evidence_kinds:['driver_local_lab_slices']"),
            ('"forbidden_transport_claims": [\n    "queue_setup_reset_paths",\n    "irq_parity",\n    "dma_paths",\n    "input_registration_lifecycle",\n    "probe_remove_lifecycle"\n  ]', '"forbidden_transport_claims": [\n    "queue_setup_reset_paths"\n  ]', f"{MANIFEST_PATH}:forbidden_transport_claims:['queue_setup_reset_paths']"),
            ('"architecture_council_reopen_required": true', '"architecture_council_reopen_required": false', f"{MANIFEST_PATH}:architecture_council_reopen_required:False"),
            ('"architecture_council_reopen_attached": false', '"architecture_council_reopen_attached": true', f"{MANIFEST_PATH}:architecture_council_reopen_attached:True"),
            (f'"freeze_boundary_owner_lane": "{EXPECTED_FREEZE_BOUNDARY_OWNER}"', '"freeze_boundary_owner_lane": "P10-L12"', f"{MANIFEST_PATH}:freeze_boundary_owner_lane:P10-L12"),
            ('"id": "phase10-build-gate",\n      "status": "starter_landed",\n      "kind": "validation"', '"id": "phase10-build-gate",\n      "status": "starter_landed",\n      "kind": "lab_driver_starter"', f"{MANIFEST_PATH}:gap:phase10-build-gate:kind:lab_driver_starter"),
            ('"id": "phase10-virtio-core-lab-starter",\n      "status": "starter_landed",\n      "kind": "lab_driver_starter"', '"id": "phase10-virtio-core-lab-starter",\n      "status": "starter_landed",\n      "kind": "validation"', f"{MANIFEST_PATH}:gap:phase10-virtio-core-lab-starter:kind:validation"),
            ('"id": "phase10-virtio-ring-survey-note",\n      "status": "starter_landed",\n      "kind": "documentation"', '"id": "phase10-virtio-ring-survey-note",\n      "status": "starter_landed",\n      "kind": "validation"', f"{MANIFEST_PATH}:gap:phase10-virtio-ring-survey-note:kind:validation"),
            ('"id": "phase10-virtqueue-shape-helper",\n      "status": "starter_landed",\n      "kind": "queue_wrapper",\n      "zigux_destination": "drivers/virtio/virtio_ring.zig"', '"id": "phase10-virtqueue-shape-helper",\n      "status": "starter_landed",\n      "kind": "queue_wrapper",\n      "zigux_destination": "drivers/virtio/virtio_ring_shape_wrong.zig"', f"{MANIFEST_PATH}:gap:phase10-virtqueue-shape-helper:zigux_destination:drivers/virtio/virtio_ring_shape_wrong.zig"),
            ('"id": "phase10-used-buffer-polling-helper",\n      "status": "starter_landed",\n      "kind": "queue_wrapper",\n      "zigux_destination": "drivers/virtio/virtio_ring.zig"', '"id": "phase10-used-buffer-polling-helper",\n      "status": "starter_landed",\n      "kind": "validation",\n      "zigux_destination": "drivers/virtio/virtio_ring.zig"', f"{MANIFEST_PATH}:gap:phase10-used-buffer-polling-helper:kind:validation"),
            ('"id": "phase10-callback-enable-helper",\n      "status": "starter_landed",\n      "kind": "queue_wrapper",\n      "zigux_destination": "drivers/virtio/virtio_ring.zig"', '"id": "phase10-callback-enable-helper",\n      "status": "starter_landed",\n      "kind": "validation",\n      "zigux_destination": "drivers/virtio/virtio_ring.zig"', f"{MANIFEST_PATH}:gap:phase10-callback-enable-helper:kind:validation"),
            ('"id": "phase10-callback-delay-helper",\n      "status": "starter_landed",\n      "kind": "queue_wrapper",\n      "zigux_destination": "drivers/virtio/virtio_ring.zig"', '"id": "phase10-callback-delay-helper",\n      "status": "starter_landed",\n      "kind": "validation",\n      "zigux_destination": "drivers/virtio/virtio_ring.zig"', f"{MANIFEST_PATH}:gap:phase10-callback-delay-helper:kind:validation"),
            ('"id": "phase10-notify-prepare-helper",\n      "status": "starter_landed",\n      "kind": "queue_wrapper",\n      "zigux_destination": "drivers/virtio/virtio_ring.zig"', '"id": "phase10-notify-prepare-helper",\n      "status": "starter_landed",\n      "kind": "validation",\n      "zigux_destination": "drivers/virtio/virtio_ring.zig"', f"{MANIFEST_PATH}:gap:phase10-notify-prepare-helper:kind:validation"),
            ('"id": "phase10-notification-data-summary-helper",\n      "status": "starter_landed",\n      "kind": "queue_wrapper",\n      "zigux_destination": "drivers/virtio/virtio_ring.zig"', '"id": "phase10-notification-data-summary-helper",\n      "status": "starter_landed",\n      "kind": "validation",\n      "zigux_destination": "drivers/virtio/virtio_ring.zig"', f"{MANIFEST_PATH}:gap:phase10-notification-data-summary-helper:kind:validation"),
            ('"id": "phase10-broken-queue-poll-guard",\n      "status": "starter_landed",\n      "kind": "queue_wrapper",\n      "zigux_destination": "drivers/virtio/virtio_ring.zig"', '"id": "phase10-broken-queue-poll-guard",\n      "status": "starter_landed",\n      "kind": "validation",\n      "zigux_destination": "drivers/virtio/virtio_ring.zig"', f"{MANIFEST_PATH}:gap:phase10-broken-queue-poll-guard:kind:validation"),
            ('"id": "phase10-queue-publish-readiness-helper",\n      "status": "starter_landed",\n      "kind": "queue_wrapper"', '"id": "phase10-queue-publish-readiness-helper",\n      "status": "starter_landed",\n      "kind": "validation"', f"{MANIFEST_PATH}:gap:phase10-queue-publish-readiness-helper:kind:validation"),
            ('"id": "phase10-ring-verify-replay",\n      "status": "starter_landed",\n      "kind": "validation",\n      "zigux_destination": "drivers/virtio/virtio_ring_verify.zig"', '"id": "phase10-ring-verify-replay",\n      "status": "starter_landed",\n      "kind": "validation",\n      "zigux_destination": "drivers/virtio/virtio_ring_wrong_verify.zig"', f"{MANIFEST_PATH}:gap:phase10-ring-verify-replay:zigux_destination:drivers/virtio/virtio_ring_wrong_verify.zig"),
            ('"id": "phase10-virtio-ring-slice-note",\n      "status": "starter_landed",\n      "kind": "documentation",\n      "zigux_destination": "Documentation/zigux/phase10-virtio-ring-slice.md"', '"id": "phase10-virtio-ring-slice-note",\n      "status": "starter_landed",\n      "kind": "documentation",\n      "zigux_destination": "Documentation/zigux/phase10-virtio-ring-slice-drift.md"', f"{MANIFEST_PATH}:gap:phase10-virtio-ring-slice-note:zigux_destination:Documentation/zigux/phase10-virtio-ring-slice-drift.md"),
            ('"id": "phase10-ring-lab-driver-bridge",\n      "status": "blocked_on_risky_transport",\n      "kind": "roadmap_gap"', '"id": "phase10-ring-lab-driver-bridge",\n      "status": "blocked_on_risky_transport",\n      "kind": "queue_wrapper"', f"{MANIFEST_PATH}:gap:phase10-ring-lab-driver-bridge:kind:queue_wrapper"),
        ]
        for old, new, expected in manifest_field_cases:
            expect_manifest_field_drift(root, old, new, expected)

        expect_missing_file(root, "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig")
        expect_missing_file(root, "drivers/virtio/virtio_ring_publish_readiness.zig")
        expect_missing_file(root, "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md")

    print("PHASE10_RING_PACKET_SELF_TEST=pass")
    print(f"PHASE10_RING_PACKET_SELF_TEST_CASE_COUNT={len(cases) + len(forbidden_cases) + len(manifest_field_cases) + 3}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current directly re-readable Phase 10 virtio ring packet.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, problems = validate(Path(args.root))
    if missing_files:
        print("PHASE10_RING_PACKET=fail")
        print("MISSING_PHASE10_RING_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_RING_FILES_END")
        return 1

    if problems:
        print("PHASE10_RING_PACKET=fail")
        print("MISSING_PHASE10_RING_MARKERS_START")
        for item in problems:
            print(item)
        print("MISSING_PHASE10_RING_MARKERS_END")
        return 1

    required_marker_count = sum(len(markers) for markers in REQUIRED_MARKERS.values())
    forbidden_marker_count = sum(len(markers) for markers in FORBIDDEN_MARKERS.values())
    print("PHASE10_RING_PACKET=pass")
    print(f"PHASE10_RING_REQUIRED_FILE_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE10_RING_REQUIRED_MARKER_COUNT={required_marker_count}")
    print(f"PHASE10_RING_FORBIDDEN_MARKER_COUNT={forbidden_marker_count}")
    print(f"PHASE10_RING_EXPECTED_GAP_METADATA_COUNT={len(EXPECTED_GAP_METADATA)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
