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
    try std.testing.expect(!blocked.can_resume_queues);

    const ready = try queue_resume.summarizeQueueResume(.{
        .reset_generation = 2,
        .receive_queue_pairs = 2,
        .refill_replay_ready = true,
        .control_queue_restored = true,
        .transmit_recycle_ready = true,
        .probe_snapshot_replayed = true,
    });
    try std.testing.expectEqual(queue_resume.QueueResumeBlocker.none, ready.blocker);
    try std.testing.expect(ready.probe_snapshot_replayed);
    try std.testing.expect(ready.can_resume_queues);
    try std.testing.expect(ready.resumes_receive_submission);
    try std.testing.expect(ready.resumes_transmit_submission);
}
