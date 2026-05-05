const std = @import("std");

pub const queue_capacity: usize = 8;
pub const feature_word_capacity: usize = 2;
pub const config_window_capacity: usize = 16;
pub const max_queue_size: u16 = 1024;
pub const mmio_window_bytes: u32 = 0x100;
pub const mmio_magic_value: u32 = 0x7472_6976;
pub const mmio_version_modern: u32 = 0x2;
pub const default_vendor_id: u32 = 0x1af4;

pub const Register = enum(u32) {
    magic_value = 0x000,
    version = 0x004,
    device_id = 0x008,
    device_features = 0x010,
    device_features_sel = 0x014,
    vendor_id = 0x00c,
    driver_features = 0x020,
    queue_sel = 0x030,
    queue_num_max = 0x034,
    queue_num = 0x038,
    queue_ready = 0x044,
    interrupt_status = 0x060,
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

pub const RegisterWindowSummary = struct {
    anchor: []const u8,
    configured_queue_count: usize,
    selected_queue: u16,
    selected_device_feature_word: u32,
    status: u8,
    interrupt_status: u32,
    config_generation: u32,
};

pub const RegisterReadSummary = struct {
    anchor: []const u8,
    register: Register,
    selected_queue: u16,
    value: u32,
};

pub const RegisterWriteSummary = struct {
    anchor: []const u8,
    register: Register,
    selected_queue: u16,
    value: u32,
};

pub const ConfigReadSummary = struct {
    anchor: []const u8,
    absolute_offset: u32,
    relative_offset: u32,
    config_generation: u32,
    value: u32,
};

pub const VirtioMmioLab = struct {
    const Self = @This();

    queue_num_max: [queue_capacity]u16 = [_]u16{0} ** queue_capacity,
    queue_num: [queue_capacity]u16 = [_]u16{0} ** queue_capacity,
    queue_ready: [queue_capacity]bool = [_]bool{false} ** queue_capacity,
    device_feature_words: [feature_word_capacity]u32 = [_]u32{0} ** feature_word_capacity,
    config_window: [config_window_capacity]u8 = [_]u8{0} ** config_window_capacity,
    configured_queue_count: usize = 0,
    config_window_size: usize = 0,
    selected_queue: u16 = 0,
    selected_device_feature_word: u32 = 0,
    status: u8 = 0,
    interrupt_status: u32 = 0,
    config_generation: u32 = 0,
    driver_features: u32 = 0,
    device_id: u32 = 0,
    vendor_id: u32 = default_vendor_id,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "virtio_mmio_lab",
            .anchor = "drivers/virtio/virtio_mmio.c",
            .provides_lab_validation = true,
            .touches_transport_mmio = true,
            .touches_dma_paths = false,
        };
    }

    pub fn init(device_id: u32, queue_sizes: []const u16) !Self {
        if (queue_sizes.len == 0) return error.EmptyQueueCapacityPlan;
        if (queue_sizes.len > queue_capacity) return error.QueueCapacityPlanTooLarge;

        var self = Self{
            .device_id = device_id,
        };
        for (queue_sizes, 0..) |queue_size, index| {
            try validateQueueSize(queue_size);
            self.queue_num_max[index] = queue_size;
        }
        self.configured_queue_count = queue_sizes.len;
        return self;
    }

    pub fn readOffset(self: *const Self, offset: u32) !RegisterReadSummary {
        const register = try registerFromOffset(offset);
        return self.readRegister(register);
    }

    pub fn readRegister(self: *const Self, register: Register) !RegisterReadSummary {
        return .{
            .anchor = descriptor().anchor,
            .register = register,
            .selected_queue = self.selected_queue,
            .value = switch (register) {
                .magic_value => mmio_magic_value,
                .version => mmio_version_modern,
                .device_id => self.device_id,
                .device_features => self.device_feature_words[try checkedFeatureWordIndex(self.selected_device_feature_word)],
                .device_features_sel => self.selected_device_feature_word,
                .vendor_id => self.vendor_id,
                .driver_features => self.driver_features,
                .queue_sel => self.selected_queue,
                .queue_num_max => self.queue_num_max[try self.checkedQueueIndex(self.selected_queue)],
                .queue_num => self.queue_num[try self.checkedQueueIndex(self.selected_queue)],
                .queue_ready => boolToU32(self.queue_ready[try self.checkedQueueIndex(self.selected_queue)]),
                .interrupt_status => self.interrupt_status,
                .status => self.status,
                .config_generation => self.config_generation,
            },
        };
    }

    pub fn writeOffset(self: *Self, offset: u32, value: u32) !RegisterWriteSummary {
        const register = try registerFromOffset(offset);
        return self.writeRegister(register, value);
    }

    pub fn writeRegister(self: *Self, register: Register, value: u32) !RegisterWriteSummary {
        switch (register) {
            .device_features_sel => {
                self.selected_device_feature_word = try checkedFeatureWordSelector(value);
            },
            .driver_features => {
                self.driver_features = value;
            },
            .queue_sel => {
                self.selected_queue = try self.checkedQueueSelector(value);
            },
            .queue_num => {
                const queue_index = try self.checkedQueueIndex(self.selected_queue);
                const queue_size = try checkedQueueSizeValue(value);
                if (queue_size > self.queue_num_max[queue_index]) return error.QueueSizeExceedsMaximum;
                self.queue_num[queue_index] = queue_size;
            },
            .queue_ready => {
                const queue_index = try self.checkedQueueIndex(self.selected_queue);
                if (value > 1) return error.QueueReadyValueOutOfRange;
                self.queue_ready[queue_index] = value == 1;
            },
            .status => {
                if (value > std.math.maxInt(u8)) return error.StatusValueOutOfRange;
                self.status = @intCast(value);
            },
            .magic_value,
            .version,
            .device_id,
            .device_features,
            .vendor_id,
            .queue_num_max,
            .interrupt_status,
            .config_generation,
            => return error.ReadOnlyRegister,
        }

        return .{
            .anchor = descriptor().anchor,
            .register = register,
            .selected_queue = self.selected_queue,
            .value = value,
        };
    }

    pub fn readConfigOffset(self: *const Self, offset: u32) !ConfigReadSummary {
        const relative_offset = try checkedConfigWindowOffset(offset);
        const start = try self.checkedConfigWordRange(relative_offset);
        return .{
            .anchor = descriptor().anchor,
            .absolute_offset = offset,
            .relative_offset = relative_offset,
            .config_generation = self.config_generation,
            .value = readLittleU32(self.config_window[start .. start + 4]),
        };
    }

    pub fn stageConfigBytes(self: *Self, bytes: []const u8) !void {
        if (bytes.len > config_window_capacity) return error.ConfigWindowTooLarge;
        @memset(self.config_window[0..], 0);
        @memcpy(self.config_window[0..bytes.len], bytes);
        self.config_window_size = bytes.len;
    }

    pub fn windowSummary(self: *const Self) RegisterWindowSummary {
        return .{
            .anchor = descriptor().anchor,
            .configured_queue_count = self.configured_queue_count,
            .selected_queue = self.selected_queue,
            .selected_device_feature_word = self.selected_device_feature_word,
            .status = self.status,
            .interrupt_status = self.interrupt_status,
            .config_generation = self.config_generation,
        };
    }

    pub fn bumpConfigGeneration(self: *Self) void {
        self.config_generation +%= 1;
    }

    pub fn stageInterruptStatus(self: *Self, bits: u32) void {
        self.interrupt_status = bits;
    }

    pub fn stageDeviceFeatureWord(self: *Self, word_index: u32, value: u32) !void {
        self.device_feature_words[try checkedFeatureWordIndex(word_index)] = value;
    }

    fn checkedQueueSelector(self: *const Self, value: u32) !u16 {
        if (value >= self.configured_queue_count) return error.QueueSelectionOutOfRange;
        return @intCast(value);
    }

    fn checkedQueueIndex(self: *const Self, queue_index: u16) !usize {
        if (queue_index >= self.configured_queue_count) return error.QueueSelectionOutOfRange;
        return @intCast(queue_index);
    }

    fn checkedConfigWordRange(self: *const Self, relative_offset: u32) !usize {
        if (relative_offset > std.math.maxInt(usize)) return error.ConfigWindowReadOutOfRange;
        const start: usize = @intCast(relative_offset);
        if (start + 4 > self.config_window_size) return error.ConfigWindowReadOutOfRange;
        return start;
    }
};

fn registerFromOffset(offset: u32) !Register {
    if (offset >= mmio_window_bytes) return error.RegisterOffsetOutOfRange;
    if ((offset & 0x3) != 0) return error.UnalignedRegisterOffset;

    return switch (offset) {
        @intFromEnum(Register.magic_value) => .magic_value,
        @intFromEnum(Register.version) => .version,
        @intFromEnum(Register.device_id) => .device_id,
        @intFromEnum(Register.device_features) => .device_features,
        @intFromEnum(Register.device_features_sel) => .device_features_sel,
        @intFromEnum(Register.vendor_id) => .vendor_id,
        @intFromEnum(Register.driver_features) => .driver_features,
        @intFromEnum(Register.queue_sel) => .queue_sel,
        @intFromEnum(Register.queue_num_max) => .queue_num_max,
        @intFromEnum(Register.queue_num) => .queue_num,
        @intFromEnum(Register.queue_ready) => .queue_ready,
        @intFromEnum(Register.interrupt_status) => .interrupt_status,
        @intFromEnum(Register.status) => .status,
        @intFromEnum(Register.config_generation) => .config_generation,
        else => error.UnsupportedRegisterOffset,
    };
}

fn validateQueueSize(queue_size: u16) !void {
    if (queue_size == 0) return error.EmptyQueueSize;
    if (queue_size > max_queue_size) return error.QueueSizeTooLarge;
    if (!std.math.isPowerOfTwo(queue_size)) return error.QueueSizeMustBePowerOfTwo;
}

fn checkedQueueSizeValue(value: u32) !u16 {
    if (value > max_queue_size) return error.QueueSizeTooLarge;
    const queue_size: u16 = @intCast(value);
    try validateQueueSize(queue_size);
    return queue_size;
}

fn checkedFeatureWordSelector(value: u32) !u32 {
    _ = try checkedFeatureWordIndex(value);
    return value;
}

fn checkedFeatureWordIndex(word_index: u32) !usize {
    if (word_index >= feature_word_capacity) return error.FeatureWordSelectionOutOfRange;
    return @intCast(word_index);
}

fn checkedConfigWindowOffset(offset: u32) !u32 {
    if (offset < mmio_window_bytes) return error.ConfigOffsetBeforeWindow;
    const relative_offset = offset - mmio_window_bytes;
    if ((relative_offset & 0x3) != 0) return error.UnalignedConfigOffset;
    return relative_offset;
}

fn readLittleU32(bytes: []const u8) u32 {
    return @as(u32, bytes[0]) |
        (@as(u32, bytes[1]) << 8) |
        (@as(u32, bytes[2]) << 16) |
        (@as(u32, bytes[3]) << 24);
}

fn boolToU32(value: bool) u32 {
    return if (value) 1 else 0;
}
