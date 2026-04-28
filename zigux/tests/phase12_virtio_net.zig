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
    try std.testing.expectEqual(virtio_net.HeaderShape.hash_report, snapshot.header_shape);
    try std.testing.expectEqual(@as(u16, 20), snapshot.hdr_len_bytes);
    try std.testing.expect(snapshot.uses_hash_report_header);
    try std.testing.expect(!snapshot.uses_udp_tunnel_header);
    try std.testing.expectEqual(virtio_net.RssSummary.active, snapshot.rss_summary);
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.none, snapshot.fallback_reason);
    try std.testing.expectEqual(virtio_net.RecoveryState.stable, snapshot.recovery_state);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.clamp_queue_pairs, snapshot.queue_recovery_action);
}

test "phase12 virtio net records rss downgrade when control virtqueue is missing" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_multiqueue,
        virtio_net.feature_hash_report,
        virtio_net.feature_rss,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_multiqueue,
            virtio_net.feature_hash_report,
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
    try std.testing.expect(snapshot.has_rss);
    try std.testing.expect(snapshot.has_rss_hash_report);
    try std.testing.expectEqual(virtio_net.HeaderShape.hash_report, snapshot.header_shape);
    try std.testing.expectEqual(@as(u16, 20), snapshot.hdr_len_bytes);
    try std.testing.expect(snapshot.uses_hash_report_header);
    try std.testing.expect(!snapshot.uses_udp_tunnel_header);
    try std.testing.expectEqual(virtio_net.RssSummary.downgraded_single_queue, snapshot.rss_summary);
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.missing_control_vq, snapshot.fallback_reason);
    try std.testing.expectEqual(virtio_net.RecoveryState.stable, snapshot.recovery_state);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.degrade_to_single_queue, snapshot.queue_recovery_action);
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
    try std.testing.expectEqual(virtio_net.RssSummary.requested_but_unavailable, renegotiate.rss_summary);
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.multiqueue_not_negotiated, renegotiate.fallback_reason);
    try std.testing.expectEqual(virtio_net.RecoveryState.renegotiate_features, renegotiate.recovery_state);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.renegotiate_features, renegotiate.queue_recovery_action);

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
    try std.testing.expectEqual(virtio_net.RssSummary.not_requested, reset.rss_summary);
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
        .max_queue_pairs = 4,
        .transport_accepts_features = false,
    });
    try std.testing.expectEqual(virtio_net.RecoveryState.renegotiate_features, snapshot.recovery_state);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.renegotiate_features, snapshot.queue_recovery_action);

    const freeze = try lab.freezeForRecovery();
    try std.testing.expectEqual(virtio_net.RecoveryAction.freeze, freeze.action);
    try std.testing.expect(!freeze.was_frozen);
    try std.testing.expect(freeze.is_frozen);
    try std.testing.expect(!freeze.planned_queue_pairs_available);
    try std.testing.expectEqual(@as(u16, 1), freeze.remembered_planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), freeze.remembered_total_queue_count);
    try std.testing.expectEqual(@as(?u16, null), freeze.remembered_control_queue_index);
    try std.testing.expectEqual(virtio_net.RssSummary.requested_but_unavailable, freeze.remembered_rss_summary);
    try std.testing.expectEqual(virtio_net.RecoveryState.renegotiate_features, freeze.remembered_recovery_state);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.renegotiate_features, freeze.remembered_queue_recovery_action);
    try std.testing.expectEqual(@as(u16, 0), freeze.recovery_generation);

    const resume_summary = try lab.planQueueResume();
    try std.testing.expect(resume_summary.is_frozen);
    try std.testing.expectEqual(@as(u16, 0), resume_summary.recovery_generation);
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.requires_feature_renegotiation, resume_summary.readiness);
    try std.testing.expectEqual(virtio_net.QueueResumeScope.data_queues_only, resume_summary.rebuild_scope);
    try std.testing.expectEqual(@as(u16, 1), resume_summary.resume_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), resume_summary.resume_total_queue_count);
    try std.testing.expectEqual(@as(?u16, null), resume_summary.resume_control_queue_index);
    try std.testing.expectEqual(virtio_net.RssSummary.requested_but_unavailable, resume_summary.remembered_rss_summary);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.renegotiate_features, resume_summary.remembered_queue_recovery_action);
    try std.testing.expect(!resume_summary.requires_control_queue_restore);
    try std.testing.expect(!resume_summary.requires_rss_reapply);

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
    try std.testing.expectEqual(@as(u16, 1), restore.remembered_planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), restore.remembered_total_queue_count);
    try std.testing.expectEqual(@as(?u16, null), restore.remembered_control_queue_index);
    try std.testing.expectEqual(virtio_net.RecoveryState.renegotiate_features, restore.remembered_recovery_state);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.renegotiate_features, restore.remembered_queue_recovery_action);
    try std.testing.expectEqual(@as(u16, 1), restore.recovery_generation);

    try std.testing.expectError(error.ProbeSnapshotUnavailable, lab.freezeForRecovery());
    try std.testing.expectError(error.TransportRecoveryNotFrozen, lab.planQueueResume());
}

test "phase12 virtio net queue resume summary preserves control and rss rebuild scope" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_hash_report,
        virtio_net.feature_rss,
    });

    _ = try lab.captureProbeSnapshot(.{
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
    _ = try lab.freezeForRecovery();

    const resume_summary = try lab.planQueueResume();
    try std.testing.expect(resume_summary.is_frozen);
    try std.testing.expectEqual(@as(u16, 0), resume_summary.recovery_generation);
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.ready, resume_summary.readiness);
    try std.testing.expectEqual(virtio_net.QueueResumeScope.data_control_and_rss, resume_summary.rebuild_scope);
    try std.testing.expectEqual(@as(u16, 4), resume_summary.resume_queue_pairs);
    try std.testing.expectEqual(@as(u16, 9), resume_summary.resume_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 8), resume_summary.resume_control_queue_index);
    try std.testing.expectEqual(virtio_net.RssSummary.active, resume_summary.remembered_rss_summary);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.clamp_queue_pairs, resume_summary.remembered_queue_recovery_action);
    try std.testing.expect(resume_summary.requires_control_queue_restore);
    try std.testing.expect(resume_summary.requires_rss_reapply);
}

test "phase12 virtio net queue resume summary escalates reset requirements" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
    });

    _ = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
        },
        .requested_queue_pairs = 2,
        .max_queue_pairs = 2,
        .device_signals_reset = true,
    });
    _ = try lab.freezeForRecovery();

    const resume_summary = try lab.planQueueResume();
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.requires_reset, resume_summary.readiness);
    try std.testing.expectEqual(virtio_net.QueueResumeScope.data_and_control_queue, resume_summary.rebuild_scope);
    try std.testing.expectEqual(@as(u16, 2), resume_summary.resume_queue_pairs);
    try std.testing.expectEqual(@as(u16, 5), resume_summary.resume_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 4), resume_summary.resume_control_queue_index);
    try std.testing.expectEqual(virtio_net.RssSummary.not_requested, resume_summary.remembered_rss_summary);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.require_reset, resume_summary.remembered_queue_recovery_action);
    try std.testing.expect(resume_summary.requires_control_queue_restore);
    try std.testing.expect(!resume_summary.requires_rss_reapply);
}

test "phase12 virtio net keeps hash-report-only requests visible" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_control_vq,
        virtio_net.feature_hash_report,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_control_vq,
            virtio_net.feature_hash_report,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });

    try std.testing.expect(!snapshot.has_rss);
    try std.testing.expect(snapshot.has_rss_hash_report);
    try std.testing.expectEqual(virtio_net.HeaderShape.hash_report, snapshot.header_shape);
    try std.testing.expectEqual(@as(u16, 20), snapshot.hdr_len_bytes);
    try std.testing.expect(snapshot.uses_hash_report_header);
    try std.testing.expect(!snapshot.uses_udp_tunnel_header);
    try std.testing.expectEqual(virtio_net.RssSummary.hash_report_only, snapshot.rss_summary);
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.none, snapshot.fallback_reason);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.none, snapshot.queue_recovery_action);
}

test "phase12 virtio net uses mergeable header shape for version1-only negotiation" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_version_1,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_version_1,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });

    try std.testing.expect(!snapshot.mergeable_rx_buffers);
    try std.testing.expectEqual(virtio_net.HeaderShape.mrg_rxbuf, snapshot.header_shape);
    try std.testing.expectEqual(@as(u16, 12), snapshot.hdr_len_bytes);
    try std.testing.expect(!snapshot.uses_hash_report_header);
    try std.testing.expect(!snapshot.uses_udp_tunnel_header);
}

test "phase12 virtio net upgrades hdr_len shape for udp tunnel support" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_control_vq,
        virtio_net.feature_hash_report,
        virtio_net.feature_guest_udp_tunnel_gso,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_control_vq,
            virtio_net.feature_hash_report,
            virtio_net.feature_guest_udp_tunnel_gso,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });

    try std.testing.expectEqual(virtio_net.HeaderShape.hash_report_tunnel, snapshot.header_shape);
    try std.testing.expectEqual(@as(u16, 24), snapshot.hdr_len_bytes);
    try std.testing.expect(snapshot.uses_hash_report_header);
    try std.testing.expect(snapshot.uses_udp_tunnel_header);
}

test "phase12 virtio net preserves legacy header shape without mergeable or hash features" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{});

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{},
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });

    try std.testing.expectEqual(virtio_net.HeaderShape.legacy, snapshot.header_shape);
    try std.testing.expectEqual(@as(u16, 10), snapshot.hdr_len_bytes);
    try std.testing.expect(!snapshot.uses_hash_report_header);
    try std.testing.expect(!snapshot.uses_udp_tunnel_header);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.none, snapshot.queue_recovery_action);
}