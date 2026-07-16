const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE10_RING_PACKET=pass";
pub const self_test_pass_marker = "PHASE10_RING_PACKET_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };
const GapExpectation = struct { id: []const u8, kind: []const u8, status: []const u8, destination: []const u8 };
const Gap = struct { id: []const u8, kind: []const u8, status: []const u8, zigux_destination: []const u8 };
const SurveySummary = struct {
    virtio_ring_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_virtio_core_zig_present: bool,
    preexisting_phase10_build_present: bool,
    preexisting_phase10_core_doc_present: bool,
    preexisting_virtio_ring_zig_present: bool,
    preexisting_virtio_ring_doc_present: bool,
    preexisting_ring_verify_present: bool,
    preexisting_ring_publish_readiness_present: bool,
    preexisting_ring_callback_enable_present: bool,
    preexisting_ring_registration_summary_present: bool,
    preexisting_ring_reset_readiness_present: bool,
    preexisting_ring_used_buffer_poll_present: bool,
};
const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    freeze_map: []const u8,
    freeze_boundary_status: []const u8,
    freeze_status_change_claimed: bool,
    risky_transport_posture: []const u8,
    allowed_evidence_kinds: []const []const u8,
    forbidden_transport_claims: []const []const u8,
    architecture_council_reopen_required: bool,
    architecture_council_reopen_attached: bool,
    study_only_anchors: []const []const u8,
    freeze_in_c_anchors: []const []const u8,
    freeze_boundary_owner_lane: []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

const markers_0 = [_][]const u8{
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
    "direct contents reads rematerialize `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `drivers/virtio/virtio_ring_notification_data.zig`, `drivers/virtio/virtio_ring_callback_enable.zig`, `drivers/virtio/virtio_ring_registration_summary.zig`, `drivers/virtio/virtio_ring_used_buffer_poll.zig`, the broader replay `zigux/tests/phase10_virtio_ring.zig`",
    "`phase10-used-buffer-polling-helper`",
    "`phase10-queue-registration-summary-helper`",
    "`phase10-ring-reset-readiness-replay`",
    "`zigux/tests/phase10_virtio_ring_queue_build_survey.zig` now gives the ring lane one focused queue-build survey replay",
    "the blocked `phase10-ring-lab-driver-bridge` remains owned by the adjacent `P10-L11` MMIO packet",
};

const markers_1 = [_][]const u8{
    "current packet lane on master: `P10-L10`",
    "adjacent freeze-boundary owner: `P10-L11`",
    "direct current-head readback now keeps the broader ring replay `zigux/tests/phase10_virtio_ring.zig` inside the same ring packet as the queue-local helper ladder",
    "the used-buffer-poll wrapper `drivers/virtio/virtio_ring_used_buffer_poll.zig`, the publish-readiness helper `drivers/virtio/virtio_ring_publish_readiness.zig`, the notification-data replay `zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`, the reset-readiness replay `zigux/tests/phase10_virtio_ring_reset_readiness.zig`, and the dedicated ring survey replay `zigux/tests/phase10_virtio_ring_survey.zig` stay part of the same directly readable ring packet",
    "the smallest same-lane follow-through is reminder-surface, checker, or manifest truthfulness work",
};

const markers_2 = [_][]const u8{
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
};

const markers_3 = [_][]const u8{
    "`scripts\\zigux/check_phase10_ring_packet.zig`, `scripts\\zigux/check_phase10_input_packet.zig`, `scripts\\zigux/check_phase10_mmio_packet.zig`",
    "`drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `drivers/virtio/virtio_ring_notification_data.zig`, `drivers/virtio/virtio_ring_callback_enable.zig`, `drivers/virtio/virtio_ring_registration_summary.zig`, `drivers/virtio/virtio_ring_reset_readiness.zig`, `drivers/virtio/virtio_ring_used_buffer_poll.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`",
    "Keep the queue-local `P10-L10` ring freeze-boundary packet distinct from the bounded `P10-L11` MMIO helper packet when shared reviewer-facing reminders refresh",
    "the ring survey, slice, and freeze-boundary notes, the direct ring helper packet through `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`,",
};

const markers_4 = [_][]const u8{
    "ring lane `P10-L10` owns the queue-local wrapper packet",
    "zigux/tests/phase10_virtio_ring_reset_readiness.zig",
    "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md",
    "queue-local wrapper reviewability does not drift into MMIO-owned blocked transport claims",
};

const markers_5 = [_][]const u8{
    "pub const QueueShapeSummary = struct {",
    "pub const NotificationDataSummary = struct {",
    "pub fn notificationSummary(self: *const Self, queue_index: u16) !QueueNotificationSummary {",
    "pub fn enableCallback(self: *Self, queue_index: u16) !CallbackEnableSummary {",
    "pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {",
};

const markers_6 = [_][]const u8{
    "pub fn summarizeNotificationState(",
    "pub fn summarizeNotificationData(",
    "pub fn summarizeDelayedCallback(",
    "pub fn summarizeResetReadiness(",
    "test \"phase10 virtio ring verify keeps notification-state wrapper explicit across publish kick and used replay\" {",
    "test \"phase10 virtio ring verify exposes reset-readiness blocker ordering after clearBroken releases queue debt\" {",
    "test \"phase10 virtio ring verify keeps reset-readiness blockers ordered through queue-local replay\" {",
};

const markers_7 = [_][]const u8{
    "pub fn summarizeNotificationData(",
    "pub fn notificationDataUsesWrapBit(summary: NotificationDataSummary) bool {",
    "pub fn queueIndexMatchesNotificationData(summary: NotificationDataSummary) bool {",
    "pub fn nextAvailStateMatchesEncoding(summary: NotificationDataSummary) bool {",
    "test \"phase10 virtio ring notification-data wrapper keeps split queue state explicit\" {",
    "test \"phase10 virtio ring notification-data wrapper preserves packed wrap encoding across u16 rollover\" {",
};

const markers_8 = [_][]const u8{
    "pub fn summarizePublishReadiness(",
    "pub fn queueCanPublish(summary: QueuePublishReadinessSummary) bool {",
    "pub fn queueHasPublishCapacity(summary: QueuePublishReadinessSummary) bool {",
    "test \"phase10 virtio ring publish-readiness wrapper keeps empty queues publishable\" {",
    "test \"phase10 virtio ring publish-readiness wrapper keeps unpublished chains visible while remaining queue-local publishable\" {",
    "test \"phase10 virtio ring publish-readiness wrapper blocks full queues until used chains return capacity\" {",
    "test \"phase10 virtio ring publish-readiness wrapper regains publish capacity before used buffers are polled\" {",
    "test \"phase10 virtio ring publish-readiness wrapper keeps broken queues fenced even when slots remain\" {",
    "test \"phase10 virtio ring publish-readiness wrapper falls back to queue-full after a broken full queue is cleared\" {",
};

const markers_9 = [_][]const u8{
    "pub fn summarizeQueueRegistration(",
    "pub fn summarizeRegisteredQueueCount(ring: *const virtio_ring.VirtioRingLab) usize {",
    "pub fn queueDefinitionDisciplineStable(",
    "test \"phase10 virtio ring registration-summary wrapper keeps definition discipline explicit\" {",
    "test \"phase10 virtio ring registration-summary wrapper stays queue-local across noncontiguous queue definitions\" {",
};

const markers_10 = [_][]const u8{
    "pub fn summarizeUsedBufferPoll(",
    "pub fn usedBufferPollHasNewChains(summary: UsedBufferPollSummary) bool {",
    "pub fn usedBufferPollSettled(summary: UsedBufferPollSummary) bool {",
    "test \"phase10 virtio ring used-buffer-poll wrapper keeps empty queues settled\" {",
    "test \"phase10 virtio ring used-buffer-poll wrapper exposes newly used chains before the follow-up poll settles\" {",
    "test \"phase10 virtio ring used-buffer-poll wrapper settles once all used chains are observed\" {",
};

const markers_11 = [_][]const u8{
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
};

const markers_12 = [_][]const u8{
    "test \"phase10 virtio ring notification-data replay keeps split and packed next-avail state explicit\" {",
    "const packed_summary = try ring.notificationDataSummary(2);",
};

const markers_13 = [_][]const u8{
    "test \"phase10 virtio ring queue build keeps the focused queue packet explicit\" {",
    ".root_source_file = b.path(\\\"../../drivers/virtio/virtio_ring_notification_data.zig\\\"),",
    ".root_source_file = b.path(\\\"phase10_virtio_ring_queue_build_survey.zig\\\"),",
    ".name = \\\"phase10-virtio-ring-notification-data-wrapper-tests\\\",",
    ".name = \\\"phase10-virtio-ring-queue-build-survey-tests\\\",",
    "run_phase10_virtio_ring_notification_data_wrapper_tests.step",
    "run_phase10_virtio_ring_queue_build_survey_tests.step",
};

const markers_14 = [_][]const u8{
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
    "phase10 virtio ring used-buffer-poll wrapper exposes newly used chains before the follow-up poll settles",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase10-virtio-ring-survey.md", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase10-virtio-ring-slice.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md", .markers = &markers_4 },
    .{ .rel = "drivers/virtio/virtio_ring.zig", .markers = &markers_5 },
    .{ .rel = "drivers/virtio/virtio_ring_verify.zig", .markers = &markers_6 },
    .{ .rel = "drivers/virtio/virtio_ring_notification_data.zig", .markers = &markers_7 },
    .{ .rel = "drivers/virtio/virtio_ring_publish_readiness.zig", .markers = &markers_8 },
    .{ .rel = "drivers/virtio/virtio_ring_registration_summary.zig", .markers = &markers_9 },
    .{ .rel = "drivers/virtio/virtio_ring_used_buffer_poll.zig", .markers = &markers_10 },
    .{ .rel = "zigux/tests/phase10_build.zig", .markers = &markers_11 },
    .{ .rel = "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig", .markers = &markers_12 },
    .{ .rel = "zigux/tests/phase10_virtio_ring_queue_build_survey.zig", .markers = &markers_13 },
    .{ .rel = "zigux/tests/phase10_virtio_ring_survey.zig", .markers = &markers_14 },
};

const forbidden_markers_0 = [_][]const u8{
    "public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` even though exact direct-path contents reads in this lane still leave that broader replay outside the queue-local helper ladder",
};

const forbidden_markers_1 = [_][]const u8{
    "public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` but it still remains outside exact direct-path current-head evidence in this slice",
    "the broader ring replay still remains outside direct current-head evidence in this slice",
};

const forbidden_markers_2 = [_][]const u8{
    "try expectContains(slice_note, \"public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` but it still remains outside exact direct-path current-head evidence in this slice\");",
    "try expectContains(freeze_note, \"public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` even though exact direct-path contents reads in this lane still leave that broader replay outside the queue-local helper ladder\");",
};

const forbidden_contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md", .markers = &forbidden_markers_0 },
    .{ .rel = "Documentation/zigux/phase10-virtio-ring-slice.md", .markers = &forbidden_markers_1 },
    .{ .rel = "zigux/tests/phase10_virtio_ring_survey.zig", .markers = &forbidden_markers_2 },
};

const expected_gaps = [_]GapExpectation{
    .{ .id = "phase10-build-gate", .kind = "validation", .status = "starter_landed", .destination = "zigux/tests/phase10_build.zig" },
    .{ .id = "phase10-virtio-core-lab-starter", .kind = "lab_driver_starter", .status = "starter_landed", .destination = "drivers/virtio/virtio.zig" },
    .{ .id = "phase10-ring-registration-replay", .kind = "validation", .status = "starter_landed", .destination = "zigux/tests/phase10_virtio_ring_registration_replay.zig" },
    .{ .id = "phase10-ring-reset-readiness-replay", .kind = "validation", .status = "starter_landed", .destination = "zigux/tests/phase10_virtio_ring_reset_readiness.zig" },
    .{ .id = "phase10-virtio-ring-survey-gate", .kind = "validation", .status = "starter_landed", .destination = "zigux/tests/phase10_virtio_ring_survey.zig" },
    .{ .id = "phase10-virtio-ring-survey-note", .kind = "documentation", .status = "starter_landed", .destination = "Documentation/zigux/phase10-virtio-ring-survey.md" },
    .{ .id = "phase10-virtqueue-shape-helper", .kind = "queue_wrapper", .status = "starter_landed", .destination = "drivers/virtio/virtio_ring.zig" },
    .{ .id = "phase10-used-buffer-polling-helper", .kind = "queue_wrapper", .status = "starter_landed", .destination = "drivers/virtio/virtio_ring_used_buffer_poll.zig" },
    .{ .id = "phase10-callback-enable-helper", .kind = "queue_wrapper", .status = "starter_landed", .destination = "drivers/virtio/virtio_ring_callback_enable.zig" },
    .{ .id = "phase10-callback-delay-helper", .kind = "queue_wrapper", .status = "starter_landed", .destination = "drivers/virtio/virtio_ring.zig" },
    .{ .id = "phase10-notify-prepare-helper", .kind = "queue_wrapper", .status = "starter_landed", .destination = "drivers/virtio/virtio_ring.zig" },
    .{ .id = "phase10-notification-data-summary-helper", .kind = "queue_wrapper", .status = "starter_landed", .destination = "drivers/virtio/virtio_ring.zig" },
    .{ .id = "phase10-broken-queue-poll-guard", .kind = "queue_wrapper", .status = "starter_landed", .destination = "drivers/virtio/virtio_ring.zig" },
    .{ .id = "phase10-queue-publish-readiness-helper", .kind = "queue_wrapper", .status = "starter_landed", .destination = "drivers/virtio/virtio_ring_publish_readiness.zig" },
    .{ .id = "phase10-queue-registration-summary-helper", .kind = "queue_wrapper", .status = "starter_landed", .destination = "drivers/virtio/virtio_ring_registration_summary.zig" },
    .{ .id = "phase10-queue-reset-helper", .kind = "queue_wrapper", .status = "starter_landed", .destination = "drivers/virtio/virtio_ring.zig" },
    .{ .id = "phase10-queue-reset-readiness-helper", .kind = "queue_wrapper", .status = "starter_landed", .destination = "drivers/virtio/virtio_ring_reset_readiness.zig" },
    .{ .id = "phase10-ring-publish-readiness-replay", .kind = "validation", .status = "starter_landed", .destination = "drivers/virtio/virtio_ring_publish_readiness.zig" },
    .{ .id = "phase10-ring-verify-replay", .kind = "validation", .status = "starter_landed", .destination = "drivers/virtio/virtio_ring_verify.zig" },
    .{ .id = "phase10-virtio-ring-slice-note", .kind = "documentation", .status = "starter_landed", .destination = "Documentation/zigux/phase10-virtio-ring-slice.md" },
    .{ .id = "phase10-ring-lab-driver-bridge", .kind = "roadmap_gap", .status = "blocked_on_risky_transport", .destination = "drivers/virtio/virtio_mmio.zig" },
};

const roadmap_destinations = [_][]const u8{"drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"};
const allowed_evidence = [_][]const u8{"driver_local_lab_slices", "survey_manifests", "shared_validation_gates"};
const forbidden_claims = [_][]const u8{"queue_setup_reset_paths", "irq_parity", "dma_paths", "input_registration_lifecycle", "probe_remove_lifecycle"};
const study_only_anchors = [_][]const u8{"kernel/workqueue.c", "kernel/trace/ring_buffer.c"};
const freeze_in_c_anchors = [_][]const u8{"kernel/sched/core.c", "mm/page_alloc.c", "kernel/rcu/tree.c", "net/core/skbuff.c"};

fn expectStrings(actual: []const []const u8, expected: []const []const u8) !void {
    if (actual.len != expected.len) return error.StringArrayLengthDrift;
    for (actual, expected) |a, e| if (!std.mem.eql(u8, a, e)) return error.StringArrayValueDrift;
}

fn checkManifest(allocator: std.mem.Allocator, source: []const u8) !void {
    const parsed = try std.json.parseFromSlice(Manifest, allocator, source, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();
    const value = parsed.value;
    if (!std.mem.eql(u8, value.lane_key, "P10-L10")) return error.LaneKeyDrift;
    if (!std.mem.eql(u8, value.phase, "Phase 10")) return error.PhaseDrift;
    if (!std.mem.eql(u8, value.anchor, "drivers/virtio/virtio_ring.c")) return error.AnchorDrift;
    try expectStrings(value.roadmap_destinations, &roadmap_destinations);
    if (!std.mem.eql(u8, value.freeze_map, "Documentation/zigux/freeze-map.md")) return error.FreezeMapDrift;
    if (!std.mem.eql(u8, value.freeze_boundary_status, "aligned") or value.freeze_status_change_claimed) return error.FreezeBoundaryDrift;
    if (!std.mem.eql(u8, value.risky_transport_posture, "blocked_on_risky_transport")) return error.TransportPostureDrift;
    try expectStrings(value.allowed_evidence_kinds, &allowed_evidence);
    try expectStrings(value.forbidden_transport_claims, &forbidden_claims);
    if (!value.architecture_council_reopen_required or value.architecture_council_reopen_attached) return error.ArchitectureBoundaryDrift;
    try expectStrings(value.study_only_anchors, &study_only_anchors);
    try expectStrings(value.freeze_in_c_anchors, &freeze_in_c_anchors);
    if (!std.mem.eql(u8, value.freeze_boundary_owner_lane, "P10-L11")) return error.FreezeOwnerDrift;
    if (value.survey_summary.virtio_ring_c_lines != 3940) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_phase10_test_files != 9) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_virtio_core_zig_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_phase10_build_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_phase10_core_doc_present != false) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_virtio_ring_zig_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_virtio_ring_doc_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_ring_verify_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_ring_publish_readiness_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_ring_callback_enable_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_ring_registration_summary_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_ring_reset_readiness_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_ring_used_buffer_poll_present != true) return error.SurveySummaryDrift;
    for (expected_gaps) |expected| {
        var found: ?Gap = null;
        for (value.gaps) |gap| if (std.mem.eql(u8, gap.id, expected.id)) { found = gap; break; };
        const gap = found orelse return error.MissingGap;
        if (!std.mem.eql(u8, gap.kind, expected.kind) or !std.mem.eql(u8, gap.status, expected.status) or !std.mem.eql(u8, gap.zigux_destination, expected.destination)) return error.GapMetadataDrift;
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
    for (forbidden_contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| if (std.mem.indexOf(u8, text, marker) != null) return error.ForbiddenMarkerPresent;
    }
    const manifest_path = try guard.joinPath(allocator, root, "zigux/tests/phase10_virtio_ring_manifest.json");
    defer allocator.free(manifest_path);
    const manifest = try guard.readUtf8File(io, allocator, manifest_path);
    defer allocator.free(manifest);
    try checkManifest(allocator, manifest);
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE10_RING_PACKET_REQUIRED_PATH_COUNT=15", .{});
    try guard.printLine(io, "PHASE10_RING_PACKET_GAP_COUNT=21", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE10_RING_PACKET_SELF_TEST_CASE_COUNT=17", .{});
    try emitCounts(io);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try emitCounts(io);
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE10_RING_PACKET_SELF_TEST=pass";
//
// const EXPECTED_MANIFEST_FIELDS = [_][]const u8{
//     "lane_key",
//     "P10-L10",
//     "phase",
//     "Phase 10",
//     "anchor",
//     "drivers/virtio/virtio_ring.c",
//     "roadmap_destinations",
//     "drivers/virtio/*.zig",
//     "zigux/kernel/",
//     "zigux/helpers/",
//     "freeze_map",
//     "Documentation/zigux/freeze-map.md",
//     "freeze_boundary_status",
//     "aligned",
//     "freeze_status_change_claimed",
//     "risky_transport_posture",
//     "blocked_on_risky_transport",
//     "allowed_evidence_kinds",
//     "driver_local_lab_slices",
//     "survey_manifests",
//     "shared_validation_gates",
//     "forbidden_transport_claims",
//     "queue_setup_reset_paths",
//     "irq_parity",
//     "dma_paths",
//     "input_registration_lifecycle",
//     "probe_remove_lifecycle",
//     "architecture_council_reopen_required",
//     "architecture_council_reopen_attached",
//     "study_only_anchors",
//     "kernel/workqueue.c",
//     "kernel/trace/ring_buffer.c",
//     "freeze_in_c_anchors",
//     "kernel/sched/core.c",
//     "mm/page_alloc.c",
//     "kernel/rcu/tree.c",
//     "net/core/skbuff.c",
// };
//
// const EXPECTED_SURVEY_SUMMARY_FIELDS = [_][]const u8{
//     "virtio_ring_c_lines",
//     "preexisting_phase10_test_files",
//     "preexisting_virtio_core_zig_present",
//     "preexisting_phase10_build_present",
//     "preexisting_phase10_core_doc_present",
//     "preexisting_virtio_ring_zig_present",
//     "preexisting_virtio_ring_doc_present",
//     "preexisting_ring_verify_present",
//     "preexisting_ring_publish_readiness_present",
//     "preexisting_ring_callback_enable_present",
//     "preexisting_ring_registration_summary_present",
//     "preexisting_ring_reset_readiness_present",
//     "preexisting_ring_used_buffer_poll_present",
// };
//
// const EXPECTED_GAP_METADATA = [_][]const u8{
//     "phase10-build-gate",
//     "validation",
//     "starter_landed",
//     "zigux/tests/phase10_build.zig",
//     "phase10-virtio-core-lab-starter",
//     "lab_driver_starter",
//     "starter_landed",
//     "drivers/virtio/virtio.zig",
//     "phase10-ring-registration-replay",
//     "validation",
//     "starter_landed",
//     "zigux/tests/phase10_virtio_ring_registration_replay.zig",
//     "phase10-ring-reset-readiness-replay",
//     "validation",
//     "starter_landed",
//     "zigux/tests/phase10_virtio_ring_reset_readiness.zig",
//     "phase10-virtio-ring-survey-gate",
//     "validation",
//     "starter_landed",
//     "zigux/tests/phase10_virtio_ring_survey.zig",
//     "phase10-virtio-ring-survey-note",
//     "documentation",
//     "starter_landed",
//     "Documentation/zigux/phase10-virtio-ring-survey.md",
//     "phase10-virtqueue-shape-helper",
//     "queue_wrapper",
//     "starter_landed",
//     "drivers/virtio/virtio_ring.zig",
//     "phase10-used-buffer-polling-helper",
//     "queue_wrapper",
//     "starter_landed",
//     "drivers/virtio/virtio_ring_used_buffer_poll.zig",
//     "phase10-callback-enable-helper",
//     "queue_wrapper",
//     "starter_landed",
//     "drivers/virtio/virtio_ring_callback_enable.zig",
//     "phase10-callback-delay-helper",
//     "queue_wrapper",
//     "starter_landed",
//     "drivers/virtio/virtio_ring.zig",
//     "phase10-notify-prepare-helper",
//     "queue_wrapper",
//     "starter_landed",
//     "drivers/virtio/virtio_ring.zig",
//     "phase10-notification-data-summary-helper",
//     "queue_wrapper",
//     "starter_landed",
//     "drivers/virtio/virtio_ring.zig",
//     "phase10-broken-queue-poll-guard",
//     "queue_wrapper",
//     "starter_landed",
//     "drivers/virtio/virtio_ring.zig",
//     "phase10-queue-publish-readiness-helper",
//     "queue_wrapper",
//     "starter_landed",
//     "drivers/virtio/virtio_ring_publish_readiness.zig",
//     "phase10-queue-registration-summary-helper",
//     "queue_wrapper",
//     "starter_landed",
//     "drivers/virtio/virtio_ring_registration_summary.zig",
//     "phase10-queue-reset-helper",
//     "queue_wrapper",
//     "starter_landed",
//     "drivers/virtio/virtio_ring.zig",
//     "phase10-queue-reset-readiness-helper",
//     "queue_wrapper",
//     "starter_landed",
//     "drivers/virtio/virtio_ring_reset_readiness.zig",
//     "phase10-ring-publish-readiness-replay",
//     "validation",
//     "starter_landed",
//     "drivers/virtio/virtio_ring_publish_readiness.zig",
//     "phase10-ring-verify-replay",
//     "validation",
//     "starter_landed",
//     "drivers/virtio/virtio_ring_verify.zig",
//     "phase10-virtio-ring-slice-note",
//     "documentation",
//     "starter_landed",
//     "Documentation/zigux/phase10-virtio-ring-slice.md",
//     "phase10-ring-lab-driver-bridge",
//     "roadmap_gap",
//     "blocked_on_risky_transport",
//     "drivers/virtio/virtio_mmio.zig",
// };
//
// const REQUIRED_MARKERS = [_][]const u8{
//     "Documentation/zigux/phase10-virtio-ring-survey.md",
//     "lane: `P10-L10`",
//     "`phase10-virtio-ring-survey-gate`",
//     "`drivers/virtio/virtio_ring_publish_readiness.zig`",
//     "`drivers/virtio/virtio_ring_notification_data.zig`",
//     "`drivers/virtio/virtio_ring_registration_summary.zig`",
//     "`drivers/virtio/virtio_ring_used_buffer_poll.zig`",
//     "`zigux/tests/phase10_virtio_ring.zig`",
//     "`zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`",
//     "`zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`",
//     "`zigux/tests/phase10_virtio_ring_reset_reuse.zig`",
//     "`zigux/tests/phase10_virtio_ring_reset_readiness.zig`",
//     "`zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`",
//     "`zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`",
//     "`zigux/tests/phase10_virtio_ring_queue_build_survey.zig`",
//     "direct contents reads rematerialize `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `drivers/virtio/virtio_ring_notification_data.zig`, `drivers/virtio/virtio_ring_callback_enable.zig`, `drivers/virtio/virtio_ring_registration_summary.zig`, `drivers/virtio/virtio_ring_used_buffer_poll.zig`, the broader replay `zigux/tests/phase10_virtio_ring.zig`",
//     "`phase10-used-buffer-polling-helper`",
//     "`phase10-queue-registration-summary-helper`",
//     "`phase10-ring-reset-readiness-replay`",
//     "`zigux/tests/phase10_virtio_ring_queue_build_survey.zig` now gives the ring lane one focused queue-build survey replay",
//     "the blocked `phase10-ring-lab-driver-bridge` remains owned by the adjacent `P10-L11` MMIO packet",
//     "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md",
//     "current packet lane on master: `P10-L10`",
//     "adjacent freeze-boundary owner: `P10-L11`",
//     "direct current-head readback now keeps the broader ring replay `zigux/tests/phase10_virtio_ring.zig` inside the same ring packet as the queue-local helper ladder",
//     "the used-buffer-poll wrapper `drivers/virtio/virtio_ring_used_buffer_poll.zig`, the publish-readiness helper `drivers/virtio/virtio_ring_publish_readiness.zig`, the notification-data replay `zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`, the reset-readiness replay `zigux/tests/phase10_virtio_ring_reset_readiness.zig`, and the dedicated ring survey replay `zigux/tests/phase10_virtio_ring_survey.zig` stay part of the same directly readable ring packet",
//     "the smallest same-lane follow-through is reminder-surface, checker, or manifest truthfulness work",
//     "Documentation/zigux/phase10-virtio-ring-slice.md",
//     "`drivers/virtio/virtio_ring_publish_readiness.zig`",
//     "`drivers/virtio/virtio_ring_registration_summary.zig`",
//     "`drivers/virtio/virtio_ring_used_buffer_poll.zig`",
//     "`zigux/tests/phase10_virtio_ring.zig`",
//     "`zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`",
//     "`zigux/tests/phase10_virtio_ring_reset_readiness.zig`",
//     "`zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`",
//     "`zigux/tests/phase10_virtio_ring_survey.zig`",
//     "the broader ring replay `zigux/tests/phase10_virtio_ring.zig` now sits beside that queue-local helper ladder as direct current-head evidence in this slice",
//     "the used-buffer-poll wrapper, the notification-data replay, the registration replay, the registration-summary wrapper, the reset-readiness replay, and the dedicated survey gate are now landed review surfaces inside this slice",
//     "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
//     "`scripts/zigux/check_phase10_ring_packet.zig`, `scripts/zigux/check_phase10_input_packet.zig`, `scripts/zigux/check_phase10_mmio_packet.zig`",
//     "`drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `drivers/virtio/virtio_ring_notification_data.zig`, `drivers/virtio/virtio_ring_callback_enable.zig`, `drivers/virtio/virtio_ring_registration_summary.zig`, `drivers/virtio/virtio_ring_reset_readiness.zig`, `drivers/virtio/virtio_ring_used_buffer_poll.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`",
//     "Keep the queue-local `P10-L10` ring freeze-boundary packet distinct from the bounded `P10-L11` MMIO helper packet when shared reviewer-facing reminders refresh",
//     "the ring survey, slice, and freeze-boundary notes, the direct ring helper packet through `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`,",
//     "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
//     "ring lane `P10-L10` owns the queue-local wrapper packet",
//     "zigux/tests/phase10_virtio_ring_reset_readiness.zig",
//     "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md",
//     "queue-local wrapper reviewability does not drift into MMIO-owned blocked transport claims",
//     "drivers/virtio/virtio_ring.zig",
//     "pub const QueueShapeSummary = struct {",
//     "pub const NotificationDataSummary = struct {",
//     "pub fn notificationSummary(self: *const Self, queue_index: u16) !QueueNotificationSummary {",
//     "pub fn enableCallback(self: *Self, queue_index: u16) !CallbackEnableSummary {",
//     "pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {",
//     "drivers/virtio/virtio_ring_verify.zig",
//     "pub fn summarizeNotificationState(",
//     "pub fn summarizeNotificationData(",
//     "pub fn summarizeDelayedCallback(",
//     "pub fn summarizeResetReadiness(",
//     "test \"phase10 virtio ring verify keeps notification-state wrapper explicit across publish kick and used replay\" {",
//     "test \"phase10 virtio ring verify exposes reset-readiness blocker ordering after clearBroken releases queue debt\" {",
//     "test \"phase10 virtio ring verify keeps reset-readiness blockers ordered through queue-local replay\" {",
//     "drivers/virtio/virtio_ring_notification_data.zig",
//     "pub fn summarizeNotificationData(",
//     "pub fn notificationDataUsesWrapBit(summary: NotificationDataSummary) bool {",
//     "pub fn queueIndexMatchesNotificationData(summary: NotificationDataSummary) bool {",
//     "pub fn nextAvailStateMatchesEncoding(summary: NotificationDataSummary) bool {",
//     "test \"phase10 virtio ring notification-data wrapper keeps split queue state explicit\" {",
//     "test \"phase10 virtio ring notification-data wrapper preserves packed wrap encoding across u16 rollover\" {",
//     "drivers/virtio/virtio_ring_publish_readiness.zig",
//     "pub fn summarizePublishReadiness(",
//     "pub fn queueCanPublish(summary: QueuePublishReadinessSummary) bool {",
//     "pub fn queueHasPublishCapacity(summary: QueuePublishReadinessSummary) bool {",
//     "test \"phase10 virtio ring publish-readiness wrapper keeps empty queues publishable\" {",
//     "test \"phase10 virtio ring publish-readiness wrapper keeps unpublished chains visible while remaining queue-local publishable\" {",
//     "test \"phase10 virtio ring publish-readiness wrapper blocks full queues until used chains return capacity\" {",
//     "test \"phase10 virtio ring publish-readiness wrapper regains publish capacity before used buffers are polled\" {",
//     "test \"phase10 virtio ring publish-readiness wrapper keeps broken queues fenced even when slots remain\" {",
//     "test \"phase10 virtio ring publish-readiness wrapper falls back to queue-full after a broken full queue is cleared\" {",
//     "drivers/virtio/virtio_ring_registration_summary.zig",
//     "pub fn summarizeQueueRegistration(",
//     "pub fn summarizeRegisteredQueueCount(ring: *const virtio_ring.VirtioRingLab) usize {",
//     "pub fn queueDefinitionDisciplineStable(",
//     "test \"phase10 virtio ring registration-summary wrapper keeps definition discipline explicit\" {",
//     "test \"phase10 virtio ring registration-summary wrapper stays queue-local across noncontiguous queue definitions\" {",
//     "drivers/virtio/virtio_ring_used_buffer_poll.zig",
//     "pub fn summarizeUsedBufferPoll(",
//     "pub fn usedBufferPollHasNewChains(summary: UsedBufferPollSummary) bool {",
//     "pub fn usedBufferPollSettled(summary: UsedBufferPollSummary) bool {",
//     "test \"phase10 virtio ring used-buffer-poll wrapper keeps empty queues settled\" {",
//     "test \"phase10 virtio ring used-buffer-poll wrapper exposes newly used chains before the follow-up poll settles\" {",
//     "test \"phase10 virtio ring used-buffer-poll wrapper settles once all used chains are observed\" {",
//     "zigux/tests/phase10_build.zig",
//     ".root_source_file = b.path(\"../../drivers/virtio/virtio_ring_notification_data.zig\"),",
//     ".root_source_file = b.path(\"../../drivers/virtio/virtio_ring_publish_readiness.zig\"),",
//     ".root_source_file = b.path(\"../../drivers/virtio/virtio_ring_used_buffer_poll.zig\"),",
//     ".root_source_file = b.path(\"phase10_virtio_ring_registration_replay.zig\"),",
//     ".root_source_file = b.path(\"phase10_virtio_ring_prepare_kick_idempotent.zig\"),",
//     ".root_source_file = b.path(\"phase10_virtio_ring_reset_reuse.zig\"),",
//     ".root_source_file = b.path(\"phase10_virtio_ring_broken_queue_queue_discipline.zig\"),",
//     ".root_source_file = b.path(\"phase10_virtio_ring_delayed_callback_budget.zig\"),",
//     ".root_source_file = b.path(\"phase10_virtio_ring_queue_build_survey.zig\"),",
//     ".root_source_file = b.path(\"phase10_virtio_ring_survey.zig\"),",
//     ".name = \"phase10-virtio-ring-notification-data-readiness-tests\",",
//     ".name = \"phase10-virtio-ring-registration-replay-tests\",",
//     ".name = \"phase10-virtio-ring-reset-readiness-tests\",",
//     ".name = \"phase10-virtio-ring-notification-data-wrapper-tests\",",
//     ".name = \"phase10-virtio-ring-publish-readiness-tests\",",
//     ".name = \"phase10-virtio-ring-used-buffer-poll-tests\",",
//     ".name = \"phase10-virtio-ring-prepare-kick-idempotent-tests\",",
//     ".name = \"phase10-virtio-ring-reset-reuse-tests\",",
//     ".name = \"phase10-virtio-ring-broken-queue-queue-discipline-tests\",",
//     ".name = \"phase10-virtio-ring-delayed-callback-budget-tests\",",
//     ".name = \"phase10-virtio-ring-queue-build-survey-tests\",",
//     ".name = \"phase10-virtio-ring-survey-tests\",",
//     "test_step.dependOn(&run_phase10_virtio_ring_notification_data_readiness_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_ring_registration_replay_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_ring_reset_readiness_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_ring_notification_data_wrapper_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_ring_publish_readiness_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_ring_used_buffer_poll_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_ring_prepare_kick_idempotent_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_ring_reset_reuse_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_ring_broken_queue_queue_discipline_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_ring_delayed_callback_budget_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_ring_queue_build_survey_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_ring_survey_tests.step);",
//     "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig",
//     "test \"phase10 virtio ring notification-data replay keeps split and packed next-avail state explicit\" {",
//     "const packed_summary = try ring.notificationDataSummary(2);",
//     "zigux/tests/phase10_virtio_ring_queue_build_survey.zig",
//     "test \"phase10 virtio ring queue build keeps the focused queue packet explicit\" {",
//     ".root_source_file = b.path(\\\"../../drivers/virtio/virtio_ring_notification_data.zig\\\"),",
//     ".root_source_file = b.path(\\\"phase10_virtio_ring_queue_build_survey.zig\\\"),",
//     ".name = \\\"phase10-virtio-ring-notification-data-wrapper-tests\\\",",
//     ".name = \\\"phase10-virtio-ring-queue-build-survey-tests\\\",",
//     "run_phase10_virtio_ring_notification_data_wrapper_tests.step",
//     "run_phase10_virtio_ring_queue_build_survey_tests.step",
//     "zigux/tests/phase10_virtio_ring_survey.zig",
//     "try expectContains(survey_note, \"drivers/virtio/virtio_ring_registration_summary.zig\");",
//     "try expectContains(survey_note, \"drivers/virtio/virtio_ring_used_buffer_poll.zig\");",
//     "try expectContains(survey_note, \"zigux/tests/phase10_virtio_ring_reset_readiness.zig\");",
//     "try expectContains(manifest, \"\\\"preexisting_phase10_test_files\\\": 9\");",
//     "try expectContains(manifest, \"\\\"preexisting_ring_registration_summary_present\\\": true\");",
//     "try expectContains(manifest, \"\\\"preexisting_ring_used_buffer_poll_present\\\": true\");",
//     "try expectContains(manifest, \"\\\"id\\\": \\\"phase10-used-buffer-polling-helper\\\"\");",
//     "try expectContains(manifest, \"\\\"id\\\": \\\"phase10-queue-registration-summary-helper\\\"\");",
//     "const used_buffer_poll_file = try readRepoRelative(",
//     "test \"phase10 virtio ring used-buffer-poll wrapper stays direct current-head evidence in the survey packet\" {",
//     "phase10 virtio ring used-buffer-poll wrapper exposes newly used chains before the follow-up poll settles",
// };
//
// const FORBIDDEN_MARKERS = [_][]const u8{
//     "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md",
//     "public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` even though exact direct-path contents reads in this lane still leave that broader replay outside the queue-local helper ladder",
//     "Documentation/zigux/phase10-virtio-ring-slice.md",
//     "public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` but it still remains outside exact direct-path current-head evidence in this slice",
//     "the broader ring replay still remains outside direct current-head evidence in this slice",
//     "zigux/tests/phase10_virtio_ring_survey.zig",
//     "try expectContains(slice_note, \"public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` but it still remains outside exact direct-path current-head evidence in this slice\");",
//     "try expectContains(freeze_note, \"public current-`master` readback rematerializes the broader ring replay `zigux/tests/phase10_virtio_ring.zig` even though exact direct-path contents reads in this lane still leave that broader replay outside the queue-local helper ladder\");",
// };
//
// const MANIFEST_PATH = [_][]const u8{
//     "zigux/tests/phase10_virtio_ring_manifest.json",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (EXPECTED_MANIFEST_FIELDS) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_SURVEY_SUMMARY_FIELDS) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_GAP_METADATA) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
// }
//
// pub fn main() !void {
//     var gpa = std.heap.GeneralPurposeAllocator(.{}){};
//     defer _ = gpa.deinit();
//     const allocator = gpa.allocator();
//     const io = std.Io.Threaded.init(allocator, .{});
//     defer io.deinit();
//     const args = try std.process.argsAlloc(allocator);
//     defer std.process.argsFree(allocator, args);
//
//     var self_test = false;
//     for (args[1..]) |arg| {
//         if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
//     }
//
//     if (self_test) {
//         try checkText("");
//         try guard.printLine(io, "{s}", .{pass_marker});
//         return;
//     }
//
//     const root = try guard.repoRootFromScript(allocator);
//     defer allocator.free(root);
//     const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
//     const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
//     defer allocator.free(workflow_path);
//     const text = try guard.readUtf8File(io, allocator, workflow_path);
//     defer allocator.free(text);
//     try checkText(text);
//     try guard.printLine(io, "{s}", .{pass_marker});
// }
//
