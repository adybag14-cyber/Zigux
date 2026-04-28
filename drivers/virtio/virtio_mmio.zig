const std = @import("std");

pub const supported_feature_pages: usize = 2;
pub const supported_interrupt_bits: u32 = 0x3;
pub const supported_queues: usize = 2;

pub const Register = enum(u32) {
    magic_value = 0x000,
    version = 0x004,
    device_id = 0x008,
    vendor_id = 0x00c,
    device_features = 0x010,
    device_features_sel = 0x014,
    driver_features = 0x020,
    driver_features_sel = 0x024,
    queue_sel = 0x030,
    queue_num_max = 0x034,
    queue_num = 0x038,
    queue_ready = 0x044,
    interrupt_status = 0x060,
    interrupt_ack = 0x064,
    status = 0x070,
    config_generation = 0x0fc,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_lab_validation: bool,
    touches_transport_mmio: bool,
    touches_dma_paths: bool,
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

const QueueRegisterState = struct {
    max_size: u16 = 0,
    size: u16 = 0,
    ready: bool = false,
};

pub const VirtioMmioRegisterWindowLab = struct {
    const Self = @This();

    device_feature_pages: [supported_feature_pages]u32 = .{ 0, 0 },
    driver_feature_pages: [supported_feature_pages]u32 = .{ 0, 0 },
    selected_device_page: u32 = 0,
    selected_driver_page: u32 = 0,
    queues: [supported_queues]QueueRegisterState = .{ .{}, .{} },
    selected_queue: u32 = 0,
    status: u8 = 0,
    config_generation: u32 = 0,
    interrupt_status: u32 = 0,
    reset_count: usize = 0,

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

    pub fn setStatus(self: *Self, status: u8) !StatusSummary {
        if (status == 0) return error.ResetRequiresDedicatedPath;
        self.status = status;
        return self.statusSummary();
    }

    pub fn reset(self: *Self) StatusSummary {
        self.status = 0;
        self.selected_queue = 0;
        for (&self.queues) |*queue_state| {
            queue_state.size = 0;
            queue_state.ready = false;
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

test "register enum keeps the bounded mmio offsets reviewable" {
    try std.testing.expectEqual(@as(u32, 0x010), @intFromEnum(Register.device_features));
    try std.testing.expectEqual(@as(u32, 0x024), @intFromEnum(Register.driver_features_sel));
    try std.testing.expectEqual(@as(u32, 0x030), @intFromEnum(Register.queue_sel));
    try std.testing.expectEqual(@as(u32, 0x044), @intFromEnum(Register.queue_ready));
    try std.testing.expectEqual(@as(u32, 0x064), @intFromEnum(Register.interrupt_ack));
    try std.testing.expectEqual(@as(u32, 0x0fc), @intFromEnum(Register.config_generation));
}
