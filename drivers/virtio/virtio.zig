const std = @import("std");

pub const feature_bit_capacity: u16 = 128;
pub const queue_capacity: usize = 8;
pub const default_driver_name = "anonymous_driver";

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

pub const DriverBindingSummary = struct {
    anchor: []const u8,
    driver_name: []const u8,
    driver_attached: bool,
    features_negotiated: bool,
    driver_ready: bool,
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

pub const ConfigChangeSummary = struct {
    anchor: []const u8,
    reset_required: bool,
    core_enabled: bool,
    driver_disabled: bool,
    change_pending: bool,
    generation: u32,
    acknowledged_generation: u32,
    has_unacknowledged_generation: bool,
    delivery_count: usize,
};

pub const InterruptAckSummary = struct {
    anchor: []const u8,
    reset_required: bool,
    interrupt_pending: bool,
    pending_reason_bits: u8,
    acknowledged_reason_bits: u8,
    ack_count: usize,
    unacknowledged_interrupt_count: usize,
};

pub const DriverLifecycleBlocker = enum {
    missing_acknowledge,
    reset_required,
    driver_not_attached,
    feature_negotiation_incomplete,
    driver_not_ready,
    no_registered_queues,
};

pub const LifecycleGuardSummary = struct {
    anchor: []const u8,
    driver_name: []const u8,
    has_acknowledge: bool,
    driver_attached: bool,
    features_negotiated: bool,
    driver_ready: bool,
    reset_required: bool,
    registered_queue_count: usize,
    config_lifecycle_ready: bool,
    interrupt_lifecycle_ready: bool,
    queue_runtime_ready: bool,
    blocker: ?DriverLifecycleBlocker,
    ready_for_runtime: bool,
};

pub const ResetReplaySummary = struct {
    anchor: []const u8,
    reset_required: bool,
    driver_attached: bool,
    features_negotiated: bool,
    driver_ready: bool,
    registered_queue_count: usize,
    change_pending: bool,
    generation: u32,
    acknowledged_generation: u32,
    has_unacknowledged_generation: bool,
    pending_interrupt_reason_bits: u8,
    will_clear_negotiated_features: bool,
    will_clear_queue_callbacks: bool,
    will_clear_config_bookkeeping: bool,
    will_clear_interrupts: bool,
};

pub const VirtioInterruptReason = struct {
    pub const queue_used: u8 = 1;
    pub const config_change: u8 = 2;
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

    status: u8 = 0,
    device_features: FeatureSet = FeatureSet.initEmpty(),
    driver_features: FeatureSet = FeatureSet.initEmpty(),
    negotiated_features: FeatureSet = FeatureSet.initEmpty(),
    driver_name: ?[]const u8 = null,
    queues: [queue_capacity]QueueSlot = [_]QueueSlot{QueueSlot{}} ** queue_capacity,
    config_core_enabled: bool = true,
    config_driver_disabled: bool = false,
    config_change_pending: bool = false,
    config_change_delivery_count: usize = 0,
    config_generation: u32 = 0,
    acknowledged_config_generation: u32 = 0,
    pending_interrupt_reason_bits: u8 = 0,
    acknowledged_interrupt_reason_bits: u8 = 0,
    interrupt_ack_count: usize = 0,
    unacknowledged_interrupt_count: usize = 0,
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
        self.driver_name = null;
        self.queues = [_]QueueSlot{QueueSlot{}} ** queue_capacity;
        self.config_core_enabled = true;
        self.config_driver_disabled = false;
        self.config_change_pending = false;
        self.config_change_delivery_count = 0;
        self.config_generation = 0;
        self.acknowledged_config_generation = 0;
        self.pending_interrupt_reason_bits = 0;
        self.acknowledged_interrupt_reason_bits = 0;
        self.interrupt_ack_count = 0;
        self.unacknowledged_interrupt_count = 0;
        self.registered_queue_count = 0;
        self.reset_count += 1;
    }

    pub fn acknowledge(self: *Self) void {
        self.status |= DeviceStatus.acknowledge;
    }

    pub fn attachDriver(self: *Self) !void {
        try self.attachDriverNamed(default_driver_name);
    }

    pub fn attachDriverNamed(self: *Self, driver_name: []const u8) !void {
        if (!self.hasStatus(DeviceStatus.acknowledge)) return error.MissingAcknowledge;
        if (driver_name.len == 0) return error.EmptyDriverName;

        self.status |= DeviceStatus.driver;
        self.driver_name = driver_name;
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

    pub fn isResetRequired(self: *const Self) bool {
        return self.hasStatus(DeviceStatus.device_needs_reset);
    }

    pub fn hasNegotiatedFeature(self: *const Self, feature_bit: u16) !bool {
        const index = try checkedFeatureIndex(feature_bit);
        return self.negotiated_features.isSet(index);
    }

    pub fn hasDeviceFeature(self: *const Self, feature_bit: u16) !bool {
        const index = try checkedFeatureIndex(feature_bit);
        return self.device_features.isSet(index);
    }

    pub fn driverBindingSummary(self: *const Self) DriverBindingSummary {
        return .{
            .anchor = descriptor().anchor,
            .driver_name = self.driver_name orelse "",
            .driver_attached = self.hasStatus(DeviceStatus.driver),
            .features_negotiated = self.hasStatus(DeviceStatus.features_ok),
            .driver_ready = self.hasStatus(DeviceStatus.driver_ok),
        };
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

    pub fn disableConfigDriver(self: *Self) !void {
        try self.ensureCoreLifecycleActive();
        self.config_driver_disabled = true;
    }

    pub fn enableConfigDriver(self: *Self) !void {
        try self.ensureCoreLifecycleActive();
        self.config_driver_disabled = false;
        self.handleConfigChanged();
    }

    pub fn disableConfigCore(self: *Self) !void {
        try self.ensureCoreLifecycleActive();
        self.config_core_enabled = false;
    }

    pub fn enableConfigCore(self: *Self) !void {
        try self.ensureCoreLifecycleActive();
        self.config_core_enabled = true;
        self.handleConfigChanged();
    }

    pub fn noteConfigChanged(self: *Self) !void {
        try self.ensureCoreLifecycleActive();
        self.config_generation +%= 1;
        self.handleConfigChanged();
    }

    pub fn acknowledgeConfigGeneration(self: *Self, generation: u32) !void {
        try self.ensureCoreLifecycleActive();
        if (generation == 0 or generation > self.config_generation) return error.UnknownConfigGeneration;
        if (self.config_change_pending and generation == self.config_generation) {
            return error.ConfigGenerationPendingDelivery;
        }
        if (generation < self.config_generation) return error.StaleConfigGeneration;

        self.acknowledged_config_generation = generation;
    }

    pub fn noteInterruptReason(self: *Self, reason_bits: u8) !void {
        try self.ensureCoreLifecycleActive();
        if (reason_bits == 0) return error.EmptyInterruptReason;
        if ((reason_bits & ~allowedInterruptReasonBits()) != 0) return error.InterruptReasonOutOfRange;

        const new_reason_bits = reason_bits & ~self.pending_interrupt_reason_bits;
        if (new_reason_bits == 0) return;

        self.pending_interrupt_reason_bits |= new_reason_bits;
        self.unacknowledged_interrupt_count += @popCount(new_reason_bits);
    }

    pub fn acknowledgeInterrupt(self: *Self, reason_bits: u8) !void {
        try self.ensureCoreLifecycleActive();
        if (reason_bits == 0) return error.EmptyInterruptReason;
        if ((reason_bits & ~allowedInterruptReasonBits()) != 0) return error.InterruptReasonOutOfRange;
        if ((reason_bits & self.pending_interrupt_reason_bits) != reason_bits) {
            return error.InterruptReasonNotPending;
        }

        self.pending_interrupt_reason_bits &= ~reason_bits;
        self.acknowledged_interrupt_reason_bits |= reason_bits;
        self.interrupt_ack_count += 1;
    }

    pub fn interruptAckSummary(self: *const Self) InterruptAckSummary {
        return .{
            .anchor = descriptor().anchor,
            .reset_required = self.isResetRequired(),
            .interrupt_pending = self.pending_interrupt_reason_bits != 0,
            .pending_reason_bits = self.pending_interrupt_reason_bits,
            .acknowledged_reason_bits = self.acknowledged_interrupt_reason_bits,
            .ack_count = self.interrupt_ack_count,
            .unacknowledged_interrupt_count = self.unacknowledged_interrupt_count,
        };
    }

    pub fn lifecycleGuardSummary(self: *const Self) LifecycleGuardSummary {
        const has_acknowledge = self.hasStatus(DeviceStatus.acknowledge);
        const driver_attached = self.hasStatus(DeviceStatus.driver);
        const features_negotiated = self.hasStatus(DeviceStatus.features_ok);
        const driver_ready = self.hasStatus(DeviceStatus.driver_ok);
        const reset_required = self.isResetRequired();
        const config_lifecycle_ready = driver_attached and !reset_required;
        const interrupt_lifecycle_ready = driver_attached and !reset_required;
        const queue_runtime_ready = driver_ready and self.registered_queue_count != 0 and !reset_required;

        const blocker: ?DriverLifecycleBlocker = if (!has_acknowledge)
            .missing_acknowledge
        else if (reset_required)
            .reset_required
        else if (!driver_attached)
            .driver_not_attached
        else if (!features_negotiated)
            .feature_negotiation_incomplete
        else if (!driver_ready)
            .driver_not_ready
        else if (self.registered_queue_count == 0)
            .no_registered_queues
        else
            null;

        return .{
            .anchor = descriptor().anchor,
            .driver_name = self.driver_name orelse "",
            .has_acknowledge = has_acknowledge,
            .driver_attached = driver_attached,
            .features_negotiated = features_negotiated,
            .driver_ready = driver_ready,
            .reset_required = reset_required,
            .registered_queue_count = self.registered_queue_count,
            .config_lifecycle_ready = config_lifecycle_ready,
            .interrupt_lifecycle_ready = interrupt_lifecycle_ready,
            .queue_runtime_ready = queue_runtime_ready,
            .blocker = blocker,
            .ready_for_runtime = blocker == null,
        };
    }

    pub fn resetReplaySummary(self: *const Self) ResetReplaySummary {
        const features_negotiated = self.hasStatus(DeviceStatus.features_ok);
        const has_interrupt_bookkeeping = self.pending_interrupt_reason_bits != 0 or
            self.acknowledged_interrupt_reason_bits != 0 or
            self.interrupt_ack_count != 0 or
            self.unacknowledged_interrupt_count != 0;

        return .{
            .anchor = descriptor().anchor,
            .reset_required = self.isResetRequired(),
            .driver_attached = self.hasStatus(DeviceStatus.driver),
            .features_negotiated = features_negotiated,
            .driver_ready = self.hasStatus(DeviceStatus.driver_ok),
            .registered_queue_count = self.registered_queue_count,
            .change_pending = self.config_change_pending,
            .generation = self.config_generation,
            .acknowledged_generation = self.acknowledged_config_generation,
            .has_unacknowledged_generation = self.config_generation != self.acknowledged_config_generation,
            .pending_interrupt_reason_bits = self.pending_interrupt_reason_bits,
            .will_clear_negotiated_features = self.driver_features.count() != 0 or
                self.negotiated_features.count() != 0 or
                features_negotiated,
            .will_clear_queue_callbacks = self.registered_queue_count != 0,
            .will_clear_config_bookkeeping = self.config_change_pending or
                self.config_change_delivery_count != 0 or
                self.config_generation != 0 or
                self.acknowledged_config_generation != 0,
            .will_clear_interrupts = has_interrupt_bookkeeping,
        };
    }

    pub fn configChangeSummary(self: *const Self) ConfigChangeSummary {
        return .{
            .anchor = descriptor().anchor,
            .reset_required = self.isResetRequired(),
            .core_enabled = self.config_core_enabled,
            .driver_disabled = self.config_driver_disabled,
            .change_pending = self.config_change_pending,
            .generation = self.config_generation,
            .acknowledged_generation = self.acknowledged_config_generation,
            .has_unacknowledged_generation = self.config_generation != self.acknowledged_config_generation,
            .delivery_count = self.config_change_delivery_count,
        };
    }

    pub fn registeredQueueCount(self: *const Self) usize {
        return self.registered_queue_count;
    }

    fn handleConfigChanged(self: *Self) void {
        if (!self.config_core_enabled or self.config_driver_disabled) {
            self.config_change_pending = true;
            return;
        }

        self.config_change_pending = false;
        self.config_change_delivery_count += 1;
    }

    fn ensureCoreLifecycleActive(self: *const Self) !void {
        if (!self.hasStatus(DeviceStatus.driver)) return error.DriverNotAttached;
        if (self.isResetRequired()) return error.ResetRequired;
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

    fn allowedInterruptReasonBits() u8 {
        return VirtioInterruptReason.queue_used | VirtioInterruptReason.config_change;
    }
};