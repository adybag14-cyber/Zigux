const std = @import("std");
const virtio_net = @import("virtio_net");

test "phase10 virtio net descriptor and probe snapshot stay on the bounded queue-planning surface" {
    const descriptor = virtio_net.VirtioNetProbeLab.descriptor();
    try std.testing.expectEqualStrings("virtio_net_probe_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_probe_queue_snapshot);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_napi_poll);
    try std.testing.expect(!descriptor.touches_netdev_lifecycle);
    try std.testing.expect(!descriptor.touches_transport_recovery);

    var device = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
        virtio_net.feature_rss,
    });

    const snapshot = try device.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
            virtio_net.feature_rss,
        },
        .requested_queue_pairs = 2,
        .max_queue_pairs = 4,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", snapshot.anchor);
    try std.testing.expectEqual(@as(u16, 2), snapshot.requested_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), snapshot.planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), snapshot.rx_queue_count);
    try std.testing.expectEqual(@as(u16, 2), snapshot.tx_queue_count);
    try std.testing.expectEqual(@as(u16, 5), snapshot.total_queue_count);
    try std.testing.expectEqual(@as(?u16, 4), snapshot.control_queue_index);
    try std.testing.expect(snapshot.mergeable_rx_buffers);
    try std.testing.expect(snapshot.has_rss);
    try std.testing.expectEqual(virtio_net.QueueFallbackReason.none, snapshot.fallback_reason);
    try std.testing.expectEqual(virtio_net.RecoveryState.stable, snapshot.recovery_state);
}

test "phase10 virtio net plans mergeable receive buffers with aligned room and page-pool intent" {
    var device = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
    });

    const snapshot = try device.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
        },
        .requested_queue_pairs = 2,
        .max_queue_pairs = 2,
    });

    const plan = try device.planMergeableReceiveBuffer(snapshot, .{
        .header_len = 12,
        .average_packet_len = 1500,
        .min_buf_len = 512,
        .headroom = 256,
        .cache_line_size = 64,
        .skb_shared_info_size = 320,
    });

    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", plan.anchor);
    try std.testing.expectEqual(@as(u16, 2), plan.planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), plan.rx_queue_count);
    try std.testing.expectEqual(@as(u32, 256), plan.headroom);
    try std.testing.expectEqual(@as(u32, 320), plan.tailroom);
    try std.testing.expectEqual(@as(u32, 576), plan.room);
    try std.testing.expectEqual(@as(u32, 1536), plan.requested_len);
    try std.testing.expectEqual(@as(u32, 2112), plan.requested_alloc_len);
    try std.testing.expectEqual(@as(u32, virtio_net.default_page_size), plan.page_size);
    try std.testing.expect(!plan.uses_recycled_room);
    try std.testing.expect(plan.uses_page_pool);
}

test "phase10 virtio net reuses prior room when planning the next mergeable receive buffer" {
    var device = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
    });

    const snapshot = try device.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });

    const plan = try device.planMergeableReceiveBuffer(snapshot, .{
        .header_len = 12,
        .average_packet_len = 900,
        .min_buf_len = 256,
        .recycled_room = 896,
    });

    try std.testing.expectEqual(@as(u32, 0), plan.room);
    try std.testing.expectEqual(@as(u32, 3200), plan.requested_len);
    try std.testing.expectEqual(@as(u32, 3200), plan.requested_alloc_len);
    try std.testing.expect(plan.uses_recycled_room);
}

test "phase10 virtio net summarizes whether refill stays on mergeable allocation or recycled-room paths" {
    var fresh_device = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
    });
    const fresh_snapshot = try fresh_device.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
        },
        .requested_queue_pairs = 2,
        .max_queue_pairs = 2,
    });
    _ = try fresh_device.planMergeableReceiveBuffer(fresh_snapshot, .{
        .header_len = 12,
        .average_packet_len = 1500,
        .min_buf_len = 512,
        .headroom = 256,
        .cache_line_size = 64,
        .skb_shared_info_size = 320,
    });

    const fresh_summary = try fresh_device.summarizeReceiveQueueRefill();
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", fresh_summary.anchor);
    try std.testing.expectEqual(@as(u16, 2), fresh_summary.planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), fresh_summary.rx_queue_count);
    try std.testing.expectEqual(virtio_net.ReceiveQueueRefillPath.mergeable_allocation, fresh_summary.refill_path);
    try std.testing.expect(fresh_summary.keeps_aligned_room);
    try std.testing.expectEqual(@as(u32, 576), fresh_summary.room);
    try std.testing.expectEqual(@as(u32, 0), fresh_summary.recycled_room);
    try std.testing.expectEqual(@as(u32, 1536), fresh_summary.requested_len);
    try std.testing.expectEqual(@as(u32, 2112), fresh_summary.requested_alloc_len);

    var recycled_device = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
    });
    const recycled_snapshot = try recycled_device.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });
    _ = try recycled_device.planMergeableReceiveBuffer(recycled_snapshot, .{
        .header_len = 12,
        .average_packet_len = 900,
        .min_buf_len = 256,
        .recycled_room = 896,
    });

    const recycled_summary = try recycled_device.summarizeReceiveQueueRefill();
    try std.testing.expectEqual(virtio_net.ReceiveQueueRefillPath.recycled_room, recycled_summary.refill_path);
    try std.testing.expect(!recycled_summary.keeps_aligned_room);
    try std.testing.expectEqual(@as(u32, 0), recycled_summary.room);
    try std.testing.expectEqual(@as(u32, 896), recycled_summary.recycled_room);
    try std.testing.expectEqual(@as(u32, 3200), recycled_summary.requested_len);
    try std.testing.expectEqual(@as(u32, 3200), recycled_summary.requested_alloc_len);
}

test "phase10 virtio net plans bounded receive queue refill batches from the last mergeable plan" {
    var fresh_device = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
    });
    const fresh_snapshot = try fresh_device.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
        },
        .requested_queue_pairs = 2,
        .max_queue_pairs = 2,
    });
    _ = try fresh_device.planMergeableReceiveBuffer(fresh_snapshot, .{
        .header_len = 12,
        .average_packet_len = 1500,
        .min_buf_len = 512,
        .headroom = 256,
        .cache_line_size = 64,
        .skb_shared_info_size = 320,
    });

    const fresh_batch = try fresh_device.planReceiveQueueRefillBatch(.{
        .queue_capacity = 256,
        .buffers_posted = 192,
        .batch_limit = 32,
    });
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", fresh_batch.anchor);
    try std.testing.expectEqual(@as(u16, 2), fresh_batch.planned_queue_pairs);
    try std.testing.expectEqual(@as(u16, 2), fresh_batch.rx_queue_count);
    try std.testing.expectEqual(@as(u16, 256), fresh_batch.queue_capacity);
    try std.testing.expectEqual(@as(u16, 192), fresh_batch.buffers_posted);
    try std.testing.expectEqual(@as(u16, 64), fresh_batch.missing_buffers);
    try std.testing.expectEqual(@as(u16, 32), fresh_batch.refill_count);
    try std.testing.expectEqual(@as(u16, 224), fresh_batch.buffers_after_refill);
    try std.testing.expect(!fresh_batch.queue_will_be_full);
    try std.testing.expectEqual(virtio_net.ReceiveQueueRefillPath.mergeable_allocation, fresh_batch.refill_path);
    try std.testing.expectEqual(@as(u32, 49152), fresh_batch.total_posted_bytes);
    try std.testing.expectEqual(@as(u32, 67584), fresh_batch.total_allocation_bytes);

    var recycled_device = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
    });
    const recycled_snapshot = try recycled_device.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });
    _ = try recycled_device.planMergeableReceiveBuffer(recycled_snapshot, .{
        .header_len = 12,
        .average_packet_len = 900,
        .min_buf_len = 256,
        .recycled_room = 896,
    });

    const recycled_batch = try recycled_device.planReceiveQueueRefillBatch(.{
        .queue_capacity = 128,
        .buffers_posted = 120,
    });
    try std.testing.expectEqual(@as(u16, 8), recycled_batch.missing_buffers);
    try std.testing.expectEqual(@as(u16, 8), recycled_batch.refill_count);
    try std.testing.expectEqual(@as(u16, 128), recycled_batch.buffers_after_refill);
    try std.testing.expect(recycled_batch.queue_will_be_full);
    try std.testing.expectEqual(virtio_net.ReceiveQueueRefillPath.recycled_room, recycled_batch.refill_path);
    try std.testing.expectEqual(@as(u32, 25600), recycled_batch.total_posted_bytes);
    try std.testing.expectEqual(@as(u32, 25600), recycled_batch.total_allocation_bytes);
}

test "phase10 virtio net reserves refill descriptors without widening into live submission" {
    var fresh_device = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
    });
    const fresh_snapshot = try fresh_device.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
        },
        .requested_queue_pairs = 2,
        .max_queue_pairs = 2,
    });
    _ = try fresh_device.planMergeableReceiveBuffer(fresh_snapshot, .{
        .header_len = 12,
        .average_packet_len = 1500,
        .min_buf_len = 512,
        .headroom = 256,
        .cache_line_size = 64,
        .skb_shared_info_size = 320,
    });

    const fresh_reservation = try fresh_device.reserveReceiveQueueRefillDescriptors(.{
        .queue_capacity = 256,
        .buffers_posted = 192,
        .batch_limit = 32,
        .descriptors_available = 48,
        .descriptors_per_buffer = 2,
    });
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", fresh_reservation.anchor);
    try std.testing.expectEqual(@as(u16, 32), fresh_reservation.requested_refill_count);
    try std.testing.expectEqual(@as(u16, 24), fresh_reservation.refill_count);
    try std.testing.expectEqual(@as(u16, 48), fresh_reservation.descriptors_reserved);
    try std.testing.expectEqual(@as(u16, 216), fresh_reservation.buffers_after_reservation);
    try std.testing.expectEqual(@as(u16, 8), fresh_reservation.buffers_left_pending);
    try std.testing.expect(fresh_reservation.descriptor_budget_exhausted);
    try std.testing.expect(!fresh_reservation.queue_will_be_full);
    try std.testing.expectEqual(virtio_net.ReceiveQueueRefillPath.mergeable_allocation, fresh_reservation.refill_path);
    try std.testing.expectEqual(@as(u32, 36864), fresh_reservation.total_posted_bytes);
    try std.testing.expectEqual(@as(u32, 50688), fresh_reservation.total_allocation_bytes);

    var recycled_device = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
    });
    const recycled_snapshot = try recycled_device.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });
    _ = try recycled_device.planMergeableReceiveBuffer(recycled_snapshot, .{
        .header_len = 12,
        .average_packet_len = 900,
        .min_buf_len = 256,
        .recycled_room = 896,
    });

    const recycled_reservation = try recycled_device.reserveReceiveQueueRefillDescriptors(.{
        .queue_capacity = 128,
        .buffers_posted = 120,
        .descriptors_available = 16,
        .descriptors_per_buffer = 2,
    });
    try std.testing.expectEqual(@as(u16, 8), recycled_reservation.requested_refill_count);
    try std.testing.expectEqual(@as(u16, 8), recycled_reservation.refill_count);
    try std.testing.expectEqual(@as(u16, 16), recycled_reservation.descriptors_reserved);
    try std.testing.expectEqual(@as(u16, 128), recycled_reservation.buffers_after_reservation);
    try std.testing.expectEqual(@as(u16, 0), recycled_reservation.buffers_left_pending);
    try std.testing.expect(!recycled_reservation.descriptor_budget_exhausted);
    try std.testing.expect(recycled_reservation.queue_will_be_full);
    try std.testing.expectEqual(virtio_net.ReceiveQueueRefillPath.recycled_room, recycled_reservation.refill_path);
    try std.testing.expectEqual(@as(u32, 25600), recycled_reservation.total_posted_bytes);
    try std.testing.expectEqual(@as(u32, 25600), recycled_reservation.total_allocation_bytes);
}

test "phase10 virtio net makes a bounded notify decision from the queued refill reservation" {
    var device = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
        virtio_net.feature_multiqueue,
    });
    const snapshot = try device.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
            virtio_net.feature_multiqueue,
        },
        .requested_queue_pairs = 2,
        .max_queue_pairs = 2,
    });
    _ = try device.planMergeableReceiveBuffer(snapshot, .{
        .header_len = 12,
        .average_packet_len = 1500,
        .min_buf_len = 512,
        .headroom = 256,
        .cache_line_size = 64,
        .skb_shared_info_size = 320,
    });

    const reservation = try device.reserveReceiveQueueRefillDescriptors(.{
        .queue_capacity = 256,
        .buffers_posted = 192,
        .batch_limit = 32,
        .descriptors_available = 48,
        .descriptors_per_buffer = 2,
    });

    const empty_transition = device.decideReceiveQueueRefillNotify(reservation, .{
        .queue_was_empty = true,
        .notify_after_descriptors = 64,
    });
    try std.testing.expectEqualStrings("drivers/net/virtio_net.c", empty_transition.anchor);
    try std.testing.expect(empty_transition.queue_became_non_empty);
    try std.testing.expectEqual(@as(u16, 64), empty_transition.notify_after_descriptors);
    try std.testing.expect(!empty_transition.reached_notify_threshold);
    try std.testing.expect(empty_transition.should_notify);

    const threshold_only = device.decideReceiveQueueRefillNotify(reservation, .{
        .queue_was_empty = false,
        .notify_after_descriptors = 48,
    });
    try std.testing.expect(!threshold_only.queue_became_non_empty);
    try std.testing.expect(threshold_only.reached_notify_threshold);
    try std.testing.expect(threshold_only.should_notify);

    const suppressed = device.decideReceiveQueueRefillNotify(reservation, .{
        .queue_was_empty = true,
        .notifications_enabled = false,
        .notify_after_descriptors = 16,
    });
    try std.testing.expect(suppressed.queue_became_non_empty);
    try std.testing.expect(suppressed.reached_notify_threshold);
    try std.testing.expect(!suppressed.should_notify);

    const no_threshold = device.decideReceiveQueueRefillNotify(reservation, .{
        .queue_was_empty = false,
        .notify_after_descriptors = 64,
    });
    try std.testing.expect(!no_threshold.queue_became_non_empty);
    try std.testing.expect(!no_threshold.reached_notify_threshold);
    try std.testing.expect(!no_threshold.should_notify);

    const exhausted_reservation = try device.reserveReceiveQueueRefillDescriptors(.{
        .queue_capacity = 256,
        .buffers_posted = 192,
        .batch_limit = 32,
        .descriptors_available = 0,
        .descriptors_per_buffer = 2,
    });
    const no_descriptors = device.decideReceiveQueueRefillNotify(exhausted_reservation, .{
        .queue_was_empty = true,
    });
    try std.testing.expect(!no_descriptors.queue_became_non_empty);
    try std.testing.expect(!no_descriptors.reached_notify_threshold);
    try std.testing.expect(!no_descriptors.should_notify);
    try std.testing.expect(no_descriptors.descriptor_budget_exhausted);
}

test "phase10 virtio net rejects mergeable buffer plans that widen beyond the negotiated safe path" {
    var untouched_device = try virtio_net.VirtioNetProbeLab.init(&.{virtio_net.feature_mergeable_rx_buffers});
    try std.testing.expectError(error.MergeableBufferPlanUnavailable, untouched_device.summarizeReceiveQueueRefill());
    try std.testing.expectError(error.MergeableBufferPlanUnavailable, untouched_device.planReceiveQueueRefillBatch(.{
        .queue_capacity = 64,
        .buffers_posted = 0,
    }));
    try std.testing.expectError(error.MergeableBufferPlanUnavailable, untouched_device.reserveReceiveQueueRefillDescriptors(.{
        .queue_capacity = 64,
        .buffers_posted = 0,
        .descriptors_available = 4,
    }));

    var non_mergeable = try virtio_net.VirtioNetProbeLab.init(&.{virtio_net.feature_control_vq});
    const non_mergeable_snapshot = try non_mergeable.captureProbeSnapshot(.{
        .driver_feature_bits = &.{virtio_net.feature_control_vq},
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });

    try std.testing.expectError(error.MergeableBuffersNotNegotiated, non_mergeable.planMergeableReceiveBuffer(non_mergeable_snapshot, .{
        .header_len = 12,
        .average_packet_len = 512,
        .min_buf_len = 256,
    }));

    var device = try virtio_net.VirtioNetProbeLab.init(&.{
        virtio_net.feature_mergeable_rx_buffers,
        virtio_net.feature_control_vq,
    });
    const snapshot = try device.captureProbeSnapshot(.{
        .driver_feature_bits = &.{
            virtio_net.feature_mergeable_rx_buffers,
            virtio_net.feature_control_vq,
        },
        .requested_queue_pairs = 1,
        .max_queue_pairs = 1,
    });

    try std.testing.expectError(error.MissingSkbSharedInfoSize, device.planMergeableReceiveBuffer(snapshot, .{
        .header_len = 12,
        .average_packet_len = 1024,
        .min_buf_len = 256,
        .headroom = 128,
    }));
    try std.testing.expectError(error.MinBufferLenTooLarge, device.planMergeableReceiveBuffer(snapshot, .{
        .header_len = 64,
        .average_packet_len = 1024,
        .min_buf_len = virtio_net.default_page_size,
    }));
    try std.testing.expectError(error.InvalidRecycledRoom, device.planMergeableReceiveBuffer(snapshot, .{
        .header_len = 12,
        .average_packet_len = 1024,
        .min_buf_len = 256,
        .recycled_room = virtio_net.default_page_size,
    }));
    try std.testing.expectError(error.InvalidQueueCapacity, device.planReceiveQueueRefillBatch(.{
        .queue_capacity = 0,
        .buffers_posted = 0,
    }));
    _ = try device.planMergeableReceiveBuffer(snapshot, .{
        .header_len = 12,
        .average_packet_len = 1024,
        .min_buf_len = 256,
    });
    try std.testing.expectError(error.InvalidBuffersPosted, device.planReceiveQueueRefillBatch(.{
        .queue_capacity = 8,
        .buffers_posted = 9,
    }));
    try std.testing.expectError(error.InvalidDescriptorsPerBuffer, device.reserveReceiveQueueRefillDescriptors(.{
        .queue_capacity = 8,
        .buffers_posted = 4,
        .descriptors_available = 8,
        .descriptors_per_buffer = 0,
    }));
}
