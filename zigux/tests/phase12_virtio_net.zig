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
    try std.testing.expectEqual(virtio_net.ReceiveBufferMode.mergeable, snapshot.receive_buffer_mode);
    try std.testing.expectEqual(virtio_net.BigPacketReason.none, snapshot.big_packet_reason);
    try std.testing.expectEqual(
        virtio_net.HeaderScatterPolicy.separate_header_sg,
        snapshot.header_scatter_policy,
    );
    try std.testing.expectEqual(@as(u16, 0), snapshot.required_headroom_bytes);
    try std.testing.expectEqual(virtio_net.XdpConstraint.not_requested, snapshot.xdp_constraint);
    try std.testing.expectEqual(virtio_net.RssSummary.active, snapshot.rss_summary);
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.requested_queue_pairs_clamped,
        snapshot.fallback_reason,
    );
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
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.multiqueue_not_negotiated,
        freeze.remembered_fallback_reason,
    );
    try std.testing.expectEqual(virtio_net.RecoveryState.renegotiate_features, freeze.remembered_recovery_state);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.renegotiate_features, freeze.remembered_queue_recovery_action);
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
    try std.testing.expectEqual(@as(u16, 1), restore.remembered_planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), restore.remembered_total_queue_count);
    try std.testing.expectEqual(@as(?u16, null), restore.remembered_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.multiqueue_not_negotiated,
        restore.remembered_fallback_reason,
    );
    try std.testing.expectEqual(virtio_net.RecoveryState.renegotiate_features, restore.remembered_recovery_state);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.renegotiate_features, restore.remembered_queue_recovery_action);
    try std.testing.expectEqual(@as(u16, 1), restore.recovery_generation);

    try std.testing.expectError(error.ProbeSnapshotUnavailable, lab.freezeForRecovery());
}

test "phase12 virtio net queue resume planning keeps active multiqueue scope visible" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_hash_report,
        virtio_net.feature_rss,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_hash_report,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 3,
        .max_queue_pairs = 3,
    });
    try std.testing.expectEqual(virtio_net.RssSummary.active, snapshot.rss_summary);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.none, snapshot.queue_recovery_action);

    _ = try lab.freezeForRecovery();
    const resume_plan = try lab.planQueueResume();
    try std.testing.expect(resume_plan.is_frozen);
    try std.testing.expectEqual(@as(u16, 0), resume_plan.recovery_generation);
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.ready, resume_plan.readiness);
    try std.testing.expectEqual(virtio_net.QueueResumeScope.data_control_and_rss, resume_plan.rebuild_scope);
    try std.testing.expectEqual(@as(u16, 3), resume_plan.resume_queue_pairs);
    try std.testing.expectEqual(@as(u16, 7), resume_plan.resume_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 6), resume_plan.resume_control_queue_index);
    try std.testing.expectEqual(virtio_net.RssSummary.active, resume_plan.remembered_rss_summary);
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.none, resume_plan.remembered_fallback_reason);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.none, resume_plan.remembered_queue_recovery_action);
    try std.testing.expect(resume_plan.requires_control_queue_restore);
    try std.testing.expect(resume_plan.requires_rss_reapply);
}

test "phase12 virtio net recovery summaries preserve clamp versus single-queue fallback" {
    var clamp_lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_hash_report,
        virtio_net.feature_rss,
    });
    const clamp_snapshot = try clamp_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_hash_report,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 6,
        .max_queue_pairs = 4,
    });
    try std.testing.expectEqual(@as(u16, 4), clamp_snapshot.planned_queue_pairs);
    try std.testing.expectEqual(virtio_net.RssSummary.active, clamp_snapshot.rss_summary);
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.requested_queue_pairs_clamped,
        clamp_snapshot.fallback_reason,
    );
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.clamp_queue_pairs,
        clamp_snapshot.queue_recovery_action,
    );

    _ = try clamp_lab.freezeForRecovery();
    const clamp_resume = try clamp_lab.planQueueResume();
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.ready, clamp_resume.readiness);
    try std.testing.expectEqual(virtio_net.QueueResumeScope.data_control_and_rss, clamp_resume.rebuild_scope);
    try std.testing.expectEqual(@as(u16, 4), clamp_resume.resume_queue_pairs);
    try std.testing.expectEqual(@as(u16, 9), clamp_resume.resume_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 8), clamp_resume.resume_control_queue_index);
    try std.testing.expectEqual(virtio_net.RssSummary.active, clamp_resume.remembered_rss_summary);
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.requested_queue_pairs_clamped,
        clamp_resume.remembered_fallback_reason,
    );
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.clamp_queue_pairs,
        clamp_resume.remembered_queue_recovery_action,
    );
    try std.testing.expect(clamp_resume.requires_control_queue_restore);
    try std.testing.expect(clamp_resume.requires_rss_reapply);

    var single_queue_lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_multiqueue,
        virtio_net.feature_hash_report,
        virtio_net.feature_rss,
    });
    const single_queue_snapshot = try single_queue_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_multiqueue,
            virtio_net.feature_hash_report,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 4,
        .max_queue_pairs = 8,
    });
    try std.testing.expectEqual(@as(u16, 1), single_queue_snapshot.planned_queue_pairs);
    try std.testing.expectEqual(
        virtio_net.RssSummary.downgraded_single_queue,
        single_queue_snapshot.rss_summary,
    );
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.degrade_to_single_queue,
        single_queue_snapshot.queue_recovery_action,
    );

    _ = try single_queue_lab.freezeForRecovery();
    const single_queue_resume = try single_queue_lab.planQueueResume();
    try std.testing.expectEqual(
        virtio_net.QueueResumeReadiness.ready,
        single_queue_resume.readiness,
    );
    try std.testing.expectEqual(
        virtio_net.QueueResumeScope.data_queues_only,
        single_queue_resume.rebuild_scope,
    );
    try std.testing.expectEqual(@as(u16, 1), single_queue_resume.resume_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), single_queue_resume.resume_total_queue_count);
    try std.testing.expectEqual(@as(?u16, null), single_queue_resume.resume_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.RssSummary.downgraded_single_queue,
        single_queue_resume.remembered_rss_summary,
    );
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.missing_control_vq,
        single_queue_resume.remembered_fallback_reason,
    );
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.degrade_to_single_queue,
        single_queue_resume.remembered_queue_recovery_action,
    );
    try std.testing.expect(!single_queue_resume.requires_control_queue_restore);
    try std.testing.expect(!single_queue_resume.requires_rss_reapply);
}

test "phase12 virtio net queue resume planning distinguishes renegotiation from reset" {
    var renegotiate_lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_rss,
    });
    _ = try renegotiate_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 2,
        .max_queue_pairs = 4,
        .transport_accepts_features = false,
    });
    _ = try renegotiate_lab.freezeForRecovery();
    const renegotiate_resume = try renegotiate_lab.planQueueResume();
    try std.testing.expectEqual(
        virtio_net.QueueResumeReadiness.requires_feature_renegotiation,
        renegotiate_resume.readiness,
    );
    try std.testing.expectEqual(virtio_net.QueueResumeScope.data_queues_only, renegotiate_resume.rebuild_scope);
    try std.testing.expectEqual(@as(u16, 1), renegotiate_resume.resume_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), renegotiate_resume.resume_total_queue_count);
    try std.testing.expectEqual(@as(?u16, null), renegotiate_resume.resume_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.multiqueue_not_negotiated,
        renegotiate_resume.remembered_fallback_reason,
    );
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.renegotiate_features,
        renegotiate_resume.remembered_queue_recovery_action,
    );
    try std.testing.expect(!renegotiate_resume.requires_control_queue_restore);
    try std.testing.expect(!renegotiate_resume.requires_rss_reapply);

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
    try std.testing.expectEqual(virtio_net.RssSummary.not_requested, reset_resume.remembered_rss_summary);
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.none, reset_resume.remembered_fallback_reason);
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.require_reset,
        reset_resume.remembered_queue_recovery_action,
    );
    try std.testing.expect(reset_resume.requires_control_queue_restore);
    try std.testing.expect(!reset_resume.requires_rss_reapply);
}

test "phase12 virtio net queue resume planning marks stale probe snapshots for refill recheck" {
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
        .mtu = 9_000,
    });

    _ = try lab.freezeForRecovery();
    const resume_plan = try lab.planQueueResume();
    try std.testing.expect(resume_plan.requires_fresh_probe_snapshot);
    try std.testing.expect(resume_plan.requires_control_queue_restore);
    try std.testing.expect(resume_plan.requires_rss_reapply);
    try std.testing.expectEqual(virtio_net.QueueResumeScope.data_control_and_rss, resume_plan.rebuild_scope);
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

test "phase12 virtio net upgrades hdr_len shape for host udp tunnel support" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_control_vq,
        virtio_net.feature_hash_report,
        virtio_net.feature_host_udp_tunnel_gso,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_control_vq,
            virtio_net.feature_hash_report,
            virtio_net.feature_host_udp_tunnel_gso,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });

    try std.testing.expectEqual(virtio_net.HeaderShape.hash_report_tunnel, snapshot.header_shape);
    try std.testing.expectEqual(@as(u16, 24), snapshot.hdr_len_bytes);
    try std.testing.expect(snapshot.uses_hash_report_header);
    try std.testing.expect(snapshot.uses_udp_tunnel_header);
}

test "phase12 virtio net blocks mergeable xdp when split headers stay required" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
        .xdp_requested = true,
    });

    try std.testing.expectEqual(virtio_net.ReceiveBufferMode.mergeable, snapshot.receive_buffer_mode);
    try std.testing.expectEqual(virtio_net.BigPacketReason.none, snapshot.big_packet_reason);
    try std.testing.expectEqual(
        virtio_net.HeaderScatterPolicy.separate_header_sg,
        snapshot.header_scatter_policy,
    );
    try std.testing.expectEqual(@as(u16, 0), snapshot.required_headroom_bytes);
    try std.testing.expectEqual(
        virtio_net.XdpConstraint.blocked_by_split_header,
        snapshot.xdp_constraint,
    );
}

test "phase12 virtio net readies mergeable xdp when combined header scatter is available" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_version_1,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_version_1,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
        .xdp_requested = true,
    });

    try std.testing.expectEqual(virtio_net.ReceiveBufferMode.mergeable, snapshot.receive_buffer_mode);
    try std.testing.expectEqual(
        virtio_net.HeaderScatterPolicy.combined_header_and_data,
        snapshot.header_scatter_policy,
    );
    try std.testing.expectEqual(@as(u16, 12), snapshot.required_headroom_bytes);
    try std.testing.expectEqual(virtio_net.XdpConstraint.ready, snapshot.xdp_constraint);
}

test "phase12 virtio net flags big-packet receive planning for guest gso throughput" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_guest_tso4,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_guest_tso4,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
        .mtu = virtio_net.ethernet_default_mtu,
        .xdp_requested = true,
    });

    try std.testing.expectEqual(virtio_net.ReceiveBufferMode.big_packets, snapshot.receive_buffer_mode);
    try std.testing.expectEqual(virtio_net.BigPacketReason.guest_gso, snapshot.big_packet_reason);
    try std.testing.expectEqual(
        virtio_net.HeaderScatterPolicy.separate_header_sg,
        snapshot.header_scatter_policy,
    );
    try std.testing.expectEqual(
        virtio_net.XdpConstraint.blocked_by_big_packets,
        snapshot.xdp_constraint,
    );
}

test "phase12 virtio net treats either guest uso feature as guest gso pressure" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_guest_uso4,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_guest_uso4,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
        .mtu = virtio_net.ethernet_default_mtu,
        .xdp_requested = true,
    });

    try std.testing.expectEqual(virtio_net.ReceiveBufferMode.big_packets, snapshot.receive_buffer_mode);
    try std.testing.expectEqual(virtio_net.BigPacketReason.guest_gso, snapshot.big_packet_reason);
    try std.testing.expectEqual(
        virtio_net.HeaderScatterPolicy.separate_header_sg,
        snapshot.header_scatter_policy,
    );
    try std.testing.expectEqual(
        virtio_net.XdpConstraint.blocked_by_big_packets,
        snapshot.xdp_constraint,
    );
}

test "phase12 virtio net mergeable refill treats guest uso as big-packet pressure" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_guest_uso4,
    });

    const snapshot = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_guest_uso4,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });

    try std.testing.expectEqual(virtio_net.ReceiveBufferMode.mergeable, snapshot.receive_buffer_mode);
    try std.testing.expectEqual(virtio_net.BigPacketReason.guest_gso, snapshot.big_packet_reason);

    const refill = try lab.planMergeableReceiveRefill(4);
    try std.testing.expectEqual(@as(u16, 4), refill.rx_queue_entries);
    try std.testing.expectEqual(virtio_net.ReceiveQueueRefillPath.fresh_allocation, refill.refill_path);
    try std.testing.expect(refill.uses_mergeable_buffers);
    try std.testing.expectEqual(@as(u32, 65565), refill.packet_budget_bytes);
    try std.testing.expectEqual(@as(u32, 16380), refill.min_buf_len_bytes);
    try std.testing.expectEqual(virtio_net.BigPacketReason.guest_gso, refill.big_packet_reason);
}

test "phase12 virtio net plans mergeable refill budgets from mtu and header state" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_hash_report,
        virtio_net.feature_version_1,
    });

    _ = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_hash_report,
            virtio_net.feature_version_1,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
        .mtu = 9_000,
    });

    const refill = try lab.planMergeableReceiveRefill(4);
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", refill.anchor);
    try std.testing.expectEqual(@as(u16, 4), refill.rx_queue_entries);
    try std.testing.expectEqual(virtio_net.ReceiveQueueRefillPath.recycled_room_reuse, refill.refill_path);
    try std.testing.expect(refill.uses_mergeable_buffers);
    try std.testing.expectEqual(@as(u32, 9_038), refill.packet_budget_bytes);
    try std.testing.expectEqual(@as(u32, 2_240), refill.min_buf_len_bytes);
    try std.testing.expectEqual(@as(u16, 20), refill.required_headroom_bytes);
    try std.testing.expectEqual(@as(u32, 20), refill.recycled_room_bytes);
    try std.testing.expectEqual(@as(u32, 2_220), refill.fresh_allocation_bytes);
    try std.testing.expectEqual(virtio_net.BigPacketReason.mtu_above_default, refill.big_packet_reason);
}

test "phase12 virtio net rejects refill planning without queue entries" {
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

    try std.testing.expectError(error.InvalidRxQueueEntries, lab.planMergeableReceiveRefill(0));
}

test "phase12 virtio net restore clears stale refill planning state" {
    var lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
    });

    _ = try lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });

    const refill = try lab.planMergeableReceiveRefill(4);
    try std.testing.expectEqual(virtio_net.ReceiveQueueRefillPath.fresh_allocation, refill.refill_path);
    try std.testing.expectEqual(@as(u32, 0), refill.recycled_room_bytes);
    try std.testing.expectEqual(@as(u32, 1_518), refill.fresh_allocation_bytes);
    _ = try lab.freezeForRecovery();
    _ = try lab.restoreAfterRecovery();

    try std.testing.expectError(error.ProbeSnapshotUnavailable, lab.planMergeableReceiveRefill(4));
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
