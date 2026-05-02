const std = @import("std");
const virtio_scsi = @import("virtio_scsi");

test "phase12 virtio scsi syntax lab keeps bounded queue exports reachable" {
    const descriptor = virtio_scsi.VirtioScsiQueueLab.descriptor();

    _ = virtio_scsi.ModuleDescriptor;
    _ = virtio_scsi.RequestQueueKind;
    _ = virtio_scsi.RecoveryAction;
    _ = virtio_scsi.QueueLayoutSummary;
    _ = virtio_scsi.RequestQueueSummary;
    _ = virtio_scsi.RecoverySummary;
    _ = virtio_scsi.RecoveryQueuePlan;
    _ = virtio_scsi.RecoveryIoQueueMapSummary;
    _ = virtio_scsi.ProbeRequest;
    _ = virtio_scsi.ProbeSnapshot;
    _ = virtio_scsi.HostLimitRequest;
    _ = virtio_scsi.HostLimitSummary;
    _ = virtio_scsi.QueueDepthRequest;
    _ = virtio_scsi.QueueDepthSummary;
    _ = virtio_scsi.RecoveryQueueDepthSummary;
    _ = virtio_scsi.IoQueueMapSummary;
    _ = virtio_scsi.VirtioScsiQueueLab;

    try std.testing.expectEqualStrings("virtio_scsi_queue_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_queue_family_planner);
    try std.testing.expect(descriptor.provides_probe_config_snapshot);
    try std.testing.expect(descriptor.provides_host_limit_summary);
    try std.testing.expect(descriptor.provides_queue_depth_summary);
    try std.testing.expect(descriptor.provides_io_queue_map_summary);
    try std.testing.expect(descriptor.provides_recovery_restore_planner);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_scsi_host);
    try std.testing.expect(descriptor.touches_transport_reset);
}

test "phase12 virtio scsi syntax lab keeps review constants and enums stable" {
    try std.testing.expectEqual(@as(u16, 0), virtio_scsi.control_queue_index);
    try std.testing.expectEqual(@as(u16, 1), virtio_scsi.event_queue_index);
    try std.testing.expectEqual(@as(u16, 2), virtio_scsi.request_queue_base);
    try std.testing.expectEqual(@as(u16, 8), virtio_scsi.event_buffer_count);
    try std.testing.expectEqual(@as(u16, 1), virtio_scsi.min_request_queues);

    try std.testing.expectEqual(
        virtio_scsi.RequestQueueKind.request_poll,
        virtio_scsi.RequestQueueKind.request_poll,
    );
    try std.testing.expectEqual(
        virtio_scsi.RecoveryAction.restore,
        virtio_scsi.RecoveryAction.restore,
    );
}
