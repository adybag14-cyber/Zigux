const std = @import("std");

pub const QueueResumeBlocker = enum {
    none,
    reset_frozen,
    control_queue_restore,
    refill_replay,
    transmit_recycle,
    probe_snapshot_replay,
};

pub const QueueResumeCheckpoint = enum {
    after_reset_unfreeze,
    after_control_queue_restore,
    after_receive_refill_replay,
    after_transmit_recycle,
    after_probe_snapshot_replay,
    queues_may_resume,
};

pub const QueueSubmissionOwner = enum {
    recovery,
    driver,
};

pub const QueueResumeRequest = struct {
    reset_generation: u32,
    queues_frozen: bool = false,
    receive_queue_pairs: u16,
    refill_replay_ready: bool,
    control_queue_restored: bool,
    transmit_recycle_ready: bool,
    probe_snapshot_replayed: bool,
    requires_control_queue_restore: bool = true,
};

pub const QueueResumeSummary = struct {
    anchor: []const u8,
    reset_generation: u32,
    receive_queue_pairs: u16,
    queues_frozen: bool,
    refill_replay_ready: bool,
    control_queue_restored: bool,
    transmit_recycle_ready: bool,
    probe_snapshot_replayed: bool,
    requires_control_queue_restore: bool,
    blocker: QueueResumeBlocker,
    next_checkpoint: QueueResumeCheckpoint,
    resumes_receive_submission: bool,
    resumes_transmit_submission: bool,
    receive_submission_owner: QueueSubmissionOwner,
    transmit_submission_owner: QueueSubmissionOwner,
    queues_ready_for_driver_ownership: bool,
    can_resume_queues: bool,
};

pub fn summarizeQueueResume(request: QueueResumeRequest) !QueueResumeSummary {
    if (request.receive_queue_pairs == 0) return error.NoReceiveQueues;

    const blocker: QueueResumeBlocker, const next_checkpoint: QueueResumeCheckpoint = blk: {
        if (request.queues_frozen) {
            break :blk .{ .reset_frozen, .after_reset_unfreeze };
        }
        if (request.requires_control_queue_restore and !request.control_queue_restored) {
            break :blk .{ .control_queue_restore, .after_control_queue_restore };
        }
        if (!request.refill_replay_ready) {
            break :blk .{ .refill_replay, .after_receive_refill_replay };
        }
        if (!request.transmit_recycle_ready) {
            break :blk .{ .transmit_recycle, .after_transmit_recycle };
        }
        if (!request.probe_snapshot_replayed) {
            break :blk .{ .probe_snapshot_replay, .after_probe_snapshot_replay };
        }
        break :blk .{ .none, .queues_may_resume };
    };

    const resume_prereqs_ready =
        !request.queues_frozen and
        (!request.requires_control_queue_restore or request.control_queue_restored) and
        request.probe_snapshot_replayed;
    const resumes_receive_submission = resume_prereqs_ready and request.refill_replay_ready;
    const resumes_transmit_submission = resume_prereqs_ready and request.transmit_recycle_ready;
    const can_resume_queues = resumes_receive_submission and resumes_transmit_submission;
    const receive_submission_owner: QueueSubmissionOwner =
        if (resumes_receive_submission) .driver else .recovery;
    const transmit_submission_owner: QueueSubmissionOwner =
        if (resumes_transmit_submission) .driver else .recovery;

    return .{
        .anchor = "drivers/net/virtio_net.c",
        .reset_generation = request.reset_generation,
        .receive_queue_pairs = request.receive_queue_pairs,
        .queues_frozen = request.queues_frozen,
        .refill_replay_ready = request.refill_replay_ready,
        .control_queue_restored = request.control_queue_restored,
        .transmit_recycle_ready = request.transmit_recycle_ready,
        .probe_snapshot_replayed = request.probe_snapshot_replayed,
        .requires_control_queue_restore = request.requires_control_queue_restore,
        .blocker = blocker,
        .next_checkpoint = next_checkpoint,
        .resumes_receive_submission = resumes_receive_submission,
        .resumes_transmit_submission = resumes_transmit_submission,
        .receive_submission_owner = receive_submission_owner,
        .transmit_submission_owner = transmit_submission_owner,
        .queues_ready_for_driver_ownership = can_resume_queues,
        .can_resume_queues = can_resume_queues,
    };
}

test "queue resume rejects missing receive queue pairs" {
    try std.testing.expectError(error.NoReceiveQueues, summarizeQueueResume(.{
        .reset_generation = 1,
        .receive_queue_pairs = 0,
        .refill_replay_ready = true,
        .control_queue_restored = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    }));
}

test "queue resume stays blocked while reset is frozen" {
    const summary = try summarizeQueueResume(.{
        .reset_generation = 2,
        .queues_frozen = true,
        .receive_queue_pairs = 2,
        .refill_replay_ready = true,
        .control_queue_restored = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    });

    try std.testing.expectEqual(QueueResumeBlocker.reset_frozen, summary.blocker);
    try std.testing.expectEqual(QueueResumeCheckpoint.after_reset_unfreeze, summary.next_checkpoint);
    try std.testing.expect(!summary.can_resume_queues);
    try std.testing.expect(!summary.resumes_receive_submission);
    try std.testing.expect(!summary.resumes_transmit_submission);
    try std.testing.expectEqual(QueueSubmissionOwner.recovery, summary.receive_submission_owner);
    try std.testing.expectEqual(QueueSubmissionOwner.recovery, summary.transmit_submission_owner);
    try std.testing.expect(!summary.queues_ready_for_driver_ownership);
}

test "queue resume requires control queue restore when the packet says the queue is present" {
    const summary = try summarizeQueueResume(.{
        .reset_generation = 3,
        .receive_queue_pairs = 4,
        .refill_replay_ready = true,
        .control_queue_restored = false,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    });
    try std.testing.expectEqual(QueueResumeBlocker.control_queue_restore, summary.blocker);
    try std.testing.expectEqual(
        QueueResumeCheckpoint.after_control_queue_restore,
        summary.next_checkpoint,
    );
    try std.testing.expect(summary.requires_control_queue_restore);
}

test "queue resume skips control queue restore when the packet says no control queue is present" {
    const summary = try summarizeQueueResume(.{
        .reset_generation = 3,
        .receive_queue_pairs = 4,
        .refill_replay_ready = true,
        .control_queue_restored = false,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
        .requires_control_queue_restore = false,
    });

    try std.testing.expectEqual(QueueResumeBlocker.none, summary.blocker);
    try std.testing.expectEqual(QueueResumeCheckpoint.queues_may_resume, summary.next_checkpoint);
    try std.testing.expect(!summary.requires_control_queue_restore);
    try std.testing.expect(summary.can_resume_queues);
    try std.testing.expectEqual(QueueSubmissionOwner.driver, summary.receive_submission_owner);
    try std.testing.expectEqual(QueueSubmissionOwner.driver, summary.transmit_submission_owner);
    try std.testing.expect(summary.queues_ready_for_driver_ownership);
}

test "queue resume keeps receive and transmit submission ownership distinct while the overall gate stays fail-closed" {
    const refill = try summarizeQueueResume(.{
        .reset_generation = 3,
        .receive_queue_pairs = 4,
        .refill_replay_ready = false,
        .control_queue_restored = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    });
    try std.testing.expectEqual(QueueResumeBlocker.refill_replay, refill.blocker);
    try std.testing.expectEqual(
        QueueResumeCheckpoint.after_receive_refill_replay,
        refill.next_checkpoint,
    );
    try std.testing.expect(!refill.resumes_receive_submission);
    try std.testing.expect(refill.resumes_transmit_submission);
    try std.testing.expectEqual(QueueSubmissionOwner.recovery, refill.receive_submission_owner);
    try std.testing.expectEqual(QueueSubmissionOwner.driver, refill.transmit_submission_owner);
    try std.testing.expect(!refill.can_resume_queues);
    try std.testing.expect(!refill.queues_ready_for_driver_ownership);

    const transmit = try summarizeQueueResume(.{
        .reset_generation = 3,
        .receive_queue_pairs = 4,
        .refill_replay_ready = true,
        .control_queue_restored = true,
        .transmit_recycle_ready = false,
        .probe_snapshot_replayed = true,
    });
    try std.testing.expectEqual(QueueResumeBlocker.transmit_recycle, transmit.blocker);
    try std.testing.expectEqual(
        QueueResumeCheckpoint.after_transmit_recycle,
        transmit.next_checkpoint,
    );
    try std.testing.expect(transmit.resumes_receive_submission);
    try std.testing.expect(!transmit.resumes_transmit_submission);
    try std.testing.expectEqual(QueueSubmissionOwner.driver, transmit.receive_submission_owner);
    try std.testing.expectEqual(QueueSubmissionOwner.recovery, transmit.transmit_submission_owner);
    try std.testing.expect(!transmit.can_resume_queues);
    try std.testing.expect(!transmit.queues_ready_for_driver_ownership);
}

test "queue resume keeps probe snapshot replay explicit before queue submission resumes" {
    const summary = try summarizeQueueResume(.{
        .reset_generation = 4,
        .receive_queue_pairs = 8,
        .refill_replay_ready = true,
        .control_queue_restored = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = false,
    });

    try std.testing.expectEqual(QueueResumeBlocker.probe_snapshot_replay, summary.blocker);
    try std.testing.expectEqual(
        QueueResumeCheckpoint.after_probe_snapshot_replay,
        summary.next_checkpoint,
    );
    try std.testing.expect(!summary.can_resume_queues);
    try std.testing.expect(!summary.resumes_receive_submission);
    try std.testing.expect(!summary.resumes_transmit_submission);
    try std.testing.expectEqual(QueueSubmissionOwner.recovery, summary.receive_submission_owner);
    try std.testing.expectEqual(QueueSubmissionOwner.recovery, summary.transmit_submission_owner);
    try std.testing.expect(!summary.queues_ready_for_driver_ownership);
}

test "queue resume clears once the bounded replay cues are ready" {
    const summary = try summarizeQueueResume(.{
        .reset_generation = 5,
        .receive_queue_pairs = 8,
        .refill_replay_ready = true,
        .control_queue_restored = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 5), summary.reset_generation);
    try std.testing.expectEqual(@as(u16, 8), summary.receive_queue_pairs);
    try std.testing.expect(summary.requires_control_queue_restore);
    try std.testing.expectEqual(QueueResumeBlocker.none, summary.blocker);
    try std.testing.expectEqual(QueueResumeCheckpoint.queues_may_resume, summary.next_checkpoint);
    try std.testing.expect(summary.probe_snapshot_replayed);
    try std.testing.expect(summary.can_resume_queues);
    try std.testing.expect(summary.resumes_receive_submission);
    try std.testing.expect(summary.resumes_transmit_submission);
    try std.testing.expectEqual(QueueSubmissionOwner.driver, summary.receive_submission_owner);
    try std.testing.expectEqual(QueueSubmissionOwner.driver, summary.transmit_submission_owner);
    try std.testing.expect(summary.queues_ready_for_driver_ownership);
}
