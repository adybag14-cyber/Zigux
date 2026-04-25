const std = @import("std");
const virtio_input = @import("virtio_input");

test "phase10 virtio input descriptor snapshots identity and supported config selects" {
    const descriptor = virtio_input.VirtioInputLab.descriptor();
    try std.testing.expectEqualStrings("virtio_input_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_lab_validation);
    try std.testing.expect(!descriptor.touches_transport_mmio);
    try std.testing.expect(!descriptor.touches_dma_paths);

    var device = try virtio_input.VirtioInputLab.init(
        "tablet-with-a-name-longer-than-sixty-four-bytes-to-prove-capped-copying",
        "serial-0007",
        7,
        .{
            .bustype = 0x18,
            .vendor = 0x1234,
            .product = 0x5678,
            .version = 0x0001,
        },
    );
    const snapshot = device.configSnapshot();

    try std.testing.expectEqualStrings("tablet-with-a-name-longer-than-sixty-four-bytes-to-prove-capped-", snapshot.name);
    try std.testing.expectEqualStrings("serial-0007", snapshot.serial);
    try std.testing.expectEqualStrings("virtio7/input0", snapshot.phys);
    try std.testing.expectEqual(@as(u16, 0x18), snapshot.ids.bustype);
    try std.testing.expectEqual(@as(u16, 0x1234), snapshot.ids.vendor);
    try std.testing.expectEqual(@as(u16, 0x5678), snapshot.ids.product);
    try std.testing.expectEqual(@as(u16, 0x0001), snapshot.ids.version);
    try std.testing.expectEqual(virtio_input.ConfigSelect.id_name, snapshot.supported_selects[0]);
    try std.testing.expectEqual(virtio_input.ConfigSelect.abs_info, snapshot.supported_selects[5]);
}

test "phase10 virtio input plans events and status queues with capped event buffers" {
    var device = try virtio_input.VirtioInputLab.init("zigux-tablet", "serial-1", 1, null);

    try std.testing.expectError(error.EventQueueNotConfigured, device.markReady());
    try std.testing.expectError(error.EmptyDescriptorCount, device.configureEventQueue(0));
    try std.testing.expectError(error.DescriptorCountMustBePowerOfTwo, device.configureEventQueue(3));

    try device.configureEventQueue(128);
    try std.testing.expectError(error.StatusQueueNotConfigured, device.fillEventBuffers());

    try device.configureStatusQueue(8);
    var summary = try device.fillEventBuffers();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, virtio_input.event_queue_index), summary.event_queue_index);
    try std.testing.expectEqual(@as(u16, virtio_input.status_queue_index), summary.status_queue_index);
    try std.testing.expectEqual(@as(u16, 128), summary.event_descriptor_count);
    try std.testing.expectEqual(@as(u16, 8), summary.status_descriptor_count);
    try std.testing.expectEqual(@as(u16, virtio_input.static_event_buffer_capacity), summary.queued_event_buffer_count);
    try std.testing.expect(!summary.ready);

    try device.markReady();
    summary = try device.queuePlanSummary();
    try std.testing.expect(summary.ready);
}

test "phase10 virtio input suppresses MSC_TIMESTAMP status loops for multitouch devices" {
    var device = try virtio_input.VirtioInputLab.init("touch-panel", "serial-2", 2, null);

    try device.configureEventQueue(32);
    try device.configureStatusQueue(4);
    try std.testing.expectError(error.DeviceNotReady, device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 77));

    _ = try device.fillEventBuffers();
    try device.markReady();
    device.setMultitouch(true);

    var summary = try device.sendStatus(virtio_input.ev_msc, virtio_input.msc_timestamp, 88);
    try std.testing.expect(!summary.sent);
    try std.testing.expect(summary.suppressed_msc_timestamp);
    try std.testing.expectEqual(@as(usize, 0), summary.queued_status_count);
    try std.testing.expectEqual(@as(usize, 1), summary.suppressed_status_count);

    summary = try device.sendStatus(0x11, 0x00, 1);
    try std.testing.expect(summary.sent);
    try std.testing.expect(!summary.suppressed_msc_timestamp);
    try std.testing.expectEqual(@as(usize, 1), summary.queued_status_count);
    try std.testing.expectEqual(@as(usize, 1), summary.suppressed_status_count);
}

test "phase10 virtio input reset clears queue plan and returns to default bus identity" {
    var device = try virtio_input.VirtioInputLab.init("keyboard", "serial-3", 3, null);
    const snapshot = device.configSnapshot();
    try std.testing.expectEqual(@as(u16, virtio_input.bus_virtual), snapshot.ids.bustype);

    try device.configureEventQueue(16);
    try device.configureStatusQueue(8);
    _ = try device.fillEventBuffers();
    try device.markReady();
    _ = try device.sendStatus(0x11, 0x01, 1);
    device.setMultitouch(true);

    device.reset();

    try std.testing.expectError(error.EventQueueNotConfigured, device.queuePlanSummary());
    try std.testing.expectError(error.StatusQueueNotConfigured, device.sendStatus(0x11, 0x01, 1));
}
