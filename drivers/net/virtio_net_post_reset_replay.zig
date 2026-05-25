const std = @import("std");

pub const PostResetReplayBlocker = enum {
    none,
    control_queue_restore,
    receive_refill_replay,
    transmit_recycle,
    probe_snapshot_replay,
};

pub const PostResetReplayCheckpoint = enum {
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

pub const PostResetReplayRequest = struct {
    reset_generation: u32,
    receive_queue_pairs: u16,
    control_queue_restored: bool,
    receive_refill_replayed: bool,
    transmit_recycle_ready: bool,
    probe_snapshot_replayed: bool,
    requires_control_queue_restore: bool = true,
    requires_receive_refill_replay: bool = true,
    requires_transmit_recycle: bool = true,
    requires_probe_snapshot_replay: bool = true,
};

pub const PostResetReplaySummary = struct {
    anchor: []const u8,
    reset_generation: u32,
    receive_queue_pairs: u16,
    control_queue_restored: bool,
    receive_refill_replayed: bool,
    transmit_recycle_ready: bool,
    probe_snapshot_replayed: bool,
    requires_control_queue_restore: bool,
    requires_receive_refill_replay: bool,
    requires_transmit_recycle: bool,
    requires_probe_snapshot_replay: bool,
    blocker: PostResetReplayBlocker,
    next_checkpoint: PostResetReplayCheckpoint,
    replay_complete: bool,
    can_resume_queues: bool,
};

pub const PostResetOwnershipSummary = struct {
    anchor: []const u8,
    reset_generation: u32,
    receive_queue_pairs: u16,
    control_queue_restored: bool,
    receive_refill_replayed: bool,
    transmit_recycle_ready: bool,
    probe_snapshot_replayed: bool,
    blocker: PostResetReplayBlocker,
    next_checkpoint: PostResetReplayCheckpoint,
    resumes_receive_submission: bool,
    resumes_transmit_submission: bool,
    receive_submission_owner: QueueSubmissionOwner,
    transmit_submission_owner: QueueSubmissionOwner,
    queues_ready_for_driver_ownership: bool,
};

pub fn summarizePostResetReplay(request: PostResetReplayRequest) !PostResetReplaySummary {
    if (request.receive_queue_pairs == 0) return error.NoReceiveQueues;

    const blocker: PostResetReplayBlocker, const next_checkpoint: PostResetReplayCheckpoint = blk: {
        if (request.requires_control_queue_restore and !request.control_queue_restored) {
            break :blk .{ .control_queue_restore, .after_control_queue_restore };
        }
        if (request.requires_receive_refill_replay and !request.receive_refill_replayed) {
            break :blk .{ .receive_refill_replay, .after_receive_refill_replay };
        }
        if (request.requires_transmit_recycle and !request.transmit_recycle_ready) {
            break :blk .{ .transmit_recycle, .after_transmit_recycle };
        }
        if (request.requires_probe_snapshot_replay and !request.probe_snapshot_replayed) {
            break :blk .{ .probe_snapshot_replay, .after_probe_snapshot_replay };
        }
        break :blk .{ .none, .queues_may_resume };
    };

    const replay_complete = blocker == .none;
    return .{
        .anchor = "drivers/net/virtio_net.c",
        .reset_generation = request.reset_generation,
        .receive_queue_pairs = request.receive_queue_pairs,
        .control_queue_restored = request.control_queue_restored,
        .receive_refill_replayed = request.receive_refill_replayed,
        .transmit_recycle_ready = request.transmit_recycle_ready,
        .probe_snapshot_replayed = request.probe_snapshot_replayed,
        .requires_control_queue_restore = request.requires_control_queue_restore,
        .requires_receive_refill_replay = request.requires_receive_refill_replay,
        .requires_transmit_recycle = request.requires_transmit_recycle,
        .requires_probe_snapshot_replay = request.requires_probe_snapshot_replay,
        .blocker = blocker,
        .next_checkpoint = next_checkpoint,
        .replay_complete = replay_complete,
        .can_resume_queues = replay_complete,
    };
}

pub fn summarizePostResetOwnership(request: PostResetReplayRequest) !PostResetOwnershipSummary {
    const replay = try summarizePostResetReplay(request);
    const replay_prereqs_ready =
        (!replay.requires_control_queue_restore or replay.control_queue_restored) and
        (!replay.requires_probe_snapshot_replay or replay.probe_snapshot_replayed);
    const resumes_receive_submission =
        replay_prereqs_ready and
        (!replay.requires_receive_refill_replay or replay.receive_refill_replayed);
    const resumes_transmit_submission =
        replay_prereqs_ready and
        (!replay.requires_transmit_recycle or replay.transmit_recycle_ready);
    const receive_owner: QueueSubmissionOwner =
        if (resumes_receive_submission) .driver else .recovery;
    const transmit_owner: QueueSubmissionOwner =
        if (resumes_transmit_submission) .driver else .recovery;

    return .{
        .anchor = replay.anchor,
        .reset_generation = replay.reset_generation,
        .receive_queue_pairs = replay.receive_queue_pairs,
        .control_queue_restored = replay.control_queue_restored,
        .receive_refill_replayed = replay.receive_refill_replayed,
        .transmit_recycle_ready = replay.transmit_recycle_ready,
        .probe_snapshot_replayed = replay.probe_snapshot_replayed,
        .blocker = replay.blocker,
        .next_checkpoint = replay.next_checkpoint,
        .resumes_receive_submission = resumes_receive_submission,
        .resumes_transmit_submission = resumes_transmit_submission,
        .receive_submission_owner = receive_owner,
        .transmit_submission_owner = transmit_owner,
        .queues_ready_for_driver_ownership = replay.can_resume_queues,
    };
}

test "post reset replay keeps control queue restore ahead of later checkpoints" {
    const summary = try summarizePostResetReplay(.{
        .reset_generation = 3,
        .receive_queue_pairs = 2,
        .control_queue_restored = false,
        .receive_refill_replayed = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    });

    try std.testing.expectEqual(PostResetReplayBlocker.control_queue_restore, summary.blocker);
    try std.testing.expectEqual(PostResetReplayCheckpoint.after_control_queue_restore, summary.next_checkpoint);
    try std.testing.expect(!summary.replay_complete);
    try std.testing.expect(!summary.can_resume_queues);
}

test "post reset replay requires refill replay before probe snapshot replay" {
    const summary = try summarizePostResetReplay(.{
        .reset_generation = 4,
        .receive_queue_pairs = 4,
        .control_queue_restored = true,
        .receive_refill_replayed = false,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = false,
    });

    try std.testing.expectEqual(PostResetReplayBlocker.receive_refill_replay, summary.blocker);
    try std.testing.expectEqual(PostResetReplayCheckpoint.after_receive_refill_replay, summary.next_checkpoint);
}

test "post reset replay keeps transmit recycle ahead of probe snapshot replay" {
    const summary = try summarizePostResetReplay(.{
        .reset_generation = 5,
        .receive_queue_pairs = 8,
        .control_queue_restored = true,
        .receive_refill_replayed = true,
        .transmit_recycle_ready = false,
        .probe_snapshot_replayed = false,
    });

    try std.testing.expectEqual(PostResetReplayBlocker.transmit_recycle, summary.blocker);
    try std.testing.expectEqual(PostResetReplayCheckpoint.after_transmit_recycle, summary.next_checkpoint);
}

test "post reset replay keeps probe snapshot refresh explicit before queue resume" {
    const summary = try summarizePostResetReplay(.{
        .reset_generation = 6,
        .receive_queue_pairs = 8,
        .control_queue_restored = true,
        .receive_refill_replayed = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = false,
    });

    try std.testing.expectEqual(PostResetReplayBlocker.probe_snapshot_replay, summary.blocker);
    try std.testing.expectEqual(PostResetReplayCheckpoint.after_probe_snapshot_replay, summary.next_checkpoint);
    try std.testing.expect(!summary.can_resume_queues);
}

test "post reset replay skips optional replay gates when the packet marks them absent" {
    const summary = try summarizePostResetReplay(.{
        .reset_generation = 7,
        .receive_queue_pairs = 6,
        .control_queue_restored = false,
        .receive_refill_replayed = false,
        .transmit_recycle_ready = false,
        .probe_snapshot_replayed = false,
        .requires_control_queue_restore = false,
        .requires_receive_refill_replay = false,
        .requires_transmit_recycle = false,
        .requires_probe_snapshot_replay = false,
    });

    try std.testing.expectEqual(PostResetReplayBlocker.none, summary.blocker);
    try std.testing.expectEqual(PostResetReplayCheckpoint.queues_may_resume, summary.next_checkpoint);
    try std.testing.expect(!summary.requires_control_queue_restore);
    try std.testing.expect(!summary.requires_receive_refill_replay);
    try std.testing.expect(!summary.requires_transmit_recycle);
    try std.testing.expect(!summary.requires_probe_snapshot_replay);
    try std.testing.expect(summary.replay_complete);
    try std.testing.expect(summary.can_resume_queues);
}

test "post reset replay clears once all bounded replay cues are satisfied" {
    const summary = try summarizePostResetReplay(.{
        .reset_generation = 8,
        .receive_queue_pairs = 8,
        .control_queue_restored = true,
        .receive_refill_replayed = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", summary.anchor);
    try std.testing.expectEqual(PostResetReplayBlocker.none, summary.blocker);
    try std.testing.expectEqual(PostResetReplayCheckpoint.queues_may_resume, summary.next_checkpoint);
    try std.testing.expect(summary.replay_complete);
    try std.testing.expect(summary.can_resume_queues);
}

test "post reset replay rejects packets without receive queues" {
    try std.testing.expectError(error.NoReceiveQueues, summarizePostResetReplay(.{
        .reset_generation = 1,
        .receive_queue_pairs = 0,
        .control_queue_restored = true,
        .receive_refill_replayed = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    }));
}

test "post reset ownership keeps both queue submissions under recovery until probe replay clears" {
    const summary = try summarizePostResetOwnership(.{
        .reset_generation = 9,
        .receive_queue_pairs = 4,
        .control_queue_restored = true,
        .receive_refill_replayed = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = false,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", summary.anchor);
    try std.testing.expectEqual(PostResetReplayBlocker.probe_snapshot_replay, summary.blocker);
    try std.testing.expectEqual(PostResetReplayCheckpoint.after_probe_snapshot_replay, summary.next_checkpoint);
    try std.testing.expect(!summary.resumes_receive_submission);
    try std.testing.expect(!summary.resumes_transmit_submission);
    try std.testing.expectEqual(QueueSubmissionOwner.recovery, summary.receive_submission_owner);
    try std.testing.expectEqual(QueueSubmissionOwner.recovery, summary.transmit_submission_owner);
    try std.testing.expect(!summary.queues_ready_for_driver_ownership);
}

test "post reset ownership returns receive submission before transmit recycle clears" {
    const summary = try summarizePostResetOwnership(.{
        .reset_generation = 10,
        .receive_queue_pairs = 4,
        .control_queue_restored = true,
        .receive_refill_replayed = true,
        .transmit_recycle_ready = false,
        .probe_snapshot_replayed = true,
    });

    try std.testing.expectEqual(PostResetReplayBlocker.transmit_recycle, summary.blocker);
    try std.testing.expectEqual(PostResetReplayCheckpoint.after_transmit_recycle, summary.next_checkpoint);
    try std.testing.expect(summary.resumes_receive_submission);
    try std.testing.expect(!summary.resumes_transmit_submission);
    try std.testing.expectEqual(QueueSubmissionOwner.driver, summary.receive_submission_owner);
    try std.testing.expectEqual(QueueSubmissionOwner.recovery, summary.transmit_submission_owner);
    try std.testing.expect(!summary.queues_ready_for_driver_ownership);
}

test "post reset ownership returns queue submission to the driver once optional gates are parked" {
    const summary = try summarizePostResetOwnership(.{
        .reset_generation = 11,
        .receive_queue_pairs = 4,
        .control_queue_restored = false,
        .receive_refill_replayed = false,
        .transmit_recycle_ready = false,
        .probe_snapshot_replayed = false,
        .requires_control_queue_restore = false,
        .requires_receive_refill_replay = false,
        .requires_transmit_recycle = false,
        .requires_probe_snapshot_replay = false,
    });

    try std.testing.expectEqual(PostResetReplayBlocker.none, summary.blocker);
    try std.testing.expectEqual(PostResetReplayCheckpoint.queues_may_resume, summary.next_checkpoint);
    try std.testing.expect(summary.resumes_receive_submission);
    try std.testing.expect(summary.resumes_transmit_submission);
    try std.testing.expectEqual(QueueSubmissionOwner.driver, summary.receive_submission_owner);
    try std.testing.expectEqual(QueueSubmissionOwner.driver, summary.transmit_submission_owner);
    try std.testing.expect(summary.queues_ready_for_driver_ownership);
}

test "post reset ownership forwards missing-queue failures" {
    try std.testing.expectError(error.NoReceiveQueues, summarizePostResetOwnership(.{
        .reset_generation = 2,
        .receive_queue_pairs = 0,
        .control_queue_restored = true,
        .receive_refill_replayed = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    }));
}
