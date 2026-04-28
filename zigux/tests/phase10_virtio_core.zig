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

    var device = try virtio_core.VirtioCoreLabDevice.init(&.{9});
    device.acknowledge();
    try device.attachDriver();

    try std.testing.expectError(error.FeatureBitOutOfRange, device.offerDriverFeature(virtio_core.feature_bit_capacity));
    try std.testing.expectError(error.FeatureBitOutOfRange, device.hasDeviceFeature(virtio_core.feature_bit_capacity));
    try std.testing.expectError(error.FeatureBitOutOfRange, device.hasNegotiatedFeature(virtio_core.feature_bit_capacity));
}

test "phase10 virtio core tracks queue callback bookkeeping after features negotiation" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 1, 6 });

    device.acknowledge();
    try device.attachDriver();
    try device.offerDriverFeature(1);
    _ = try device.finalizeFeatures();

    try device.registerQueueCallback(2, 16, "rx_done");

    const summary = try device.queueRegistrationSummary(2);
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 2), summary.queue_index);
    try std.testing.expectEqual(@as(u16, 16), summary.descriptor_count);
    try std.testing.expectEqualStrings("rx_done", summary.callback_name);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(usize, 0), summary.callback_invocation_count);
    try std.testing.expectEqual(@as(usize, 0), summary.notification_count);
    try std.testing.expectEqual(@as(usize, 1), device.registeredQueueCount());
}

test "phase10 virtio core can disable and re-enable queue callbacks without transport glue" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 2, 9 });

    device.acknowledge();
    try device.attachDriver();
    try device.offerDriverFeature(9);
    _ = try device.finalizeFeatures();
    try device.registerQueueCallback(0, 8, "tx_done");

    try device.disableQueueCallback(0);
    try std.testing.expect(!(try device.notifyQueueUsed(0)));

    var summary = try device.queueRegistrationSummary(0);
    try std.testing.expect(!summary.callback_enabled);
    try std.testing.expectEqual(@as(usize, 0), summary.callback_invocation_count);
    try std.testing.expectEqual(@as(usize, 1), summary.notification_count);

    try device.enableQueueCallback(0);
    try std.testing.expect(try device.notifyQueueUsed(0));

    summary = try device.queueRegistrationSummary(0);
    try std.testing.expect(summary.callback_enabled);
    try std.testing.expectEqual(@as(usize, 1), summary.callback_invocation_count);
    try std.testing.expectEqual(@as(usize, 2), summary.notification_count);
}

test "phase10 virtio core keeps queue registration inside bounded feature and reset semantics" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 4, 10 });

    device.acknowledge();
    try device.attachDriver();
    try std.testing.expectError(error.MissingFeaturesOk, device.registerQueueCallback(1, 4, "before_ready"));

    try device.offerDriverFeature(4);
    _ = try device.finalizeFeatures();

    try std.testing.expectError(error.QueueIndexOutOfRange, device.registerQueueCallback(virtio_core.queue_capacity, 4, "overflow"));
    try std.testing.expectError(error.EmptyQueueDescriptorSet, device.registerQueueCallback(1, 0, "empty_desc"));
    try std.testing.expectError(error.EmptyQueueCallbackName, device.registerQueueCallback(1, 4, ""));

    try device.registerQueueCallback(1, 4, "control_done");
    try std.testing.expectError(error.QueueAlreadyRegistered, device.registerQueueCallback(1, 2, "duplicate"));
    try device.unregisterQueueCallback(1);
    try std.testing.expectEqual(@as(usize, 0), device.registeredQueueCount());
    try std.testing.expectError(error.QueueNotRegistered, device.queueRegistrationSummary(1));

    try device.registerQueueCallback(1, 4, "control_done");
    device.reset();
    try std.testing.expectEqual(@as(usize, 0), device.registeredQueueCount());
    try std.testing.expectError(error.QueueNotRegistered, device.queueRegistrationSummary(1));
}

test "phase10 virtio core records bounded queue descriptor shape metadata" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 5, 12 });

    device.acknowledge();
    try device.attachDriver();
    try device.offerDriverFeature(12);
    _ = try device.finalizeFeatures();
    try device.registerQueueCallback(3, 6, "input_done");

    try std.testing.expectError(error.QueueDescriptorShapeNotConfigured, device.queueDescriptorShapeSummary(3));

    try device.configureQueueDescriptorShape(3, 2, 3, true);
    const shape = try device.queueDescriptorShapeSummary(3);

    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", shape.anchor);
    try std.testing.expectEqual(@as(u16, 3), shape.queue_index);
    try std.testing.expectEqual(@as(u16, 6), shape.descriptor_count);
    try std.testing.expectEqual(@as(u16, 2), shape.readable_descriptor_count);
    try std.testing.expectEqual(@as(u16, 3), shape.writable_descriptor_count);
    try std.testing.expect(shape.uses_indirect_descriptors);
}

test "phase10 virtio core rejects invalid queue descriptor shapes and clears them on reset" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 7, 14 });

    device.acknowledge();
    try device.attachDriver();
    try device.offerDriverFeature(14);
    _ = try device.finalizeFeatures();
    try device.registerQueueCallback(1, 4, "control_done");

    try std.testing.expectError(error.EmptyQueueDescriptorShape, device.configureQueueDescriptorShape(1, 0, 0, false));
    try std.testing.expectError(error.QueueDescriptorShapeOverflow, device.configureQueueDescriptorShape(1, 2, 3, false));

    try device.configureQueueDescriptorShape(1, 1, 2, false);
    device.reset();

    try std.testing.expectError(error.QueueNotRegistered, device.queueDescriptorShapeSummary(1));
}

test "phase10 virtio core records bounded registration identity metadata from virtio.c" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 2, 5 });

    try std.testing.expectError(error.DeviceIdentityNotRegistered, device.deviceIdentitySummary());

    const identity = try device.registerDeviceIdentity(7, 0x1040, 0x1AF4);
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", identity.anchor);
    try std.testing.expectEqual(@as(u16, 7), identity.device_index);
    try std.testing.expectEqual(@as(u32, 0x1040), identity.device_id);
    try std.testing.expectEqual(@as(u32, 0x1AF4), identity.vendor_id);
    try std.testing.expectEqualStrings("virtio7", identity.device_name);
    try std.testing.expectEqualStrings("virtio:d00001040v00001AF4", identity.modalias);

    const summary = try device.deviceIdentitySummary();
    try std.testing.expectEqualStrings("virtio7", summary.device_name);
    try std.testing.expectEqualStrings("virtio:d00001040v00001AF4", summary.modalias);
}

test "phase10 virtio core keeps registration identity stable across reset and rejects duplicate registration" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 4, 11 });

    _ = try device.registerDeviceIdentity(3, 0x1000, 0x1AF4);
    try std.testing.expectError(error.DeviceIdentityAlreadyRegistered, device.registerDeviceIdentity(4, 0x1001, 0x1AF4));

    device.reset();
    const summary = try device.deviceIdentitySummary();
    try std.testing.expectEqual(@as(u16, 3), summary.device_index);
    try std.testing.expectEqualStrings("virtio3", summary.device_name);
    try std.testing.expectEqualStrings("virtio:d00001000v00001AF4", summary.modalias);
}

test "phase10 virtio core delivers config changes immediately when core and driver paths are enabled" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 2, 5 });

    device.acknowledge();
    try device.attachDriver();
    try device.setConfigChangedHandlerPresent(true);

    try device.noteConfigChanged();
    const summary = device.configChangeSummary();

    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", summary.anchor);
    try std.testing.expect(summary.core_enabled);
    try std.testing.expect(!summary.driver_disabled);
    try std.testing.expect(!summary.change_pending);
    try std.testing.expectEqual(@as(usize, 1), summary.delivery_count);
}

test "phase10 virtio core keeps config changes pending while the driver path is disabled and flushes on enable" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 3, 9 });

    device.acknowledge();
    try device.attachDriver();
    try device.setConfigChangedHandlerPresent(true);
    try device.disableConfigDriver();
    try device.noteConfigChanged();

    var summary = device.configChangeSummary();
    try std.testing.expect(summary.core_enabled);
    try std.testing.expect(summary.driver_disabled);
    try std.testing.expect(summary.change_pending);
    try std.testing.expectEqual(@as(usize, 0), summary.delivery_count);

    try device.enableConfigDriver();
    summary = device.configChangeSummary();
    try std.testing.expect(!summary.driver_disabled);
    try std.testing.expect(!summary.change_pending);
    try std.testing.expectEqual(@as(usize, 1), summary.delivery_count);

    try device.disableConfigDriver();
    try device.noteConfigChanged();
    device.reset();

    summary = device.configChangeSummary();
    try std.testing.expect(summary.core_enabled);
    try std.testing.expect(!summary.driver_disabled);
    try std.testing.expect(!summary.change_pending);
    try std.testing.expectEqual(@as(usize, 0), summary.delivery_count);
}

test "phase10 virtio core does not fabricate config delivery when driver re-enables without pending change" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 3, 9 });

    device.acknowledge();
    try device.attachDriver();

    var summary = device.configChangeSummary();
    try std.testing.expectEqual(@as(usize, 0), summary.delivery_count);
    try std.testing.expect(!summary.change_pending);

    try device.disableConfigDriver();
    summary = device.configChangeSummary();
    try std.testing.expect(summary.driver_disabled);
    try std.testing.expectEqual(@as(usize, 0), summary.delivery_count);
    try std.testing.expect(!summary.change_pending);

    try device.enableConfigDriver();
    summary = device.configChangeSummary();
    try std.testing.expect(!summary.driver_disabled);
    try std.testing.expectEqual(@as(usize, 0), summary.delivery_count);
    try std.testing.expect(!summary.change_pending);
}

test "phase10 virtio core records bounded driver binding around config_changed" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 4, 12 });

    device.acknowledge();
    try device.attachDriver();

    var summary = device.driverBindingSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", summary.anchor);
    try std.testing.expect(summary.driver_attached);
    try std.testing.expect(!summary.config_changed_handler_present);
    try std.testing.expect(!summary.change_pending);
    try std.testing.expectEqual(@as(usize, 0), summary.delivery_count);

    try device.setConfigChangedHandlerPresent(true);
    summary = device.driverBindingSummary();
    try std.testing.expect(summary.driver_attached);
    try std.testing.expect(summary.config_changed_handler_present);
    try std.testing.expect(!summary.change_pending);
    try std.testing.expectEqual(@as(usize, 0), summary.delivery_count);

    device.reset();
    summary = device.driverBindingSummary();
    try std.testing.expect(!summary.driver_attached);
    try std.testing.expect(!summary.config_changed_handler_present);
    try std.testing.expect(!summary.change_pending);
    try std.testing.expectEqual(@as(usize, 0), summary.delivery_count);
}

test "phase10 virtio core keeps config changes pending while the core path is disabled and clears them on reset" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 4, 11 });

    device.acknowledge();
    try device.attachDriver();
    try device.setConfigChangedHandlerPresent(true);
    try device.disableConfigCore();
    try device.noteConfigChanged();

    var summary = device.configChangeSummary();
    try std.testing.expect(!summary.core_enabled);
    try std.testing.expect(!summary.driver_disabled);
    try std.testing.expect(summary.change_pending);
    try std.testing.expectEqual(@as(usize, 0), summary.delivery_count);

    try device.enableConfigCore();
    summary = device.configChangeSummary();
    try std.testing.expect(summary.core_enabled);
    try std.testing.expect(!summary.change_pending);
    try std.testing.expectEqual(@as(usize, 1), summary.delivery_count);

    try device.disableConfigCore();
    try device.noteConfigChanged();
    device.reset();

    summary = device.configChangeSummary();
    try std.testing.expect(summary.core_enabled);
    try std.testing.expect(!summary.driver_disabled);
    try std.testing.expect(!summary.change_pending);
    try std.testing.expectEqual(@as(usize, 0), summary.delivery_count);
}

test "phase10 virtio core does not fabricate config delivery when core re-enables without pending change" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 4, 11 });

    device.acknowledge();
    try device.attachDriver();

    var summary = device.configChangeSummary();
    try std.testing.expectEqual(@as(usize, 0), summary.delivery_count);
    try std.testing.expect(!summary.change_pending);

    try device.disableConfigCore();
    summary = device.configChangeSummary();
    try std.testing.expect(!summary.core_enabled);
    try std.testing.expectEqual(@as(usize, 0), summary.delivery_count);
    try std.testing.expect(!summary.change_pending);

    try device.enableConfigCore();
    summary = device.configChangeSummary();
    try std.testing.expect(summary.core_enabled);
    try std.testing.expectEqual(@as(usize, 0), summary.delivery_count);
    try std.testing.expect(!summary.change_pending);
}

test "phase10 virtio core keeps enabled config changes inert without a config_changed handler" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 6, 13 });

    device.acknowledge();
    try device.attachDriver();
    try device.noteConfigChanged();

    const binding = device.driverBindingSummary();
    const summary = device.configChangeSummary();
    try std.testing.expect(binding.driver_attached);
    try std.testing.expect(!binding.config_changed_handler_present);
    try std.testing.expect(!binding.change_pending);
    try std.testing.expectEqual(@as(usize, 0), binding.delivery_count);
    try std.testing.expect(summary.core_enabled);
    try std.testing.expect(!summary.driver_disabled);
    try std.testing.expect(!summary.change_pending);
    try std.testing.expectEqual(@as(usize, 0), summary.delivery_count);
}

test "phase10 virtio core records config generation while change delivery is deferred" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 6, 13 });

    device.acknowledge();
    try device.attachDriver();
    try device.setConfigChangedHandlerPresent(true);

    var summary = device.configGenerationSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 0), summary.generation);
    try std.testing.expectEqual(@as(u32, 0), summary.last_observed_generation);
    try std.testing.expect(!summary.pending_generation);
    try std.testing.expect(summary.core_enabled);
    try std.testing.expect(!summary.driver_disabled);
    try std.testing.expect(!summary.change_pending);

    try device.disableConfigDriver();
    try device.noteConfigChanged();

    summary = device.configGenerationSummary();
    try std.testing.expectEqual(@as(u32, 1), summary.generation);
    try std.testing.expectEqual(@as(u32, 0), summary.last_observed_generation);
    try std.testing.expect(summary.pending_generation);
    try std.testing.expect(summary.driver_disabled);
    try std.testing.expect(summary.change_pending);
}

test "phase10 virtio core observes config generation after deferred and immediate changes" {
    var device = try virtio_core.VirtioCoreLabDevice.init(&.{ 7, 15 });

    device.acknowledge();
    try device.attachDriver();
    try device.setConfigChangedHandlerPresent(true);
    try device.disableConfigCore();
    try device.noteConfigChanged();

    var summary = device.observeConfigGeneration();
    try std.testing.expectEqual(@as(u32, 1), summary.generation);
    try std.testing.expectEqual(@as(u32, 1), summary.last_observed_generation);
    try std.testing.expect(!summary.pending_generation);
    try std.testing.expect(!summary.core_enabled);
    try std.testing.expect(summary.change_pending);

    try device.enableConfigCore();
    summary = device.configGenerationSummary();
    try std.testing.expectEqual(@as(usize, 1), device.configChangeSummary().delivery_count);
    try std.testing.expectEqual(@as(u32, 1), summary.generation);
    try std.testing.expectEqual(@as(u32, 1), summary.last_observed_generation);
    try std.testing.expect(!summary.pending_generation);
    try std.testing.expect(summary.core_enabled);
    try std.testing.expect(!summary.change_pending);

    try device.noteConfigChanged();
    summary = device.configGenerationSummary();
    try std.testing.expectEqual(@as(u32, 2), summary.generation);
    try std.testing.expectEqual(@as(u32, 1), summary.last_observed_generation);
    try std.testing.expect(summary.pending_generation);
    try std.testing.expect(!summary.change_pending);

    summary = device.observeConfigGeneration();
    try std.testing.expectEqual(@as(u32, 2), summary.generation);
    try std.testing.expectEqual(@as(u32, 2), summary.last_observed_generation);
    try std.testing.expect(!summary.pending_generation);

    device.reset();
    summary = device.configGenerationSummary();
    try std.testing.expectEqual(@as(u32, 0), summary.generation);
    try std.testing.expectEqual(@as(u32, 0), summary.last_observed_generation);
    try std.testing.expect(!summary.pending_generation);
}
