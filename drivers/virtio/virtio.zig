const std = @import("std");

pub const feature_bit_capacity: u16 = 128;
pub const queue_capacity: usize = 8;
pub const any_id: u32 = 0xffff_ffff;

pub const DeviceStatus = struct {
    pub const acknowledge: u8 = 1;
    pub const driver: u8 = 2;
    pub const driver_ok: u8 = 4;
    pub const features_ok: u8 = 8;
    pub const device_needs_reset: u8 = 64;
    pub const failed: u8 = 128;
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_lab_validation: bool,
    touches_transport_mmio: bool,
};

pub const NegotiationSummary = struct {
    anchor: []const u8,
    driver_status: u8,
    offered_feature_count: usize,
    negotiated_feature_count: usize,
    accepted_by_transport: bool,
};

pub const DriverValidationReplaySummary = struct {
    anchor: []const u8,
    driver_status: u8,
    offered_feature_count: usize,
    validated_feature_count: usize,
    negotiated_feature_count: usize,
    finalize_count: usize,
    validation_replayed_finalize: bool,
    accepted_by_transport: bool,
};

pub const QueueRegistrationSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    descriptor_count: u16,
    callback_name: []const u8,
    callback_enabled: bool,
    callback_invocation_count: usize,
    notification_count: usize,
};

pub const QueueDescriptorShapeSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    descriptor_count: u16,
    readable_descriptor_count: u16,
    writable_descriptor_count: u16,
    uses_indirect_descriptors: bool,
};

pub const DeviceIdentitySummary = struct {
    anchor: []const u8,
    device_index: u16,
    device_id: u32,
    vendor_id: u32,
    device_name: []const u8,
    modalias: []const u8,
};

pub const ConfigChangeDisposition = enum {
    none,
    deferred_until_enabled,
    delivered_to_handler,
    ignored_without_handler,
};

pub const ConfigChangeSummary = struct {
    anchor: []const u8,
    core_enabled: bool,
    driver_disabled: bool,
    change_pending: bool,
    handler_present: bool,
    delivery_count: usize,
    last_disposition: ConfigChangeDisposition,
};

pub const ConfigGenerationSummary = struct {
    anchor: []const u8,
    generation: u32,
    last_observed_generation: u32,
    pending_generation: bool,
    core_enabled: bool,
    driver_disabled: bool,
    change_pending: bool,
};

pub const DriverBindingSummary = struct {
    anchor: []const u8,
    driver_attached: bool,
    config_changed_handler_present: bool,
    change_pending: bool,
    delivery_count: usize,
};

pub const DriverRemoveSummary = struct {
    anchor: []const u8,
    driver_attached_before_remove: bool,
    status_after_remove: u8,
    config_core_enabled: bool,
    config_changed_handler_present: bool,
    registered_queue_count: usize,
};

pub const DriverIdMatchRule = struct {
    device_id: u32,
    vendor_id: u32,
};

pub const DriverIdMatchSummary = struct {
    anchor: []const u8,
    device_id: u32,
    vendor_id: u32,
    candidate_count: usize,
    matched: bool,
    matched_rule_index: ?usize,
    matched_device_any: bool,
    matched_vendor_any: bool,
};

pub const VirtioCoreLabDevice = struct {
    const Self = @This();
    const FeatureSet = std.StaticBitSet(feature_bit_capacity);
    const QueueSlot = struct {
        active: bool = false,
        descriptor_count: u16 = 0,
        callback_name: []const u8 = "",
        callback_enabled: bool = false,
        callback_invocation_count: usize = 0,
        notification_count: usize = 0,
        readable_descriptor_count: u16 = 0,
        writable_descriptor_count: u16 = 0,
        uses_indirect_descriptors: bool = false,
    };
    const device_name_capacity: usize = 16;
    const modalias_capacity: usize = 32;

    status: u8 = 0,
    device_features: FeatureSet = FeatureSet.initEmpty(),
    driver_features: FeatureSet = FeatureSet.initEmpty(),
    negotiated_features: FeatureSet = FeatureSet.initEmpty(),
    device_identity_registered: bool = false,
    device_index: u16 = 0,
    device_id: u32 = 0,
    vendor_id: u32 = 0,
    device_name_buffer: [device_name_capacity]u8 = [_]u8{0} ** device_name_capacity,
    device_name_len: usize = 0,
    modalias_buffer: [modalias_capacity]u8 = [_]u8{0} ** modalias_capacity,
    modalias_len: usize = 0,
    queues: [queue_capacity]QueueSlot = [_]QueueSlot{QueueSlot{}} ** queue_capacity,
    config_core_enabled: bool = true,
    config_driver_disabled: bool = false,
    config_change_pending: bool = false,
    config_change_delivery_count: usize = 0,
    last_config_change_disposition: ConfigChangeDisposition = .none,
    config_generation: u32 = 0,
    last_observed_generation: u32 = 0,
    config_changed_handler_present: bool = false,
    transport_accepts_features: bool = true,
    registered_queue_count: usize = 0,
    reset_count: usize = 0,
    finalize_count: usize = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "virtio_core_lab",
            .anchor = "drivers/virtio/virtio.c",
            .provides_lab_validation = true,
            .touches_transport_mmio = false,
        };
    }

    pub fn init(device_feature_bits: []const u16) !Self {
        var self = Self{};
        for (device_feature_bits) |feature_bit| {
            const index = try checkedFeatureIndex(feature_bit);
            self.device_features.set(index);
        }
        return self;
    }

    pub fn reset(self: *Self) void {
        self.status = 0;
        self.driver_features = FeatureSet.initEmpty();
        self.negotiated_features = FeatureSet.initEmpty();
        self.queues = [_]QueueSlot{QueueSlot{}} ** queue_capacity;
        self.config_core_enabled = true;
        self.config_driver_disabled = false;
        self.config_change_pending = false;
        self.config_change_delivery_count = 0;
        self.last_config_change_disposition = .none;
        self.config_generation = 0;
        self.last_observed_generation = 0;
        self.config_changed_handler_present = false;
        self.registered_queue_count = 0;
        self.reset_count += 1;
    }

    pub fn registerDeviceIdentity(
        self: *Self,
        device_index: u16,
        device_id: u32,
        vendor_id: u32,
    ) !DeviceIdentitySummary {
        if (self.device_identity_registered) return error.DeviceIdentityAlreadyRegistered;

        self.device_index = device_index;
        self.device_id = device_id;
        self.vendor_id = vendor_id;
        self.device_name_len = (try std.fmt.bufPrint(&self.device_name_buffer, "virtio{d}", .{device_index})).len;
        self.modalias_len = (try std.fmt.bufPrint(
            &self.modalias_buffer,
            "virtio:d{X:0>8}v{X:0>8}",
            .{ device_id, vendor_id },
        )).len;
        self.device_identity_registered = true;

        return self.deviceIdentitySummary();
    }

    pub fn acknowledge(self: *Self) void {
        self.status |= DeviceStatus.acknowledge;
    }

    pub fn attachDriver(self: *Self) !void {
        if (!self.hasStatus(DeviceStatus.acknowledge)) return error.MissingAcknowledge;
        self.status |= DeviceStatus.driver;
    }

    pub fn offerDriverFeature(self: *Self, feature_bit: u16) !void {
        if (!self.hasStatus(DeviceStatus.driver)) return error.DriverNotAttached;
        if (self.hasStatus(DeviceStatus.features_ok) or self.hasStatus(DeviceStatus.driver_ok)) {
            return error.FeatureWindowClosed;
        }

        const index = try checkedFeatureIndex(feature_bit);
        if (!self.device_features.isSet(index)) return error.DriverOfferedUnsupportedFeature;

        self.driver_features.set(index);
    }

    pub fn finalizeFeatures(self: *Self) !NegotiationSummary {
        if (!self.hasStatus(DeviceStatus.driver)) return error.DriverNotAttached;

        self.finalize_count += 1;
        self.negotiated_features = FeatureSet.initEmpty();
        self.status &= ~DeviceStatus.features_ok;

        if (self.transport_accepts_features) {
            self.negotiated_features = self.driver_features;
            self.status |= DeviceStatus.features_ok;
        }

        return .{
            .anchor = descriptor().anchor,
            .driver_status = self.status,
            .offered_feature_count = self.driver_features.count(),
            .negotiated_feature_count = self.negotiated_features.count(),
            .accepted_by_transport = self.hasStatus(DeviceStatus.features_ok),
        };
    }

    pub fn finalizeFeaturesWithDriverValidation(
        self: *Self,
        validated_feature_bits: []const u16,
    ) !DriverValidationReplaySummary {
        if (!self.hasStatus(DeviceStatus.driver)) return error.DriverNotAttached;
        if (self.hasStatus(DeviceStatus.features_ok) or self.hasStatus(DeviceStatus.driver_ok)) {
            return error.FeatureWindowClosed;
        }

        var validated_features = FeatureSet.initEmpty();
        for (validated_feature_bits) |feature_bit| {
            const index = try checkedFeatureIndex(feature_bit);
            if (!self.driver_features.isSet(index)) return error.ValidationSelectedUnofferedFeature;
            validated_features.set(index);
        }

        self.finalize_count += 1;
        const validation_replayed_finalize = !featureSetsEqual(self.driver_features, validated_features);
        if (validation_replayed_finalize) {
            self.finalize_count += 1;
        }

        self.negotiated_features = FeatureSet.initEmpty();
        self.status &= ~DeviceStatus.features_ok;

        if (self.transport_accepts_features) {
            self.negotiated_features = validated_features;
            self.status |= DeviceStatus.features_ok;
        }

        return .{
            .anchor = descriptor().anchor,
            .driver_status = self.status,
            .offered_feature_count = self.driver_features.count(),
            .validated_feature_count = validated_features.count(),
            .negotiated_feature_count = self.negotiated_features.count(),
            .finalize_count = self.finalize_count,
            .validation_replayed_finalize = validation_replayed_finalize,
            .accepted_by_transport = self.hasStatus(DeviceStatus.features_ok),
        };
    }

    pub fn markDriverReady(self: *Self) !void {
        if (!self.hasStatus(DeviceStatus.acknowledge)) return error.MissingAcknowledge;
        if (!self.hasStatus(DeviceStatus.driver)) return error.DriverNotAttached;
        if (!self.hasStatus(DeviceStatus.features_ok)) return error.MissingFeaturesOk;

        self.status |= DeviceStatus.driver_ok;
    }

    pub fn fail(self: *Self) void {
        self.status |= DeviceStatus.failed;
    }

    pub fn noteNeedsReset(self: *Self) void {
        self.status |= DeviceStatus.device_needs_reset;
    }

    pub fn setTransportFeatureAcceptance(self: *Self, accept: bool) void {
        self.transport_accepts_features = accept;
    }

    pub fn hasStatus(self: *const Self, status_bit: u8) bool {
        return (self.status & status_bit) != 0;
    }

    pub fn hasNegotiatedFeature(self: *const Self, feature_bit: u16) !bool {
        const index = try checkedFeatureIndex(feature_bit);
        return self.negotiated_features.isSet(index);
    }

    pub fn hasDeviceFeature(self: *const Self, feature_bit: u16) !bool {
        const index = try checkedFeatureIndex(feature_bit);
        return self.device_features.isSet(index);
    }

    pub fn registerQueueCallback(
        self: *Self,
        queue_index: u16,
        descriptor_count: u16,
        callback_name: []const u8,
    ) !void {
        if (!self.hasStatus(DeviceStatus.driver)) return error.DriverNotAttached;
        if (!self.hasStatus(DeviceStatus.features_ok)) return error.MissingFeaturesOk;
        if (descriptor_count == 0) return error.EmptyQueueDescriptorSet;
        if (callback_name.len == 0) return error.EmptyQueueCallbackName;

        const index = try checkedQueueIndex(queue_index);
        const slot = &self.queues[index];
        if (slot.active) return error.QueueAlreadyRegistered;

        slot.* = .{
            .active = true,
            .descriptor_count = descriptor_count,
            .callback_name = callback_name,
            .callback_enabled = true,
        };
        self.registered_queue_count += 1;
    }

    pub fn unregisterQueueCallback(self: *Self, queue_index: u16) !void {
        const index = try checkedQueueIndex(queue_index);
        const slot = &self.queues[index];
        if (!slot.active) return error.QueueNotRegistered;

        slot.* = QueueSlot{};
        self.registered_queue_count -= 1;
    }

    pub fn disableQueueCallback(self: *Self, queue_index: u16) !void {
        const slot = try self.checkedQueueSlot(queue_index);
        slot.callback_enabled = false;
    }

    pub fn enableQueueCallback(self: *Self, queue_index: u16) !void {
        const slot = try self.checkedQueueSlot(queue_index);
        slot.callback_enabled = true;
    }

    pub fn notifyQueueUsed(self: *Self, queue_index: u16) !bool {
        const slot = try self.checkedQueueSlot(queue_index);
        slot.notification_count += 1;
        if (!slot.callback_enabled) return false;

        slot.callback_invocation_count += 1;
        return true;
    }

    pub fn queueRegistrationSummary(self: *const Self, queue_index: u16) !QueueRegistrationSummary {
        const index = try checkedQueueIndex(queue_index);
        const slot = self.queues[index];
        if (!slot.active) return error.QueueNotRegistered;

        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .descriptor_count = slot.descriptor_count,
            .callback_name = slot.callback_name,
            .callback_enabled = slot.callback_enabled,
            .callback_invocation_count = slot.callback_invocation_count,
            .notification_count = slot.notification_count,
        };
    }

    pub fn configureQueueDescriptorShape(
        self: *Self,
        queue_index: u16,
        readable_descriptor_count: u16,
        writable_descriptor_count: u16,
        uses_indirect_descriptors: bool,
    ) !void {
        const slot = try self.checkedQueueSlot(queue_index);
        if (readable_descriptor_count == 0 and writable_descriptor_count == 0) {
            return error.EmptyQueueDescriptorShape;
        }

        const total_descriptor_count = @as(u32, readable_descriptor_count) + @as(u32, writable_descriptor_count);
        if (total_descriptor_count > slot.descriptor_count) return error.QueueDescriptorShapeOverflow;

        slot.readable_descriptor_count = readable_descriptor_count;
        slot.writable_descriptor_count = writable_descriptor_count;
        slot.uses_indirect_descriptors = uses_indirect_descriptors;
    }

    pub fn queueDescriptorShapeSummary(self: *const Self, queue_index: u16) !QueueDescriptorShapeSummary {
        const index = try checkedQueueIndex(queue_index);
        const slot = self.queues[index];
        if (!slot.active) return error.QueueNotRegistered;
        if (slot.readable_descriptor_count == 0 and slot.writable_descriptor_count == 0) {
            return error.QueueDescriptorShapeNotConfigured;
        }

        return .{
            .anchor = descriptor().anchor,
            .queue_index = queue_index,
            .descriptor_count = slot.descriptor_count,
            .readable_descriptor_count = slot.readable_descriptor_count,
            .writable_descriptor_count = slot.writable_descriptor_count,
            .uses_indirect_descriptors = slot.uses_indirect_descriptors,
        };
    }

    pub fn deviceIdentitySummary(self: *const Self) !DeviceIdentitySummary {
        if (!self.device_identity_registered) return error.DeviceIdentityNotRegistered;

        return .{
            .anchor = descriptor().anchor,
            .device_index = self.device_index,
            .device_id = self.device_id,
            .vendor_id = self.vendor_id,
            .device_name = self.device_name_buffer[0..self.device_name_len],
            .modalias = self.modalias_buffer[0..self.modalias_len],
        };
    }

    pub fn disableConfigDriver(self: *Self) !void {
        if (!self.hasStatus(DeviceStatus.driver)) return error.DriverNotAttached;
        if (self.config_driver_disabled) return error.ConfigDriverAlreadyDisabled;
        self.config_driver_disabled = true;
    }

    pub fn enableConfigDriver(self: *Self) !void {
        if (!self.hasStatus(DeviceStatus.driver)) return error.DriverNotAttached;
        if (!self.config_driver_disabled) return error.ConfigDriverAlreadyEnabled;
        self.config_driver_disabled = false;
        self.flushPendingConfigChange();
    }

    pub fn disableConfigCore(self: *Self) !void {
        if (!self.hasStatus(DeviceStatus.driver)) return error.DriverNotAttached;
        self.config_core_enabled = false;
    }

    pub fn enableConfigCore(self: *Self) !void {
        if (!self.hasStatus(DeviceStatus.driver)) return error.DriverNotAttached;
        self.config_core_enabled = true;
        self.flushPendingConfigChange();
    }

    pub fn setConfigChangedHandlerPresent(self: *Self, present: bool) !void {
        if (!self.hasStatus(DeviceStatus.driver)) return error.DriverNotAttached;
        self.config_changed_handler_present = present;
    }

    pub fn noteConfigChanged(self: *Self) !void {
        if (!self.hasStatus(DeviceStatus.driver)) return error.DriverNotAttached;
        self.config_generation +%= 1;
        self.handleConfigChanged();
    }

    pub fn configChangeSummary(self: *const Self) ConfigChangeSummary {
        return .{
            .anchor = descriptor().anchor,
            .core_enabled = self.config_core_enabled,
            .driver_disabled = self.config_driver_disabled,
            .change_pending = self.config_change_pending,
            .handler_present = self.config_changed_handler_present,
            .delivery_count = self.config_change_delivery_count,
            .last_disposition = self.last_config_change_disposition,
        };
    }

    pub fn observeConfigGeneration(self: *Self) ConfigGenerationSummary {
        self.last_observed_generation = self.config_generation;
        return self.configGenerationSummary();
    }

    pub fn configGenerationSummary(self: *const Self) ConfigGenerationSummary {
        return .{
            .anchor = descriptor().anchor,
            .generation = self.config_generation,
            .last_observed_generation = self.last_observed_generation,
            .pending_generation = self.last_observed_generation != self.config_generation,
            .core_enabled = self.config_core_enabled,
            .driver_disabled = self.config_driver_disabled,
            .change_pending = self.config_change_pending,
        };
    }

    pub fn driverBindingSummary(self: *const Self) DriverBindingSummary {
        return .{
            .anchor = descriptor().anchor,
            .driver_attached = self.hasStatus(DeviceStatus.driver),
            .config_changed_handler_present = self.config_changed_handler_present,
            .change_pending = self.config_change_pending,
            .delivery_count = self.config_change_delivery_count,
        };
    }

    pub fn removeDriver(self: *Self) !DriverRemoveSummary {
        if (!self.hasStatus(DeviceStatus.driver)) return error.DriverNotAttached;

        self.config_core_enabled = false;
        self.config_driver_disabled = false;
        self.config_change_pending = false;
        self.config_change_delivery_count = 0;
        self.last_config_change_disposition = .none;
        self.config_generation = 0;
        self.last_observed_generation = 0;
        self.config_changed_handler_present = false;
        self.driver_features = FeatureSet.initEmpty();
        self.negotiated_features = FeatureSet.initEmpty();
        self.queues = [_]QueueSlot{QueueSlot{}} ** queue_capacity;
        self.registered_queue_count = 0;
        self.status = DeviceStatus.acknowledge;

        return .{
            .anchor = descriptor().anchor,
            .driver_attached_before_remove = true,
            .status_after_remove = self.status,
            .config_core_enabled = self.config_core_enabled,
            .config_changed_handler_present = self.config_changed_handler_present,
            .registered_queue_count = self.registered_queue_count,
        };
    }

    pub fn driverIdMatchSummary(
        self: *const Self,
        rules: []const DriverIdMatchRule,
    ) !DriverIdMatchSummary {
        if (!self.device_identity_registered) return error.DeviceIdentityNotRegistered;

        for (rules, 0..) |rule, index| {
            const device_matches = rule.device_id == self.device_id or rule.device_id == any_id;
            if (!device_matches) continue;

            const vendor_matches = rule.vendor_id == self.vendor_id or rule.vendor_id == any_id;
            if (!vendor_matches) continue;

            return .{
                .anchor = descriptor().anchor,
                .device_id = self.device_id,
                .vendor_id = self.vendor_id,
                .candidate_count = rules.len,
                .matched = true,
                .matched_rule_index = index,
                .matched_device_any = rule.device_id == any_id,
                .matched_vendor_any = rule.vendor_id == any_id,
            };
        }

        return .{
            .anchor = descriptor().anchor,
            .device_id = self.device_id,
            .vendor_id = self.vendor_id,
            .candidate_count = rules.len,
            .matched = false,
            .matched_rule_index = null,
            .matched_device_any = false,
            .matched_vendor_any = false,
        };
    }

    pub fn registeredQueueCount(self: *const Self) usize {
        return self.registered_queue_count;
    }

    fn handleConfigChanged(self: *Self) void {
        if (!self.config_core_enabled or self.config_driver_disabled) {
            self.config_change_pending = true;
            self.last_config_change_disposition = .deferred_until_enabled;
            return;
        }

        if (self.config_changed_handler_present) {
            self.config_change_pending = false;
            self.config_change_delivery_count += 1;
            self.last_config_change_disposition = .delivered_to_handler;
            return;
        }

        self.config_change_pending = false;
        self.last_config_change_disposition = .ignored_without_handler;
    }

    fn flushPendingConfigChange(self: *Self) void {
        if (!self.config_change_pending) return;
        self.handleConfigChanged();
    }

    fn checkedFeatureIndex(feature_bit: u16) !usize {
        if (feature_bit >= feature_bit_capacity) return error.FeatureBitOutOfRange;
        return @intCast(feature_bit);
    }

    fn checkedQueueIndex(queue_index: u16) !usize {
        if (queue_index >= queue_capacity) return error.QueueIndexOutOfRange;
        return @intCast(queue_index);
    }

    fn checkedQueueSlot(self: *Self, queue_index: u16) !*QueueSlot {
        const index = try checkedQueueIndex(queue_index);
        const slot = &self.queues[index];
        if (!slot.active) return error.QueueNotRegistered;
        return slot;
    }

    fn featureSetsEqual(lhs: FeatureSet, rhs: FeatureSet) bool {
        var index: usize = 0;
        while (index < feature_bit_capacity) : (index += 1) {
            if (lhs.isSet(index) != rhs.isSet(index)) return false;
        }
        return true;
    }
};

test "phase10 virtio core validation replay narrows negotiated features and reruns finalize" {
    var device = try VirtioCoreLabDevice.init(&.{ 1, 7, 33 });

    device.acknowledge();
    try device.attachDriver();
    try device.offerDriverFeature(1);
    try device.offerDriverFeature(7);
    try device.offerDriverFeature(33);

    const summary = try device.finalizeFeaturesWithDriverValidation(&.{ 1, 33 });
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", summary.anchor);
    try std.testing.expect(summary.accepted_by_transport);
    try std.testing.expect(summary.validation_replayed_finalize);
    try std.testing.expectEqual(@as(usize, 3), summary.offered_feature_count);
    try std.testing.expectEqual(@as(usize, 2), summary.validated_feature_count);
    try std.testing.expectEqual(@as(usize, 2), summary.negotiated_feature_count);
    try std.testing.expectEqual(@as(usize, 2), summary.finalize_count);
    try std.testing.expect(device.hasStatus(DeviceStatus.features_ok));
    try std.testing.expect(try device.hasNegotiatedFeature(1));
    try std.testing.expect(!(try device.hasNegotiatedFeature(7)));
    try std.testing.expect(try device.hasNegotiatedFeature(33));
}

test "phase10 virtio core validation replay stays single-pass when validation keeps offered features" {
    var device = try VirtioCoreLabDevice.init(&.{ 2, 5 });

    device.acknowledge();
    try device.attachDriver();
    try device.offerDriverFeature(2);
    try device.offerDriverFeature(5);

    const summary = try device.finalizeFeaturesWithDriverValidation(&.{ 2, 5 });
    try std.testing.expect(summary.accepted_by_transport);
    try std.testing.expect(!summary.validation_replayed_finalize);
    try std.testing.expectEqual(@as(usize, 2), summary.offered_feature_count);
    try std.testing.expectEqual(@as(usize, 2), summary.validated_feature_count);
    try std.testing.expectEqual(@as(usize, 2), summary.negotiated_feature_count);
    try std.testing.expectEqual(@as(usize, 1), summary.finalize_count);
    try std.testing.expect(try device.hasNegotiatedFeature(2));
    try std.testing.expect(try device.hasNegotiatedFeature(5));
}

test "phase10 virtio core validation replay rejects features the driver never offered" {
    var device = try VirtioCoreLabDevice.init(&.{ 3, 9 });

    device.acknowledge();
    try device.attachDriver();
    try device.offerDriverFeature(3);

    try std.testing.expectError(
        error.ValidationSelectedUnofferedFeature,
        device.finalizeFeaturesWithDriverValidation(&.{ 3, 9 }),
    );
    try std.testing.expectEqual(@as(usize, 0), device.finalize_count);
    try std.testing.expect(!(try device.hasNegotiatedFeature(3)));
}
