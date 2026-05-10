#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path(__file__).resolve().parent

FILES = [
    "scripts/zigux/check-phase10-ring-packet.py",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase10_build.zig",
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_ring_verify.zig",
    "zigux/tests/phase10_virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "Documentation/zigux/phase10-virtio-ring-slice.md",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
]

EXPECTED_BUILD_MARKERS = [
    "phase10_virtio_ring_module",
    "phase10_virtio_ring_survey_module",
    "phase10_virtio_ring_verify_module",
    '"phase10-virtio-ring-tests"',
    '"phase10-virtio-ring-survey-tests"',
    '"phase10-virtio-ring-verify-tests"',
]

EXPECTED_MAKEFILE_MARKERS = [
    "phase10-test:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py\n",
    "$(ZIG) build test --build-file zigux/tests/phase10_build.zig",
]

EXPECTED_HELPER_MARKERS = [
    "pub const PackedEventIndexSummary = struct {",
    "pub fn packedEventIndexSummary(self: *Self, queue_index: u16) !PackedEventIndexSummary {",
    "pub const NotificationDataSummary = struct {",
    "pub fn notificationDataSummary(self: *const Self, queue_index: u16) !NotificationDataSummary {",
    "pub const QueueResetReadinessSummary = struct {",
    "pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {",
    "pub fn resetQueue(self: *Self, queue_index: u16) !QueueResetSummary {",
    "pub fn markBroken(self: *Self, queue_index: u16) !BrokenQueueSummary {",
]

EXPECTED_VERIFY_TEST_MARKERS = [
    'test "virtio ring packed event-index summary stays queue-local and reports when polling can wait" {',
    "try testing.expectError(error.QueueLayoutDoesNotSupportPackedEventIndex, lab.packedEventIndexSummary(1));",
    "try testing.expectError(error.QueueDoesNotUseEventIndex, lab.packedEventIndexSummary(2));",
    "try testing.expectEqual(@as(u16, 3), summary.event_index_window);",
    "try testing.expect(!summary.should_poll);",
    "try testing.expectEqual(@as(u16, 1), summary.event_index_window);",
    "try testing.expect(summary.should_poll);",
    'test "virtio ring clearBroken exposes the next reset blocker instead of hiding queue debt" {',
    "_ = try lab.clearBroken(4);",
    "try testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.unpublished_chains, readiness.blocker.?);",
    "_ = try lab.clearBroken(5);",
    "try testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.outstanding_chains, readiness.blocker.?);",
    "_ = try lab.clearBroken(6);",
    "try testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.unpolled_used_chains, readiness.blocker.?);",
    'test "virtio ring notification-data summary tracks packed wrap and split reset transitions" {',
    "try testing.expectEqual(@as(u32, 0x8001_0001), summary.notification_data);",
    "try testing.expectEqual(@as(u32, 1), summary.notification_data);",
]

EXPECTED_TEST_MARKERS = [
    'test "phase10 virtio ring reset-readiness preflight reports the current queue blocker" {',
    'test "phase10 virtio ring broken summary keeps queue-local debt reviewable while blocking queue work" {',
    'test "phase10 virtio ring delayed callback pacing reports both thresholded and immediate poll cases" {',
    'test "phase10 virtio ring callback re-enable reports pending used work and settles after poll" {',
]

EXPECTED_SURVEY_TEST_MARKERS = [
    'test "phase10 virtio ring survey manifest records the queue-local foothold and remaining lab-driver bridge" {',
    'try std.testing.expectEqualStrings("P10-L07", manifest.lane_key);',
    'try std.testing.expect(manifest.gaps.len >= 16);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "notification-data summary") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, verify_replay, "test \\\"virtio ring notification-data summary tracks packed wrap and split reset transitions\\\" {") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, verify_replay, "try testing.expectEqual(@as(u32, 0x8001_0001), summary.notification_data);") != null);',
    'var saw_notification_data_helper = false;',
    'if (std.mem.eql(u8, gap.id, "phase10-notification-data-summary-helper")) {',
    'try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "packed wrap-bit transitions") != null);',
    'try std.testing.expectEqual(@as(usize, 15), starter_landed_count);',
    'try std.testing.expectEqual(@as(usize, 1), blocked_count);',
    "var saw_ring_verify_replay = false;",
    "var saw_ring_lab_driver_bridge = false;",
    'try std.testing.expect(saw_notification_data_helper);',
]

EXPECTED_SLICE_MARKERS = [
    "dedicated ring packet review guard",
    "scripts/zigux/check-phase10-ring-packet.py",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "drivers/virtio/virtio_ring_verify.zig",
    "zig test zigux/tests/phase10_virtio_ring.zig",
    "zig test zigux/tests/phase10_virtio_ring_survey.zig",
]

EXPECTED_SURVEY_NOTE_MARKERS = [
    "lab-driver threshold",
    "queue-local ring foothold",
    "notification-data summary",
    "phase10-ring-lab-driver-bridge",
    "owned by the adjacent `P10-L10` MMIO packet",
    "`drivers/virtio/virtio_ring_verify.zig`",
    "make -C zigux phase10-test",
    "`Documentation/zigux/freeze-map.md` is the governing boundary note",
    "freeze-boundary owner: `P10-L10`",
    "`kernel/workqueue.c` or `kernel/trace/ring_buffer.c`",
    "`kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`",
    "roadmap-backed destination boundary through `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`",
    "does not claim a freeze-map status change or an attached Architecture Council reopen request",
]

EXPECTED_DOCS_README_MARKERS = [
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "drivers/virtio/virtio_ring_verify.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "make -C zigux phase10-test",
]

EXPECTED_REVIEW_CHECKLIST_MARKERS = [
    "Documentation/zigux/phase10-closure-evidence.md",
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_ring_verify.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]

EXPECTED_FREEZE_MAP_MARKERS = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
]

EXPECTED_CLOSURE_NOTE_MARKERS = [
    "Documentation/zigux/review-checklist.md",
    "drivers/virtio/virtio_ring_verify.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "queue-local virtqueue foothold",
]

EXPECTED_TESTS_README_MARKERS = [
    "phase10_virtio_ring.zig",
    "phase10_virtio_ring_survey.zig",
    "phase10_virtio_ring_manifest.json",
]

EXPECTED_COMPANION_MARKERS = [
    "Documentation/zigux/phase10-closure-evidence.md",
    "scripts/zigux/check-phase10-ring-packet.py",
    "drivers/virtio/virtio_ring_verify.zig",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "make -C zigux phase10-test",
]

EXPECTED_SCRIPTS_README_MARKERS = [
    "check-phase10-ring-packet.py",
    "the lane-sequenced virtio ring plus the focused ring-verify replay",
    "drivers/virtio/virtio_mmio_verify.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "make -C zigux phase10",
]

EXPECTED_SEQUENCING_MARKERS = [
    "`P10-L07` ring lane owns queue-local virtqueue-wrapper evidence:",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "scripts/zigux/check-phase10-ring-packet.py",
    "drivers/virtio/virtio_ring_verify.zig",
    "broken-queue recovery or packed-ring event-index review",
]

EXPECTED_GAPS = {
    "phase10-build-gate": "starter_landed",
    "phase10-virtio-core-lab-starter": "starter_landed",
    "phase10-virtio-ring-survey-gate": "starter_landed",
    "phase10-virtio-ring-survey-note": "starter_landed",
    "phase10-virtqueue-shape-helper": "starter_landed",
    "phase10-used-buffer-polling-helper": "starter_landed",
    "phase10-callback-enable-helper": "starter_landed",
    "phase10-callback-delay-helper": "starter_landed",
    "phase10-notify-prepare-helper": "starter_landed",
    "phase10-notification-data-summary-helper": "starter_landed",
    "phase10-broken-queue-poll-guard": "starter_landed",
    "phase10-queue-reset-helper": "starter_landed",
    "phase10-queue-reset-readiness-helper": "starter_landed",
    "phase10-ring-verify-replay": "starter_landed",
    "phase10-virtio-ring-slice-note": "starter_landed",
    "phase10-ring-lab-driver-bridge": "blocked_on_risky_transport",
}

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

EXPECTED_STUDY_ONLY_ANCHORS = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
]

EXPECTED_FREEZE_IN_C_ANCHORS = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
]

BASELINE_FIXTURE = {
    "scripts/zigux/check-phase10-ring-packet.py": "# synthetic fixture for self-test\n",
    "Documentation/zigux/README.md": """- Documentation/zigux/phase10-virtio-driver-lane-sequencing.md
- Documentation/zigux/phase10-closure-evidence.md
- drivers/virtio/virtio_ring_verify.zig
- zigux/tests/phase10_virtio_ring_manifest.json
- zigux/tests/phase10_virtio_ring_survey.zig
- make -C zigux phase10-test
""",
    "Documentation/zigux/review-checklist.md": """- Documentation/zigux/phase10-closure-evidence.md
- drivers/virtio/virtio_ring.zig
- drivers/virtio/virtio_ring_verify.zig
- zigux/tests/phase10_virtio_ring_manifest.json
- zigux/tests/phase10_virtio_ring_survey.zig
- make -C zigux phase10-test
- make -C zigux phase10
""",
    "Documentation/zigux/freeze-map.md": """- kernel/sched/core.c
- mm/page_alloc.c
- kernel/rcu/tree.c
- net/core/skbuff.c
- kernel/workqueue.c
- kernel/trace/ring_buffer.c
""",
    "Documentation/zigux/phase10-closure-evidence.md": """- Documentation/zigux/review-checklist.md
- drivers/virtio/virtio_ring_verify.zig
- zigux/tests/phase10_virtio_ring_manifest.json
- zigux/tests/phase10_virtio_ring_survey.zig
- queue-local virtqueue foothold
""",
    "scripts/zigux/README.md": """- check-phase10-ring-packet.py
- the lane-sequenced virtio ring plus the focused ring-verify replay
- drivers/virtio/virtio_mmio_verify.zig
- zigux/tests/phase10_closure_manifest.json
- make -C zigux phase10
""",
    "zigux/tests/README.md": """- phase10_virtio_ring.zig
- phase10_virtio_ring_survey.zig
- phase10_virtio_ring_manifest.json
""",
    "zigux/Makefile": """phase10-test:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-core-packet.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-core-packet.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-input-packet.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-input-packet.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-mmio-packet.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-mmio-packet.py
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase10_build.zig
""",
    "zigux/tests/phase10_build.zig": """const phase10_virtio_ring_module = b.createModule(.{});
const phase10_virtio_ring_survey_module = b.createModule(.{});
const phase10_virtio_ring_verify_module = b.createModule(.{});
const phase10_virtio_ring_tests = b.addTest(.{ .name = \"phase10-virtio-ring-tests\" });
const phase10_virtio_ring_survey_tests = b.addTest(.{ .name = \"phase10-virtio-ring-survey-tests\" });
const phase10_virtio_ring_verify_tests = b.addTest(.{ .name = \"phase10-virtio-ring-verify-tests\" });
""",
    "drivers/virtio/virtio_ring.zig": """pub const PackedEventIndexSummary = struct {};
pub fn packedEventIndexSummary(self: *Self, queue_index: u16) !PackedEventIndexSummary { _ = self; _ = queue_index; }
pub const NotificationDataSummary = struct {};
pub fn notificationDataSummary(self: *const Self, queue_index: u16) !NotificationDataSummary { _ = self; _ = queue_index; }
pub const QueueResetReadinessSummary = struct {};
pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary { _ = self; _ = queue_index; }
pub fn resetQueue(self: *Self, queue_index: u16) !QueueResetSummary { _ = self; _ = queue_index; }
pub fn markBroken(self: *Self, queue_index: u16) !BrokenQueueSummary { _ = self; _ = queue_index; }
""",
    "drivers/virtio/virtio_ring_verify.zig": """test \"virtio ring clearBroken exposes the next reset blocker instead of hiding queue debt\" {
    _ = try lab.clearBroken(4);
    try testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.unpublished_chains, readiness.blocker.?);
    _ = try lab.clearBroken(5);
    try testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.outstanding_chains, readiness.blocker.?);
    _ = try lab.clearBroken(6);
    try testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.unpolled_used_chains, readiness.blocker.?);
}
test \"virtio ring packed event-index summary stays queue-local and reports when polling can wait\" {
    try testing.expectError(error.QueueLayoutDoesNotSupportPackedEventIndex, lab.packedEventIndexSummary(1));
    try testing.expectError(error.QueueDoesNotUseEventIndex, lab.packedEventIndexSummary(2));
    try testing.expectEqual(@as(u16, 3), summary.event_index_window);
    try testing.expect(!summary.should_poll);
    try testing.expectEqual(@as(u16, 1), summary.event_index_window);
    try testing.expect(summary.should_poll);
}
test \"virtio ring notification-data summary tracks packed wrap and split reset transitions\" {
    try testing.expectEqual(@as(u32, 0x8001_0001), summary.notification_data);
    try testing.expectEqual(@as(u32, 1), summary.notification_data);
}
""",
    "zigux/tests/phase10_virtio_ring.zig": """test \"phase10 virtio ring reset-readiness preflight reports the current queue blocker\" {}
test \"phase10 virtio ring broken summary keeps queue-local debt reviewable while blocking queue work\" {}
test \"phase10 virtio ring delayed callback pacing reports both thresholded and immediate poll cases\" {}
test \"phase10 virtio ring callback re-enable reports pending used work and settles after poll\" {}
""",
    "zigux/tests/phase10_virtio_ring_survey.zig": """test \"phase10 virtio ring survey manifest records the queue-local foothold and remaining lab-driver bridge\" {
    try std.testing.expectEqualStrings(\"P10-L07\", manifest.lane_key);
    try std.testing.expect(manifest.gaps.len >= 16);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, \"notification-data summary\") != null);
    try std.testing.expect(std.mem.indexOf(u8, verify_replay, \"test \\\"virtio ring notification-data summary tracks packed wrap and split reset transitions\\\" {\") != null);
    try std.testing.expect(std.mem.indexOf(u8, verify_replay, \"try testing.expectEqual(@as(u32, 0x8001_0001), summary.notification_data);\") != null);
    var saw_notification_data_helper = false;
    var saw_ring_verify_replay = false;
    var saw_ring_lab_driver_bridge = false;
    if (std.mem.eql(u8, gap.id, \"phase10-notification-data-summary-helper\")) {
        try std.testing.expect(std.mem.indexOf(u8, gap.why_now, \"packed wrap-bit transitions\") != null);
    }
    try std.testing.expectEqual(@as(usize, 15), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_notification_data_helper);
}
""",
    "Documentation/zigux/phase10-virtio-ring-slice.md": """- dedicated ring packet review guard
- `scripts/zigux/check-phase10-ring-packet.py`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `drivers/virtio/virtio_ring_verify.zig`
- `zig test zigux/tests/phase10_virtio_ring.zig`
- `zig test zigux/tests/phase10_virtio_ring_survey.zig`
""",
    "Documentation/zigux/phase10-virtio-ring-survey.md": """- lab-driver threshold
- queue-local ring foothold
- notification-data summary
- phase10-ring-lab-driver-bridge
- owned by the adjacent `P10-L10` MMIO packet
- `drivers/virtio/virtio_ring_verify.zig`
- `make -C zigux phase10-test`
- `Documentation/zigux/freeze-map.md` is the governing boundary note
- freeze-boundary owner: `P10-L10`
- `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`
- `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`
- roadmap-backed destination boundary through `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`
- does not claim a freeze-map status change or an attached Architecture Council reopen request
""",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": """- `Documentation/zigux/phase10-closure-evidence.md`
- `scripts/zigux/check-phase10-ring-packet.py`
- `drivers/virtio/virtio_ring_verify.zig`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `zigux/tests/phase10_virtio_ring_survey.zig`
- `make -C zigux phase10-test`
""",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": """- `P10-L07` ring lane owns queue-local virtqueue-wrapper evidence:
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `scripts/zigux/check-phase10-ring-packet.py`
- `drivers/virtio/virtio_ring_verify.zig`
- broken-queue recovery or packed-ring event-index review
""",
    "zigux/tests/phase10_virtio_ring_manifest.json": json.dumps(
        {
            "lane_key": "P10-L07",
            "phase": "Phase 10",
            "surveyed_commit": "e42103fc02f544e1bd23a5ec2e5b584734f5af7d",
            "anchor": "drivers/virtio/virtio_ring.c",
            "roadmap_destinations": ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"],
            "freeze_map": "Documentation/zigux/freeze-map.md",
            "freeze_boundary_status": "aligned",
            "freeze_status_change_claimed": False,
            "risky_transport_posture": "blocked_on_risky_transport",
            "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
            "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
            "architecture_council_reopen_required": True,
            "architecture_council_reopen_attached": False,
            "freeze_boundary_owner_lane": "P10-L10",
            "study_only_anchors": EXPECTED_STUDY_ONLY_ANCHORS,
            "freeze_in_c_anchors": EXPECTED_FREEZE_IN_C_ANCHORS,
            "survey_summary": {
                "virtio_ring_c_lines": 3940,
                "preexisting_phase10_test_files": 7,
                "preexisting_virtio_core_zig_present": True,
                "preexisting_phase10_build_present": True,
                "preexisting_phase10_core_doc_present": True,
                "preexisting_virtio_ring_zig_present": True,
                "preexisting_virtio_ring_doc_present": True,
                "preexisting_ring_verify_present": True,
            },
            "gaps": [
                {"id": "phase10-build-gate", "status": "starter_landed"},
                {"id": "phase10-virtio-core-lab-starter", "status": "starter_landed"},
                {"id": "phase10-virtio-ring-survey-gate", "status": "starter_landed"},
                {"id": "phase10-virtio-ring-survey-note", "status": "starter_landed"},
                {"id": "phase10-virtqueue-shape-helper", "status": "starter_landed"},
                {"id": "phase10-used-buffer-polling-helper", "status": "starter_landed"},
                {"id": "phase10-callback-enable-helper", "status": "starter_landed"},
                {"id": "phase10-callback-delay-helper", "status": "starter_landed"},
                {"id": "phase10-notify-prepare-helper", "status": "starter_landed"},
                {"id": "phase10-notification-data-summary-helper", "status": "starter_landed"},
                {"id": "phase10-broken-queue-poll-guard", "status": "starter_landed"},
                {"id": "phase10-queue-reset-helper", "status": "starter_landed"},
                {"id": "phase10-queue-reset-readiness-helper", "status": "starter_landed"},
                {"id": "phase10-ring-verify-replay", "status": "starter_landed"},
                {"id": "phase10-virtio-ring-slice-note", "status": "starter_landed"},
                {"id": "phase10-ring-lab-driver-bridge", "status": "blocked_on_risky_transport"},
            ],
        },
        indent=2,
    )
    + "\n",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def expect_markers(text: str, markers: list[str], prefix: str, missing_markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing_markers.append(f"{prefix}:{marker}")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []

    expect_markers(read_text(root, "Documentation/zigux/README.md"), EXPECTED_DOCS_README_MARKERS, "docs_readme", missing_markers)
    expect_markers(read_text(root, "Documentation/zigux/review-checklist.md"), EXPECTED_REVIEW_CHECKLIST_MARKERS, "review_checklist", missing_markers)
    expect_markers(read_text(root, "Documentation/zigux/freeze-map.md"), EXPECTED_FREEZE_MAP_MARKERS, "freeze_map", missing_markers)
    expect_markers(read_text(root, "Documentation/zigux/phase10-closure-evidence.md"), EXPECTED_CLOSURE_NOTE_MARKERS, "closure_note", missing_markers)
    expect_markers(read_text(root, "scripts/zigux/README.md"), EXPECTED_SCRIPTS_README_MARKERS, "scripts_readme", missing_markers)
    expect_markers(read_text(root, "zigux/tests/README.md"), EXPECTED_TESTS_README_MARKERS, "tests_readme", missing_markers)
    expect_markers(read_text(root, "zigux/tests/phase10_build.zig"), EXPECTED_BUILD_MARKERS, "build", missing_markers)
    expect_markers(read_text(root, "zigux/Makefile"), EXPECTED_MAKEFILE_MARKERS, "makefile", missing_markers)
    expect_markers(read_text(root, "drivers/virtio/virtio_ring.zig"), EXPECTED_HELPER_MARKERS, "helper", missing_markers)
    expect_markers(read_text(root, "drivers/virtio/virtio_ring_verify.zig"), EXPECTED_VERIFY_TEST_MARKERS, "verify", missing_markers)
    expect_markers(read_text(root, "zigux/tests/phase10_virtio_ring.zig"), EXPECTED_TEST_MARKERS, "tests", missing_markers)
    expect_markers(read_text(root, "zigux/tests/phase10_virtio_ring_survey.zig"), EXPECTED_SURVEY_TEST_MARKERS, "survey_test", missing_markers)
    expect_markers(read_text(root, "Documentation/zigux/phase10-virtio-ring-slice.md"), EXPECTED_SLICE_MARKERS, "slice", missing_markers)
    expect_markers(read_text(root, "Documentation/zigux/phase10-virtio-ring-survey.md"), EXPECTED_SURVEY_NOTE_MARKERS, "survey_note", missing_markers)
    expect_markers(read_text(root, "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"), EXPECTED_COMPANION_MARKERS, "companion", missing_markers)
    expect_markers(read_text(root, "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md"), EXPECTED_SEQUENCING_MARKERS, "sequencing", missing_markers)

    manifest = json.loads(read_text(root, "zigux/tests/phase10_virtio_ring_manifest.json"))
    if manifest.get("lane_key") != "P10-L07":
        missing_markers.append("manifest:lane_key=P10-L07")
    if manifest.get("phase") != "Phase 10":
        missing_markers.append("manifest:phase=Phase 10")
    if manifest.get("anchor") != "drivers/virtio/virtio_ring.c":
        missing_markers.append("manifest:anchor=drivers/virtio/virtio_ring.c")
    if manifest.get("surveyed_commit") != "e42103fc02f544e1bd23a5ec2e5b584734f5af7d":
        missing_markers.append("manifest:surveyed_commit")
    if manifest.get("roadmap_destinations") != ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"]:
        missing_markers.append("manifest:roadmap_destinations")
    if manifest.get("freeze_map") != "Documentation/zigux/freeze-map.md":
        missing_markers.append("manifest:freeze_map")
    if manifest.get("freeze_boundary_status") != "aligned":
        missing_markers.append("manifest:freeze_boundary_status=aligned")
    if manifest.get("freeze_status_change_claimed") is not False:
        missing_markers.append("manifest:freeze_status_change_claimed=false")
    if manifest.get("risky_transport_posture") != "blocked_on_risky_transport":
        missing_markers.append("manifest:risky_transport_posture=blocked_on_risky_transport")
    if manifest.get("allowed_evidence_kinds") != EXPECTED_ALLOWED_EVIDENCE_KINDS:
        missing_markers.append("manifest:allowed_evidence_kinds")
    if manifest.get("forbidden_transport_claims") != EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS:
        missing_markers.append("manifest:forbidden_transport_claims")
    if manifest.get("architecture_council_reopen_required") is not True:
        missing_markers.append("manifest:architecture_council_reopen_required=true")
    if manifest.get("architecture_council_reopen_attached") is not False:
        missing_markers.append("manifest:architecture_council_reopen_attached=false")
    if manifest.get("freeze_boundary_owner_lane") != "P10-L10":
        missing_markers.append("manifest:freeze_boundary_owner_lane=P10-L10")
    if manifest.get("study_only_anchors") != EXPECTED_STUDY_ONLY_ANCHORS:
        missing_markers.append("manifest:study_only_anchors")
    if manifest.get("freeze_in_c_anchors") != EXPECTED_FREEZE_IN_C_ANCHORS:
        missing_markers.append("manifest:freeze_in_c_anchors")

    summary = manifest.get("survey_summary", {})
    if summary.get("virtio_ring_c_lines") != 3940:
        missing_markers.append("manifest:virtio_ring_c_lines=3940")
    if summary.get("preexisting_phase10_test_files") != 7:
        missing_markers.append("manifest:preexisting_phase10_test_files=7")
    for key in [
        "preexisting_virtio_core_zig_present",
        "preexisting_phase10_build_present",
        "preexisting_phase10_core_doc_present",
        "preexisting_virtio_ring_zig_present",
        "preexisting_virtio_ring_doc_present",
        "preexisting_ring_verify_present",
    ]:
        if summary.get(key) is not True:
            missing_markers.append(f"manifest:{key}")

    gaps = manifest.get("gaps", [])
    if len(gaps) != len(EXPECTED_GAPS):
        missing_markers.append(f"manifest:gaps={len(gaps)}")
    gap_index = {gap.get("id"): gap for gap in gaps if isinstance(gap, dict)}
    for gap_id, status in EXPECTED_GAPS.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            missing_markers.append(f"manifest:gap:{gap_id}")
            continue
        if gap.get("status") != status:
            missing_markers.append(f"manifest:gap_status:{gap_id}={gap.get('status')}")

    return missing_files, missing_markers


def write_fixture(root: Path, rel_path: str, content: str) -> None:
    target = root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def assert_missing(root: Path, rel_path: str, old: str, new: str, expected: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    _, missing_markers = validate(root)
    if expected not in missing_markers:
        raise SystemExit(f"phase10-ring-self-test:expected_marker_missing:{expected}")
    path.write_text(original, encoding="utf-8")


def assert_manifest_drift(root: Path, transform, expected: str) -> None:
    path = root / "zigux/tests/phase10_virtio_ring_manifest.json"
    original = path.read_text(encoding="utf-8")
    manifest = json.loads(original)
    transform(manifest)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    _, missing_markers = validate(root)
    if expected not in missing_markers:
        raise SystemExit(f"phase10-ring-self-test:expected_marker_missing:{expected}")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_ring_packet_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        for rel_path, content in BASELINE_FIXTURE.items():
            write_fixture(tmp_root, rel_path, content)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-ring-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        case_count = 0

        def run_manifest_case(transform, expected: str) -> None:
            nonlocal case_count
            assert_manifest_drift(tmp_root, transform, expected)
            case_count += 1

        def run_missing_case(root: Path, rel_path: str, old: str, new: str, expected: str) -> None:
            nonlocal case_count
            assert_missing(root, rel_path, old, new, expected)
            case_count += 1

        run_manifest_case(
            lambda manifest: manifest.__setitem__("lane_key", "P10-drift"),
            "manifest:lane_key=P10-L07",
        )
        run_manifest_case(
            lambda manifest: manifest.__setitem__("freeze_boundary_status", "drifted"),
            "manifest:freeze_boundary_status=aligned",
        )
        run_manifest_case(
            lambda manifest: manifest.__setitem__("freeze_status_change_claimed", True),
            "manifest:freeze_status_change_claimed=false",
        )
        run_manifest_case(
            lambda manifest: manifest.__setitem__("risky_transport_posture", "ready_for_transport"),
            "manifest:risky_transport_posture=blocked_on_risky_transport",
        )
        run_manifest_case(
            lambda manifest: manifest.__setitem__("allowed_evidence_kinds", ["driver_local_lab_slices"]),
            "manifest:allowed_evidence_kinds",
        )
        run_manifest_case(
            lambda manifest: manifest.__setitem__("forbidden_transport_claims", ["queue_setup_reset_paths", "irq_parity"]),
            "manifest:forbidden_transport_claims",
        )
        run_manifest_case(
            lambda manifest: manifest.__setitem__("architecture_council_reopen_required", False),
            "manifest:architecture_council_reopen_required=true",
        )
        run_manifest_case(
            lambda manifest: manifest.__setitem__("architecture_council_reopen_attached", True),
            "manifest:architecture_council_reopen_attached=false",
        )
        run_manifest_case(
            lambda manifest: manifest.__setitem__("freeze_boundary_owner_lane", "P10-drift"),
            "manifest:freeze_boundary_owner_lane=P10-L10",
        )
        run_manifest_case(
            lambda manifest: manifest.__setitem__("study_only_anchors", ["kernel/workqueue.c"]),
            "manifest:study_only_anchors",
        )
        run_manifest_case(
            lambda manifest: manifest.__setitem__(
                "freeze_in_c_anchors",
                ["kernel/sched/core.c", "mm/page_alloc.c", "kernel/rcu/tree.c"],
            ),
            "manifest:freeze_in_c_anchors",
        )

        def drift_gap_status(manifest: dict) -> None:
            for gap in manifest.get("gaps", []):
                if gap.get("id") == "phase10-queue-reset-helper":
                    gap["status"] = "ready_next"

        run_manifest_case(
            drift_gap_status,
            "manifest:gap_status:phase10-queue-reset-helper=ready_next",
        )

        run_missing_case(
            tmp_root,
            "zigux/Makefile",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py --self-test\n",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-drift.py --self-test\n",
            "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py --self-test\n",
        )
        run_missing_case(
            tmp_root,
            "zigux/tests/phase10_build.zig",
            '"phase10-virtio-ring-verify-tests"',
            '"phase10-virtio-ring-verify-drift-tests"',
            'build:"phase10-virtio-ring-verify-tests"',
        )
        run_missing_case(
            tmp_root,
            "drivers/virtio/virtio_ring.zig",
            "pub fn packedEventIndexSummary(self: *Self, queue_index: u16) !PackedEventIndexSummary {",
            "pub fn packedEventIndexDrift(self: *Self, queue_index: u16) !PackedEventIndexSummary {",
            "helper:pub fn packedEventIndexSummary(self: *Self, queue_index: u16) !PackedEventIndexSummary {",
        )
        run_missing_case(
            tmp_root,
            "drivers/virtio/virtio_ring.zig",
            "pub fn notificationDataSummary(self: *const Self, queue_index: u16) !NotificationDataSummary {",
            "pub fn notificationDataDrift(self: *const Self, queue_index: u16) !NotificationDataSummary {",
            "helper:pub fn notificationDataSummary(self: *const Self, queue_index: u16) !NotificationDataSummary {",
        )
        run_missing_case(
            tmp_root,
            "drivers/virtio/virtio_ring.zig",
            "pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {",
            "pub fn queueResetReadinessDrift(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {",
            "helper:pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {",
        )
        run_missing_case(
            tmp_root,
            "drivers/virtio/virtio_ring_verify.zig",
            'test "virtio ring packed event-index summary stays queue-local and reports when polling can wait" {',
            'test "virtio ring packed event-index drift" {',
            'verify:test "virtio ring packed event-index summary stays queue-local and reports when polling can wait" {',
        )
        run_missing_case(
            tmp_root,
            "drivers/virtio/virtio_ring_verify.zig",
            'test "virtio ring notification-data summary tracks packed wrap and split reset transitions" {',
            'test "virtio ring notification-data drift" {',
            'verify:test "virtio ring notification-data summary tracks packed wrap and split reset transitions" {',
        )
        run_missing_case(
            tmp_root,
            "drivers/virtio/virtio_ring_verify.zig",
            "_ = try lab.clearBroken(4);",
            "_ = try lab.clearBroken(7);",
            "verify:_ = try lab.clearBroken(4);",
        )
        run_missing_case(
            tmp_root,
            "drivers/virtio/virtio_ring_verify.zig",
            "try testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.unpolled_used_chains, readiness.blocker.?);",
            "try testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.queue_broken, readiness.blocker.?);",
            "verify:try testing.expectEqual(virtio_ring.QueueResetReadinessBlocker.unpolled_used_chains, readiness.blocker.?);",
        )
        run_missing_case(
            tmp_root,
            "zigux/tests/phase10_virtio_ring.zig",
            'test "phase10 virtio ring broken summary keeps queue-local debt reviewable while blocking queue work" {',
            'test "phase10 virtio ring blocks publish drift while a queue is broken" {',
            'tests:test "phase10 virtio ring broken summary keeps queue-local debt reviewable while blocking queue work" {',
        )
        run_missing_case(
            tmp_root,
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "lab-driver threshold",
            "roadmap threshold",
            "survey_note:lab-driver threshold",
        )
        run_missing_case(
            tmp_root,
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "notification-data summary",
            "notification-data drift",
            "survey_note:notification-data summary",
        )
        run_missing_case(
            tmp_root,
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "`drivers/virtio/virtio_ring_verify.zig`",
            "`drivers/virtio/virtio_ring_verify_drift.zig`",
            "survey_note:`drivers/virtio/virtio_ring_verify.zig`",
        )
        run_missing_case(
            tmp_root,
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "freeze-boundary owner: `P10-L10`",
            "freeze-boundary owner: `P10-drift`",
            "survey_note:freeze-boundary owner: `P10-L10`",
        )
        run_missing_case(
            tmp_root,
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "roadmap-backed destination boundary through `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`",
            "roadmap-backed destination boundary through `drivers/virtio/*.zig`",
            "survey_note:roadmap-backed destination boundary through `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`",
        )
        run_missing_case(
            tmp_root,
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "`kernel/workqueue.c` or `kernel/trace/ring_buffer.c`",
            "`kernel/workqueue.c` or `kernel/trace/ring_buffer_drift.c`",
            "survey_note:`kernel/workqueue.c` or `kernel/trace/ring_buffer.c`",
        )
        run_missing_case(
            tmp_root,
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "`kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`",
            "`kernel/sched/core.c`, `mm/page_alloc.c`, and `kernel/rcu/tree.c`",
            "survey_note:`kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`",
        )
        run_missing_case(
            tmp_root,
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "does not claim a freeze-map status change or an attached Architecture Council reopen request",
            "does not claim a status change or reopen request",
            "survey_note:does not claim a freeze-map status change or an attached Architecture Council reopen request",
        )
        run_missing_case(
            tmp_root,
            "Documentation/zigux/README.md",
            "drivers/virtio/virtio_ring_verify.zig",
            "drivers/virtio/virtio_ring_verify_drift.zig",
            "docs_readme:drivers/virtio/virtio_ring_verify.zig",
        )
        run_missing_case(
            tmp_root,
            "Documentation/zigux/review-checklist.md",
            "drivers/virtio/virtio_ring_verify.zig",
            "drivers/virtio/virtio_ring_verify_drift.zig",
            "review_checklist:drivers/virtio/virtio_ring_verify.zig",
        )
        run_missing_case(
            tmp_root,
            "Documentation/zigux/freeze-map.md",
            "kernel/trace/ring_buffer.c",
            "kernel/trace/ring_buffer_drift.c",
            "freeze_map:kernel/trace/ring_buffer.c",
        )
        run_missing_case(
            tmp_root,
            "Documentation/zigux/phase10-closure-evidence.md",
            "zigux/tests/phase10_virtio_ring_manifest.json",
            "zigux/tests/phase10_virtio_ring_manifest_drift.json",
            "closure_note:zigux/tests/phase10_virtio_ring_manifest.json",
        )
        run_missing_case(
            tmp_root,
            "zigux/tests/README.md",
            "phase10_virtio_ring_manifest.json",
            "phase10_virtio_ring_manifest_drift.json",
            "tests_readme:phase10_virtio_ring_manifest.json",
        )
        run_missing_case(
            tmp_root,
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
            "Documentation/zigux/phase10-closure-evidence.md",
            "Documentation/zigux/phase10-closure-drift.md",
            "companion:Documentation/zigux/phase10-closure-evidence.md",
        )
        run_missing_case(
            tmp_root,
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
            "scripts/zigux/check-phase10-ring-packet.py",
            "scripts/zigux/check-phase10-ring-drift.py",
            "companion:scripts/zigux/check-phase10-ring-packet.py",
        )
        run_missing_case(
            tmp_root,
            "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
            "scripts/zigux/check-phase10-ring-packet.py",
            "scripts/zigux/check-phase10-ring-drift.py",
            "sequencing:scripts/zigux/check-phase10-ring-packet.py",
        )
        run_missing_case(
            tmp_root,
            "scripts/zigux/README.md",
            "the lane-sequenced virtio ring plus the focused ring-verify replay",
            "the lane-sequenced virtio ring plus a drifted verifier cue",
            "scripts_readme:the lane-sequenced virtio ring plus the focused ring-verify replay",
        )
        run_missing_case(
            tmp_root,
            "zigux/tests/phase10_virtio_ring_survey.zig",
            "var saw_notification_data_helper = false;",
            "var saw_notification_data_drift = false;",
            "survey_test:var saw_notification_data_helper = false;",
        )

    print("PHASE10_RING_PACKET_SELF_TEST=pass")
    print(f"PHASE10_RING_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 10 virtio_ring packet.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in drift checks against a synthetic fixture tree.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_RING_PACKET=fail")
        print("MISSING_PHASE10_RING_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_RING_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_RING_PACKET=fail")
        print("MISSING_PHASE10_RING_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_RING_MARKERS_END")
        return 1

    print("PHASE10_RING_PACKET=pass")
    print(f"PHASE10_RING_REQUIRED_FILE_COUNT={len(FILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
