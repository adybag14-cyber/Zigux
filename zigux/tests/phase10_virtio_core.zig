const std = @import("std");
const virtio_core = @import("virtio_core");

test "phase10 virtio core tracks lifecycle guard bookkeeping across driver model milestones" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 1, 7, 11 });

    var lifecycle = device.lifecycleGuardSummary();
    try std.testing.expectEqual(virtio_core.DriverLifecycleBlocker.missing_acknowledge, lifecycle.blocker.?);

    device.acknowledge();
    lifecycle = device.lifecycleGuardSummary();
    try std.testing.expectEqual(virtio_core.DriverLifecycleBlocker.driver_not_attached, lifecycle.blocker.?);

    try device.attachDriverNamed("virtio_blk_lab");
    lifecycle = device.lifecycleGuardSummary();
    try std.testing.expectEqual(virtio_core.DriverLifecycleBlocker.feature_negotiation_incomplete, lifecycle.blocker.?);

    try device.offerDriverFeature(1);
    try device.offerDriverFeature(7);
    try device.offerDriverFeature(11);
    _ = try device.finalizeFeaturesWithDriverValidation(&.{ 1, 11 });
    lifecycle = device.lifecycleGuardSummary();
    try std.testing.expectEqual(virtio_core.DriverLifecycleBlocker.driver_not_ready, lifecycle.blocker.?);

    try device.markDriverReady();
    lifecycle = device.lifecycleGuardSummary();
    try std.testing.expectEqual(virtio_core.DriverLifecycleBlocker.no_registered_queues, lifecycle.blocker.?);

    try device.registerQueueCallback(0, 8, "rx_done");
    const lifecycle_final = device.lifecycleGuardSummary();
    try std.testing.expectEqual(@as(usize, 1), lifecycle_final.registered_queue_count);
    try std.testing.expect(lifecycle_final.queue_runtime_ready);
    try std.testing.expect(lifecycle_final.ready_for_runtime);
    try std.testing.expect(lifecycle_final.blocker == null);

    device.noteNeedsReset();
    lifecycle = device.lifecycleGuardSummary();
    try std.testing.expectEqual(virtio_core.DriverLifecycleBlocker.reset_required, lifecycle.blocker.?);
}

test "phase10 virtio core reaches queue runtime readiness after validated feature narrowing" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 1, 7, 11 });
    device.acknowledge();
    try device.attachDriverNamed("virtio_blk_lab");
    try device.offerDriverFeature(1);
    try device.offerDriverFeature(7);
    try device.offerDriverFeature(11);

    const negotiation = try device.finalizeFeaturesWithDriverValidation(&.{ 1, 11 });
    try std.testing.expect(negotiation.accepted_by_transport);
    try std.testing.expectEqual(@as(usize, 2), negotiation.offered_feature_count);
    try std.testing.expectEqual(@as(usize, 2), negotiation.negotiated_feature_count);
    try std.testing.expectEqual(@as(usize, 2), device.finalize_count);
    try std.testing.expect(try device.hasNegotiatedFeature(1));
    try std.testing.expect(!(try device.hasNegotiatedFeature(7)));
    try std.testing.expect(try device.hasNegotiatedFeature(11));

    try device.markDriverReady();
    try device.registerQueueCallback(0, 8, "rx_done");

    const lifecycle = device.lifecycleGuardSummary();
    try std.testing.expectEqual(@as(usize, 1), lifecycle.registered_queue_count);
    try std.testing.expect(lifecycle.queue_runtime_ready);
    try std.testing.expect(lifecycle.ready_for_runtime);

    const queue_summary = try device.queueRegistrationSummary(0);
    try std.testing.expectEqualStrings("rx_done", queue_summary.callback_name);
}

test "phase10 virtio core exposes reset replay bookkeeping before reset clears state" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 1, 7, 11 });
    device.acknowledge();
    try device.attachDriverNamed("virtio_blk_lab");
    try device.offerDriverFeature(1);
    try device.offerDriverFeature(7);
    try device.offerDriverFeature(11);
    _ = try device.finalizeFeaturesWithDriverValidation(&.{ 1, 11 });
    try device.markDriverReady();
    try device.disableConfigDriver();
    try device.noteConfigChanged();
    try device.enableConfigDriver();
    try device.acknowledgeConfigGeneration(1);
    try device.registerQueueCallback(2, 8, "rx_done");
    try device.configureQueueDescriptorShape(2, 3, 2, true);
    try device.noteInterruptReason(
        virtio_core.VirtioInterruptReason.queue_used |
            virtio_core.VirtioInterruptReason.config_change,
    );
    try device.acknowledgeInterrupt(virtio_core.VirtioInterruptReason.config_change);
    device.noteNeedsReset();

    const reset_summary = device.resetReplaySummary();
    try std.testing.expect(reset_summary.reset_required);
    try std.testing.expect(reset_summary.features_negotiated);
    try std.testing.expect(reset_summary.driver_ready);
    try std.testing.expectEqual(@as(usize, 1), reset_summary.registered_queue_count);
    try std.testing.expectEqual(virtio_core.VirtioInterruptReason.queue_used, reset_summary.pending_interrupt_reason_bits);
    try std.testing.expect(reset_summary.will_clear_negotiated_features);
    try std.testing.expect(reset_summary.will_clear_queue_callbacks);
    try std.testing.expect(reset_summary.will_clear_config_bookkeeping);
    try std.testing.expect(reset_summary.will_clear_interrupts);

    device.reset();

    const cleared_summary = device.resetReplaySummary();
    try std.testing.expect(!cleared_summary.reset_required);
    try std.testing.expect(!cleared_summary.features_negotiated);
    try std.testing.expect(!cleared_summary.driver_ready);
    try std.testing.expectEqual(@as(usize, 0), cleared_summary.registered_queue_count);
    try std.testing.expect(!cleared_summary.will_clear_negotiated_features);
    try std.testing.expect(!cleared_summary.will_clear_queue_callbacks);
    try std.testing.expect(!cleared_summary.will_clear_config_bookkeeping);
    try std.testing.expect(!cleared_summary.will_clear_interrupts);
}
