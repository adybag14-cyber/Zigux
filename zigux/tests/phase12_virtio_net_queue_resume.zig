const std = @import("std");
const virtio_net_queue_resume = @import("virtio_net_queue_resume");

test "phase12 virtio net queue resume summary stays anchored to virtio_net.c" {
    const summary = try virtio_net_queue_resume.summarizeQueueResume(.{
        .effective_queue_pairs = 1,
        .receive_queue_count = 1,
        .transmit_queue_count = 1,
        .total_queue_count = 2,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 1), summary.effective_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), summary.total_queue_count);
    try std.testing.expectEqual(
        virtio_net_queue_resume.QueueResumeCheckpoint.after_transmit_queue_restore,
        summary.checkpoint,
    );
    try std.testing.expectEqual(
        virtio_net_queue_resume.QueueResumeScope.data_queues_only,
        summary.scope,
    );
    try std.testing.expectEqual(
        virtio_net_queue_resume.QueueResumeDisposition.resume_after_transmit_restore,
        summary.disposition,
    );
    try std.testing.expect(!summary.requires_fresh_probe_snapshot);
}

test "phase12 virtio net queue resume keeps mergeable replay and throughput guard explicit" {
    const summary = try virtio_net_queue_resume.summarizeQueueResume(.{
        .effective_queue_pairs = 1,
        .receive_queue_count = 1,
        .transmit_queue_count = 1,
        .total_queue_count = 2,
        .requires_receive_buffer_refill = true,
        .requires_mergeable_buffer_refill = true,
        .requires_post_reset_probe_replay = true,
        .post_reset_probe_replay_checkpoint = .after_receive_refill,
    });

    try std.testing.expectEqual(
        virtio_net_queue_resume.QueueResumeCheckpoint.after_receive_refill,
        summary.checkpoint,
    );
    try std.testing.expectEqual(
        virtio_net_queue_resume.QueueResumeScope.data_and_refill,
        summary.scope,
    );
    try std.testing.expect(summary.requires_receive_buffer_refill);
    try std.testing.expect(summary.requires_mergeable_buffer_refill);
    try std.testing.expect(summary.requires_fresh_probe_snapshot);
    try std.testing.expect(summary.throughput_guard_active);
}

test "phase12 virtio net queue resume keeps control replay markers explicit" {
    const summary = try virtio_net_queue_resume.summarizeQueueResume(.{
        .effective_queue_pairs = 4,
        .receive_queue_count = 4,
        .transmit_queue_count = 4,
        .first_control_queue_index = 8,
        .total_queue_count = 9,
        .rss_enabled = true,
        .requires_control_queue_restore = true,
        .requires_post_reset_probe_replay = true,
        .post_reset_probe_replay_checkpoint = .after_control_queue_restore,
        .requires_receive_mode_sync = true,
        .requires_hash_report_restore = true,
        .requires_mac_table_sync = true,
        .requires_vlan_filter_sync = true,
        .requires_rss_config_sync = true,
    });

    try std.testing.expectEqual(@as(?u16, 8), summary.control_queue_index);
    try std.testing.expectEqual(
        virtio_net_queue_resume.QueueResumeCheckpoint.after_control_queue_restore,
        summary.checkpoint,
    );
    try std.testing.expectEqual(
        virtio_net_queue_resume.QueueResumeScope.data_control_and_probe_replay,
        summary.scope,
    );
    try std.testing.expect(summary.requires_control_queue_restore);
    try std.testing.expect(summary.restores_receive_mode);
    try std.testing.expect(summary.restores_hash_report);
    try std.testing.expect(summary.restores_mac_table);
    try std.testing.expect(summary.restores_vlan_filters);
    try std.testing.expect(summary.restores_rss_config);
}
