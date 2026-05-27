const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoRelative(allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    const io = std.testing.io;
    return try std.Io.Dir.cwd().readFileAlloc(io, relative_path, allocator, .limited(64 * 1024));
}

test "phase10 virtio ring survey note keeps the broader replay explicit beside the queue-local helper packet" {
    const allocator = std.testing.allocator;

    const survey_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-ring-survey.md",
    );
    defer allocator.free(survey_note);

    const build_file = try readRepoRelative(allocator, "zigux/tests/phase10_build.zig");
    defer allocator.free(build_file);

    const shared_build_file = try readRepoRelative(allocator, "zigux/tests/build.zig");
    defer allocator.free(shared_build_file);

    const verify_file = try readRepoRelative(allocator, "drivers/virtio/virtio_ring_verify.zig");
    defer allocator.free(verify_file);

    const publish_readiness_file = try readRepoRelative(
        allocator,
        "drivers/virtio/virtio_ring_publish_readiness.zig",
    );
    defer allocator.free(publish_readiness_file);

    const registration_summary_file = try readRepoRelative(
        allocator,
        "drivers/virtio/virtio_ring_registration_summary.zig",
    );
    defer allocator.free(registration_summary_file);

    const used_buffer_poll_file = try readRepoRelative(
        allocator,
        "drivers/virtio/virtio_ring_used_buffer_poll.zig",
    );
    defer allocator.free(used_buffer_poll_file);

    const registration_replay_file = try readRepoRelative(
        allocator,
        "zigux/tests/phase10_virtio_ring_registration_replay.zig",
    );
    defer allocator.free(registration_replay_file);

    const reset_readiness_file = try readRepoRelative(
        allocator,
        "zigux/tests/phase10_virtio_ring_reset_readiness.zig",
    );
    defer allocator.free(reset_readiness_file);

    try expectContains(survey_note, "PHASE10_STATUS=parked");
    try expectContains(survey_note, "lane: `P10-L10`");
    try expectContains(survey_note, "drivers/virtio/virtio_ring.zig");
    try expectContains(survey_note, "drivers/virtio/virtio_ring_verify.zig");
    try expectContains(survey_note, "drivers/virtio/virtio_ring_publish_readiness.zig");
    try expectContains(survey_note, "drivers/virtio/virtio_ring_registration_summary.zig");
    try expectContains(survey_note, "drivers/virtio/virtio_ring_used_buffer_poll.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_ring.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_ring_registration_replay.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_ring_reset_readiness.zig");
    try expectContains(
        survey_note,
        "direct contents reads rematerialize `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `drivers/virtio/virtio_ring_registration_summary.zig`, `drivers/virtio/virtio_ring_used_buffer_poll.zig`, the broader replay `zigux/tests/phase10_virtio_ring.zig`",
    );
    try expectContains(survey_note, "phase10-used-buffer-polling-helper");
    try expectContains(survey_note, "phase10-queue-registration-summary-helper");
    try expectContains(survey_note, "phase10-ring-reset-readiness-replay");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_ring_survey.zig");
    try expectContains(survey_note, "zig test zigux/tests/phase10_virtio_ring_survey.zig");
    try expectContains(
        verify_file,
        "test \"phase10 virtio ring verify exposes reset-readiness blocker ordering after clearBroken releases queue debt\" {",
    );
    try expectContains(
        verify_file,
        "test \"phase10 virtio ring verify keeps reset-readiness blockers ordered through queue-local replay\" {",
    );
    try expectContains(
        publish_readiness_file,
        "pub fn summarizePublishReadiness(",
    );
    try expectContains(
        publish_readiness_file,
        "pub fn queueHasPublishCapacity(summary: QueuePublishReadinessSummary) bool {",
    );
    try expectContains(
        publish_readiness_file,
        "test \"phase10 virtio ring publish-readiness wrapper keeps unpublished chains visible while remaining queue-local publishable\" {",
    );
    try expectContains(
        publish_readiness_file,
        "test \"phase10 virtio ring publish-readiness wrapper blocks full queues until used chains return capacity\" {",
    );
    try expectContains(
        registration_summary_file,
        "pub fn summarizeQueueRegistration(",
    );
    try expectContains(
        registration_summary_file,
        "test \"phase10 virtio ring registration-summary wrapper keeps definition discipline explicit\" {",
    );
    try expectContains(
        registration_summary_file,
        "test \"phase10 virtio ring registration-summary wrapper stays queue-local across noncontiguous queue definitions\" {",
    );
    try expectContains(
        used_buffer_poll_file,
        "pub fn summarizeUsedBufferPoll(",
    );
    try expectContains(
        used_buffer_poll_file,
        "pub fn usedBufferPollHasNewChains(summary: UsedBufferPollSummary) bool {",
    );
    try expectContains(
        used_buffer_poll_file,
        "test \"phase10 virtio ring used-buffer-poll wrapper exposes newly used chains before the follow-up poll settles\" {",
    );
    try expectContains(
        used_buffer_poll_file,
        "test \"phase10 virtio ring used-buffer-poll wrapper settles once all used chains are observed\" {",
    );
    try expectContains(
        registration_replay_file,
        "test \"phase10 virtio ring registration replay keeps noncontiguous queue registration counts explicit\" {",
    );
    try expectContains(
        registration_replay_file,
        "test \"phase10 virtio ring registration replay keeps failed definitions from inflating queue counts\" {",
    );
    try expectContains(
        reset_readiness_file,
        "test \"phase10 virtio ring reset-readiness replay keeps queue-local blocker progression explicit\" {",
    );
    try expectContains(
        reset_readiness_file,
        "test \"phase10 virtio ring reset-readiness replay keeps broken fences distinct from callback and queue debt\" {",
    );
    try expectContains(build_file, "virtio_ring_publish_readiness_module");
    try expectContains(build_file, "virtio_ring_used_buffer_poll_module");
    try expectContains(build_file, "phase10_virtio_ring_survey_module");
    try expectContains(build_file, "\"phase10-virtio-ring-registration-replay-tests\"");
    try expectContains(build_file, "\"phase10-virtio-ring-reset-readiness-tests\"");
    try expectContains(build_file, "\"phase10-virtio-ring-publish-readiness-tests\"");
    try expectContains(build_file, "\"phase10-virtio-ring-used-buffer-poll-tests\"");
    try expectContains(build_file, "\"phase10-virtio-ring-prepare-kick-idempotent-tests\"");
    try expectContains(build_file, "\"phase10-virtio-ring-reset-reuse-tests\"");
    try expectContains(build_file, "\"phase10-virtio-ring-broken-queue-queue-discipline-tests\"");
    try expectContains(build_file, "\"phase10-virtio-ring-delayed-callback-budget-tests\"");
    try expectContains(build_file, "\"phase10-virtio-ring-survey-tests\"");
    try expectContains(build_file, "run_phase10_virtio_ring_registration_replay_tests.step");
    try expectContains(build_file, "run_phase10_virtio_ring_reset_readiness_tests.step");
    try expectContains(build_file, "run_phase10_virtio_ring_publish_readiness_tests.step");
    try expectContains(build_file, "run_phase10_virtio_ring_used_buffer_poll_tests.step");
    try expectContains(build_file, "run_phase10_virtio_ring_prepare_kick_idempotent_tests.step");
    try expectContains(build_file, "run_phase10_virtio_ring_reset_reuse_tests.step");
    try expectContains(build_file, "run_phase10_virtio_ring_broken_queue_queue_discipline_tests.step");
    try expectContains(build_file, "run_phase10_virtio_ring_delayed_callback_budget_tests.step");
    try expectContains(build_file, "run_phase10_virtio_ring_survey_tests.step");
    try expectContains(shared_build_file, "\"phase10-virtio-ring-survey\"");
    try expectContains(shared_build_file, "\"phase10_virtio_ring_survey.zig\"");
    try expectContains(shared_build_file, "phase10_ring_step.dependOn(&phase10_virtio_ring_survey.step);");
    try expectContains(shared_build_file, "smoke_step.dependOn(&phase10_virtio_ring_survey.step);");
    try expectContains(shared_build_file, "test_step.dependOn(&phase10_virtio_ring_survey.step);");
}

test "phase10 virtio ring used-buffer-poll wrapper stays direct current-head evidence in the survey packet" {
    const allocator = std.testing.allocator;

    const survey_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-ring-survey.md",
    );
    defer allocator.free(survey_note);

    const slice_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-ring-slice.md",
    );
    defer allocator.free(slice_note);

    const manifest = try readRepoRelative(
        allocator,
        "zigux/tests/phase10_virtio_ring_manifest.json",
    );
    defer allocator.free(manifest);

    try expectContains(survey_note, "drivers/virtio/virtio_ring_used_buffer_poll.zig");
    try expectContains(slice_note, "drivers/virtio/virtio_ring_used_buffer_poll.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_ring_reset_readiness.zig");
    try expectContains(manifest, "\"preexisting_ring_used_buffer_poll_present\": true");
    try expectContains(manifest, "\"id\": \"phase10-used-buffer-polling-helper\"");
    try expectContains(
        manifest,
        "\"zigux_destination\": \"drivers/virtio/virtio_ring_used_buffer_poll.zig\"",
    );
}

test "phase10 virtio ring survey manifest keeps lane identity and freeze-boundary posture explicit" {
    const allocator = std.testing.allocator;

    const manifest = try readRepoRelative(
        allocator,
        "zigux/tests/phase10_virtio_ring_manifest.json",
    );
    defer allocator.free(manifest);

    try expectContains(manifest, "\"lane_key\": \"P10-L10\"");
    try expectContains(manifest, "\"freeze_status_change_claimed\": false");
    try expectContains(manifest, "\"risky_transport_posture\": \"blocked_on_risky_transport\"");
    try expectContains(manifest, "\"allowed_evidence_kinds\": [");
    try expectContains(manifest, "\"driver_local_lab_slices\"");
    try expectContains(manifest, "\"survey_manifests\"");
    try expectContains(manifest, "\"preexisting_phase10_test_files\": 9");
    try expectContains(manifest, "\"preexisting_ring_used_buffer_poll_present\": true");
    try expectContains(manifest, "\"shared_validation_gates\"");
    try expectContains(manifest, "\"forbidden_transport_claims\": [");
    try expectContains(manifest, "\"queue_setup_reset_paths\"");
    try expectContains(manifest, "\"irq_parity\"");
    try expectContains(manifest, "\"dma_paths\"");
    try expectContains(manifest, "\"input_registration_lifecycle\"");
    try expectContains(manifest, "\"probe_remove_lifecycle\"");
    try expectContains(manifest, "\"architecture_council_reopen_required\": true");
    try expectContains(manifest, "\"architecture_council_reopen_attached\": false");
    try expectContains(manifest, "\"freeze_boundary_owner_lane\": \"P10-L11\"");
    try expectContains(manifest, "\"id\": \"phase10-virtio-ring-survey-gate\"");
    try expectContains(manifest, "\"id\": \"phase10-used-buffer-polling-helper\"");
    try expectContains(manifest, "\"id\": \"phase10-queue-registration-summary-helper\"");
    try expectContains(manifest, "\"id\": \"phase10-queue-reset-helper\"");
    try expectContains(manifest, "\"id\": \"phase10-queue-reset-readiness-helper\"");
    try expectContains(manifest, "\"id\": \"phase10-ring-reset-readiness-replay\"");
    try expectContains(manifest, "\"status\": \"starter_landed\"");
    try expectContains(manifest, "\"zigux_destination\": \"zigux/tests/phase10_virtio_ring_survey.zig\"");
}

test "phase10 virtio ring slice companions keep the used-buffer-poll wrapper, notification-data replay, direct-readback broader replay, and landed survey gate explicit" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-ring-slice.md",
    );
    defer allocator.free(slice_note);

    try expectContains(slice_note, "drivers/virtio/virtio_ring_used_buffer_poll.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig");
    try expectContains(slice_note, "drivers/virtio/virtio_ring_registration_summary.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_ring_reset_readiness.zig");
    try expectContains(
        slice_note,
        "the broader ring replay `zigux/tests/phase10_virtio_ring.zig` now sits beside that queue-local helper ladder as direct current-head evidence in this slice",
    );
    try expectContains(
        slice_note,
        "the used-buffer-poll wrapper, the notification-data replay, the registration replay, the registration-summary wrapper, the reset-readiness replay, and the dedicated survey gate are now landed review surfaces inside this slice",
    );
    try expectContains(slice_note, "zigux/tests/phase10_virtio_ring_survey.zig");
}

test "phase10 virtio ring freeze-boundary note keeps risky transport work blocked" {
    const allocator = std.testing.allocator;

    const freeze_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md",
    );
    defer allocator.free(freeze_note);

    try expectContains(freeze_note, "current packet lane on master: `P10-L10`");
    try expectContains(freeze_note, "transport-backed queue setup or reset parity");
    try expectContains(freeze_note, "IRQ parity");
    try expectContains(freeze_note, "DMA-facing paths");
    try expectContains(freeze_note, "probe or remove lifecycle closure");
    try expectContains(
        freeze_note,
        "direct current-head readback now keeps the broader ring replay `zigux/tests/phase10_virtio_ring.zig` inside the same ring packet as the queue-local helper ladder",
    );
    try expectContains(freeze_note, "drivers/virtio/virtio_ring_used_buffer_poll.zig");
    try expectContains(freeze_note, "zigux/tests/phase10_virtio_ring_reset_readiness.zig");
    try expectContains(freeze_note, "zigux/tests/phase10_virtio_ring_survey.zig");
}

test "phase10 virtio ring lane sequencing keeps P10-L10 queue ownership explicit beside P10-L11" {
    const allocator = std.testing.allocator;

    const lane_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    );
    defer allocator.free(lane_note);

    try expectContains(lane_note, "ring lane `P10-L10` owns the queue-local wrapper packet");
    try expectContains(lane_note, "zigux/tests/phase10_virtio_ring_reset_readiness.zig");
    try expectContains(lane_note, "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md");
    try expectContains(
        lane_note,
        "queue-local wrapper reviewability does not drift into MMIO-owned blocked transport claims",
    );
}
