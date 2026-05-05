const std = @import("std");
const virtio_core = @import("virtio_core");

fn readyDevice() !virtio_core.VirtioCoreLabDevice {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 1, 7, 11 });
    device.acknowledge();
    try device.attachDriver();
    try device.offerDriverFeature(1);
    _ = try device.finalizeFeatures();
    return device;
}

test "phase10 virtio core blocks fresh queue registration once reset is required" {
    var device = try readyDevice();
    device.noteNeedsReset();

    try std.testing.expectError(error.ResetRequired, device.registerQueueCallback(0, 8, "rx_done"));
    try std.testing.expectEqual(@as(usize, 0), device.registeredQueueCount());
}

test "phase10 virtio core blocks queue callback toggles and notifications once reset is required" {
    var device = try readyDevice();
    try device.registerQueueCallback(0, 8, "rx_done");
    device.noteNeedsReset();

    try std.testing.expectError(error.ResetRequired, device.disableQueueCallback(0));
    try std.testing.expectError(error.ResetRequired, device.enableQueueCallback(0));
    try std.testing.expectError(error.ResetRequired, device.notifyQueueUsed(0));

    const summary = try device.queueRegistrationSummary(0);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(usize, 0), summary.notification_count);
}

test "phase10 virtio core blocks queue teardown and reshaping once reset is required but keeps replay summaries visible" {
    var device = try readyDevice();
    try device.registerQueueCallback(1, 4, "control_done");
    try device.configureQueueDescriptorShape(1, 1, 2, false);
    device.noteNeedsReset();

    try std.testing.expectError(error.ResetRequired, device.unregisterQueueCallback(1));
    try std.testing.expectError(error.ResetRequired, device.configureQueueDescriptorShape(1, 2, 1, true));

    const queue_summary = try device.queueRegistrationSummary(1);
    try std.testing.expectEqual(@as(u16, 4), queue_summary.descriptor_count);

    const shape_summary = try device.queueDescriptorShapeSummary(1);
    try std.testing.expectEqual(@as(u16, 1), shape_summary.readable_descriptor_count);
    try std.testing.expectEqual(@as(u16, 2), shape_summary.writable_descriptor_count);
    try std.testing.expect(!shape_summary.uses_indirect_descriptors);
}

test "phase10 virtio core blocks driver-model progression once reset is required" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 1, 7, 11 });
    device.acknowledge();
    try device.attachDriverNamed("virtio_blk_lab");
    device.noteNeedsReset();

    try std.testing.expectError(error.ResetRequired, device.offerDriverFeature(1));
    try std.testing.expectError(error.ResetRequired, device.finalizeFeatures());
    try std.testing.expectError(error.ResetRequired, device.markDriverReady());

    var summary = device.lifecycleGuardSummary();
    try std.testing.expect(summary.reset_required);
    try std.testing.expect(summary.driver_attached);
    try std.testing.expect(!summary.features_negotiated);
    try std.testing.expect(!summary.driver_ready);
    try std.testing.expectEqual(virtio_core.DriverLifecycleBlocker.reset_required, summary.blocker.?);

    device.reset();
    device.acknowledge();
    try device.attachDriverNamed("virtio_blk_lab");
    try device.offerDriverFeature(1);
    _ = try device.finalizeFeatures();
    try device.markDriverReady();

    summary = device.lifecycleGuardSummary();
    try std.testing.expect(!summary.reset_required);
    try std.testing.expect(summary.features_negotiated);
    try std.testing.expect(summary.driver_ready);
}

test "phase10 virtio core blocks fresh driver attachment once reset is required" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{1});
    device.acknowledge();
    device.noteNeedsReset();

    try std.testing.expectError(error.ResetRequired, device.attachDriver());
    const summary = device.driverBindingSummary();
    try std.testing.expectEqualStrings("", summary.driver_name);
    try std.testing.expect(!summary.driver_attached);
}
