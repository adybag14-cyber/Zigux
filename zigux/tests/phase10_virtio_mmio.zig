const std = @import("std");
const virtio_mmio = @import("virtio_mmio");

test "phase10 virtio mmio descriptor stays anchored to virtio_mmio.c" {
    const descriptor = virtio_mmio.VirtioMmioRegisterWindowLab.descriptor();

    try std.testing.expectEqualStrings("virtio_mmio_register_window_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_lab_validation);
    try std.testing.expect(descriptor.touches_transport_mmio);
    try std.testing.expect(!descriptor.touches_dma_paths);
}

test "phase10 virtio mmio selects feature pages and records driver feature writes" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.init(.{ 0x89abcdef, 0x01234567 }, 7);

    var summary = try window.featureWindowSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 0), summary.selected_device_page);
    try std.testing.expectEqual(@as(u32, 0), summary.selected_driver_page);
    try std.testing.expectEqual(@as(u32, 0x89abcdef), summary.selected_device_features);
    try std.testing.expectEqual(@as(u32, 0), summary.selected_driver_features);

    try window.selectDeviceFeaturePage(1);
    try window.selectDriverFeaturePage(1);
    summary = try window.writeSelectedDriverFeatures(0x0000ffff);

    try std.testing.expectEqual(@as(u32, 1), summary.selected_device_page);
    try std.testing.expectEqual(@as(u32, 1), summary.selected_driver_page);
    try std.testing.expectEqual(@as(u32, 0x01234567), summary.selected_device_features);
    try std.testing.expectEqual(@as(u32, 0x0000ffff), summary.selected_driver_features);

    try std.testing.expectError(error.FeaturePageOutOfRange, window.selectDeviceFeaturePage(virtio_mmio.supported_feature_pages));
    try std.testing.expectError(error.FeaturePageOutOfRange, window.selectDriverFeaturePage(virtio_mmio.supported_feature_pages));
}

test "phase10 virtio mmio keeps status writes separate from reset" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.init(.{ 0, 0 }, 0);

    try std.testing.expectError(error.ResetRequiresDedicatedPath, window.setStatus(0));

    var status = try window.setStatus(0x07);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", status.anchor);
    try std.testing.expectEqual(@as(u8, 0x07), status.status);
    try std.testing.expectEqual(@as(usize, 0), status.reset_count);

    status = window.reset();
    try std.testing.expectEqual(@as(u8, 0), status.status);
    try std.testing.expectEqual(@as(usize, 1), status.reset_count);
}

test "phase10 virtio mmio tracks config generation changes without config-space IO" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.init(.{ 0, 0 }, 9);

    var generation = window.configGenerationSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", generation.anchor);
    try std.testing.expectEqual(@as(u32, 9), generation.generation);
    try std.testing.expect(!generation.changed);

    generation = window.bumpConfigGeneration();
    try std.testing.expectEqual(@as(u32, 10), generation.generation);
    try std.testing.expect(generation.changed);
}

test "phase10 virtio mmio acknowledges only pending bounded interrupt bits" {
    var window = virtio_mmio.VirtioMmioRegisterWindowLab.init(.{ 0, 0 }, 0);

    try std.testing.expectError(error.EmptyInterruptMask, window.raiseInterrupt(0));
    try std.testing.expectError(error.UnsupportedInterruptBits, window.raiseInterrupt(0x4));

    try window.raiseInterrupt(0x3);
    try std.testing.expectEqual(@as(u32, 0x3), window.readInterruptStatus());

    var ack = try window.acknowledgeInterrupt(0x1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", ack.anchor);
    try std.testing.expectEqual(@as(u32, 0x1), ack.acknowledged_bits);
    try std.testing.expectEqual(@as(u32, 0x3), ack.pending_bits_before_ack);
    try std.testing.expectEqual(@as(u32, 0x2), ack.pending_bits_after_ack);

    ack = try window.acknowledgeInterrupt(0x3);
    try std.testing.expectEqual(@as(u32, 0x2), ack.acknowledged_bits);
    try std.testing.expectEqual(@as(u32, 0x2), ack.pending_bits_before_ack);
    try std.testing.expectEqual(@as(u32, 0), ack.pending_bits_after_ack);

    try std.testing.expectError(error.EmptyInterruptMask, window.acknowledgeInterrupt(0));
    try std.testing.expectError(error.UnsupportedInterruptBits, window.acknowledgeInterrupt(0x8));
}
