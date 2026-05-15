const std = @import("std");
const virtio_input = @import("virtio_input");

test "virtio input wrapper-facing identity review keeps config snapshots anchored to the lab helper" {
    const ids = virtio_input.DeviceIds{
        .bustype = virtio_input.bus_virtual,
        .vendor = 0x1af4,
        .product = 0x1052,
        .version = 2,
    };
    const device = try virtio_input.VirtioInputLab.init("verify-tablet", "verify-serial", 40, ids);

    const snapshot = device.configSnapshot();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", snapshot.anchor);
    try std.testing.expectEqualStrings("verify-tablet", snapshot.name);
    try std.testing.expectEqualStrings("verify-serial", snapshot.serial);
    try std.testing.expectEqualStrings("virtio40/input0", snapshot.phys);
    try std.testing.expectEqual(@as(u16, 0x1af4), snapshot.ids.vendor);
    try std.testing.expectEqual(@as(u16, 0x1052), snapshot.ids.product);
    try std.testing.expectEqual(@as(u16, 2), snapshot.ids.version);
}

test "virtio input wrapper-facing queue review keeps queue plan readiness local to the helper packet" {
    var device = try virtio_input.VirtioInputLab.init("verify-tablet", "verify-serial", 41, null);

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);

    var summary = try device.queuePlanSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqual(virtio_input.event_queue_index, summary.event_queue_index);
    try std.testing.expectEqual(virtio_input.status_queue_index, summary.status_queue_index);
    try std.testing.expectEqual(@as(u16, 16), summary.event_descriptor_count);
    try std.testing.expectEqual(@as(u16, 8), summary.status_descriptor_count);
    try std.testing.expectEqual(@as(u16, 0), summary.queued_event_buffer_count);
    try std.testing.expect(!summary.ready);

    _ = try device.fillEventBuffers();
    summary = try device.queuePlanSummary();
    try std.testing.expectEqual(@as(u16, 16), summary.queued_event_buffer_count);
    try std.testing.expect(!summary.ready);

    try device.markReady();
    summary = try device.queuePlanSummary();
    try std.testing.expect(summary.ready);
}

test "virtio input wrapper-facing status review keeps suppressed multitouch timestamps explicit" {
    var device = try virtio_input.VirtioInputLab.init("verify-tablet", "verify-status", 42, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();
    device.setMultitouch(true);

    _ = try device.sendStatus(0x11, 0x01, 1);
    _ = try device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 2);

    const summary = try device.drainStatusQueue(1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqual(@as(usize, 1), summary.completed_status_count);
    try std.testing.expectEqual(@as(usize, 1), summary.pending_status_count_before);
    try std.testing.expectEqual(@as(usize, 0), summary.pending_status_count_after);
    try std.testing.expectEqual(@as(usize, 1), summary.suppressed_status_count);
    try std.testing.expect(summary.ready);
}
