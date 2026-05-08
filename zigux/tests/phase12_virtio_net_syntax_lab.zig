const std = @import("std");

const virtio_net = @import("virtio_net");

test "phase12 virtio net syntax lab keeps bounded probe exports reachable" {
    const descriptor = virtio_net.VirtioNetProbeLab.descriptor();

    _ = virtio_net.ModuleDescriptor;
    _ = virtio_net.RecoveryAction;
    _ = virtio_net.QueueFallbackReason;
    _ = virtio_net.RecoveryState;
    _ = virtio_net.RssRecoveryState;
    _ = virtio_net.QueueRecoveryAction;
    _ = virtio_net.ProbeRequest;
    _ = virtio_net.ProbeSnapshot;
    _ = virtio_net.QueueRecoverySummary;
    _ = virtio_net.QueueResumeReadiness;
    _ = virtio_net.QueueResumeScope;
    _ = virtio_net.QueueResumeSummary;
    _ = virtio_net.RecoveryOwnershipStage;
    _ = virtio_net.RecoveryOwnershipSummary;
    _ = virtio_net.ReceiveBufferMode;
    _ = virtio_net.ReceiveRefillSummary;
    _ = virtio_net.ControlQueueRestoreDisposition;
    _ = virtio_net.ControlQueueRestoreSummary;
    _ = virtio_net.MergeableBufferLengthSource;
    _ = virtio_net.MergeableBufferLengthRequest;
    _ = virtio_net.MergeableBufferLengthSummary;
    _ = virtio_net.TransmitRecycleOrder;
    _ = virtio_net.TransmitRecycleSummary;

    try std.testing.expectEqualStrings("virtio_net_probe_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_probe_queue_snapshot);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_napi_poll);
    try std.testing.expect(!descriptor.touches_netdev_lifecycle);
    try std.testing.expect(descriptor.touches_transport_recovery);
}

test "phase12 virtio net syntax lab keeps current follow-up enums stable" {
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.clamp_queue_pairs,
        virtio_net.QueueRecoveryAction.clamp_queue_pairs,
    );
    try std.testing.expectEqual(virtio_net.RecoveryState.stable, virtio_net.RecoveryState.stable);
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.invalid_max_queue_pairs,
        virtio_net.QueueFallbackReason.invalid_max_queue_pairs,
    );
    try std.testing.expectEqual(
        virtio_net.RssRecoveryState.downgraded_single_queue,
        virtio_net.RssRecoveryState.downgraded_single_queue,
    );
    try std.testing.expectEqual(
        virtio_net.QueueResumeReadiness.ready,
        virtio_net.QueueResumeReadiness.ready,
    );
    try std.testing.expectEqual(
        virtio_net.QueueResumeScope.data_control_and_rss,
        virtio_net.QueueResumeScope.data_control_and_rss,
    );
    try std.testing.expectEqual(
        virtio_net.RecoveryOwnershipStage.control_queue_restore,
        virtio_net.RecoveryOwnershipStage.control_queue_restore,
    );
    try std.testing.expectEqual(
        virtio_net.ReceiveBufferMode.mergeable_rx_buffers,
        virtio_net.ReceiveBufferMode.mergeable_rx_buffers,
    );
    try std.testing.expectEqual(
        virtio_net.ControlQueueRestoreDisposition.restore_before_rss_reapply,
        virtio_net.ControlQueueRestoreDisposition.restore_before_rss_reapply,
    );
    try std.testing.expectEqual(
        virtio_net.MergeableBufferLengthSource.minimum_buffer_floor,
        virtio_net.MergeableBufferLengthSource.minimum_buffer_floor,
    );
    try std.testing.expectEqual(
        virtio_net.TransmitRecycleOrder.after_control_queue_restore_and_rss_reapply,
        virtio_net.TransmitRecycleOrder.after_control_queue_restore_and_rss_reapply,
    );
}

test "phase12 virtio net syntax lab keeps remaining recovery transitions reachable" {
    try std.testing.expectEqual(
        virtio_net.RecoveryState.renegotiate_features,
        virtio_net.RecoveryState.renegotiate_features,
    );
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.none,
        virtio_net.QueueRecoveryAction.none,
    );
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.degrade_to_single_queue,
        virtio_net.QueueRecoveryAction.degrade_to_single_queue,
    );
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.renegotiate_features,
        virtio_net.QueueRecoveryAction.renegotiate_features,
    );
    try std.testing.expectEqual(
        virtio_net.QueueResumeReadiness.requires_reset,
        virtio_net.QueueResumeReadiness.requires_reset,
    );
}

test "phase12 virtio net syntax lab keeps alternate recovery and throughput variants reachable" {
    try std.testing.expectEqual(
        virtio_net.RecoveryState.reset_required,
        virtio_net.RecoveryState.reset_required,
    );
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.require_reset,
        virtio_net.QueueRecoveryAction.require_reset,
    );
    try std.testing.expectEqual(
        virtio_net.QueueResumeReadiness.requires_feature_renegotiation,
        virtio_net.QueueResumeReadiness.requires_feature_renegotiation,
    );
    try std.testing.expectEqual(
        virtio_net.QueueResumeScope.data_and_control_queue,
        virtio_net.QueueResumeScope.data_and_control_queue,
    );
    try std.testing.expectEqual(
        virtio_net.RecoveryOwnershipStage.post_restore_probe_replay,
        virtio_net.RecoveryOwnershipStage.post_restore_probe_replay,
    );
    try std.testing.expectEqual(
        virtio_net.ReceiveBufferMode.one_buffer_per_rx,
        virtio_net.ReceiveBufferMode.one_buffer_per_rx,
    );
    try std.testing.expectEqual(
        virtio_net.ControlQueueRestoreDisposition.restore_after_data_queue_restore,
        virtio_net.ControlQueueRestoreDisposition.restore_after_data_queue_restore,
    );
    try std.testing.expectEqual(
        virtio_net.MergeableBufferLengthSource.page_size_cap,
        virtio_net.MergeableBufferLengthSource.page_size_cap,
    );
    try std.testing.expectEqual(
        virtio_net.MergeableBufferLengthSource.page_minus_room,
        virtio_net.MergeableBufferLengthSource.page_minus_room,
    );
    try std.testing.expectEqual(
        virtio_net.TransmitRecycleOrder.after_control_queue_restore,
        virtio_net.TransmitRecycleOrder.after_control_queue_restore,
    );
}

test "phase12 virtio net syntax lab keeps base recovery and smoke variants reachable" {
    try std.testing.expectEqual(virtio_net.RecoveryAction.freeze, virtio_net.RecoveryAction.freeze);
    try std.testing.expectEqual(virtio_net.RecoveryAction.restore, virtio_net.RecoveryAction.restore);
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.none,
        virtio_net.QueueFallbackReason.none,
    );
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.multiqueue_not_negotiated,
        virtio_net.QueueFallbackReason.multiqueue_not_negotiated,
    );
    try std.testing.expectEqual(
        virtio_net.QueueFallbackReason.missing_control_vq,
        virtio_net.QueueFallbackReason.missing_control_vq,
    );
    try std.testing.expectEqual(
        virtio_net.RssRecoveryState.not_requested,
        virtio_net.RssRecoveryState.not_requested,
    );
    try std.testing.expectEqual(
        virtio_net.RssRecoveryState.requested_but_unavailable,
        virtio_net.RssRecoveryState.requested_but_unavailable,
    );
    try std.testing.expectEqual(
        virtio_net.RssRecoveryState.active,
        virtio_net.RssRecoveryState.active,
    );
    try std.testing.expectEqual(
        virtio_net.QueueResumeScope.data_queues_only,
        virtio_net.QueueResumeScope.data_queues_only,
    );
    try std.testing.expectEqual(
        virtio_net.RecoveryOwnershipStage.frozen_snapshot,
        virtio_net.RecoveryOwnershipStage.frozen_snapshot,
    );
    try std.testing.expectEqual(
        virtio_net.ControlQueueRestoreDisposition.not_required,
        virtio_net.ControlQueueRestoreDisposition.not_required,
    );
    try std.testing.expectEqual(
        virtio_net.MergeableBufferLengthSource.observed_average_packet,
        virtio_net.MergeableBufferLengthSource.observed_average_packet,
    );
    try std.testing.expectEqual(
        virtio_net.TransmitRecycleOrder.data_queues_only,
        virtio_net.TransmitRecycleOrder.data_queues_only,
    );
}

test "phase12 virtio net syntax lab keeps control queue restore planning reachable" {
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
    const active_restore = try active_lab.planControlQueueRestore();
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.ready, active_restore.readiness);
    try std.testing.expectEqual(
        virtio_net.ControlQueueRestoreDisposition.restore_before_rss_reapply,
        active_restore.restore_disposition,
    );
    try std.testing.expectEqual(@as(u16, 3), active_restore.restore_queue_pairs);
    try std.testing.expectEqual(@as(u16, 7), active_restore.restore_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 6), active_restore.restore_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.none,
        active_restore.remembered_queue_recovery_action,
    );
    try std.testing.expectEqual(
        virtio_net.RssRecoveryState.active,
        active_restore.remembered_rss_recovery_state,
    );
    try std.testing.expect(active_restore.requires_rss_reapply);
    try std.testing.expect(active_restore.requires_fresh_probe_snapshot);
    try std.testing.expect(active_restore.requires_post_restore_probe_replay);

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
    const reset_restore = try reset_lab.planControlQueueRestore();
    try std.testing.expectEqual(
        virtio_net.QueueResumeReadiness.requires_reset,
        reset_restore.readiness,
    );
    try std.testing.expectEqual(
        virtio_net.ControlQueueRestoreDisposition.restore_after_data_queue_restore,
        reset_restore.restore_disposition,
    );
    try std.testing.expectEqual(@as(u16, 2), reset_restore.restore_queue_pairs);
    try std.testing.expectEqual(@as(u16, 5), reset_restore.restore_total_queue_count);
    try std.testing.expectEqual(@as(?u16, 4), reset_restore.restore_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.require_reset,
        reset_restore.remembered_queue_recovery_action,
    );
    try std.testing.expectEqual(
        virtio_net.RssRecoveryState.not_requested,
        reset_restore.remembered_rss_recovery_state,
    );
    try std.testing.expect(!reset_restore.requires_rss_reapply);
    try std.testing.expect(reset_restore.requires_fresh_probe_snapshot);
    try std.testing.expect(reset_restore.requires_post_restore_probe_replay);

    var data_only_lab = try virtio_net.VirtioNetProbeLab.init(&.{});
    _ = try data_only_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{},
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });
    _ = try data_only_lab.freezeForRecovery();
    const data_only_restore = try data_only_lab.planControlQueueRestore();
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.ready, data_only_restore.readiness);
    try std.testing.expectEqual(
        virtio_net.ControlQueueRestoreDisposition.not_required,
        data_only_restore.restore_disposition,
    );
    try std.testing.expectEqual(@as(u16, 1), data_only_restore.restore_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), data_only_restore.restore_total_queue_count);
    try std.testing.expectEqual(@as(?u16, null), data_only_restore.restore_control_queue_index);
    try std.testing.expectEqual(
        virtio_net.QueueRecoveryAction.none,
        data_only_restore.remembered_queue_recovery_action,
    );
    try std.testing.expectEqual(
        virtio_net.RssRecoveryState.not_requested,
        data_only_restore.remembered_rss_recovery_state,
    );
    try std.testing.expect(!data_only_restore.requires_rss_reapply);
    try std.testing.expect(data_only_restore.requires_fresh_probe_snapshot);
    try std.testing.expect(data_only_restore.requires_post_restore_probe_replay);
}

test "phase12 virtio net syntax lab keeps recovery ownership planning reachable" {
    var active_lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_rss,
    });
    _ = try active_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 3,
        .max_queue_pairs = 3,
    });
    _ = try active_lab.freezeForRecovery();
    const active_ownership = try active_lab.planRecoveryOwnership();
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.ready, active_ownership.readiness);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.none, active_ownership.queue_recovery_action);
    try std.testing.expectEqual(
        virtio_net.RecoveryOwnershipStage.frozen_snapshot,
        active_ownership.queue_shape_owner,
    );
    try std.testing.expectEqual(
        virtio_net.RecoveryOwnershipStage.data_queue_resume,
        active_ownership.data_queue_owner,
    );
    try std.testing.expectEqual(
        @as(?virtio_net.RecoveryOwnershipStage, .control_queue_restore),
        active_ownership.control_queue_owner,
    );
    try std.testing.expectEqual(
        @as(?virtio_net.RecoveryOwnershipStage, .rss_reapply),
        active_ownership.rss_owner,
    );
    try std.testing.expectEqual(
        virtio_net.RecoveryOwnershipStage.receive_refill,
        active_ownership.receive_refill_owner,
    );
    try std.testing.expectEqual(
        virtio_net.RecoveryOwnershipStage.transmit_recycle,
        active_ownership.transmit_recycle_owner,
    );
    try std.testing.expectEqual(
        virtio_net.RecoveryOwnershipStage.post_restore_probe_replay,
        active_ownership.steady_state_owner,
    );
    try std.testing.expectEqual(@as(u16, 3), active_ownership.planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 7), active_ownership.total_queue_count);
    try std.testing.expectEqual(@as(?u16, 6), active_ownership.control_queue_index);
    try std.testing.expect(active_ownership.requires_mergeable_buffer_headroom);
    try std.testing.expect(active_ownership.requires_control_queue_restore);
    try std.testing.expect(active_ownership.requires_rss_reapply);
    try std.testing.expect(active_ownership.requires_fresh_probe_snapshot);
    try std.testing.expect(active_ownership.requires_post_restore_probe_replay);

    var data_only_lab = try virtio_net.VirtioNetProbeLab.init(&.{});
    _ = try data_only_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{},
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });
    _ = try data_only_lab.freezeForRecovery();
    const data_only_ownership = try data_only_lab.planRecoveryOwnership();
    try std.testing.expectEqual(virtio_net.QueueResumeReadiness.ready, data_only_ownership.readiness);
    try std.testing.expectEqual(virtio_net.QueueRecoveryAction.none, data_only_ownership.queue_recovery_action);
    try std.testing.expectEqual(
        virtio_net.RecoveryOwnershipStage.frozen_snapshot,
        data_only_ownership.queue_shape_owner,
    );
    try std.testing.expectEqual(
        virtio_net.RecoveryOwnershipStage.data_queue_resume,
        data_only_ownership.data_queue_owner,
    );
    try std.testing.expectEqual(
        @as(?virtio_net.RecoveryOwnershipStage, null),
        data_only_ownership.control_queue_owner,
    );
    try std.testing.expectEqual(
        @as(?virtio_net.RecoveryOwnershipStage, null),
        data_only_ownership.rss_owner,
    );
    try std.testing.expectEqual(
        virtio_net.RecoveryOwnershipStage.receive_refill,
        data_only_ownership.receive_refill_owner,
    );
    try std.testing.expectEqual(
        virtio_net.RecoveryOwnershipStage.transmit_recycle,
        data_only_ownership.transmit_recycle_owner,
    );
    try std.testing.expectEqual(
        virtio_net.RecoveryOwnershipStage.post_restore_probe_replay,
        data_only_ownership.steady_state_owner,
    );
    try std.testing.expectEqual(@as(u16, 1), data_only_ownership.planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), data_only_ownership.total_queue_count);
    try std.testing.expectEqual(@as(?u16, null), data_only_ownership.control_queue_index);
    try std.testing.expect(!data_only_ownership.requires_mergeable_buffer_headroom);
    try std.testing.expect(!data_only_ownership.requires_control_queue_restore);
    try std.testing.expect(!data_only_ownership.requires_rss_reapply);
    try std.testing.expect(data_only_ownership.requires_fresh_probe_snapshot);
    try std.testing.expect(data_only_ownership.requires_post_restore_probe_replay);
}

test "phase12 virtio net syntax lab keeps mergeable buffer length planning reachable" {
    var mergeable_lab = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_hash_report,
    });
    _ = try mergeable_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_hash_report,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });
    _ = try mergeable_lab.freezeForRecovery();

    const observed_average = try mergeable_lab.planMergeableBufferLength(.{
        .observed_average_packet_len_bytes = 1800,
        .min_buf_len_bytes = 1024,
    });
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", observed_average.anchor);
    try std.testing.expectEqual(
        virtio_net.MergeableBufferLengthSource.observed_average_packet,
        observed_average.source,
    );
    try std.testing.expectEqual(@as(u16, 1800), observed_average.observed_average_packet_len_bytes);
    try std.testing.expectEqual(@as(u16, 1024), observed_average.min_buf_len_bytes);
    try std.testing.expectEqual(@as(u16, 0), observed_average.xdp_headroom_bytes);
    try std.testing.expectEqual(@as(u16, 0), observed_average.tailroom_bytes);
    try std.testing.expectEqual(@as(u16, 0), observed_average.room_bytes);
    try std.testing.expectEqual(@as(u16, 4076), observed_average.payload_limit_bytes);
    try std.testing.expectEqual(@as(u16, 1800), observed_average.selected_payload_bytes);
    try std.testing.expectEqual(@as(u16, 20), observed_average.hdr_len_bytes);
    try std.testing.expectEqual(@as(u16, 1856), observed_average.submit_len_bytes);
    try std.testing.expectEqual(@as(u16, 1856), observed_average.allocation_len_bytes);

    const minimum_floor = try mergeable_lab.planMergeableBufferLength(.{
        .observed_average_packet_len_bytes = 512,
        .min_buf_len_bytes = 1024,
    });
    try std.testing.expectEqual(
        virtio_net.MergeableBufferLengthSource.minimum_buffer_floor,
        minimum_floor.source,
    );
    try std.testing.expectEqual(@as(u16, 1024), minimum_floor.selected_payload_bytes);
    try std.testing.expectEqual(@as(u16, 1088), minimum_floor.submit_len_bytes);
    try std.testing.expectEqual(@as(u16, 1088), minimum_floor.allocation_len_bytes);

    const page_size_cap = try mergeable_lab.planMergeableBufferLength(.{
        .observed_average_packet_len_bytes = 5000,
        .min_buf_len_bytes = 512,
    });
    try std.testing.expectEqual(
        virtio_net.MergeableBufferLengthSource.page_size_cap,
        page_size_cap.source,
    );
    try std.testing.expectEqual(@as(u16, 4076), page_size_cap.selected_payload_bytes);
    try std.testing.expectEqual(@as(u16, 4096), page_size_cap.submit_len_bytes);
    try std.testing.expectEqual(@as(u16, 4096), page_size_cap.allocation_len_bytes);

    const page_minus_room = try mergeable_lab.planMergeableBufferLength(.{
        .observed_average_packet_len_bytes = 1800,
        .min_buf_len_bytes = 1024,
        .xdp_headroom_bytes = 192,
    });
    try std.testing.expectEqual(
        virtio_net.MergeableBufferLengthSource.page_minus_room,
        page_minus_room.source,
    );
    try std.testing.expectEqual(@as(u16, 192), page_minus_room.xdp_headroom_bytes);
    try std.testing.expectEqual(@as(u16, 320), page_minus_room.tailroom_bytes);
    try std.testing.expectEqual(@as(u16, 512), page_minus_room.room_bytes);
    try std.testing.expectEqual(@as(u16, 4076), page_minus_room.payload_limit_bytes);
    try std.testing.expectEqual(@as(u16, 3564), page_minus_room.selected_payload_bytes);
    try std.testing.expectEqual(@as(u16, 20), page_minus_room.hdr_len_bytes);
    try std.testing.expectEqual(@as(u16, 3584), page_minus_room.submit_len_bytes);
    try std.testing.expectEqual(@as(u16, 4096), page_minus_room.allocation_len_bytes);

    var one_buffer_lab = try virtio_net.VirtioNetProbeLab.init(&.{});
    _ = try one_buffer_lab.captureProbeSnapshot(.{
        .driver_feature_bits = &.{},
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });
    _ = try one_buffer_lab.freezeForRecovery();
    try std.testing.expectError(
        error.ReceiveBufferModeNotMergeable,
        one_buffer_lab.planMergeableBufferLength(.{
            .observed_average_packet_len_bytes = 512,
            .min_buf_len_bytes = 256,
        }),
    );
}
