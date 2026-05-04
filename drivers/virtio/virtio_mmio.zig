const std = @import("std");

pub const supported_feature_pages: usize = 2;
pub const queue_interrupt_bit: u32 = 0x1;
pub const config_interrupt_bit: u32 = 0x2;
pub const supported_interrupt_bits: u32 = queue_interrupt_bit | config_interrupt_bit;
pub const supported_queues: usize = 2;
pub const supported_config_window_bytes: usize = 16;
pub const expected_magic_value: u32 = 0x74726976;
pub const legacy_transport_version: u32 = 1;
pub const modern_transport_version: u32 = 2;

pub const Register = enum(u32) {
    magic_value = 0x000,
    version = 0x004,
    device_id = 0x008,
    vendor_id = 0x00c,
    device_features = 0x010,
    device_features_sel = 0x014,
    driver_features = 0x020,
    driver_features_sel = 0x024,
    guest_page_size = 0x028,
    queue_sel = 0x030,
    queue_num_max = 0x034,
    queue_num = 0x038,
    queue_align = 0x03c,
    queue_pfn = 0x040,
    queue_ready = 0x044,
    queue_notify = 0x050,
    interrupt_status = 0x060,
    interrupt_ack = 0x064,
    status = 0x070,
    queue_desc_low = 0x080,
    queue_desc_high = 0x084,
    queue_avail_low = 0x090,
    queue_avail_high = 0x094,
    queue_used_low = 0x0a0,
    queue_used_high = 0x0a4,
    config_generation = 0x0fc,
    config = 0x100,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_lab_validation: bool,
    touches_transport_mmio: bool,
    touches_dma_paths: bool,
};

pub const DeviceIdentitySummary = struct {
    anchor: []const u8,
    magic_value: u32,
    version: u32,
    device_id: u32,
    vendor_id: u32,
    magic_matches: bool,
    version_supported: bool,
    device_present: bool,
};

pub const FeatureWindowSummary = struct {
    anchor: []const u8,
    selected_device_page: u32,
    selected_driver_page: u32,
    selected_device_features: u32,
    selected_driver_features: u32,
};

pub const QueueRegisterSummary = struct {
    anchor: []const u8,
    selected_queue: u32,
    selected_queue_size_max: u16,
    selected_queue_size: u16,
    selected_queue_ready: bool,
};

pub const QueueNotifySummary = struct {
    anchor: []const u8,
    selected_queue: u32,
    notified_queue: u32,
    queue_size: u16,
    queue_ready_before_notify: bool,
    notification_count: usize,
};

pub const QueueAddressKind = enum {
    legacy,
    modern,
};

pub const QueueAddressSummary = struct {
    anchor: []const u8,
    selected_queue: u32,
    kind: QueueAddressKind,
    legacy_guest_page_size: ?u32,
    legacy_queue_align: ?u32,
    legacy_queue_pfn: ?u32,
    modern_desc: ?u64,
    modern_avail: ?u64,
    modern_used: ?u64,
    queue_size: u16,
    queue_ready: bool,
};

pub const ConfigWindowWidth = enum(u8) {
    byte = 1,
    half = 2,
    word = 4,
};

pub const ConfigWindowSummary = struct {
    anchor: []const u8,
    offset: u32,
    width: ConfigWindowWidth,
    generation: u32,
    value: u32,
};

pub const ConfigWritePlanSummary = struct {
    anchor: []const u8,
    offset: u32,
    width: ConfigWindowWidth,
    generation: u32,
    previous_value: u32,
    planned_value: u32,
};

pub const StatusSummary = struct {
    anchor: []const u8,
    status: u8,
    reset_count: usize,
};

pub const ConfigGenerationSummary = struct {
    anchor: []const u8,
    generation: u32,
    changed: bool,
};

pub const InterruptAckSummary = struct {
    anchor: []const u8,
    acknowledged_bits: u32,
    pending_bits_before_ack: u32,
    pending_bits_after_ack: u32,
};

pub const InterruptSummary = struct {
    anchor: []const u8,
    pending_bits: u32,
    queue_interrupt_pending: bool,
    config_interrupt_pending: bool,
    line_asserted: bool,
};

const QueueRegisterState = struct {
    max_size: u16 = 0,
    size: u16 = 0,
    ready: bool = false,
    legacy_queue_align: u32 = 0,
    legacy_queue_pfn: u32 = 0,
    modern_desc: u64 = 0,
    modern_avail: u64 = 0,
    modern_used: u64 = 0,
};

pub const VirtioMmioRegisterWindowLab = struct {
    const Self = @This();

    device_feature_pages: [supported_feature_pages]u32 = .{ 0, 0 },
    driver_feature_pages: [supported_feature_pages]u32 = .{ 0, 0 },
    selected_device_page: u32 = 0,
    selected_driver_page: u32 = 0,
    queues: [supported_queues]QueueRegisterState = .{ .{}, .{} },
    config_window: [supported_config_window_bytes]u8 = [_]u8{0} ** supported_config_window_bytes,
    pending_config_write: ?ConfigWritePlanSummary = null,
    selected_queue: u32 = 0,
    legacy_guest_page_size: u32 = 0,
    status: u8 = 0,
    config_generation: u32 = 0,
    interrupt_status: u32 = 0,
    reset_count: usize = 0,
    notification_count: usize = 0,
    magic_value: u32 = expected_magic_value,
    version: u32 = modern_transport_version,
    device_id: u32 = 0,
    vendor_id: u32 = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "virtio_mmio_register_window_lab",
            .anchor = "drivers/virtio/virtio_mmio.c",
            .provides_lab_validation = true,
            .touches_transport_mmio = true,
            .touches_dma_paths = false,
        };
    }

    pub fn init(device_feature_pages: [supported_feature_pages]u32, config_generation: u32) Self {
        return initWithQueueMaximums(
            device_feature_pages,
            config_generation,
            [_]u16{0} ** supported_queues,
        );
    }

    pub fn initWithQueueMaximums(
        device_feature_pages: [supported_feature_pages]u32,
        config_generation: u32,
        queue_maximums: [supported_queues]u16,
    ) Self {
        var queue_states: [supported_queues]QueueRegisterState = undefined;
        for (queue_maximums, 0..) |max_size, index| {
            queue_states[index] = .{ .max_size = max_size };
        }

        return .{
            .device_feature_pages = device_feature_pages,
            .queues = queue_states,
            .config_generation = config_generation,
        };
    }

    pub fn initWithQueueMaximumsAndConfigWindow(
        device_feature_pages: [supported_feature_pages]u32,
        config_generation: u32,
        queue_maximums: [supported_queues]u16,
        config_window: [supported_config_window_bytes]u8,
    ) Self {
        var self = initWithQueueMaximums(device_feature_pages, config_generation, queue_maximums);
        self.config_window = config_window;
        return self;
    }

    pub fn seedTransportIdentity(
        self: *Self,
        magic_value: u32,
        version: u32,
        device_id: u32,
        vendor_id: u32,
    ) DeviceIdentitySummary {
        self.magic_value = magic_value;
        self.version = version;
        self.device_id = device_id;
        self.vendor_id = vendor_id;
        return self.deviceIdentitySummary();
    }

    pub fn deviceIdentitySummary(self: *const Self) DeviceIdentitySummary {
        return .{
            .anchor = descriptor().anchor,
            .magic_value = self.magic_value,
            .version = self.version,
            .device_id = self.device_id,
            .vendor_id = self.vendor_id,
            .magic_matches = self.magic_value == expected_magic_value,
            .version_supported = self.version == legacy_transport_version or self.version == modern_transport_version,
            .device_present = self.device_id != 0,
        };
    }

    pub fn selectDeviceFeaturePage(self: *Self, page: u32) !void {
        _ = try checkedFeaturePage(page);
        self.selected_device_page = page;
    }

    pub fn readSelectedDeviceFeatures(self: *const Self) !u32 {
        return self.device_feature_pages[try checkedFeaturePage(self.selected_device_page)];
    }

    pub fn selectDriverFeaturePage(self: *Self, page: u32) !void {
        _ = try checkedFeaturePage(page);
        self.selected_driver_page = page;
    }

    pub fn writeSelectedDriverFeatures(self: *Self, feature_bits: u32) !FeatureWindowSummary {
        const page_index = try checkedFeaturePage(self.selected_driver_page);
        self.driver_feature_pages[page_index] = feature_bits;
        return self.featureWindowSummary();
    }

    pub fn featureWindowSummary(self: *const Self) !FeatureWindowSummary {
        return .{
            .anchor = descriptor().anchor,
            .selected_device_page = self.selected_device_page,
            .selected_driver_page = self.selected_driver_page,
            .selected_device_features = try self.readSelectedDeviceFeatures(),
            .selected_driver_features = self.driver_feature_pages[try checkedFeaturePage(self.selected_driver_page)],
        };
    }

    pub fn selectQueue(self: *Self, queue: u32) !QueueRegisterSummary {
        _ = try checkedQueue(queue);
        self.selected_queue = queue;
        return self.queueRegisterSummary();
    }

    pub fn writeSelectedQueueSize(self: *Self, size: u16) !QueueRegisterSummary {
        const queue_index = try checkedQueue(self.selected_queue);
        const queue_state = &self.queues[queue_index];

        if (queue_state.max_size == 0) return error.QueueSizeUnavailable;
        if (size == 0) return error.QueueSizeMustBeNonZero;
        if (size > queue_state.max_size) return error.QueueSizeExceedsMaximum;
        if (queue_state.ready) return error.QueueReadyBlocksResize;

        queue_state.size = size;
        return self.queueRegisterSummary();
    }

    pub fn writeSelectedQueueReady(self: *Self, ready: bool) !QueueRegisterSummary {
        const queue_index = try checkedQueue(self.selected_queue);
        const queue_state = &self.queues[queue_index];

        if (ready and queue_state.size == 0) return error.QueueReadyRequiresConfiguredSize;

        queue_state.ready = ready;
        return self.queueRegisterSummary();
    }

    pub fn queueRegisterSummary(self: *const Self) !QueueRegisterSummary {
        const queue_state = self.queues[try checkedQueue(self.selected_queue)];
        return .{
            .anchor = descriptor().anchor,
            .selected_queue = self.selected_queue,
            .selected_queue_size_max = queue_state.max_size,
            .selected_queue_size = queue_state.size,
            .selected_queue_ready = queue_state.ready,
        };
    }

    pub fn notifySelectedQueue(self: *Self) !QueueNotifySummary {
        const queue_index = try checkedQueue(self.selected_queue);
        const queue_state = self.queues[queue_index];

        if (queue_state.size == 0) return error.QueueNotifyRequiresConfiguredSize;
        if (!queue_state.ready) return error.QueueNotifyRequiresReadyQueue;

        self.notification_count += 1;
        return .{
            .anchor = descriptor().anchor,
            .selected_queue = self.selected_queue,
            .notified_queue = self.selected_queue,
            .queue_size = queue_state.size,
            .queue_ready_before_notify = queue_state.ready,
            .notification_count = self.notification_count,
        };
    }

    pub fn planLegacyQueueAddress(
        self: *Self,
        guest_page_size: u32,
        queue_align: u32,
        queue_pfn: u32,
    ) !QueueAddressSummary {
        const queue_index = try checkedQueue(self.selected_queue);
        const queue_state = &self.queues[queue_index];

        if (queue_state.size == 0) return error.QueueAddressRequiresConfiguredSize;
        if (queue_state.ready) return error.QueueReadyBlocksAddressRewrite;
        if (guest_page_size == 0) return error.LegacyGuestPageSizeMustBeNonZero;
        if (queue_align == 0) return error.LegacyQueueAlignMustBeNonZero;
        if (queue_pfn == 0) return error.LegacyQueuePfnMustBeNonZero;

        self.legacy_guest_page_size = guest_page_size;
        queue_state.legacy_queue_align = queue_align;
        queue_state.legacy_queue_pfn = queue_pfn;
        queue_state.modern_desc = 0;
        queue_state.modern_avail = 0;
        queue_state.modern_used = 0;

        return self.queueAddressSummary(.legacy);
    }

    pub fn planModernQueueAddress(
        self: *Self,
        desc: u64,
        avail: u64,
        used: u64,
    ) !QueueAddressSummary {
        const queue_index = try checkedQueue(self.selected_queue);
        const queue_state = &self.queues[queue_index];

        if (queue_state.size == 0) return error.QueueAddressRequiresConfiguredSize;
        if (queue_state.ready) return error.QueueReadyBlocksAddressRewrite;
        if (desc == 0) return error.ModernQueueDescMustBeNonZero;
        if (avail == 0) return error.ModernQueueAvailMustBeNonZero;
        if (used == 0) return error.ModernQueueUsedMustBeNonZero;

        queue_state.legacy_queue_align = 0;
        queue_state.legacy_queue_pfn = 0;
        queue_state.modern_desc = desc;
        queue_state.modern_avail = avail;
        queue_state.modern_used = used;

        return self.queueAddressSummary(.modern);
    }

    pub fn queueAddressSummary(self: *const Self, kind: QueueAddressKind) !QueueAddressSummary {
        const queue_state = self.queues[try checkedQueue(self.selected_queue)];
        return .{
            .anchor = descriptor().anchor,
            .selected_queue = self.selected_queue,
            .kind = kind,
            .legacy_guest_page_size = if (kind == .legacy) self.legacy_guest_page_size else null,
            .legacy_queue_align = if (kind == .legacy) queue_state.legacy_queue_align else null,
            .legacy_queue_pfn = if (kind == .legacy) queue_state.legacy_queue_pfn else null,
            .modern_desc = if (kind == .modern) queue_state.modern_desc else null,
            .modern_avail = if (kind == .modern) queue_state.modern_avail else null,
            .modern_used = if (kind == .modern) queue_state.modern_used else null,
            .queue_size = queue_state.size,
            .queue_ready = queue_state.ready,
        };
    }

    pub fn snapshotConfigWindow(
        self: *const Self,
        offset: u32,
        width: ConfigWindowWidth,
    ) !ConfigWindowSummary {
        const config_offset = try checkedConfigWindow(offset, width);
        const width_bytes = @intFromEnum(width);
        var value: u32 = 0;

        for (0..width_bytes) |index| {
            value |= @as(u32, self.config_window[config_offset + index]) << @intCast(index * 8);
        }

        return .{
            .anchor = descriptor().anchor,
            .offset = offset,
            .width = width,
            .generation = self.config_generation,
            .value = value,
        };
    }

    pub fn planConfigWrite(
        self: *Self,
        offset: u32,
        width: ConfigWindowWidth,
        value: u32,
    ) !ConfigWritePlanSummary {
        const config_offset = try checkedConfigWindow(offset, width);
        const width_bytes = @intFromEnum(width);
        try validateConfigWriteValue(width, value);

        var previous_value: u32 = 0;
        for (0..width_bytes) |index| {
            previous_value |= @as(u32, self.config_window[config_offset + index]) << @intCast(index * 8);
        }

        const plan: ConfigWritePlanSummary = .{
            .anchor = descriptor().anchor,
            .offset = offset,
            .width = width,
            .generation = self.config_generation,
            .previous_value = previous_value,
            .planned_value = value,
        };
        self.pending_config_write = plan;
        return plan;
    }

    pub fn pendingConfigWritePlan(self: *const Self) ?ConfigWritePlanSummary {
        return self.pending_config_write;
    }

    pub fn discardPendingConfigWritePlan(self: *Self) void {
        self.pending_config_write = null;
    }

    pub fn setStatus(self: *Self, status: u8) !StatusSummary {
        if (status == 0) return error.ResetRequiresDedicatedPath;
        self.status = status;
        return self.statusSummary();
    }

    pub fn reset(self: *Self) StatusSummary {
        self.status = 0;
        self.selected_device_page = 0;
        self.selected_driver_page = 0;
        self.driver_feature_pages = [_]u32{0} ** supported_feature_pages;
        self.selected_queue = 0;
        self.legacy_guest_page_size = 0;
        self.interrupt_status = 0;
        self.notification_count = 0;
        self.pending_config_write = null;
        for (&self.queues) |*queue_state| {
            queue_state.size = 0;
            queue_state.ready = false;
            queue_state.legacy_queue_align = 0;
            queue_state.legacy_queue_pfn = 0;
            queue_state.modern_desc = 0;
            queue_state.modern_avail = 0;
            queue_state.modern_used = 0;
        }
        self.reset_count += 1;
        return self.statusSummary();
    }

    pub fn statusSummary(self: *const Self) StatusSummary {
        return .{
            .anchor = descriptor().anchor,
            .status = self.status,
            .reset_count = self.reset_count,
        };
    }

    pub fn configGenerationSummary(self: *const Self) ConfigGenerationSummary {
        return .{
            .anchor = descriptor().anchor,
            .generation = self.config_generation,
            .changed = false,
        };
    }

    pub fn bumpConfigGeneration(self: *Self) ConfigGenerationSummary {
        self.config_generation +%= 1;
        return .{
            .anchor = descriptor().anchor,
            .generation = self.config_generation,
            .changed = true,
        };
    }

    pub fn raiseInterrupt(self: *Self, bits: u32) !void {
        try validateInterruptBits(bits);
        self.interrupt_status |= bits;
    }

    pub fn acknowledgeInterrupt(self: *Self, bits: u32) !InterruptAckSummary {
        try validateInterruptBits(bits);

        const pending_before_ack = self.interrupt_status;
        const acknowledged_bits = pending_before_ack & bits;
        self.interrupt_status = pending_before_ack & ~bits;

        return .{
            .anchor = descriptor().anchor,
            .acknowledged_bits = acknowledged_bits,
            .pending_bits_before_ack = pending_before_ack,
            .pending_bits_after_ack = self.interrupt_status,
        };
    }

    pub fn interruptSummary(self: *const Self) InterruptSummary {
        return .{
            .anchor = descriptor().anchor,
            .pending_bits = self.interrupt_status,
            .queue_interrupt_pending = (self.interrupt_status & queue_interrupt_bit) != 0,
            .config_interrupt_pending = (self.interrupt_status & config_interrupt_bit) != 0,
            .line_asserted = self.interrupt_status != 0,
        };
    }

    pub fn readInterruptStatus(self: *const Self) u32 {
        return self.interrupt_status;
    }
};

fn checkedFeaturePage(page: u32) !usize {
    if (page >= supported_feature_pages) return error.FeaturePageOutOfRange;
    return @intCast(page);
}

fn checkedQueue(queue: u32) !usize {
    if (queue >= supported_queues) return error.QueueIndexOutOfRange;
    return @intCast(queue);
}

fn validateInterruptBits(bits: u32) !void {
    if (bits == 0) return error.EmptyInterruptMask;
    if ((bits & ~supported_interrupt_bits) != 0) return error.UnsupportedInterruptBits;
}

fn checkedConfigWindow(offset: u32, width: ConfigWindowWidth) !usize {
    const config_offset: usize = @intCast(offset);
    const width_bytes: usize = @intFromEnum(width);
    const end = config_offset +| width_bytes;
    if (end > supported_config_window_bytes) return error.ConfigWindowOutOfRange;
    return config_offset;
}

fn validateConfigWriteValue(width: ConfigWindowWidth, value: u32) !void {
    const max_value: u32 = switch (width) {
        .byte => 0xff,
        .half => 0xffff,
        .word => std.math.maxInt(u32),
    };
    if (value > max_value) return error.ConfigWriteValueTooWide;
}

test "register enum keeps the bounded mmio offsets reviewable" {
    try std.testing.expectEqual(@as(u32, 0x028), @intFromEnum(Register.guest_page_size));
    try std.testing.expectEqual(@as(u32, 0x03c), @intFromEnum(Register.queue_align));
    try std.testing.expectEqual(@as(u32, 0x040), @intFromEnum(Register.queue_pfn));
    try std.testing.expectEqual(@as(u32, 0x050), @intFromEnum(Register.queue_notify));
    try std.testing.expectEqual(@as(u32, 0x080), @intFromEnum(Register.queue_desc_low));
    try std.testing.expectEqual(@as(u32, 0x0a4), @intFromEnum(Register.queue_used_high));
    try std.testing.expectEqual(@as(u32, 0x0fc), @intFromEnum(Register.config_generation));
    try std.testing.expectEqual(@as(u32, 0x100), @intFromEnum(Register.config));
}

test "phase10 virtio mmio reset clears driver-owned queue state and feature writes while preserving queue maxima" {
    var window = VirtioMmioRegisterWindowLab.initWithQueueMaximums(
        .{ 0x0000_00a5, 0x5a5a_0000 },
        7,
        .{ 8, 16 },
    );

    try window.selectDeviceFeaturePage(1);
    try window.selectDriverFeaturePage(1);
    _ = try window.writeSelectedDriverFeatures(0xf0f0_0001);
    _ = try window.selectQueue(1);
    _ = try window.writeSelectedQueueSize(16);
    _ = try window.planModernQueueAddress(0x1000, 0x2000, 0x3000);
    _ = try window.writeSelectedQueueReady(true);
    _ = try window.notifySelectedQueue();
    _ = try window.planConfigWrite(4, .half, 0x1234);
    try window.raiseInterrupt(queue_interrupt_bit | config_interrupt_bit);
    _ = try window.setStatus(3);

    const reset = window.reset();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", reset.anchor);
    try std.testing.expectEqual(@as(u8, 0), reset.status);
    try std.testing.expectEqual(@as(usize, 1), reset.reset_count);
    try std.testing.expectEqual(@as(u32, 0), window.readInterruptStatus());
    try std.testing.expect(window.pendingConfigWritePlan() == null);

    const feature_summary = try window.featureWindowSummary();
    try std.testing.expectEqual(@as(u32, 0), feature_summary.selected_device_page);
    try std.testing.expectEqual(@as(u32, 0), feature_summary.selected_driver_page);
    try std.testing.expectEqual(@as(u32, 0x0000_00a5), feature_summary.selected_device_features);
    try std.testing.expectEqual(@as(u32, 0), feature_summary.selected_driver_features);

    var queue = try window.queueRegisterSummary();
    try std.testing.expectEqual(@as(u32, 0), queue.selected_queue);
    try std.testing.expectEqual(@as(u16, 8), queue.selected_queue_size_max);
    try std.testing.expectEqual(@as(u16, 0), queue.selected_queue_size);
    try std.testing.expect(!queue.selected_queue_ready);

    queue = try window.selectQueue(1);
    try std.testing.expectEqual(@as(u16, 16), queue.selected_queue_size_max);
    try std.testing.expectEqual(@as(u16, 0), queue.selected_queue_size);
    try std.testing.expect(!queue.selected_queue_ready);
    try std.testing.expectError(error.QueueNotifyRequiresConfiguredSize, window.notifySelectedQueue());
    try std.testing.expectError(error.QueueAddressRequiresConfiguredSize, window.planModernQueueAddress(0x1110, 0x2220, 0x3330));
}
