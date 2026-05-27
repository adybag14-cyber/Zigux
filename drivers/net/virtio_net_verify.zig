const std = @import("std");
const control_restore = @import("virtio_net_control_queue_restore.zig");
const queue_resume = @import("virtio_net_queue_resume.zig");
const receive_refill = @import("virtio_net_receive_refill_replay.zig");
const transmit_recycle = @import("virtio_net_transmit_recycle.zig");
const post_reset = @import("virtio_net_post_reset_replay.zig");
const throughput = @import("virtio_net_throughput_parity.zig");

pub const RecoveryPipelineRequest = struct {
    reset_generation: u32,
    queues_frozen: bool = false,
    receive_queue_pairs_before_reset: u16,
    receive_queue_pairs_after_restore: u16,
    receive_buffers_before_reset: u16,
    receive_buffers_after_restore: u16,
    descriptors_posted_after_restore: u16,
    control_queue_present_before_reset: bool = true,
    control_queue_present_after_restore: bool,
    control_queue_enabled_after_restore: bool,
    control_commands_before_reset: u16 = 0,
    control_commands_replayed_after_restore: u16 = 0,
    in_flight_transmit_descriptors: u16,
    free_transmit_descriptors_before_recycle: u16 = 0,
    completed_transmit_descriptors: u16,
    wake_threshold: u16 = transmit_recycle.default_wake_threshold,
    transmit_queue_was_stopped: bool = false,
    probe_snapshot_replayed: bool = false,
    requires_probe_snapshot_replay: bool = true,
    expected_min_ratio_pct: u8 = 90,
};

pub const RecoveryPipelineSummary = struct {
    anchor: []const u8,
    reset_generation: u32,
    control_restore: control_restore.ControlQueueRestoreSummary,
    refill: receive_refill.ReceiveRefillReplaySummary,
    recycle: transmit_recycle.TransmitRecycleSummary,
    replay: post_reset.PostResetReplaySummary,
    ownership: post_reset.PostResetOwnershipSummary,
    queue_resume_summary: queue_resume.QueueResumeSummary,
    throughput: throughput.ThroughputParitySummary,
    can_return_driver_ownership: bool,
    recovery_owns_any_submission: bool,
};

pub fn summarizeRecoveryPipeline(request: RecoveryPipelineRequest) !RecoveryPipelineSummary {
    const control = try control_restore.summarizeControlQueueRestore(.{
        .reset_generation = request.reset_generation,
        .receive_queue_pairs_after_restore = request.receive_queue_pairs_after_restore,
        .control_queue_present_before_reset = request.control_queue_present_before_reset,
        .control_queue_present_after_restore = request.control_queue_present_after_restore,
        .control_queue_enabled_after_restore = request.control_queue_enabled_after_restore,
        .control_commands_before_reset = request.control_commands_before_reset,
        .control_commands_replayed_after_restore = request.control_commands_replayed_after_restore,
    });

    const refill = try receive_refill.summarizeReceiveRefillReplay(.{
        .reset_generation = request.reset_generation,
        .receive_queue_pairs_before_reset = request.receive_queue_pairs_before_reset,
        .receive_queue_pairs_after_restore = request.receive_queue_pairs_after_restore,
        .receive_buffers_before_reset = request.receive_buffers_before_reset,
        .receive_buffers_after_restore = request.receive_buffers_after_restore,
        .descriptors_posted_after_restore = request.descriptors_posted_after_restore,
        .control_queue_restored = control.control_queue_restored,
        .requires_control_queue_restore = control.requires_control_queue_restore,
    });

    const recycle = try transmit_recycle.summarizeTransmitRecycle(.{
        .in_flight_descriptors = request.in_flight_transmit_descriptors,
        .free_descriptors_before = request.free_transmit_descriptors_before_recycle,
        .completed_descriptors = request.completed_transmit_descriptors,
        .wake_threshold = request.wake_threshold,
        .queue_stopped = request.transmit_queue_was_stopped,
    });

    const checkpoint = throughputCheckpoint(
        control.control_queue_restored,
        control.requires_control_queue_restore,
        refill.replay_ready,
        recycle.reaches_wake_threshold or !request.transmit_queue_was_stopped,
    );
    const probe_replayed_for_resume =
        request.probe_snapshot_replayed or !request.requires_probe_snapshot_replay;
    const throughput_summary = try throughput.summarizeThroughputParity(.{
        .queue_pairs_before_reset = request.receive_queue_pairs_before_reset,
        .queue_pairs_after_restore = request.receive_queue_pairs_after_restore,
        .receive_buffers_before_reset = request.receive_buffers_before_reset,
        .receive_buffers_after_restore = request.receive_buffers_after_restore,
        .receive_descriptors_reposted = refill.descriptors_reposted,
        .free_transmit_descriptors_before_recycle = request.free_transmit_descriptors_before_recycle,
        .recycled_transmit_descriptors = request.completed_transmit_descriptors,
        .wake_threshold = request.wake_threshold,
        .transmit_queue_was_stopped = request.transmit_queue_was_stopped,
        .replay_checkpoint = checkpoint,
        .requires_control_queue_restore = control.requires_control_queue_restore,
        .expected_min_ratio_pct = request.expected_min_ratio_pct,
    });

    const replay_request = post_reset.PostResetReplayRequest{
        .reset_generation = request.reset_generation,
        .receive_queue_pairs = request.receive_queue_pairs_after_restore,
        .control_queue_restored = control.control_queue_restored,
        .receive_refill_replayed = refill.replay_ready,
        .transmit_recycle_ready = throughput_summary.transmit_recycle_ready,
        .probe_snapshot_replayed = probe_replayed_for_resume,
        .requires_control_queue_restore = control.requires_control_queue_restore,
        .requires_probe_snapshot_replay = request.requires_probe_snapshot_replay,
    };
    const replay = try post_reset.summarizePostResetReplay(replay_request);
    const ownership = try post_reset.summarizePostResetOwnership(replay_request);
    const queue_resume_summary = try queue_resume.summarizeQueueResume(.{
        .reset_generation = request.reset_generation,
        .queues_frozen = request.queues_frozen,
        .receive_queue_pairs = request.receive_queue_pairs_after_restore,
        .refill_replay_ready = refill.replay_ready,
        .control_queue_restored = control.control_queue_restored,
        .transmit_recycle_ready = throughput_summary.transmit_recycle_ready,
        .probe_snapshot_replayed = probe_replayed_for_resume,
        .requires_control_queue_restore = control.requires_control_queue_restore,
    });

    const recovery_owns_any_submission =
        ownership.receive_submission_owner == .recovery or
        ownership.transmit_submission_owner == .recovery or
        queue_resume_summary.receive_submission_owner == .recovery or
        queue_resume_summary.transmit_submission_owner == .recovery;
    const can_return_driver_ownership =
        ownership.queues_ready_for_driver_ownership and
        queue_resume_summary.queues_ready_for_driver_ownership and
        throughput_summary.status == .parity_gate_ready and
        throughput_summary.meets_expected_min_ratio;

    return .{
        .anchor = "drivers/net/virtio_net.c",
        .reset_generation = request.reset_generation,
        .control_restore = control,
        .refill = refill,
        .recycle = recycle,
        .replay = replay,
        .ownership = ownership,
        .queue_resume_summary = queue_resume_summary,
        .throughput = throughput_summary,
        .can_return_driver_ownership = can_return_driver_ownership,
        .recovery_owns_any_submission = recovery_owns_any_submission,
    };
}

pub fn driverOwnsBothSubmissions(summary: RecoveryPipelineSummary) bool {
    return !summary.recovery_owns_any_submission and summary.can_return_driver_ownership;
}

pub fn pipelineNeedsProbeReplay(summary: RecoveryPipelineSummary) bool {
    return summary.replay.blocker == .probe_snapshot_replay or
        summary.queue_resume_summary.blocker == .probe_snapshot_replay or
        summary.throughput.status == .needs_post_reset_probe_replay;
}

fn throughputCheckpoint(
    control_queue_restored: bool,
    requires_control_queue_restore: bool,
    refill_ready: bool,
    transmit_ready: bool,
) throughput.PostResetProbeReplayCheckpoint {
    if (requires_control_queue_restore and !control_queue_restored) return .before_receive_refill;
    if (!refill_ready) return .after_control_queue_restore;
    if (!transmit_ready) return .after_receive_refill;
    return .after_transmit_queue_restore;
}

test "virtio net recovery pipeline keeps control queue restore as the first fail-closed gate" {
    const summary = try summarizeRecoveryPipeline(.{
        .reset_generation = 11,
        .receive_queue_pairs_before_reset = 2,
        .receive_queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 128,
        .descriptors_posted_after_restore = 128,
        .control_queue_present_after_restore = false,
        .control_queue_enabled_after_restore = false,
        .control_commands_before_reset = 2,
        .control_commands_replayed_after_restore = 0,
        .in_flight_transmit_descriptors = 0,
        .completed_transmit_descriptors = 0,
        .probe_snapshot_replayed = true,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", summary.anchor);
    try std.testing.expectEqual(
        control_restore.ControlQueueRestoreBlocker.queue_absent_after_restore,
        summary.control_restore.blocker,
    );
    try std.testing.expectEqual(receive_refill.ReceiveRefillReplayBlocker.control_queue_restore, summary.refill.blocker);
    try std.testing.expectEqual(post_reset.PostResetReplayBlocker.control_queue_restore, summary.replay.blocker);
    try std.testing.expectEqual(queue_resume.QueueResumeBlocker.control_queue_restore, summary.queue_resume_summary.blocker);
    try std.testing.expectEqual(throughput.ThroughputParityStatus.needs_control_queue_restore, summary.throughput.status);
    try std.testing.expect(summary.recovery_owns_any_submission);
    try std.testing.expect(!summary.can_return_driver_ownership);
}

test "virtio net recovery pipeline blocks on control queue enablement after the queue reappears" {
    const summary = try summarizeRecoveryPipeline(.{
        .reset_generation = 12,
        .receive_queue_pairs_before_reset = 2,
        .receive_queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 128,
        .receive_buffers_after_restore = 128,
        .descriptors_posted_after_restore = 128,
        .control_queue_present_after_restore = true,
        .control_queue_enabled_after_restore = false,
        .control_commands_before_reset = 1,
        .control_commands_replayed_after_restore = 0,
        .in_flight_transmit_descriptors = 0,
        .completed_transmit_descriptors = 0,
        .probe_snapshot_replayed = true,
    });

    try std.testing.expectEqual(
        control_restore.ControlQueueRestoreBlocker.queue_enable,
        summary.control_restore.blocker,
    );
    try std.testing.expectEqual(receive_refill.ReceiveRefillReplayBlocker.control_queue_restore, summary.refill.blocker);
    try std.testing.expectEqual(post_reset.PostResetReplayBlocker.control_queue_restore, summary.replay.blocker);
    try std.testing.expectEqual(queue_resume.QueueResumeBlocker.control_queue_restore, summary.queue_resume_summary.blocker);
    try std.testing.expectEqual(throughput.ThroughputParityStatus.needs_control_queue_restore, summary.throughput.status);
    try std.testing.expect(!summary.can_return_driver_ownership);
}

test "virtio net recovery pipeline returns receive ownership before stopped transmit recycle clears" {
    const summary = try summarizeRecoveryPipeline(.{
        .reset_generation = 13,
        .receive_queue_pairs_before_reset = 2,
        .receive_queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 256,
        .receive_buffers_after_restore = 256,
        .descriptors_posted_after_restore = 256,
        .control_queue_present_after_restore = true,
        .control_queue_enabled_after_restore = true,
        .control_commands_before_reset = 2,
        .control_commands_replayed_after_restore = 2,
        .in_flight_transmit_descriptors = 3,
        .completed_transmit_descriptors = 1,
        .transmit_queue_was_stopped = true,
        .wake_threshold = 2,
        .probe_snapshot_replayed = true,
    });

    try std.testing.expect(summary.control_restore.control_queue_restored);
    try std.testing.expect(summary.refill.replay_ready);
    try std.testing.expectEqual(transmit_recycle.RecycleDisposition.keep_stopped, summary.recycle.disposition);
    try std.testing.expectEqual(post_reset.PostResetReplayBlocker.transmit_recycle, summary.replay.blocker);
    try std.testing.expect(summary.ownership.resumes_receive_submission);
    try std.testing.expect(!summary.ownership.resumes_transmit_submission);
    try std.testing.expectEqual(post_reset.QueueSubmissionOwner.driver, summary.ownership.receive_submission_owner);
    try std.testing.expectEqual(post_reset.QueueSubmissionOwner.recovery, summary.ownership.transmit_submission_owner);
    try std.testing.expectEqual(queue_resume.QueueSubmissionOwner.driver, summary.queue_resume_summary.receive_submission_owner);
    try std.testing.expectEqual(queue_resume.QueueSubmissionOwner.recovery, summary.queue_resume_summary.transmit_submission_owner);
    try std.testing.expectEqual(throughput.ThroughputParityStatus.needs_transmit_recycle, summary.throughput.status);
    try std.testing.expect(summary.recovery_owns_any_submission);
    try std.testing.expect(!summary.can_return_driver_ownership);
}

test "virtio net recovery pipeline counts preexisting free transmit descriptors toward stopped queue readiness" {
    const summary = try summarizeRecoveryPipeline(.{
        .reset_generation = 14,
        .receive_queue_pairs_before_reset = 2,
        .receive_queue_pairs_after_restore = 2,
        .receive_buffers_before_reset = 256,
        .receive_buffers_after_restore = 256,
        .descriptors_posted_after_restore = 256,
        .control_queue_present_after_restore = true,
        .control_queue_enabled_after_restore = true,
        .control_commands_before_reset = 1,
        .control_commands_replayed_after_restore = 1,
        .in_flight_transmit_descriptors = 0,
        .free_transmit_descriptors_before_recycle = 2,
        .completed_transmit_descriptors = 0,
        .transmit_queue_was_stopped = true,
        .wake_threshold = 2,
        .probe_snapshot_replayed = true,
    });

    try std.testing.expect(summary.control_restore.control_queue_restored);
    try std.testing.expect(summary.refill.replay_ready);
    try std.testing.expect(summary.recycle.reaches_wake_threshold);
    try std.testing.expect(!summary.recycle.wakes_transmit_queue);
    try std.testing.expectEqual(throughput.ThroughputParityStatus.parity_gate_ready, summary.throughput.status);
    try std.testing.expect(summary.throughput.transmit_recycle_ready);
    try std.testing.expectEqual(post_reset.PostResetReplayBlocker.none, summary.replay.blocker);
    try std.testing.expectEqual(queue_resume.QueueResumeBlocker.none, summary.queue_resume_summary.blocker);
    try std.testing.expect(summary.can_return_driver_ownership);
    try std.testing.expect(driverOwnsBothSubmissions(summary));
}

test "virtio net recovery pipeline stays probe-gated until the final replay checkpoint lands" {
    const summary = try summarizeRecoveryPipeline(.{
        .reset_generation = 15,
        .receive_queue_pairs_before_reset = 4,
        .receive_queue_pairs_after_restore = 4,
        .receive_buffers_before_reset = 512,
        .receive_buffers_after_restore = 512,
        .descriptors_posted_after_restore = 512,
        .control_queue_present_after_restore = true,
        .control_queue_enabled_after_restore = true,
        .control_commands_before_reset = 2,
        .control_commands_replayed_after_restore = 2,
        .in_flight_transmit_descriptors = 4,
        .free_transmit_descriptors_before_recycle = 1,
        .completed_transmit_descriptors = 1,
        .transmit_queue_was_stopped = true,
        .wake_threshold = 2,
        .probe_snapshot_replayed = false,
    });

    try std.testing.expect(summary.control_restore.control_queue_restored);
    try std.testing.expect(summary.refill.replay_ready);
    try std.testing.expect(summary.recycle.wakes_transmit_queue);
    try std.testing.expectEqual(post_reset.PostResetReplayBlocker.probe_snapshot_replay, summary.replay.blocker);
    try std.testing.expectEqual(queue_resume.QueueResumeBlocker.probe_snapshot_replay, summary.queue_resume_summary.blocker);
    try std.testing.expectEqual(throughput.ThroughputParityStatus.parity_gate_ready, summary.throughput.status);
    try std.testing.expect(summary.throughput.meets_expected_min_ratio);
    try std.testing.expect(pipelineNeedsProbeReplay(summary));
    try std.testing.expect(summary.recovery_owns_any_submission);
    try std.testing.expect(!summary.can_return_driver_ownership);
}

test "virtio net recovery pipeline clears once control queue restore refill recycle throughput and probe replay all align" {
    const summary = try summarizeRecoveryPipeline(.{
        .reset_generation = 16,
        .receive_queue_pairs_before_reset = 4,
        .receive_queue_pairs_after_restore = 4,
        .receive_buffers_before_reset = 512,
        .receive_buffers_after_restore = 512,
        .descriptors_posted_after_restore = 512,
        .control_queue_present_after_restore = true,
        .control_queue_enabled_after_restore = true,
        .control_commands_before_reset = 2,
        .control_commands_replayed_after_restore = 2,
        .in_flight_transmit_descriptors = 4,
        .free_transmit_descriptors_before_recycle = 1,
        .completed_transmit_descriptors = 1,
        .transmit_queue_was_stopped = true,
        .wake_threshold = 2,
        .probe_snapshot_replayed = true,
    });

    try std.testing.expect(summary.control_restore.control_queue_restored);
    try std.testing.expectEqual(post_reset.PostResetReplayBlocker.none, summary.replay.blocker);
    try std.testing.expectEqual(queue_resume.QueueResumeBlocker.none, summary.queue_resume_summary.blocker);
    try std.testing.expectEqual(throughput.ThroughputParityStatus.parity_gate_ready, summary.throughput.status);
    try std.testing.expect(summary.throughput.meets_expected_min_ratio);
    try std.testing.expect(summary.can_return_driver_ownership);
    try std.testing.expect(driverOwnsBothSubmissions(summary));
    try std.testing.expect(!pipelineNeedsProbeReplay(summary));
}
