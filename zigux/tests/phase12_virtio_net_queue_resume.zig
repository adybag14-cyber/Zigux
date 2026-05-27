const std = @import("std");
const queue_resume = @import("virtio_net_queue_resume");

test "phase12 virtio net queue resume stays lab-only and fail-closed" {
    const blocked = try queue_resume.summarizeQueueResume(.{
        .reset_generation = 1,
        .receive_queue_pairs = 2,
        .refill_replay_ready = true,
        .control_queue_restored = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = false,
    });
    try std.testing.expectEqual(
        queue_resume.QueueResumeBlocker.probe_snapshot_replay,
        blocked.blocker,
    );
    try std.testing.expectEqual(
        queue_resume.QueueResumeCheckpoint.after_probe_snapshot_replay,
        blocked.next_checkpoint,
    );
    try std.testing.expect(!blocked.can_resume_queues);
    try std.testing.expectEqual(
        queue_resume.QueueSubmissionOwner.recovery,
        blocked.receive_submission_owner,
    );
    try std.testing.expectEqual(
        queue_resume.QueueSubmissionOwner.recovery,
        blocked.transmit_submission_owner,
    );
    try std.testing.expect(!blocked.queues_ready_for_driver_ownership);

    const ready = try queue_resume.summarizeQueueResume(.{
        .reset_generation = 2,
        .receive_queue_pairs = 2,
        .refill_replay_ready = true,
        .control_queue_restored = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    });
    try std.testing.expectEqual(queue_resume.QueueResumeBlocker.none, ready.blocker);
    try std.testing.expectEqual(
        queue_resume.QueueResumeCheckpoint.queues_may_resume,
        ready.next_checkpoint,
    );
    try std.testing.expect(ready.probe_snapshot_replayed);
    try std.testing.expect(ready.can_resume_queues);
    try std.testing.expect(ready.resumes_receive_submission);
    try std.testing.expect(ready.resumes_transmit_submission);
    try std.testing.expectEqual(
        queue_resume.QueueSubmissionOwner.driver,
        ready.receive_submission_owner,
    );
    try std.testing.expectEqual(
        queue_resume.QueueSubmissionOwner.driver,
        ready.transmit_submission_owner,
    );
    try std.testing.expect(ready.queues_ready_for_driver_ownership);
}

test "phase12 virtio net queue resume keeps control queue restore optional when the device has no control queue" {
    const summary = try queue_resume.summarizeQueueResume(.{
        .reset_generation = 3,
        .receive_queue_pairs = 2,
        .refill_replay_ready = true,
        .control_queue_restored = false,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
        .requires_control_queue_restore = false,
    });

    try std.testing.expectEqual(queue_resume.QueueResumeBlocker.none, summary.blocker);
    try std.testing.expectEqual(
        queue_resume.QueueResumeCheckpoint.queues_may_resume,
        summary.next_checkpoint,
    );
    try std.testing.expect(!summary.requires_control_queue_restore);
    try std.testing.expect(summary.can_resume_queues);
    try std.testing.expect(summary.resumes_receive_submission);
    try std.testing.expect(summary.resumes_transmit_submission);
    try std.testing.expectEqual(
        queue_resume.QueueSubmissionOwner.driver,
        summary.receive_submission_owner,
    );
    try std.testing.expectEqual(
        queue_resume.QueueSubmissionOwner.driver,
        summary.transmit_submission_owner,
    );
    try std.testing.expect(summary.queues_ready_for_driver_ownership);
}

test "phase12 virtio net queue resume keeps receive and transmit ownership distinct while the overall gate stays blocked" {
    const refill_blocked = try queue_resume.summarizeQueueResume(.{
        .reset_generation = 4,
        .receive_queue_pairs = 2,
        .refill_replay_ready = false,
        .control_queue_restored = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    });
    try std.testing.expectEqual(queue_resume.QueueResumeBlocker.refill_replay, refill_blocked.blocker);
    try std.testing.expectEqual(
        queue_resume.QueueResumeCheckpoint.after_receive_refill_replay,
        refill_blocked.next_checkpoint,
    );
    try std.testing.expect(!refill_blocked.resumes_receive_submission);
    try std.testing.expect(refill_blocked.resumes_transmit_submission);
    try std.testing.expectEqual(
        queue_resume.QueueSubmissionOwner.recovery,
        refill_blocked.receive_submission_owner,
    );
    try std.testing.expectEqual(
        queue_resume.QueueSubmissionOwner.driver,
        refill_blocked.transmit_submission_owner,
    );
    try std.testing.expect(!refill_blocked.can_resume_queues);
    try std.testing.expect(!refill_blocked.queues_ready_for_driver_ownership);

    const transmit_blocked = try queue_resume.summarizeQueueResume(.{
        .reset_generation = 5,
        .receive_queue_pairs = 2,
        .refill_replay_ready = true,
        .control_queue_restored = true,
        .transmit_recycle_ready = false,
        .probe_snapshot_replayed = true,
    });
    try std.testing.expectEqual(
        queue_resume.QueueResumeBlocker.transmit_recycle,
        transmit_blocked.blocker,
    );
    try std.testing.expectEqual(
        queue_resume.QueueResumeCheckpoint.after_transmit_recycle,
        transmit_blocked.next_checkpoint,
    );
    try std.testing.expect(transmit_blocked.resumes_receive_submission);
    try std.testing.expect(!transmit_blocked.resumes_transmit_submission);
    try std.testing.expectEqual(
        queue_resume.QueueSubmissionOwner.driver,
        transmit_blocked.receive_submission_owner,
    );
    try std.testing.expectEqual(
        queue_resume.QueueSubmissionOwner.recovery,
        transmit_blocked.transmit_submission_owner,
    );
    try std.testing.expect(!transmit_blocked.can_resume_queues);
    try std.testing.expect(!transmit_blocked.queues_ready_for_driver_ownership);
}
