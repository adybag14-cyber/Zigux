const std = @import("std");

pub const feature_bit_capacity: u16 = 128;

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

pub const VirtioCoreLabDevice = struct {
    const Self = @This();
    const FeatureSet = std.StaticBitSet(feature_bit_capacity);

    status: u8 = 0,
    device_features: FeatureSet = FeatureSet.initEmpty(),
    driver_features: FeatureSet = FeatureSet.initEmpty(),
    negotiated_features: FeatureSet = FeatureSet.initEmpty(),
    transport_accepts_features: bool = true,
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
        self.reset_count += 1;
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

    fn checkedFeatureIndex(feature_bit: u16) !usize {
        if (feature_bit >= feature_bit_capacity) return error.FeatureBitOutOfRange;
        return @intCast(feature_bit);
    }
};