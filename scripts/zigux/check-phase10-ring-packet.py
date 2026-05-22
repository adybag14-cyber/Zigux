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
    "lane_key": "P10-L10",
    "phase": "Phase 10",
    "anchor": "drivers/virtio/virtio_ring.c",
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
    "phase10-build-gate": ("validation", "starter_landed", "zigux/tests/phase10_build.zig"),
    "phase10-virtio-core-lab-starter": ("lab_driver_starter", "starter_landed", "drivers/virtio/virtio.zig"),
    "phase10-virtio-ring-survey-gate": ("validation", "starter_landed", "zigux/tests/phase10_virtio_ring_survey.zig"),
    "phase10-virtio-ring-survey-note": ("documentation", "starter_landed", "Documentation/zigux/phase10-virtio-ring-survey.md"),
    "phase10-virtqueue-shape-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-used-buffer-polling-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-callback-enable-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-callback-delay-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-notify-prepare-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-notification-data-summary-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-broken-queue-poll-guard": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-queue-publish-readiness-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring_publish_readiness.zig"),
    "phase10-queue-reset-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-queue-reset-readiness-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-ring-publish-readiness-replay": ("validation", "starter_landed", "drivers/virtio/virtio_ring_publish_readiness.zig"),
    "phase10-ring-verify-replay": ("validation", "starter_landed", "drivers/virtio/virtio_ring_verify.zig"),
    "phase10-virtio-ring-slice-note": ("documentation", "starter_landed", "Documentation/zigux/phase10-virtio-ring-slice.md"),
    "phase10-ring-lab-driver-bridge": ("roadmap_gap", "blocked_on_risky_transport", "drivers/virtio/virtio_mmio.zig"),
}

REQUIRED_MARKERS = {
    "Documentation/zigux/phase10-virtio-ring-survey.md": [
        "lane: `P10-L10`",
        "`phase10-virtio-ring-survey-gate`",
        "`drivers/virtio/virtio_ring_publish_readiness.zig`",
        "`zigux/tests/phase10_virtio_ring.zig`",
        "`zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`",
        "`zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`",
        "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
        "`zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`",
        "`zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`",
        "direct contents reads rematerialize `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, the broader replay `zigux/tests/phase10_virtio_ring.zig`",
        "the blocked `phase10-ring-lab-driver-bridge` remains owned by the adjacent `P10-L11` MMIO packet",
    ],
    "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md": [
        "current packet lane on master: `P10-L10`",
        "adjacent freeze-boundary owner: `P10-L11`",
        "direct current-head readback now keeps the broader ring replay `zigux/tests/phase10_virtio_ring.zig` inside the same ring packet as the queue-local helper ladder",
        "the publish-readiness helper `drivers/virtio/virtio_ring_publish_readiness.zig`, the notification-data replay `zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`, and the dedicated ring survey replay `zigux/tests/phase10_virtio_ring_survey.zig` stay part of the same directly readable ring packet",
        "the smallest same-lane follow-through is reminder-surface, checker, or manifest truthfulness work",
    ],
    "Documentation/zigux/phase10-virtio-ring-slice.md": [
        "`drivers/virtio/virtio_ring_publish_readiness.zig`",
        "`zigux/tests/phase10_virtio_ring.zig`",
        "`zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`",
        "`zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`",
        "`zigux/tests/phase10_virtio_ring_survey.zig`",
        "the broader ring replay `zigux/tests/phase10_virtio_ring.zig` now sits beside that queue-local helper ladder as direct current-head evidence in this slice",
        "the notification-data replay and the dedicated survey gate are now landed review surfaces inside this slice",
    ],
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": [
        "`scripts/zigux/check-phase10-ring-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, `scripts/zigux/check-phase10-mmio-packet.py`",
        "`drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`",
        "Keep the queue-local `P10-L10` ring freeze-boundary packet distinct from the bounded `P10-L11` MMIO helper packet when shared reviewer-facing reminders refresh",
        "the ring survey, slice, and freeze-boundary notes, the direct ring helper packet through `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`,",
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
        "pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {",
    ],
    "drivers/virtio/virtio_ring_verify.zig": [
        "pub fn summarizeNotificationState(",
        "pub fn summarizeNotificationData(",
        "pub fn summarizeDelayedCallback(",
        "pub fn summarizeResetReadiness(",
        "test \"phase10 virtio ring verify keeps notification-state wrapper explicit across publish kick and used replay\" {",
        "test \"phase10 virtio ring verify exposes reset-readiness blocker ordering after clearBroken releases queue debt\" {",
        "test \"phase10 virtio ring verify keeps reset-readiness blockers ordered through queue-local replay\" {",
    ],
    "drivers/virtio/virtio_ring_publish_readiness.zig": [
        "pub fn summarizePublishReadiness(",
        "pub fn queueCanPublish(summary: QueuePublishReadinessSummary) bool {",
        "pub fn queueHasPublishCapacity(summary: QueuePublishReadinessSummary) bool {",
        "test \"phase10 virtio ring publish-readiness wrapper keeps empty queues publishable\" {",
        "test \"phase10 virtio ring publish-readiness wrapper keeps unpublished chains visible while remaining queue-local publishable\" {",
        "test \"phase10 virtio ring publish-readiness wrapper blocks full queues until used chains return capacity\" {",
        "test \"phase10 virtio ring publish-readiness wrapper regains publish capacity before used buffers are polled\" {",
        "test \"phase10 virtio ring publish-readiness wrapper keeps broken queues fenced even when slots remain\" {",
        "test \"phase10 virtio ring publish-readiness wrapper falls back to queue-full after a broken full queue is cleared\" {",
    ],
    "zigux/tests/phase10_build.zig": [
        ".root_source_file = b.path(\"phase10_virtio_ring_notification_data_readiness.zig\"),",
        ".root_source_file = b.path(\"../../drivers/virtio/virtio_ring_publish_readiness.zig\"),",
        ".root_source_file = b.path(\"phase10_virtio_ring_survey.zig\"),",
        ".name = \"phase10-virtio-ring-notification-data-readiness-tests\",",
        ".name = \"phase10-virtio-ring-publish-readiness-tests\",",
        ".name = \"phase10-virtio-ring-survey-tests\",",
        "test_step.dependOn(&run_phase10_virtio_ring_notification_data_readiness_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_publish_readiness_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_survey_tests.step);",
    ],
    "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig": [
        "test \"phase10 virtio ring notification-data replay keeps split and packed next-avail state explicit\" {",
        "const packed_summary = try ring.notificationDataSummary(2);",
    ],
    "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig": [
        "test \"phase10 virtio ring delayed callback budget stays bounded to queue-local replay state\" {",
        "try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(7));",
    ],
    "zigux/tests/phase10_virtio_ring_survey.zig": [
        "try expectContains(slice_note, \"the broader ring replay `zigux/tests/phase10_virtio_ring.zig` now sits beside that queue-local helper ladder as direct current-head evidence in this slice\");",
        "try expectContains(freeze_note, \"direct current-head readback now keeps the broader ring replay `zigux/tests/phase10_virtio_ring.zig` inside the same ring packet as the queue-local helper ladder\");",
        "test \"phase10 virtio ring lane sequencing keeps P10-L10 queue ownership explicit beside P10-L11\" {",
    ],
}

FORBIDDEN_MARKERS = {
    "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md": [
        "public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` even though exact direct-path contents reads in this lane still leave that broader replay outside the queue-local helper ladder",
    ],
    "Documentation/zigux/phase10-virtio-ring-slice.md": [
        "public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` but it still remains outside exact direct-path current-head evidence in this slice",
        "the broader ring replay still remains outside direct current-head evidence in this slice",
    ],
    "zigux/tests/phase10_virtio_ring_survey.zig": [
        "try expectContains(slice_note, \"public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` but it still remains outside exact direct-path current-head evidence in this slice\");",
        "try expectContains(freeze_note, \"public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` even though exact direct-path contents reads in this lane still leave that broader replay outside the queue-local helper ladder\");",
    ],
}

def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")

def validate_manifest_fields(root: Path) -> list[str]:
    manifest = json.loads(read_text(root, MANIFEST_PATH))
    problems: list[str] = []
    for field_name, expected_value in EXPECTED_MANIFEST_FIELDS.items():
        actual_value = manifest.get(field_name)
        if actual_value != expected_value:
            problems.append(f"{MANIFEST_PATH}:{field_name}:{actual_value}")
    if manifest.get("freeze_boundary_owner_lane") != EXPECTED_FREEZE_BOUNDARY_OWNER:
        problems.append(
            f"{MANIFEST_PATH}:freeze_boundary_owner_lane:{manifest.get('freeze_boundary_owner_lane')}"
        )
    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        return [f"{MANIFEST_PATH}:gaps:not_a_list"]
    gap_index = {
        gap.get("id"): gap
        for gap in gaps
        if isinstance(gap, dict) and isinstance(gap.get("id"), str)
    }
    for gap_id, (expected_kind, expected_status, expected_destination) in EXPECTED_GAP_METADATA.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            problems.append(f"{MANIFEST_PATH}:gap_missing:{gap_id}")
            continue
        if gap.get("kind") != expected_kind:
            problems.append(f"{MANIFEST_PATH}:gap:{gap_id}:kind:{gap.get('kind')}")
        if gap.get("status") != expected_status:
            problems.append(f"{MANIFEST_PATH}:gap:{gap_id}:status:{gap.get('status')}")
        if gap.get("zigux_destination") != expected_destination:
            problems.append(
                f"{MANIFEST_PATH}:gap:{gap_id}:zigux_destination:{gap.get('zigux_destination')}"
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
    gaps = []
    for gap_id, (kind, status, destination) in EXPECTED_GAP_METADATA.items():
        gaps.append(
            {
                "id": gap_id,
                "kind": kind,
                "status": status,
                "zigux_destination": destination,
            }
        )
    return {
        **EXPECTED_MANIFEST_FIELDS,
        "surveyed_commit": "fixture",
        "roadmap_destinations": ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"],
        "freeze_map": "Documentation/zigux/freeze-map.md",
        "freeze_boundary_status": "aligned",
        "freeze_boundary_owner_lane": EXPECTED_FREEZE_BOUNDARY_OWNER,
        "study_only_anchors": ["kernel/workqueue.c", "kernel/trace/ring_buffer.c"],
        "freeze_in_c_anchors": ["kernel/sched/core.c", "mm/page_alloc.c", "kernel/rcu/tree.c", "net/core/skbuff.c"],
        "survey_summary": {
            "virtio_ring_c_lines": 3940,
            "preexisting_phase10_test_files": 7,
            "preexisting_virtio_core_zig_present": True,
            "preexisting_phase10_build_present": True,
            "preexisting_phase10_core_doc_present": False,
            "preexisting_virtio_ring_zig_present": True,
            "preexisting_virtio_ring_doc_present": True,
            "preexisting_ring_verify_present": True,
            "preexisting_ring_publish_readiness_present": True,
        },
        "gaps": gaps,
    }
}

def write_fixture(root: Path) -> None:
    for rel_path, markers in REQUIRED_MARKERS.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(markers) + "\n", encoding="utf-8")
    manifest_path = root / MANIFEST_PATH
    manifest_path.write_text(json.dumps(fixture_manifest(), indent=2) + "\n")

def expect_problem(root: Path, mutate, expected: str) -> None:
    mutate(root)
    missing_files, problems = validate(root)
    if missing_files:
        actual = ",".join(missing_files)
        raise SystemExit(f"phase10-ring-self-test:unexpected_missing={actual}")
    if expected not in problems:
        actual = ",".join(problems) if problems else "none"
        raise SystemExit(f"phase10-ring-self-test:expected={expected}:actual={actual}")

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

        def remove_slice_marker(tmp_root: Path) -> None:
            path = tmp_root / "Documentation/zigux/phase10-virtio-ring-slice.md"
            text = path.read_text(encoding="utf-8")
            marker = "the broader ring replay `zigux/tests/phase10_virtio_ring.zig` now sits beside that queue-local helper ladder as direct current-head evidence in this slice"
            path.write_text(text.replace(marker, "__removed__", 1), encoding="utf-8")

        expect_problem(
            root,
            remove_slice_marker,
            "Documentation/zigux/phase10-virtio-ring-slice.md:the broader ring replay `zigux/tests/phase10_virtio_ring.zig` now sits beside that queue-local helper ladder as direct current-head evidence in this slice",
        )
        write_fixture(root)

        def remove_prepare_kick_marker(tmp_root: Path) -> None:
            path = tmp_root / "Documentation/zigux/phase10-virtio-ring-survey.md"
            text = path.read_text(encoding="utf-8")
            marker = "`zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`"
            path.write_text(text.replace(marker, "`zigux/tests/phase10_virtio_ring_prepare_kick_missing.zig`", 1), encoding="utf-8")

        expect_problem(
            root,
            remove_prepare_kick_marker,
            "Documentation/zigux/phase10-virtio-ring-survey.md:`zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`",
        )
        write_fixture(root)

        def add_forbidden_freeze_marker(tmp_root: Path) -> None:
            path = tmp_root / "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md"
            text = path.read_text(encoding="utf-8")
            marker = "public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` even though exact direct-path contents reads in this lane still leave that broader replay outside the queue-local helper ladder"
            path.write_text(text + "\n", encoding="utf-8")

        expect_problem(
            root,
            add_forbidden_freeze_marker,
            "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md:forbidden:public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` even though exact direct-path contents reads in this lane still leave that broader replay outside the queue-local helper ladder",
        )
        write_fixture(root)

        def drift_manifest(tmp_root: Path) -> None:
            path = tmp_root / MANIFEST_PATH
            data = json.loads(path.read_text(encoding="utf-8"))
            data["freeze_boundary_owner_lane"] = "P10-L12"
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        expect_problem(
            root,
            drift_manifest,
            f"{MANIFEST_PATH}:freeze_boundary_owner_lane:P10-L12",
        )
        write_fixture(root)

        def drift_freeze_status_change_claimed(tmp_root: Path) -> None:
            path = tmp_root / MANIFEST_PATH
            data = json.loads(path.read_text(encoding="utf-8"))
            data["freeze_status_change_claimed"] = True
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        expect_problem(
            root,
            drift_freeze_status_change_claimed,
            f"{MANIFEST_PATH}:freeze_status_change_claimed:True",
        )
        write_fixture(root)

        def drift_risky_transport_posture(tmp_root: Path) -> None:
            path = tmp_root / MANIFEST_PATH
            data = json.loads(path.read_text(encoding="utf-8"))
            data["risky_transport_posture"] = "starter_landed"
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        expect_problem(
            root,
            drift_risky_transport_posture,
            f"{MANIFEST_PATH}:risky_transport_posture:starter_landed",
        )
        write_fixture(root)

        def drift_allowed_evidence_kinds(tmp_root: Path) -> None:
            path = tmp_root / MANIFEST_PATH
            data = json.loads(path.read_text(encoding="utf-8"))
            data["allowed_evidence_kinds"] = "driver_local_lab_slices"
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        expect_problem(
            root,
            drift_allowed_evidence_kinds,
            f"{MANIFEST_PATH}:allowed_evidence_kinds:driver_local_lab_slices",
        )
        write_fixture(root)

        def drift_forbidden_transport_claims(tmp_root: Path) -> None:
            path = tmp_root / MANIFEST_PATH
            data = json.loads(path.read_text(encoding="utf-8"))
            data["forbidden_transport_claims"] = "queue_setup_reset_paths"
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        expect_problem(
            root,
            drift_forbidden_transport_claims,
            f"{MANIFEST_PATH}:forbidden_transport_claims:queue_setup_reset_paths",
        )
        write_fixture(root)

        def drift_architecture_council_reopen_required(tmp_root: Path) -> None:
            path = tmp_root / MANIFEST_PATH
            data = json.loads(path.read_text(encoding="utf-8"))
            data["architecture_council_reopen_required"] = False
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        expect_problem(
            root,
            drift_architecture_council_reopen_required,
            f"{MANIFEST_PATH}:architecture_council_reopen_required:False",
        )
        write_fixture(root)

        def drift_architecture_council_reopen_attached(tmp_root: Path) -> None:
            path = tmp_root / MANIFEST_PATH
            data = json.loads(path.read_text(encoding="utf-8"))
            data["architecture_council_reopen_attached"] = True
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        expect_problem(
            root,
            drift_architecture_council_reopen_attached,
            f"{MANIFEST_PATH}:architecture_council_reopen_attached:True",
        )
        write_fixture(root)

        def remove_empty_queue_test(tmp_root: Path) -> None:
            path = tmp_root / "drivers/virtio/virtio_ring_publish_readiness.zig"
            text = path.read_text(encoding="utf-8")
            marker = 'test "phase10 virtio ring publish-readiness wrapper keeps empty queues publishable" {'
            path.write_text(text.replace(marker, 'test "phase10 virtio ring publish-readiness wrapper keeps empty queues hidden" {', 1), encoding="utf-8")

        expect_problem(
            root,
            remove_empty_queue_test,
            'drivers/virtio/virtio_ring_publish_readiness.zig:test "phase10 virtio ring publish-readiness wrapper keeps empty queues publishable" {',
        )
        write_fixture(root)

        def remove_used_buffer_recovery_test(tmp_root: Path) -> None:
            path = tmp_root / "drivers/virtio/virtio_ring_publish_readiness.zig"
            text = path.read_text(encoding="utf-8")
            marker = 'test "phase10 virtio ring publish-readiness wrapper regains publish capacity before used buffers are polled" {'
            path.write_text(text.replace(marker, 'test "phase10 virtio ring publish-readiness wrapper regains publish capacity late" {', 1), encoding="utf-8")

        expect_problem(
            root,
            remove_used_buffer_recovery_test,
            'drivers/virtio/virtio_ring_publish_readiness.zig:test "phase10 virtio ring publish-readiness wrapper regains publish capacity before used buffers are polled" {',
        )
        write_fixture(root)

        def remove_broken_full_queue_recovery_test(tmp_root: Path) -> None:
            path = tmp_root / "drivers/virtio/virtio_ring_publish_readiness.zig"
            text = path.read_text(encoding="utf-8")
            marker = 'test "phase10 virtio ring publish-readiness wrapper falls back to queue-full after a broken full queue is cleared" {'
            path.write_text(text.replace(marker, 'test "phase10 virtio ring publish-readiness wrapper forgets queue-full after clearBroken" {', 1), encoding="utf-8")

        expect_problem(
            root,
            remove_broken_full_queue_recovery_test,
            'drivers/virtio/virtio_ring_publish_readiness.zig:test "phase10 virtio ring publish-readiness wrapper falls back to queue-full after a broken full queue is cleared" {',
        )
        write_fixture(root)

        def remove_publish_readiness_build_step_name(tmp_root: Path) -> None:
            path = tmp_root / "zigux/tests/phase10_build.zig"
            text = path.read_text(encoding="utf-8")
            marker = '.name = "phase10-virtio-ring-publish-readiness-tests",'
            path.write_text(
                text.replace(
                    marker,
                    '.name = "phase10-virtio-ring-publish-readiness-missing-tests",',
                    1,
                ),
                encoding="utf-8",
            )

        expect_problem(
            root,
            remove_publish_readiness_build_step_name,
            'zigux/tests/phase10_build.zig:.name = "phase10-virtio-ring-publish-readiness-tests",',
        )
        write_fixture(root)

        def remove_publish_readiness_build_dependency(tmp_root: Path) -> None:
            path = tmp_root / "zigux/tests/phase10_build.zig"
            text = path.read_text(encoding="utf-8")
            marker = "test_step.dependOn(&run_phase10_virtio_ring_publish_readiness_tests.step);"
            path.write_text(
                text.replace(
                    marker,
                    "test_step.dependOn(&run_phase10_virtio_ring_prepare_kick_idempotent_tests.step);",
                    1,
                ),
                encoding="utf-8",
            )

        expect_problem(
            root,
            remove_publish_readiness_build_dependency,
            "zigux/tests/phase10_build.zig:test_step.dependOn(&run_phase10_virtio_ring_publish_readiness_tests.step);",
        )
        write_fixture(root)

        def remove_tests_root_ring_boundary_marker(tmp_root: Path) -> None:
            path = tmp_root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"
            text = path.read_text(encoding="utf-8")
            marker = "Keep the queue-local `P10-L10` ring freeze-boundary packet distinct from the bounded `P10-L11` MMIO helper packet when shared reviewer-facing reminders refresh"
            path.write_text(text.replace(marker, "__removed__", 1), encoding="utf-8")

        expect_problem(
            root,
            remove_tests_root_ring_boundary_marker,
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:Keep the queue-local `P10-L10` ring freeze-boundary packet distinct from the bounded `P10-L11` MMIO helper packet when shared reviewer-facing reminders refresh",
        )
        write_fixture(root)

        (root / "zigux/tests/phase10_virtio_ring_survey.zig").unlink()
        missing_files, problems = validate(root)
        if problems:
            actual = ",".join(problems)
            raise SystemExit(f"phase10-ring-self-test:unexpected_problems={actual}")
        if "zigux/tests/phase10_virtio_ring_survey.zig" not in missing_files:
            actual = ",".join(missing_files) if missing_files else "none"
            raise SystemExit(f"phase10-ring-self-test:expected_missing=zigux/tests/phase10_virtio_ring_survey.zig:actual={actual}")

    print("PHASE10_RING_PACKET_SELF_TEST=pass")
    print("PHASE10_RING_PACKET_SELF_TEST_CASE_COUNT=17")
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