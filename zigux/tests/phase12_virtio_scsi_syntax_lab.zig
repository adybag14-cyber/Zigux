const std = @import("std");

const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi syntax lab keeps current queue-planning exports reachable" {
    const descriptor = virtio_scsi.VirtioScsiQueueLab.descriptor();

    _ = virtio_scsi.ModuleDescriptor;
    _ = virtio_scsi.QueueLayoutSummary;
    _ = virtio_scsi.ProbeRequest;
    _ = virtio_scsi.ProbeSnapshot;
    _ = virtio_scsi.HostLimitRequest;
    _ = virtio_scsi.HostLimitSummary;
    _ = virtio_scsi.QueueDepthRequest;
    _ = virtio_scsi.QueueDepthSummary;
    _ = virtio_scsi.IoQueueMapSummary;
    _ = virtio_scsi.RecoverySummary;
    _ = virtio_scsi.RecoveryQueuePlan;
    _ = virtio_scsi.RecoveryIoQueueMapSummary;
    _ = virtio_scsi.RecoveryQueueDepthSummary;
    _ = virtio_scsi.RecoveryEventBufferOwnershipSummary;
    _ = virtio_scsi.RecoveryHostScanSummary;
    _ = virtio_scsi.RequestQueueSummary;

    try std.testing.expectEqualStrings("virtio_scsi_queue_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_queue_family_planner);
    try std.testing.expect(descriptor.provides_probe_config_snapshot);
    try std.testing.expect(descriptor.provides_host_limit_summary);
    try std.testing.expect(descriptor.provides_queue_depth_summary);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_scsi_host);
    try std.testing.expect(descriptor.touches_transport_reset);

    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    const layout = try lab.planQueueLayout(4, 2);
    try std.testing.expectEqual(@as(u16, 4), layout.request_queues);
    try std.testing.expectEqual(@as(u16, 2), layout.requested_poll_queues);
    try std.testing.expectEqual(@as(u16, 2), layout.default_queues);
    try std.testing.expectEqual(@as(u16, 2), layout.poll_queues);
    try std.testing.expectEqual(@as(u16, 6), layout.total_queues);
    try std.testing.expectEqual(@as(?u16, 4), layout.first_poll_queue_index);

    const probe = try lab.captureProbeSnapshot(.{
        .num_queues = 4,
        .requested_poll_queues = 2,
        .seg_max = 128,
        .cmd_per_lun = 64,
        .max_target = 255,
        .max_lun = 32,
        .max_sectors = 1024,
    });
    try std.testing.expectEqual(@as(u16, 4), probe.config_num_queues);
    try std.testing.expectEqual(@as(u32, 128), probe.config_seg_max);
    try std.testing.expectEqual(@as(u16, 2), probe.default_queue_count);
    try std.testing.expectEqual(@as(u16, 2), probe.poll_queue_count);
    try std.testing.expectEqual(@as(?u16, 4), probe.first_poll_queue_index);

    const host = try lab.captureHostLimitSummary(.{
        .probe = .{
            .num_queues = 4,
            .requested_poll_queues = 2,
            .seg_max = 128,
            .cmd_per_lun = 64,
            .max_target = 255,
            .max_lun = 32,
            .max_sectors = 1024,
        },
        .synthetic_can_queue = 16,
    });
    try std.testing.expectEqualStrings(descriptor.anchor, host.anchor);
    try std.testing.expectEqual(@as(u32, 16), host.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 16), host.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u16, 4), host.nr_hw_queues);

    const depth = try lab.captureQueueDepthSummary(.{
        .host_limit = .{
            .probe = .{
                .num_queues = 4,
                .requested_poll_queues = 2,
                .cmd_per_lun = 64,
            },
            .synthetic_can_queue = 16,
        },
        .requested_depth = 10,
    });
    try std.testing.expectEqual(@as(u32, 10), depth.clamped_queue_depth);
    try std.testing.expect(depth.tracks_queue_depth);
    try std.testing.expect(depth.uses_change_queue_depth);

    const request_queue = try lab.requestQueue(3);
    try std.testing.expectEqual(@as(u16, 3), request_queue.local_index);
    try std.testing.expectEqual(@as(u16, 5), request_queue.global_index);
    try std.testing.expectEqual(virtio_scsi.RequestQueueKind.request_poll, request_queue.kind);

    const mapping = try lab.captureIoQueueMapSummary(4, 2);
    try std.testing.expectEqual(@as(u16, 3), mapping.nr_maps);
    try std.testing.expectEqual(@as(u16, 2), mapping.default_queue_count);
    try std.testing.expectEqual(@as(u16, 2), mapping.poll_queue_count);
    try std.testing.expect(mapping.default_queues_use_virtio_affinity);
    try std.testing.expect(mapping.poll_queues_use_blk_mq_mapping);
}

test "phase12 virtio scsi syntax lab keeps transport-reset recovery exports reachable" {
    var lab = virtio_scsi.VirtioScsiQueueLab.init();
    _ = try lab.captureQueueDepthSummary(.{
        .host_limit = .{
            .probe = .{
                .num_queues = 4,
                .requested_poll_queues = 2,
                .cmd_per_lun = 9,
                .max_target = 3,
                .max_lun = 2,
                .max_sectors = 1536,
            },
            .synthetic_can_queue = 7,
        },
        .requested_depth = 11,
    });

    const freeze = try lab.freezeForTransportReset();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", freeze.anchor);
    try std.testing.expectEqual(virtio_scsi.RecoveryAction.freeze, freeze.action);
    try std.testing.expect(!freeze.was_frozen);
    try std.testing.expect(freeze.is_frozen);
    try std.testing.expectEqual(@as(u16, 4), freeze.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 2), freeze.remembered_poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), freeze.remembered_event_buffer_count);

    const plan = try lab.recoveryQueuePlan();
    try std.testing.expectEqual(@as(u16, 4), plan.request_queues);
    try std.testing.expectEqual(@as(u16, 2), plan.default_queues);
    try std.testing.expectEqual(@as(u16, 2), plan.poll_queues);
    try std.testing.expectEqual(@as(u16, 6), plan.total_queues);
    try std.testing.expectEqual(@as(?u16, 4), plan.first_poll_queue_index);
    try std.testing.expect(plan.requires_control_queue_restore);
    try std.testing.expect(plan.requires_event_queue_refill);
    try std.testing.expect(plan.requires_request_queue_restore);

    const depth = try lab.recoveryQueueDepthSummary();
    try std.testing.expectEqual(@as(u32, 11), depth.requested_depth);
    try std.testing.expectEqual(@as(u32, 7), depth.effective_can_queue);
    try std.testing.expectEqual(@as(u32, 7), depth.effective_cmd_per_lun);
    try std.testing.expectEqual(@as(u32, 7), depth.clamped_queue_depth);
    try std.testing.expect(depth.tracks_queue_depth);
    try std.testing.expect(depth.requires_change_queue_depth_restore);

    const mapping = try lab.recoveryIoQueueMapSummary();
    try std.testing.expectEqual(@as(u16, 3), mapping.nr_maps);
    try std.testing.expectEqual(@as(u16, 2), mapping.default_queue_count);
    try std.testing.expectEqual(@as(u16, 2), mapping.poll_queue_count);
    try std.testing.expect(mapping.requires_blk_mq_map_restore);
    try std.testing.expect(mapping.requires_virtio_affinity_restore);
    try std.testing.expect(mapping.requires_poll_map_restore);

    const ownership = try lab.recoveryEventBufferOwnershipSummary();
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_queue_index), ownership.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), ownership.remembered_event_buffer_count);
    try std.testing.expectEqual(@as(u16, 4), ownership.request_queue_count);
    try std.testing.expectEqual(@as(u16, 2), ownership.poll_queue_count);
    try std.testing.expect(ownership.event_buffers_reserved_for_event_queue);
    try std.testing.expect(!ownership.request_queues_can_borrow_event_buffers);
    try std.testing.expect(ownership.requires_device_ready_before_event_rearm);
    try std.testing.expect(ownership.requires_event_rearm_before_request_queue_reuse);

    const host_scan = try lab.recoveryHostScanSummary();
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", host_scan.anchor);
    try std.testing.expectEqual(@as(u16, 4), host_scan.remembered_request_queues);
    try std.testing.expectEqual(@as(u16, 2), host_scan.remembered_poll_queues);
    try std.testing.expectEqual(@as(u16, virtio_scsi.event_buffer_count), host_scan.remembered_event_buffer_count);
    try std.testing.expectEqual(@as(u16, 0), host_scan.recovery_generation);
    try std.testing.expect(host_scan.requires_control_queue_restore_before_scan);
    try std.testing.expect(host_scan.requires_event_rearm_before_scan);
    try std.testing.expect(host_scan.requires_request_queue_restore_before_scan);
    try std.testing.expect(host_scan.requires_async_scan_resume);

    const restore = try lab.restoreAfterTransportReset();
    try std.testing.expectEqual(virtio_scsi.RecoveryAction.restore, restore.action);
    try std.testing.expect(restore.was_frozen);
    try std.testing.expect(!restore.is_frozen);
    try std.testing.expect(restore.request_planning_available);
    try std.testing.expect(restore.event_recycling_enabled);
    try std.testing.expectEqual(@as(u16, 1), restore.recovery_generation);

    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryQueuePlan());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryIoQueueMapSummary());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryQueueDepthSummary());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryEventBufferOwnershipSummary());
    try std.testing.expectError(error.TransportNotFrozen, lab.recoveryHostScanSummary());
}
