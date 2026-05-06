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

test "phase12 virtio net keeps invalid max_queue_pairs fallback explicit" {
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
        .requested_queue_pairs = 4,
        .max_queue_pairs = 0,
    });

    try std.testing.expectEqual(@as(u16, 1), snapshot.max_queue_pairs);
    try std.testing.expectEqual(@as(u16, 1), snapshot.planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 1), snapshot.rx_queue_count);
    try std.testing.expectEqual(@as(u16, 1), snapshot.tx_queue_count);
    try std.testing.expectEqual(@as(u16, 3), snapshot.total_queue_count);
    try std.testing.expectEqual(@as(?u16, 2), snapshot.control_queue_index);
    try std.testing.expectEqual(
        virtio_net.RssRecoveryState.downgraded_single_queue,
        snapshot.rss_recovery_state,
    );
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.invalid_max_queue_pairs,
        snapshot.fallback_reason,
    );
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

test "phase12 virtio net receive refill planning keeps buffer mode and replay needs explicit" {
    var active_lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_hash_report,
        virtio_net.feature_rss,
    });
    _ = try active_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_hash_report,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 3,
        .max_queue_pairs = 3,
    });
    _ = try active_lab.freezeForRecovery();
    const active_refill = try active_lab.planReceiveRefill();
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.ready, active_refill.readiness);
    try std.testing.expectEqual(virtio_net.QueueResumeScope.data_control_and_rss, active_refill.resume_scope);
    try std.testing.expectEqual(virtio_net.ReceiveBufferMode.mergeable_rx_buffers, active_refill.buffer_mode);
    try std.testing.expectEqual(@as(u16, 3), active_refill.refill_queue_pairs);
    try std.testing.expectEqual(@as(u16, 3), active_refill.refill_rx_queue_count);
    try std.testing.expectEqual(@as(u16, 7), active_refill.refill_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 6), active_refill.resume_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.none,
        active_refill.remembered_queue_recovery_action,
    );
    try std.testing.expect(active_refill.requires_control_queue_restore);
    try std.testing.expect(active_refill.requires_rss_reapply);
    try std.testing.expect(active_refill.requires_mergeable_buffer_headroom);
    try std.testing.expect(active_refill.requires_fresh_probe_snapshot);
    try std.testing.expect(active_refill.requires_post_restore_probe_replay);

    var single_queue_lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_multiqueue,
        virtio_net.feature_rss,
    });
    _ = try single_queue_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_multiqueue,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 4,
        .max_queue_pairs = 8,
    });
    _ = try single_queue_lab.freezeForRecovery();
    const single_queue_refill = try single_queue_lab.planReceiveRefill();
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.ready, single_queue_refill.readiness);
    try std.testing.expectEqual(virtio_net.QueueResumeScope.data_queues_only, single_queue_refill.resume_scope);
    try std.testing.expectEqual(virtio_net.ReceiveBufferMode.mergeable_rx_buffers, single_queue_refill.buffer_mode);
    try std.testing.expectEqual(@as(u16, 1), single_queue_refill.refill_queue_pairs);
    try std.testing.expectEqual(@as(u16, 1), single_queue_refill.refill_rx_queue_count);
    try std.testing.expectEqual(@as(u16, 2), single_queue_refill.refill_total_queue_count);
    try std.testing.expectEqual(@as(?u16, null), single_queue_refill.resume_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.degrade_to_single_queue,
        single_queue_refill.remembered_queue_recovery_action,
    );
    try std.testing.expect(!single_queue_refill.requires_control_queue_restore);
    try std.testing.expect(!single_queue_refill.requires_rss_reapply);
    try std.testing.expect(single_queue_refill.requires_mergeable_buffer_headroom);
    try std.testing.expect(single_queue_refill.requires_fresh_probe_snapshot);
    try std.testing.expect(single_queue_refill.requires_post_restore_probe_replay);

    var clamp_lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_hash_report,
        virtio_net.feature_rss,
    });
    _ = try clamp_lab.captureProbeSnapshot(.{
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
    _ = try clamp_lab.freezeForRecovery();
    const clamp_refill = try clamp_lab.planReceiveRefill();
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.ready, clamp_refill.readiness);
    try std.testing.expectEqual(virtio_net.QueueResumeScope.data_control_and_rss, clamp_refill.resume_scope);
    try std.testing.expectEqual(virtio_net.ReceiveBufferMode.mergeable_rx_buffers, clamp_refill.buffer_mode);
    try std.testing.expectEqual(@as(u16, 4), clamp_refill.refill_queue_pairs);
    try std.testing.expectEqual(@as(u16, 4), clamp_refill.refill_rx_queue_count);
    try std.testing.expectEqual(@as(u16, 9), clamp_refill.refill_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 8), clamp_refill.resume_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.clamp_queue_pairs,
        clamp_refill.remembered_queue_recovery_action,
    );
    try std.testing.expect(clamp_refill.requires_control_queue_restore);
    try std.testing.expect(clamp_refill.requires_rss_reapply);
    try std.testing.expect(clamp_refill.requires_mergeable_buffer_headroom);
    try std.testing.expect(clamp_refill.requires_fresh_probe_snapshot);
    try std.testing.expect(clamp_refill.requires_post_restore_probe_replay);

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
    const reset_refill = try reset_lab.planReceiveRefill();
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.requires_reset, reset_refill.readiness);
    try std.testing.expectEqual(virtio_net.QueueResumeScope.data_and_control_queue, reset_refill.resume_scope);
    try std.testing.expectEqual(virtio_net.ReceiveBufferMode.one_buffer_per_rx, reset_refill.buffer_mode);
    try std.testing.expectEqual(@as(u16, 2), reset_refill.refill_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), reset_refill.refill_rx_queue_count);
    try std.testing.expectEqual(@as(u16, 5), reset_refill.refill_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 4), reset_refill.resume_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.require_reset,
        reset_refill.remembered_queue_recovery_action,
    );
    try std.testing.expect(reset_refill.requires_control_queue_restore);
    try std.testing.expect(!reset_refill.requires_rss_reapply);
    try std.testing.expect(!reset_refill.requires_mergeable_buffer_headroom);
    try std.testing.expect(reset_refill.requires_fresh_probe_snapshot);
    try std.testing.expect(reset_refill.requires_post_restore_probe_replay);
}

test "phase12 virtio net transmit recycle keeps control and rss ordering explicit" {
    var active_lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_hash_report,
        virtio_net.feature_rss,
    });
    _ = try active_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_hash_report,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 3,
        .max_queue_pairs = 3,
    });
    _ = try active_lab.freezeForRecovery();
    const active_recycle = try active_lab.planTransmitRecycle();
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.ready, active_recycle.readiness);
    try std.testing.expectEqual(
        virtio_net.TransmitRecycleOrder.after_control_queue_restore_and_rss_reapply,
        active_recycle.recycle_order,
    );
    try std.testing.expectEqual(@as(u16, 3), active_recycle.recycle_queue_pairs);
    try std.testing.expectEqual(@as(u16, 3), active_recycle.recycle_tx_queue_count);
    try std.testing.expectEqual(@as(u16, 7), active_recycle.recycle_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 6), active_recycle.resume_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.none,
        active_recycle.remembered_queue_recovery_action,
    );
    try std.testing.expect(active_recycle.requires_control_queue_restore);
    try std.testing.expect(active_recycle.requires_rss_reapply);
    try std.testing.expect(active_recycle.requires_receive_refill_coordination);
    try std.testing.expect(active_recycle.requires_fresh_probe_snapshot);
    try std.testing.expect(active_recycle.requires_post_restore_probe_replay);

    var data_only_lab = try virtio_net.VirtioNetProbeLab.init(&.{});
    _ = try data_only_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{},
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });
    _ = try data_only_lab.freezeForRecovery();
    const data_only_recycle = try data_only_lab.planTransmitRecycle();
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.ready, data_only_recycle.readiness);
    try std.testing.expectEqual(
        virtio_net.TransmitRecycleOrder.data_queues_only,
        data_only_recycle.recycle_order,
    );
    try std.testing.expectEqual(@as(u16, 1), data_only_recycle.recycle_queue_pairs);
    try std.testing.expectEqual(@as(u16, 1), data_only_recycle.recycle_tx_queue_count);
    try std.testing.expectEqual(@as(u16, 2), data_only_recycle.recycle_total_queue_count);
    try std.testing.expectEqual(@as(?u16, null), data_only_recycle.resume_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.none,
        data_only_recycle.remembered_queue_recovery_action,
    );
    try std.testing.expect(!data_only_recycle.requires_control_queue_restore);
    try std.testing.expect(!data_only_recycle.requires_rss_reapply);
    try std.testing.expect(!data_only_recycle.requires_receive_refill_coordination);
    try std.testing.expect(data_only_recycle.requires_fresh_probe_snapshot);
    try std.testing.expect(data_only_recycle.requires_post_restore_probe_replay);

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
    const reset_recycle = try reset_lab.planTransmitRecycle();
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.requires_reset, reset_recycle.readiness);
    try std.testing.expectEqual(
        virtio_net.TransmitRecycleOrder.after_control_queue_restore,
        reset_recycle.recycle_order,
    );
    try std.testing.expectEqual(@as(u16, 2), reset_recycle.recycle_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), reset_recycle.recycle_tx_queue_count);
    try std.testing.expectEqual(@as(u16, 5), reset_recycle.recycle_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 4), reset_recycle.resume_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.require_reset,
        reset_recycle.remembered_queue_recovery_action,
    );
    try std.testing.expect(reset_recycle.requires_control_queue_restore);
    try std.testing.expect(!reset_recycle.requires_rss_reapply);
    try std.testing.expect(reset_recycle.requires_receive_refill_coordination);
    try std.testing.expect(reset_recycle.requires_fresh_probe_snapshot);
    try std.testing.expect(reset_recycle.requires_post_restore_probe_replay);
}

test "phase12 virtio net transmit recycle refreshes after a repeated recovery cycle" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_rss,
    });

    _ = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 3,
        .max_queue_pairs = 3,
    });
    _ = try lab.freezeForRecovery();
    const first_recycle = try lab.planTransmitRecycle();
    try std.testing.expectEqual(@as(u16, 0), first_recycle.recovery_generation);
    try std.testing.expectEqual(
        virtio_net.TransmitRecycleOrder.after_control_queue_restore_and_rss_reapply,
        first_recycle.recycle_order,
    );
    try std.testing.expectEqual(@as(u16, 3), first_recycle.recycle_queue_pairs);
    try std.testing.expectEqual(@as(u16, 3), first_recycle.recycle_tx_queue_count);
    try std.testing.expectEqual(@as(u16, 7), first_recycle.recycle_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 6), first_recycle.resume_control_queue_index);
    try std.testing.expect(first_recycle.requires_control_queue_restore);
    try std.testing.expect(first_recycle.requires_rss_reapply);
    try std.testing.expect(first_recycle.requires_receive_refill_coordination);
    _ = try lab.restoreAfterRecovery();

    _ = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_multiqueue,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 4,
        .max_queue_pairs = 8,
    });
    _ = try lab.freezeForRecovery();
    const second_recycle = try lab.planTransmitRecycle();
    try std.testing.expectEqual(@as(u16, 1), second_recycle.recovery_generation);
    try std.testing.expectEqual(
        virtio_net.TransmitRecycleOrder.data_queues_only,
        second_recycle.recycle_order,
    );
    try std.testing.expectEqual(@as(u16, 1), second_recycle.recycle_queue_pairs);
    try std.testing.expectEqual(@as(u16, 1), second_recycle.recycle_tx_queue_count);
    try std.testing.expectEqual(@as(u16, 2), second_recycle.recycle_total_queue_count);
    try std.testing.expectEqual(@as(?u16, null), second_recycle.resume_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.degrade_to_single_queue,
        second_recycle.remembered_queue_recovery_action,
    );
    try std.testing.expect(!second_recycle.requires_control_queue_restore);
    try std.testing.expect(!second_recycle.requires_rss_reapply);
    try std.testing.expect(second_recycle.requires_receive_refill_coordination);
    try std.testing.expect(second_recycle.requires_fresh_probe_snapshot);
    try std.testing.expect(second_recycle.requires_post_restore_probe_replay);
}

test "phase12 virtio net clamps mergeable buffer length to the minimum floor" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
    });
    _ = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });
    _ = try lab.freezeForRecovery();

    const summary = try lab.planMergeableBufferLength(.{
        .observed_average_packet_len_bytes = 256,
        .min_buf_len_bytes = 1536,
    });
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", summary.anchor);
    try std.testing.expectEqual(virtio_net.MergeableBufferLengthSource.minimum_buffer_floor, summary.source);
    try std.testing.expectEqual(@as(u16, 256), summary.observed_average_packet_len_bytes);
    try std.testing.expectEqual(@as(u16, 1536), summary.min_buf_len_bytes);
    try std.testing.expectEqual(@as(u16, 0), summary.xdp_headroom_bytes);
    try std.testing.expectEqual(@as(u16, 0), summary.tailroom_bytes);
    try std.testing.expectEqual(@as(u16, 0), summary.room_bytes);
    try std.testing.expectEqual(@as(u16, 4084), summary.payload_limit_bytes);
    try std.testing.expectEqual(@as(u16, 1536), summary.selected_payload_bytes);
    try std.testing.expectEqual(@as(u16, 12), summary.hdr_len_bytes);
    try std.testing.expectEqual(@as(u16, 1600), summary.submit_len_bytes);
    try std.testing.expectEqual(@as(u16, 1600), summary.allocation_len_bytes);
}

test "phase12 virtio net keeps observed average mergeable buffer length when already in range" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
    });
    _ = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });
    _ = try lab.freezeForRecovery();

    const summary = try lab.planMergeableBufferLength(.{
        .observed_average_packet_len_bytes = 1500,
        .min_buf_len_bytes = 1024,
    });
    try std.testing.expectEqual(virtio_net.MergeableBufferLengthSource.observed_average_packet, summary.source);
    try std.testing.expectEqual(@as(u16, 1500), summary.observed_average_packet_len_bytes);
    try std.testing.expectEqual(@as(u16, 1024), summary.min_buf_len_bytes);
    try std.testing.expectEqual(@as(u16, 0), summary.xdp_headroom_bytes);
    try std.testing.expectEqual(@as(u16, 0), summary.tailroom_bytes);
    try std.testing.expectEqual(@as(u16, 0), summary.room_bytes);
    try std.testing.expectEqual(@as(u16, 4084), summary.payload_limit_bytes);
    try std.testing.expectEqual(@as(u16, 1500), summary.selected_payload_bytes);
    try std.testing.expectEqual(@as(u16, 12), summary.hdr_len_bytes);
    try std.testing.expectEqual(@as(u16, 1536), summary.submit_len_bytes);
    try std.testing.expectEqual(@as(u16, 1536), summary.allocation_len_bytes);
}

test "phase12 virtio net caps mergeable buffer length at page payload limit" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_hash_report,
    });
    _ = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_hash_report,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });
    _ = try lab.freezeForRecovery();

    const summary = try lab.planMergeableBufferLength(.{
        .observed_average_packet_len_bytes = 5000,
        .min_buf_len_bytes = 1536,
    });
    try std.testing.expectEqual(virtio_net.MergeableBufferLengthSource.page_size_cap, summary.source);
    try std.testing.expectEqual(@as(u16, 4076), summary.payload_limit_bytes);
    try std.testing.expectEqual(@as(u16, 4076), summary.selected_payload_bytes);
    try std.testing.expectEqual(@as(u16, 20), summary.hdr_len_bytes);
    try std.testing.expectEqual(@as(u16, 4096), summary.submit_len_bytes);
    try std.testing.expectEqual(@as(u16, 4096), summary.allocation_len_bytes);
}

test "phase12 virtio net uses page minus room when xdp headroom is present" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
    });
    _ = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });
    _ = try lab.freezeForRecovery();

    const summary = try lab.planMergeableBufferLength(.{
        .observed_average_packet_len_bytes = 1024,
        .min_buf_len_bytes = 1536,
        .xdp_headroom_bytes = 256,
    });
    try std.testing.expectEqual(virtio_net.MergeableBufferLengthSource.page_minus_room, summary.source);
    try std.testing.expectEqual(@as(u16, 256), summary.xdp_headroom_bytes);
    try std.testing.expectEqual(@as(u16, 320), summary.tailroom_bytes);
    try std.testing.expectEqual(@as(u16, 576), summary.room_bytes);
    try std.testing.expectEqual(@as(u16, 4084), summary.payload_limit_bytes);
    try std.testing.expectEqual(@as(u16, 3508), summary.selected_payload_bytes);
    try std.testing.expectEqual(@as(u16, 12), summary.hdr_len_bytes);
    try std.testing.expectEqual(@as(u16, 3520), summary.submit_len_bytes);
    try std.testing.expectEqual(@as(u16, 4096), summary.allocation_len_bytes);
}

test "phase12 virtio net rejects mergeable buffer length planning for non-mergeable snapshots" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{});
    _ = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{},
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });
    _ = try lab.freezeForRecovery();

    try std.testing.expectError(error.ReceiveBufferModeNotMergeable, lab.planMergeableBufferLength(.{
        .observed_average_packet_len_bytes = 512,
        .min_buf_len_bytes = 1536,
    }));
}
