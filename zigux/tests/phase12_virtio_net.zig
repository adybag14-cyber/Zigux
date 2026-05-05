const std = @import("std");
const virtio_net = @import("virtio_net");

test "phase12 virtio net probe starter stays anchored to virtio_net.c" {
    const descriptor = virtio_net.VirtioNetProbeLab.descriptor();
    try std.testing.expectEqualStrings("virtio_net_probe_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_probe_queue_snapshot);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_napi_poll);
    try std.testing.expect(!descriptor.touches_netdev_lifecycle);
    try std.testing.expect(descriptor.touches_transport_recovery);
}

test "phase12 virtio net probe snapshot plans multiqueue control and rss state" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_hash_report,
        virtio_net.feature_rss,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_hash_report,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 6,
        .max_queue_pairs = 4,
    });

    try std.testing.expectEqual(@as(usize, 5), snapshot.offered_feature_count);
    try std.testing.expectEqual(@as(usize, 5), snapshot.negotiated_feature_count);
    try std.testing.expectEqual(@as(u16, 4), snapshot.max_queue_pairs);
    try std.testing.expectEqual(@as(u16, 4), snapshot.planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 4), snapshot.rx_queue_count);
    try std.testing.expectEqual(@as(u16, 4), snapshot.tx_queue_count);
    try std.testing.expectEqual(@as(u16, 9), snapshot.total_queue_count);
    try std.testing.expectEqual(@as(?u16, 8), snapshot.control_queue_index);
    try std.testing.expect(snapshot.mergeable_rx_buffers);
    try std.testing.expect(snapshot.has_rss);
    try std.testing.expect(snapshot.has_rss_hash_report);
    try std.testing.expectEqual(virtio_net.RssRecoveryState.active, snapshot.rss_recovery_state);
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.none, snapshot.fallback_reason);
    try std.testing.expectEqual(virtio_net.RecoveryState.stable, snapshot.recovery_state);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.clamp_queue_pairs, snapshot.queue_recovery_action);
}

test "phase12 virtio net falls back to one queue pair without control virtqueue" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_multiqueue,
        virtio_net.feature_rss,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_multiqueue,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 4,
        .max_queue_pairs = 8,
    });

    try std.testing.expectEqual(@as(u16, 1), snapshot.max_queue_pairs);
    try std.testing.expectEqual(@as(u16, 1), snapshot.planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), snapshot.total_queue_count);
    try std.testing.expectEqual(@as(?u16, null), snapshot.control_queue_index);
    try std.testing.expect(snapshot.mergeable_rx_buffers);
    try std.testing.expectEqual(
        virtio_net.RssRecoveryState.downgraded_single_queue,
        snapshot.rss_recovery_state,
    );
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.missing_control_vq, snapshot.fallback_reason);
    try std.testing.expectEqual(virtio_net.RecoveryState.stable, snapshot.recovery_state);
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.degrade_to_single_queue,
        snapshot.queue_recovery_action,
    );
}

test "phase12 virtio net distinguishes renegotiation from reset-required recovery" {
    var renegotiate_lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_rss,
    });
    const renegotiate = try renegotiate_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 3,
        .max_queue_pairs = 4,
        .transport_accepts_features = false,
    });
    try std.testing.expectEqual(@as(usize, 3), renegotiate.offered_feature_count);
    try std.testing.expectEqual(@as(usize, 0), renegotiate.negotiated_feature_count);
    try std.testing.expectEqual(@as(u16, 1), renegotiate.planned_queue_pairs);
    try std.testing.expectEqual(
        virtio_net.RssRecoveryState.requested_but_unavailable,
        renegotiate.rss_recovery_state,
    );
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.multiqueue_not_negotiated, renegotiate.fallback_reason);
    try std.testing.expectEqual(virtio_net.RecoveryState.renegotiate_features, renegotiate.recovery_state);
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.renegotiate_features,
        renegotiate.queue_recovery_action,
    );

    var reset_lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
    });
    const reset = try reset_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
        },
        .requested_queue_pairs = 2,
        .max_queue_pairs = 2,
        .device_signals_reset = true,
    });
    try std.testing.expectEqual(@as(u16, 2), reset.planned_queue_pairs);
    try std.testing.expectEqual(virtio_net.RssRecoveryState.not_requested, reset.rss_recovery_state);
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.none, reset.fallback_reason);
    try std.testing.expectEqual(virtio_net.RecoveryState.reset_required, reset.recovery_state);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.require_reset, reset.queue_recovery_action);
}

test "phase12 virtio net freeze and restore preserve queue recovery intent" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_rss,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 3,
        .max_queue_pairs = 3,
    });
    try std.testing.expectEqual(virtio_net.RecoveryState.stable, snapshot.recovery_state);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.none, snapshot.queue_recovery_action);

    const freeze = try lab.freezeForRecovery();
    try std.testing.expectEqual(virtio_net.RecoveryAction.freeze, freeze.action);
    try std.testing.expect(!freeze.was_frozen);
    try std.testing.expect(freeze.is_frozen);
    try std.testing.expect(!freeze.planned_queue_pairs_available);
    try std.testing.expectEqual(@as(u16, 3), freeze.remembered_planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 7), freeze.remembered_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 6), freeze.remembered_control_queue_index);
    try std.testing.expectEqual(virtio_net.RssRecoveryState.active, freeze.remembered_rss_recovery_state);
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.none, freeze.remembered_fallback_reason);
    try std.testing.expectEqual(virtio_net.RecoveryState.stable, freeze.remembered_recovery_state);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.none, freeze.remembered_queue_recovery_action);
    try std.testing.expectEqual(@as(u16, 0), freeze.recovery_generation);

    try std.testing.expectError(error.TransportRecoveryFrozen, lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{ virtio_net.feature_control_vq, virtio_net.feature_multiqueue },
        .requested_queue_pairs = 2,
        .max_queue_pairs = 2,
    }));

    const restore = try lab.restoreAfterRecovery();
    try std.testing.expectEqual(virtio_net.RecoveryAction.restore, restore.action);
    try std.testing.expect(restore.was_frozen);
    try std.testing.expect(!restore.is_frozen);
    try std.testing.expect(restore.planned_queue_pairs_available);
    try std.testing.expectEqual(@as(u16, 3), restore.remembered_planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 7), restore.remembered_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 6), restore.remembered_control_queue_index);
    try std.testing.expectEqual(virtio_net.RssRecoveryState.active, restore.remembered_rss_recovery_state);
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.none, restore.remembered_fallback_reason);
    try std.testing.expectEqual(virtio_net.RecoveryState.stable, restore.remembered_recovery_state);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.none, restore.remembered_queue_recovery_action);
    try std.testing.expectEqual(@as(u16, 1), restore.recovery_generation);

    try std.testing.expectError(error.ProbeSnapshotUnavailable, lab.freezeForRecovery());
}

test "phase12 virtio net queue resume planning keeps rebuild scope explicit" {
    var active_lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_rss,
    });
    _ = try active_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 3,
        .max_queue_pairs = 3,
    });
    _ = try active_lab.freezeForRecovery();
    const active_resume = try active_lab.planQueueResume();
    try std.testing.expect(active_resume.is_frozen);
    try std.testing.expectEqual(@as(u16, 0), active_resume.recovery_generation);
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.ready, active_resume.readiness);
    try std.testing.expectEqual(virtio_net.QueueResumeScope.data_control_and_rss, active_resume.rebuild_scope);
    try std.testing.expectEqual(@as(u16, 3), active_resume.resume_queue_pairs);
    try std.testing.expectEqual(@as(u16, 7), active_resume.resume_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 6), active_resume.resume_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.RssRecoveryState.active,
        active_resume.remembered_rss_recovery_state,
    );
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.none, active_resume.remembered_fallback_reason);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.none, active_resume.remembered_queue_recovery_action);
    try std.testing.expect(active_resume.requires_control_queue_restore);
    try std.testing.expect(active_resume.requires_rss_reapply);
    try std.testing.expect(active_resume.requires_fresh_probe_snapshot);

    var reset_lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
    });
    _ = try reset_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
        },
        .requested_queue_pairs = 2,
        .max_queue_pairs = 2,
        .device_signals_reset = true,
    });
    _ = try reset_lab.freezeForRecovery();
    const reset_resume = try reset_lab.planQueueResume();
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.requires_reset, reset_resume.readiness);
    try std.testing.expectEqual(virtio_net.QueueResumeScope.data_and_control_queue, reset_resume.rebuild_scope);
    try std.testing.expectEqual(@as(u16, 2), reset_resume.resume_queue_pairs);
    try std.testing.expectEqual(@as(u16, 5), reset_resume.resume_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 4), reset_resume.resume_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.require_reset,
        reset_resume.remembered_queue_recovery_action,
    );
    try std.testing.expect(reset_resume.requires_control_queue_restore);
    try std.testing.expect(!reset_resume.requires_rss_reapply);
    try std.testing.expect(reset_resume.requires_fresh_probe_snapshot);
}
