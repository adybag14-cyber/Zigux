const std = @import("std");
const virtio_core = @import("virtio.zig");

test "virtio core lifecycle guard advances through bounded wrapper readiness checkpoints" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 1, 7, 33 });

    var lifecycle = device.lifecycleGuardSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", lifecycle.anchor);
    try std.testing.expect(!lifecycle.has_acknowledge);
    try std.testing.expect(!lifecycle.ready_for_runtime);
    try std.testing.expectEqual(virtio_core.DriverLifecycleBlocker.missing_acknowledge, lifecycle.blocker.?);

    device.acknowledge();
    lifecycle = device.lifecycleGuardSummary();
    try std.testing.expect(lifecycle.has_acknowledge);
    try std.testing.expectEqual(virtio_core.DriverLifecycleBlocker.driver_not_attached, lifecycle.blocker.?);

    try device.attachDriverNamed("virtio_blk_verify");
    lifecycle = device.lifecycleGuardSummary();
    try std.testing.expectEqualStrings("virtio_blk_verify", lifecycle.driver_name);
    try std.testing.expect(lifecycle.driver_attached);
    try std.testing.expect(lifecycle.config_lifecycle_ready);
    try std.testing.expect(lifecycle.interrupt_lifecycle_ready);
    try std.testing.expectEqual(virtio_core.DriverLifecycleBlocker.feature_negotiation_incomplete, lifecycle.blocker.?);

    try device.offerDriverFeature(1);
    try device.offerDriverFeature(7);
    try device.offerDriverFeature(33);
    const negotiation = try device.finalizeFeaturesWithDriverValidation(&.{ 1, 33 });
    try std.testing.expect(negotiation.accepted_by_transport);
    try std.testing.expectEqual(@as(usize, 2), negotiation.offered_feature_count);
    try std.testing.expectEqual(@as(usize, 2), negotiation.negotiated_feature_count);

    lifecycle = device.lifecycleGuardSummary();
    try std.testing.expect(lifecycle.features_negotiated);
    try std.testing.expectEqual(virtio_core.DriverLifecycleBlocker.driver_not_ready, lifecycle.blocker.?);

    const binding = device.driverBindingSummary();
    try std.testing.expectEqualStrings("virtio_blk_verify", binding.driver_name);
    try std.testing.expect(binding.features_negotiated);
    try std.testing.expect(!binding.driver_ready);

    try device.markDriverReady();
    lifecycle = device.lifecycleGuardSummary();
    try std.testing.expect(lifecycle.driver_ready);
    try std.testing.expectEqual(virtio_core.DriverLifecycleBlocker.no_registered_queues, lifecycle.blocker.?);

    try device.registerQueueCallback(0, 8, "rx_done");
    lifecycle = device.lifecycleGuardSummary();
    try std.testing.expectEqual(@as(usize, 1), lifecycle.registered_queue_count);
    try std.testing.expect(lifecycle.queue_runtime_ready);
    try std.testing.expect(lifecycle.ready_for_runtime);
    try std.testing.expectEqual(@as(?virtio_core.DriverLifecycleBlocker, null), lifecycle.blocker);
}

test "virtio core wrapper summaries keep narrowed features and reset teardown visible" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 1, 7, 33 });

    device.acknowledge();
    try device.attachDriverNamed("virtio_console_verify");
    try device.offerDriverFeature(1);
    try device.offerDriverFeature(7);
    try device.offerDriverFeature(33);

    const negotiation = try device.finalizeFeaturesWithDriverValidation(&.{ 1, 33 });
    try std.testing.expect(negotiation.accepted_by_transport);
    try std.testing.expectEqual(@as(usize, 2), device.finalize_count);

    var status = try device.statusAttributeSummary();
    try std.testing.expectEqualStrings("0x0000000b\n", status.value());

    const driver_bits = device.featureAttributeSummary(.driver);
    try std.testing.expectEqual(virtio_core.FeatureAttributeKind.driver, driver_bits.kind);
    try std.testing.expectEqual(@as(u8, '1'), driver_bits.value()[1]);
    try std.testing.expectEqual(@as(u8, '0'), driver_bits.value()[7]);
    try std.testing.expectEqual(@as(u8, '1'), driver_bits.value()[33]);
    try std.testing.expectEqual(@as(u8, '\n'), driver_bits.value()[virtio_core.feature_bit_capacity]);

    try device.markDriverReady();
    try device.registerQueueCallback(2, 8, "queue_done");

    status = try device.statusAttributeSummary();
    try std.testing.expectEqualStrings("0x0000000f\n", status.value());

    device.noteNeedsReset();
    const replay = device.resetReplaySummary();
    try std.testing.expect(replay.reset_required);
    try std.testing.expect(replay.features_negotiated);
    try std.testing.expect(replay.driver_ready);
    try std.testing.expectEqual(@as(usize, 1), replay.registered_queue_count);
    try std.testing.expect(replay.will_clear_negotiated_features);
    try std.testing.expect(replay.will_clear_queue_callbacks);

    device.reset();

    status = try device.statusAttributeSummary();
    try std.testing.expectEqualStrings("0x00000000\n", status.value());

    const negotiated_bits = device.featureAttributeSummary(.negotiated);
    try std.testing.expectEqual(virtio_core.FeatureAttributeKind.negotiated, negotiated_bits.kind);
    try std.testing.expectEqual(@as(u8, '0'), negotiated_bits.value()[1]);
    try std.testing.expectEqual(@as(u8, '0'), negotiated_bits.value()[33]);
    try std.testing.expectEqual(@as(u8, '\n'), negotiated_bits.value()[virtio_core.feature_bit_capacity]);
}
