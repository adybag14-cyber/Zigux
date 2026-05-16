const std = @import("std");
const virtio_core = @import("virtio.zig");

test "virtio core wrapper-facing lifecycle guard checkpoints keep narrowed-feature summaries visible" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 1, 7, 33 });

    try std.testing.expectEqualStrings(
        "drivers/virtio/virtio.c",
        virtio_core.VirtioCoreLabDevice.descriptor().anchor,
    );
    try std.testing.expectError(error.MissingAcknowledge, device.attachDriverNamed("verify-core"));

    device.acknowledge();
    try device.attachDriverNamed("verify-core");
    try std.testing.expectError(error.MissingFeaturesOk, device.markDriverReady());

    try device.offerDriverFeature(1);
    try device.offerDriverFeature(33);

    const negotiation = try device.finalizeFeatures();
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", negotiation.anchor);
    try std.testing.expectEqual(
        @as(
            u8,
            virtio_core.DeviceStatus.acknowledge |
                virtio_core.DeviceStatus.driver |
                virtio_core.DeviceStatus.features_ok,
        ),
        negotiation.driver_status,
    );
    try std.testing.expectEqual(@as(usize, 2), negotiation.offered_feature_count);
    try std.testing.expectEqual(@as(usize, 2), negotiation.negotiated_feature_count);
    try std.testing.expect(negotiation.accepted_by_transport);

    var binding = device.driverBindingSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", binding.anchor);
    try std.testing.expectEqualStrings("verify-core", binding.driver_name);
    try std.testing.expect(binding.driver_attached);
    try std.testing.expect(binding.features_negotiated);
    try std.testing.expect(!binding.driver_ready);

    try device.markDriverReady();
    binding = device.driverBindingSummary();
    try std.testing.expect(binding.driver_ready);
}

test "virtio core wrapper-facing transport rejection keeps failed feature handoff local to the helper packet" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 1, 7, 33 });

    device.acknowledge();
    try device.attachDriverNamed("verify-reject");
    device.setTransportFeatureAcceptance(false);
    try device.offerDriverFeature(1);
    try device.offerDriverFeature(7);

    const negotiation = try device.finalizeFeatures();
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", negotiation.anchor);
    try std.testing.expectEqual(@as(usize, 2), negotiation.offered_feature_count);
    try std.testing.expectEqual(@as(usize, 0), negotiation.negotiated_feature_count);
    try std.testing.expect(!negotiation.accepted_by_transport);
    try std.testing.expect(!device.hasStatus(virtio_core.DeviceStatus.features_ok));
    try std.testing.expectError(error.MissingFeaturesOk, device.markDriverReady());
}

test "virtio core wrapper-facing failed-status teardown stays bounded to reset replay" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 1, 7, 33 });

    device.acknowledge();
    try device.attachDriverNamed("verify-reset");
    try device.offerDriverFeature(1);
    try device.offerDriverFeature(33);
    _ = try device.finalizeFeatures();
    try device.markDriverReady();
    try device.registerQueueCallback(0, 8, "verify-callback");
    try device.configureQueueDescriptorShape(0, 4, 4, true);
    try device.noteConfigChanged();
    try device.noteInterruptReason(
        virtio_core.VirtioInterruptReason.queue_used |
            virtio_core.VirtioInterruptReason.config_change,
    );
    device.fail();
    device.noteNeedsReset();

    const replay = device.resetReplaySummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", replay.anchor);
    try std.testing.expect(replay.reset_required);
    try std.testing.expect(replay.driver_attached);
    try std.testing.expect(replay.features_negotiated);
    try std.testing.expect(replay.driver_ready);
    try std.testing.expectEqual(@as(usize, 1), replay.registered_queue_count);
    try std.testing.expect(replay.has_unacknowledged_generation);
    try std.testing.expectEqual(
        virtio_core.VirtioInterruptReason.queue_used |
            virtio_core.VirtioInterruptReason.config_change,
        replay.pending_interrupt_reason_bits,
    );
    try std.testing.expect(replay.will_clear_negotiated_features);
    try std.testing.expect(replay.will_clear_queue_callbacks);
    try std.testing.expect(replay.will_clear_config_bookkeeping);
    try std.testing.expect(replay.will_clear_interrupts);
    try std.testing.expect(device.hasStatus(virtio_core.DeviceStatus.failed));

    device.reset();

    const cleared = device.resetReplaySummary();
    try std.testing.expect(!device.hasStatus(virtio_core.DeviceStatus.failed));
    try std.testing.expect(!device.isResetRequired());
    try std.testing.expect(!cleared.driver_attached);
    try std.testing.expect(!cleared.features_negotiated);
    try std.testing.expect(!cleared.driver_ready);
    try std.testing.expectEqual(@as(usize, 0), cleared.registered_queue_count);
    try std.testing.expect(!cleared.will_clear_negotiated_features);
    try std.testing.expect(!cleared.will_clear_queue_callbacks);
    try std.testing.expect(!cleared.will_clear_config_bookkeeping);
    try std.testing.expect(!cleared.will_clear_interrupts);
}
