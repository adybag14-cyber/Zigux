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
}
EXPECTED_SURVEY_SUMMARY_FIELDS = {
    "virtio_ring_c_lines": 3940,
    "preexisting_phase10_test_files": 9,
    "preexisting_virtio_core_zig_present": True,
    "preexisting_phase10_build_present": True,
    "preexisting_phase10_core_doc_present": False,
    "preexisting_virtio_ring_zig_present": True,
    "preexisting_virtio_ring_doc_present": True,
    "preexisting_ring_verify_present": True,
    "preexisting_ring_publish_readiness_present": True,
    "preexisting_ring_registration_summary_present": True,
    "preexisting_ring_used_buffer_poll_present": True,
}
EXPECTED_GAP_METADATA = {
    "phase10-build-gate": ("validation", "starter_landed", "zigux/tests/phase10_build.zig"),
    "phase10-virtio-core-lab-starter": ("lab_driver_starter", "starter_landed", "drivers/virtio/virtio.zig"),
    "phase10-ring-registration-replay": (
        "validation",
        "starter_landed",
        "zigux/tests/phase10_virtio_ring_registration_replay.zig",
    ),
    "phase10-ring-reset-readiness-replay": (
        "validation",
        "starter_landed",
        "zigux/tests/phase10_virtio_ring_reset_readiness.zig",
    ),
    "phase10-virtio-ring-survey-gate": ("validation", "starter_landed", "zigux/tests/phase10_virtio_ring_survey.zig"),
    "phase10-virtio-ring-survey-note": ("documentation", "starter_landed", "Documentation/zigux/phase10-virtio-ring-survey.md"),
    "phase10-virtqueue-shape-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-used-buffer-polling-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring_used_buffer_poll.zig"),
    "phase10-callback-enable-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-callback-delay-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-notify-prepare-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-notification-data-summary-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-broken-queue-poll-guard": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-queue-publish-readiness-helper": ("queue_wrapper", "starter_landed", "drivers/virtio/virtio_ring_publish_readiness.zig"),
    "phase10-queue-registration-summary-helper": (
        "queue_wrapper",
        "starter_landed",
        "drivers/virtio/virtio_ring_registration_summary.zig",
    ),
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
        "`drivers/virtio/virtio_ring_notification_data.zig`",
        "`drivers/virtio/virtio_ring_registration_summary.zig`",
        "`drivers/virtio/virtio_ring_used_buffer_poll.zig`",
        "`zigux/tests/phase10_virtio_ring.zig`",
        "`zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`",
        "`zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`",
        "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
        "`zigux/tests/phase10_virtio_ring_reset_readiness.zig`",
        "`zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`",
        "`zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`",
        "`zigux/tests/phase10_virtio_ring_queue_build_survey.zig`",
        "direct contents reads rematerialize `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `drivers/virtio/virtio_ring_notification_data.zig`, `drivers/virtio/virtio_ring_registration_summary.zig`, `drivers/virtio/virtio_ring_used_buffer_poll.zig`, the broader replay `zigux/tests/phase10_virtio_ring.zig`",
        "`phase10-used-buffer-polling-helper`",
        "`phase10-queue-registration-summary-helper`",
        "`phase10-ring-reset-readiness-replay`",
        "`zigux/tests/phase10_virtio_ring_queue_build_survey.zig` now gives the ring lane one focused queue-build survey replay",
        "the blocked `phase10-ring-lab-driver-bridge` remains owned by the adjacent `P10-L11` MMIO packet",
    ],
    "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md": [
        "current packet lane on master: `P10-L10`",
        "adjacent freeze-boundary owner: `P10-L11`",
        "direct current-head readback now keeps the broader ring replay `zigux/tests/phase10_virtio_ring.zig` inside the same ring packet as the queue-local helper ladder",
        "the used-buffer-poll wrapper `drivers/virtio/virtio_ring_used_buffer_poll.zig`, the publish-readiness helper `drivers/virtio/virtio_ring_publish_readiness.zig`, the notification-data replay `zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`, the reset-readiness replay `zigux/tests/phase10_virtio_ring_reset_readiness.zig`, and the dedicated ring survey replay `zigux/tests/phase10_virtio_ring_survey.zig` stay part of the same directly readable ring packet",
        "the smallest same-lane follow-through is reminder-surface, checker, or manifest truthfulness work",
    ],
    "Documentation/zigux/phase10-virtio-ring-slice.md": [
        "`drivers/virtio/virtio_ring_publish_readiness.zig`",
        "`drivers/virtio/virtio_ring_registration_summary.zig`",
        "`drivers/virtio/virtio_ring_used_buffer_poll.zig`",
        "`zigux/tests/phase10_virtio_ring.zig`",
        "`zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`",
        "`zigux/tests/phase10_virtio_ring_reset_readiness.zig`",
        "`zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`",
        "`zigux/tests/phase10_virtio_ring_survey.zig`",
        "the broader ring replay `zigux/tests/phase10_virtio_ring.zig` now sits beside that queue-local helper ladder as direct current-head evidence in this slice",
        "the used-buffer-poll wrapper, the notification-data replay, the registration replay, the registration-summary wrapper, the reset-readiness replay, and the dedicated survey gate are now landed review surfaces inside this slice",
    ],
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": [
        "`scripts/zigux/check-phase10-ring-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, `scripts/zigux/check-phase10-mmio-packet.py`",
        "`drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`",
        "Keep the queue-local `P10-L10` ring freeze-boundary packet distinct from the bounded `P10-L11` MMIO helper packet when shared reviewer-facing reminders refresh",
        "the ring survey, slice, and freeze-boundary notes, the direct ring helper packet through `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`,",
    ],
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": [
        "ring lane `P10-L10` owns the queue-local wrapper packet",
        "zigux/tests/phase10_virtio_ring_reset_readiness.zig",
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
    "drivers/virtio/virtio_ring_notification_data.zig": [
        "pub fn summarizeNotificationData(",
        "pub fn notificationDataUsesWrapBit(summary: NotificationDataSummary) bool {",
        "pub fn queueIndexMatchesNotificationData(summary: NotificationDataSummary) bool {",
        "pub fn nextAvailStateMatchesEncoding(summary: NotificationDataSummary) bool {",
        "test \"phase10 virtio ring notification-data wrapper keeps split queue state explicit\" {",
        "test \"phase10 virtio ring notification-data wrapper preserves packed wrap encoding across u16 rollover\" {",
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
    "drivers/virtio/virtio_ring_registration_summary.zig": [
        "pub fn summarizeQueueRegistration(",
        "pub fn summarizeRegisteredQueueCount(ring: *const virtio_ring.VirtioRingLab) usize {",
        "pub fn queueDefinitionDisciplineStable(",
        "test \"phase10 virtio ring registration-summary wrapper keeps definition discipline explicit\" {",
        "test \"phase10 virtio ring registration-summary wrapper stays queue-local across noncontiguous queue definitions\" {",
    ],
    "drivers/virtio/virtio_ring_used_buffer_poll.zig": [
        "pub fn summarizeUsedBufferPoll(",
        "pub fn usedBufferPollHasNewChains(summary: UsedBufferPollSummary) bool {",
        "pub fn usedBufferPollSettled(summary: UsedBufferPollSummary) bool {",
        "test \"phase10 virtio ring used-buffer-poll wrapper keeps empty queues settled\" {",
        "test \"phase10 virtio ring used-buffer-poll wrapper exposes newly used chains before the follow-up poll settles\" {",
        "test \"phase10 virtio ring used-buffer-poll wrapper settles once all used chains are observed\" {",
    ],
    "zigux/tests/phase10_build.zig": [
        ".root_source_file = b.path(\"../../drivers/virtio/virtio_ring_notification_data.zig\"),",
        ".root_source_file = b.path(\"../../drivers/virtio/virtio_ring_publish_readiness.zig\"),",
        ".root_source_file = b.path(\"../../drivers/virtio/virtio_ring_used_buffer_poll.zig\"),",
        ".root_source_file = b.path(\"phase10_virtio_ring_registration_replay.zig\"),",
        ".root_source_file = b.path(\"phase10_virtio_ring_prepare_kick_idempotent.zig\"),",
        ".root_source_file = b.path(\"phase10_virtio_ring_reset_reuse.zig\"),",
        ".root_source_file = b.path(\"phase10_virtio_ring_broken_queue_queue_discipline.zig\"),",
        ".root_source_file = b.path(\"phase10_virtio_ring_delayed_callback_budget.zig\"),",
        ".root_source_file = b.path(\"phase10_virtio_ring_queue_build_survey.zig\"),",
        ".root_source_file = b.path(\"phase10_virtio_ring_survey.zig\"),",
        ".name = \"phase10-virtio-ring-notification-data-readiness-tests\",",
        ".name = \"phase10-virtio-ring-registration-replay-tests\",",
        ".name = \"phase10-virtio-ring-reset-readiness-tests\",",
        ".name = \"phase10-virtio-ring-notification-data-wrapper-tests\",",
        ".name = \"phase10-virtio-ring-publish-readiness-tests\",",
        ".name = \"phase10-virtio-ring-used-buffer-poll-tests\",",
        ".name = \"phase10-virtio-ring-prepare-kick-idempotent-tests\",",
        ".name = \"phase10-virtio-ring-reset-reuse-tests\",",
        ".name = \"phase10-virtio-ring-broken-queue-queue-discipline-tests\",",
        ".name = \"phase10-virtio-ring-delayed-callback-budget-tests\",",
        ".name = \"phase10-virtio-ring-queue-build-survey-tests\",",
        ".name = \"phase10-virtio-ring-survey-tests\",",
        "test_step.dependOn(&run_phase10_virtio_ring_notification_data_readiness_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_registration_replay_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_reset_readiness_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_notification_data_wrapper_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_publish_readiness_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_used_buffer_poll_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_prepare_kick_idempotent_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_reset_reuse_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_broken_queue_queue_discipline_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_delayed_callback_budget_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_queue_build_survey_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_survey_tests.step);",
    ],
    "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig": [
        "test \"phase10 virtio ring notification-data replay keeps split and packed next-avail state explicit\" {",
        "const packed_summary = try ring.notificationDataSummary(2);",
    ],
    "zigux/tests/phase10_virtio_ring_queue_build_survey.zig": [
        "test \"phase10 virtio ring queue build keeps the focused queue packet explicit\" {",
        ".root_source_file = b.path(\"../../drivers/virtio/virtio_ring_notification_data.zig\"),",
        ".root_source_file = b.path(\"phase10_virtio_ring_queue_build_survey.zig\"),",
        ".name = \"phase10-virtio-ring-notification-data-wrapper-tests\",",
        ".name = \"phase10-virtio-ring-queue-build-survey-tests\",",
        "run_phase10_virtio_ring_notification_data_wrapper_tests.step",
        "run_phase10_virtio_ring_queue_build_survey_tests.step",
    ],
    "zigux/tests/phase10_virtio_ring_survey.zig": [
        "try expectContains(survey_note, \"drivers/virtio/virtio_ring_registration_summary.zig\");",
        "try expectContains(survey_note, \"drivers/virtio/virtio_ring_used_buffer_poll.zig\");",
        "try expectContains(survey_note, \"zigux/tests/phase10_virtio_ring_reset_readiness.zig\");",
        "try expectContains(manifest, \"\\\"preexisting_phase10_test_files\\\": 9\");",
        "try expectContains(manifest, \"\\\"preexisting_ring_registration_summary_present\\\": true\");",
        "try expectContains(manifest, \"\\\"preexisting_ring_used_buffer_poll_present\\\": true\");",
        "try expectContains(manifest, \"\\\"id\\\": \\\"phase10-used-buffer-polling-helper\\\"\");",
        "try expectContains(manifest, \"\\\"id\\\": \\\"phase10-queue-registration-summary-helper\\\"\");",
        "const used_buffer_poll_file = try readRepoRelative(",
        "test \"phase10 virtio ring used-buffer-poll wrapper stays direct current-head evidence in the survey packet\" {",
        "try expectContains(used_buffer_poll_file, \"test \\\"phase10 virtio ring used-buffer-poll wrapper exposes newly used chains before the follow-up poll settles\\\" {\");",
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
    survey_summary = manifest.get("survey_summary")
    if not isinstance(survey_summary, dict):
        problems.append(f"{MANIFEST_PATH}:survey_summary:not_a_dict")
    else:
        for field_name, expected_value in EXPECTED_SURVEY_SUMMARY_FIELDS.items():
            actual_value = survey_summary.get(field_name)
            if actual_value != expected_value:
                problems.append(
                    f"{MANIFEST_PATH}:survey_summary:{field_name}:{actual_value}"
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
    if not (root / MANIFEST_PATH).exists():
        missing_files.append(MANIFEST_PATH)
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
        "freeze_boundary_owner_lane": EXPECTED_FREEZE_BOUNDARY_OWNER,
        "survey_summary": EXPECTED_SURVEY_SUMMARY_FIELDS,
        "gaps": gaps,
    }


def write_file(root: Path, rel_path: str, text: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    for rel_path, markers in REQUIRED_MARKERS.items():
        write_file(root, rel_path, "\n".join(markers) + "\n")
    write_file(root, MANIFEST_PATH, json.dumps(fixture_manifest(), indent=2) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_ring_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)

        missing, problems = validate(root)
        if missing or problems:
            raise SystemExit(
                "phase10-ring-packet:self-test-baseline-failed:"
                + ",".join(missing + problems)
            )

        removal_cases = {
            "missing_survey_note": "Documentation/zigux/phase10-virtio-ring-survey.md",
            "missing_registration_summary_wrapper": "drivers/virtio/virtio_ring_registration_summary.zig",
            "missing_used_buffer_poll_wrapper": "drivers/virtio/virtio_ring_used_buffer_poll.zig",
            "missing_notification_data_wrapper": "drivers/virtio/virtio_ring_notification_data.zig",
            "missing_queue_build_survey": "zigux/tests/phase10_virtio_ring_queue_build_survey.zig",
            "missing_manifest": MANIFEST_PATH,
        }
        for label, rel_path in removal_cases.items():
            with tempfile.TemporaryDirectory(prefix=f"zigux_phase10_ring_packet_{label}_") as tmp_case:
                case_root = Path(tmp_case)
                write_fixture_tree(case_root)
                (case_root / rel_path).unlink()
                missing, problems = validate(case_root)
                expected = rel_path
                if expected not in missing:
                    raise SystemExit(
                        f"phase10-ring-packet:{label}-not-detected:"
                        + ",".join(missing + problems)
                    )

        manifest_problem_cases = {
            "wrong_lane": lambda manifest: manifest.__setitem__("lane_key", "P10-L99"),
            "wrong_freeze_owner": lambda manifest: manifest.__setitem__(
                "freeze_boundary_owner_lane", "P10-L12"
            ),
            "missing_gap": lambda manifest: manifest.__setitem__(
                "gaps",
                [gap for gap in manifest["gaps"] if gap["id"] != "phase10-queue-registration-summary-helper"],
            ),
            "wrong_summary": lambda manifest: manifest["survey_summary"].__setitem__(
                "preexisting_ring_used_buffer_poll_present", False
            ),
        }
        for label, mutate in manifest_problem_cases.items():
            with tempfile.TemporaryDirectory(prefix=f"zigux_phase10_ring_packet_{label}_") as tmp_case:
                case_root = Path(tmp_case)
                write_fixture_tree(case_root)
                manifest = json.loads(read_text(case_root, MANIFEST_PATH))
                mutate(manifest)
                write_file(case_root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
                missing, problems = validate(case_root)
                if not problems:
                    raise SystemExit(f"phase10-ring-packet:{label}-not-detected")

        with tempfile.TemporaryDirectory(prefix="zigux_phase10_ring_packet_missing_build_marker_") as tmp_case:
            case_root = Path(tmp_case)
            write_fixture_tree(case_root)
            build_path = case_root / "zigux/tests/phase10_build.zig"
            build_text = build_path.read_text(encoding="utf-8")
            build_text = build_text.replace(
                ".name = \"phase10-virtio-ring-queue-build-survey-tests\",",
                "",
                1,
            )
            build_path.write_text(build_text, encoding="utf-8")
            missing, problems = validate(case_root)
            if not problems:
                raise SystemExit("phase10-ring-packet:missing-build-marker-not-detected")

        forbidden_case_count = 0
        for forbidden_case_path, forbidden_markers in FORBIDDEN_MARKERS.items():
            for forbidden_index, forbidden_marker in enumerate(forbidden_markers, start=1):
                forbidden_case_count += 1
                with tempfile.TemporaryDirectory(
                    prefix=f"zigux_phase10_ring_packet_forbidden_{forbidden_case_count}_"
                ) as tmp_case:
                    case_root = Path(tmp_case)
                    write_fixture_tree(case_root)
                    current = read_text(case_root, forbidden_case_path)
                    write_file(case_root, forbidden_case_path, current + forbidden_marker + "\n")
                    missing, problems = validate(case_root)
                    if not problems:
                        raise SystemExit(
                            "phase10-ring-packet:forbidden-marker-not-detected:"
                            f"{forbidden_case_path}:{forbidden_index}"
                        )

    print("PHASE10_RING_PACKET_SELF_TEST=pass")
    print("PHASE10_RING_PACKET_SELF_TEST_CASE_COUNT=17")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=ROOT, type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    missing, problems = validate(args.root)
    if missing or problems:
        print("PHASE10_RING_PACKET=fail")
        for rel_path in missing:
            print(f"missing:{rel_path}")
        for problem in problems:
            print(f"problem:{problem}")
        return 1

    print("PHASE10_RING_PACKET=pass")
    print(f"PHASE10_RING_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE10_RING_PACKET_GAP_COUNT={len(EXPECTED_GAP_METADATA)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
