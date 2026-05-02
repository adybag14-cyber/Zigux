const std = @import("std");
const virtio = @import("virtio");

test "phase10 virtio core records device identity and feature negotiation" {
    const descriptor = virtio.VirtioCoreLabDevice.descriptor();
    try std.testing.expectEqualStrings("virtio_core_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_lab_validation);
    try std.testing.expect(!descriptor.touches_transport_mmio);

    var dev = try virtio.VirtioCoreLabDevice.init(&.{ 1, 9, 17 });
    try std.testing.expect(try dev.hasDeviceFeature(9));
    try std.testing.expect(!try dev.hasDeviceFeature(5));

    const identity = try dev.registerDeviceIdentity(4, 0x1041, 0x1af4);
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", identity.anchor);
    try std.testing.expectEqual(@as(u16, 4), identity.device_index);
    try std.testing.expectEqual(@as(u32, 0x1041), identity.device_id);
    try std.testing.expectEqual(@as(u32, 0x1af4), identity.vendor_id);
    try std.testing.expectEqualStrings("virtio4", identity.device_name);
    try std.testing.expectEqualStrings("virtio:d00001041v00001AF4", identity.modalias);
    try std.testing.expectError(error.DeviceIdentityAlreadyRegistered, dev.registerDeviceIdentity(5, 0x1042, 0x1af4));

    dev.acknowledge();
    try dev.attachDriver();
    try dev.offerDriverFeature(1);
    try dev.offerDriverFeature(17);

    const negotiation = try dev.finalizeFeatures();
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", negotiation.anchor);
    try std.testing.expectEqual(@as(usize, 2), negotiation.offered_feature_count);
    try std.testing.expectEqual(@as(usize, 2), negotiation.negotiated_feature_count);
    try std.testing.expect(negotiation.accepted_by_transport);
    try std.testing.expect(dev.hasStatus(virtio.DeviceStatus.features_ok));
    try std.testing.expect(try dev.hasNegotiatedFeature(17));

    try dev.markDriverReady();
    try std.testing.expect(dev.hasStatus(virtio.DeviceStatus.driver_ok));
    try std.testing.expectError(error.FeatureWindowClosed, dev.offerDriverFeature(9));
}

test "phase10 virtio core defers config changes until the core is re-enabled" {
    var dev = try virtio.VirtioCoreLabDevice.init(&.{3});
    dev.acknowledge();
    try dev.attachDriver();
    try dev.offerDriverFeature(3);
    _ = try dev.finalizeFeatures();

    var generation = dev.observeConfigGeneration();
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", generation.anchor);
    try std.testing.expectEqual(@as(u32, 0), generation.generation);
    try std.testing.expectEqual(@as(u32, 0), generation.last_observed_generation);
    try std.testing.expect(!generation.pending_generation);

    try dev.setConfigChangedHandlerPresent(true);
    try dev.disableConfigCore();
    try dev.noteConfigChanged();

    var change = dev.configChangeSummary();
    try std.testing.expect(!change.core_enabled);
    try std.testing.expect(!change.driver_disabled);
    try std.testing.expect(change.change_pending);
    try std.testing.expect(change.handler_present);
    try std.testing.expectEqual(@as(usize, 0), change.delivery_count);
    try std.testing.expectEqual(virtio.ConfigChangeDisposition.deferred_until_enabled, change.last_disposition);

    generation = dev.configGenerationSummary();
    try std.testing.expectEqual(@as(u32, 1), generation.generation);
    try std.testing.expectEqual(@as(u32, 0), generation.last_observed_generation);
    try std.testing.expect(generation.pending_generation);
    try std.testing.expect(change.change_pending);

    try dev.enableConfigCore();
    change = dev.configChangeSummary();
    try std.testing.expect(change.core_enabled);
    try std.testing.expect(!change.driver_disabled);
    try std.testing.expect(!change.change_pending);
    try std.testing.expectEqual(@as(usize, 1), change.delivery_count);
    try std.testing.expectEqual(virtio.ConfigChangeDisposition.delivered_to_handler, change.last_disposition);

    generation = dev.observeConfigGeneration();
    try std.testing.expectEqual(@as(u32, 1), generation.generation);
    try std.testing.expectEqual(@as(u32, 1), generation.last_observed_generation);
    try std.testing.expect(!generation.pending_generation);
}

test "phase10 virtio core tracks queue callback registration and descriptor shape" {
    var dev = try virtio.VirtioCoreLabDevice.init(&.{ 2, 7 });
    dev.acknowledge();
    try dev.attachDriver();
    try dev.offerDriverFeature(2);
    _ = try dev.finalizeFeatures();

    try dev.registerQueueCallback(1, 8, "req_done");
    try std.testing.expectEqual(@as(usize, 1), dev.registeredQueueCount());

    var queue = try dev.queueRegistrationSummary(1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", queue.anchor);
    try std.testing.expectEqual(@as(u16, 1), queue.queue_index);
    try std.testing.expectEqual(@as(u16, 8), queue.descriptor_count);
    try std.testing.expectEqualStrings("req_done", queue.callback_name);
    try std.testing.expect(queue.callback_enabled);
    try std.testing.expectEqual(@as(usize, 0), queue.callback_invocation_count);
    try std.testing.expectEqual(@as(usize, 0), queue.notification_count);

    try std.testing.expectError(error.QueueDescriptorShapeNotConfigured, dev.queueDescriptorShapeSummary(1));
    try dev.configureQueueDescriptorShape(1, 3, 2, true);

    const shape = try dev.queueDescriptorShapeSummary(1);
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", shape.anchor);
    try std.testing.expectEqual(@as(u16, 8), shape.descriptor_count);
    try std.testing.expectEqual(@as(u16, 3), shape.readable_descriptor_count);
    try std.testing.expectEqual(@as(u16, 2), shape.writable_descriptor_count);
    try std.testing.expect(shape.uses_indirect_descriptors);

    try dev.disableQueueCallback(1);
    try std.testing.expect(!(try dev.notifyQueueUsed(1)));
    queue = try dev.queueRegistrationSummary(1);
    try std.testing.expect(!queue.callback_enabled);
    try std.testing.expectEqual(@as(usize, 0), queue.callback_invocation_count);
    try std.testing.expectEqual(@as(usize, 1), queue.notification_count);

    try dev.enableQueueCallback(1);
    try std.testing.expect(try dev.notifyQueueUsed(1));
    queue = try dev.queueRegistrationSummary(1);
    try std.testing.expect(queue.callback_enabled);
    try std.testing.expectEqual(@as(usize, 1), queue.callback_invocation_count);
    try std.testing.expectEqual(@as(usize, 2), queue.notification_count);
}

test "phase10 virtio core removeDriver clears queue and config-change state" {
    var dev = try virtio.VirtioCoreLabDevice.init(&.{5});
    dev.acknowledge();
    try dev.attachDriver();
    try dev.offerDriverFeature(5);
    _ = try dev.finalizeFeatures();
    try dev.registerQueueCallback(0, 4, "cfg_done");
    try dev.setConfigChangedHandlerPresent(true);
    try dev.noteConfigChanged();

    const binding_before_remove = dev.driverBindingSummary();
    try std.testing.expect(binding_before_remove.driver_attached);
    try std.testing.expect(binding_before_remove.config_changed_handler_present);
    try std.testing.expectEqual(@as(usize, 1), binding_before_remove.delivery_count);

    const removed = try dev.removeDriver();
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", removed.anchor);
    try std.testing.expect(removed.driver_attached_before_remove);
    try std.testing.expectEqual(virtio.DeviceStatus.acknowledge, removed.status_after_remove);
    try std.testing.expect(!removed.config_core_enabled);
    try std.testing.expect(!removed.config_changed_handler_present);
    try std.testing.expectEqual(@as(usize, 0), removed.registered_queue_count);
    try std.testing.expectEqual(@as(usize, 0), dev.registeredQueueCount());
    try std.testing.expectError(error.QueueNotRegistered, dev.queueRegistrationSummary(0));

    const binding_after_remove = dev.driverBindingSummary();
    try std.testing.expect(!binding_after_remove.config_changed_handler_present);
    try std.testing.expect(!binding_after_remove.change_pending);
    try std.testing.expectEqual(@as(usize, 0), binding_after_remove.delivery_count);

    const generation = dev.configGenerationSummary();
    try std.testing.expectEqual(@as(u32, 0), generation.generation);
    try std.testing.expectEqual(@as(u32, 0), generation.last_observed_generation);
    try std.testing.expect(!generation.pending_generation);
}
