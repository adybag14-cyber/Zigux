const std = @import("std");

pub const QueueResumeBlocker = enum {
    none,
    reset_frozen,
    control_queue_restore,
    refill_replay,
    transmit_recycle,
};

pub const QueueResumeRequest = struct {
    reset_generation: u32,
    queues_frozen: bool = false,
    receive_queue_pairs: u16,
    refill_replay_ready: bool,
    control_queue_restored: bool,
    transmit_recycle_ready: bool,
};

pub const QueueResumeSummary = struct {
    anchor: []const u8,
    reset_generation: u32,
    receive_queue_pairs: u16,
    queues_frozen: bool,
    refill_replay_ready: bool,
    control_queue_restored: bool,
    transmit_recycle_ready: bool,
    blocker: QueueResumeBlocker,
    resumes_receive_submission: bool,
    resumes_transmit_submission: bool,
    can_resume_queues: bool,
};

pub fn summarizeQueueResume(request: QueueResumeRequest) !QueueResumeSummary {
    if (request.receive_queue_pairs == 0) return error.NoReceiveQueues;

    const blocker: QueueResumeBlocker = blk: {
        if (request.queues_frozen) break :blk .reset_frozen;
        if (!request.control_queue_restored) break :blk .control_queue_restore;
        if (!request.refill_replay_ready) break :blk .refill_replay;
        if (!request.transmit_recycle_ready) break :blk .transmit_recycle;
        break :blk .none;
    };

    const can_resume_queues = blocker == .none;
    return .{
        .anchor = "drivers/net/virtio_net.c",
        .reset_generation = request.reset_generation,
        .receive_queue_pairs = request.receive_queue_pairs,
        .queues_frozen = request.queues_frozen,
        .refill_replay_ready = request.refill_replay_ready,
        .control_queue_restored = request.control_queue_restored,
        .transmit_recycle_ready = request.transmit_recycle_ready,
        .blocker = blocker,
        .resumes_receive_submission = can_resume_queues,
        .resumes_transmit_submission = can_resume_queues,
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
    });

    try std.testing.expectEqual(QueueResumeBlocker.reset_frozen, summary.blocker);
    try std.testing.expect(!summary.can_resume_queues);
    try std.testing.expect(!summary.resumes_receive_submission);
    try std.testing.expect(!summary.resumes_transmit_submission);
}

test "queue resume requires control queue, refill replay, and transmit recycle readiness" {
    const control = try summarizeQueueResume(.{
        .reset_generation = 3,
        .receive_queue_pairs = 4,
        .refill_replay_ready = true,
        .control_queue_restored = false,
        .transmit_recycle_ready = true,
    });
    try std.testing.expectEqual(QueueResumeBlocker.control_queue_restore, control.blocker);

    const refill = try summarizeQueueResume(.{
        .reset_generation = 3,
        .receive_queue_pairs = 4,
        .refill_replay_ready = false,
        .control_queue_restored = true,
        .transmit_recycle_ready = true,
    });
    try std.testing.expectEqual(QueueResumeBlocker.refill_replay, refill.blocker);

    const transmit = try summarizeQueueResume(.{
        .reset_generation = 3,
        .receive_queue_pairs = 4,
        .refill_replay_ready = true,
        .control_queue_restored = true,
        .transmit_recycle_ready = false,
    });
    try std.testing.expectEqual(QueueResumeBlocker.transmit_recycle, transmit.blocker);
}

test "queue resume clears once the bounded replay cues are ready" {
    const summary = try summarizeQueueResume(.{
        .reset_generation = 4,
        .receive_queue_pairs = 8,
        .refill_replay_ready = true,
        .control_queue_restored = true,
        .transmit_recycle_ready = true,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 4), summary.reset_generation);
    try std.testing.expectEqual(@as(u16, 8), summary.receive_queue_pairs);
    try std.testing.expectEqual(QueueResumeBlocker.none, summary.blocker);
    try std.testing.expect(summary.can_resume_queues);
    try std.testing.expect(summary.resumes_receive_submission);
    try std.testing.expect(summary.resumes_transmit_submission);
}
