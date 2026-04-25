const std = @import("std");
const virtio_core = @import("virtio_core");

test "phase10 virtio core descriptor stays anchored to virtio.c" {
    const descriptor = virtio_core.VirtioCoreLabDevice.descriptor();

    try std.testing.expectEqualStrings("virtio_core_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_lab_validation);
    try std.testing.expect(!descriptor.touches_transport_mmio);
}

test "phase10 virtio core accepts offered features and reaches driver ok" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 1, 7, 33 });

    device.reset();
    device.acknowledge();
    try device.attachDriver();
    try device.offerDriverFeature(1);
    try device.offerDriverFeature(33);

    const summary = try device.finalizeFeatures();
    try std.testing.expect(summary.accepted_by_transport);
    try std.testing.expectEqual(@as(usize, 2), summary.offered_feature_count);
    try std.testing.expectEqual(@as(usize, 2), summary.negotiated_feature_count);
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", summary.anchor);

    try device.markDriverReady();
    try std.testing.expect(device.hasStatus(virtio_core.DeviceStatus.acknowledge));
    try std.testing.expect(device.hasStatus(virtio_core.DeviceStatus.driver));
    try std.testing.expect(device.hasStatus(virtio_core.DeviceStatus.features_ok));
    try std.testing.expect(device.hasStatus(virtio_core.DeviceStatus.driver_ok));
    try std.testing.expect(try device.hasNegotiatedFeature(1));
    try std.testing.expect(try device.hasNegotiatedFeature(33));
    try std.testing.expectEqual(@as(usize, 1), device.reset_count);
    try std.testing.expectEqual(@as(usize, 1), device.finalize_count);
}

test "phase10 virtio core rejects unsupported driver features" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 1, 5 });

    device.acknowledge();
    try device.attachDriver();
    try std.testing.expectError(error.DriverOfferedUnsupportedFeature, device.offerDriverFeature(7));
    try std.testing.expect(!(try device.hasDeviceFeature(7)));
}

test "phase10 virtio core models transport refusal of features ok" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 2, 8 });

    device.acknowledge();
    try device.attachDriver();
    try device.offerDriverFeature(8);
    device.setTransportFeatureAcceptance(false);

    const summary = try device.finalizeFeatures();
    try std.testing.expect(!summary.accepted_by_transport);
    try std.testing.expect(!device.hasStatus(virtio_core.DeviceStatus.features_ok));
    try std.testing.expectError(error.MissingFeaturesOk, device.markDriverReady());
    try std.testing.expect(!(try device.hasNegotiatedFeature(8)));
}

test "phase10 virtio core closes the feature window after finalize" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 3, 11 });

    device.acknowledge();
    try device.attachDriver();
    try device.offerDriverFeature(3);
    _ = try device.finalizeFeatures();

    try std.testing.expectError(error.FeatureWindowClosed, device.offerDriverFeature(11));

    try device.markDriverReady();
    try std.testing.expectError(error.FeatureWindowClosed, device.offerDriverFeature(11));
    try std.testing.expectEqual(@as(usize, 1), device.finalize_count);
    try std.testing.expect(try device.hasNegotiatedFeature(3));
}

test "phase10 virtio core reset clears negotiated state and keeps failure bits opt-in" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 4, 9 });

    device.acknowledge();
    try device.attachDriver();
    try device.offerDriverFeature(4);
    _ = try device.finalizeFeatures();
    try device.markDriverReady();
    device.fail();
    device.noteNeedsReset();

    try std.testing.expect(device.hasStatus(virtio_core.DeviceStatus.failed));
    try std.testing.expect(device.hasStatus(virtio_core.DeviceStatus.device_needs_reset));

    device.reset();
    try std.testing.expectEqual(@as(u8, 0), device.status);
    try std.testing.expect(!(try device.hasNegotiatedFeature(4)));
    try std.testing.expectEqual(@as(usize, 1), device.finalize_count);
    try std.testing.expectEqual(@as(usize, 1), device.reset_count);
}

test "phase10 virtio core rejects feature bits outside the bounded lab capacity" {
    try std.testing.expectError(error.FeatureBitOutOfRange, virtio_core.VirtioCoreLabDevice.init(&.{virtio_core.feature_bit_capacity}));

    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 9 });
    device.acknowledge();
    try device.attachDriver();

    try std.testing.expectError(error.FeatureBitOutOfRange, device.offerDriverFeature(virtio_core.feature_bit_capacity));
    try std.testing.expectError(error.FeatureBitOutOfRange, device.hasDeviceFeature(virtio_core.feature_bit_capacity));
    try std.testing.expectError(error.FeatureBitOutOfRange, device.hasNegotiatedFeature(virtio_core.feature_bit_capacity));
}
