const std = @import("std");

pub const queue_capacity: usize = 8;
pub const feature_word_capacity: usize = 2;
pub const config_window_capacity: usize = 16;
pub const max_queue_size: u16 = 1024;
pub const mmio_window_bytes: u32 = 0x100;
pub const mmio_magic_value: u32 = 0x7472_6976;
pub const mmio_version_legacy: u32 = 0x1;
pub const mmio_version_modern: u32 = 0x2;
pub const default_vendor_id: u32 = 0x1af4;
pub const guest_page_size_register_offset: u32 = 0x028;
pub const interrupt_ack_register_offset: u32 = 0x064;
pub const queue_interrupt_bit: u32 = 0x1;
pub const config_interrupt_bit: u32 = 0x2;
pub const supported_interrupt_bits: u32 = queue_interrupt_bit | config_interrupt_bit;

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

pub const ConfigWritePlanSummary = struct {
    anchor: []const u8,
    absolute_offset: u32,
    relative_offset: u32,
    config_generation: u32,
    previous_value: u32,
    planned_value: u32,
};

pub const ConfigWriteDispositionSummary = struct {
    anchor: []const u8,
    absolute_offset: u32,
    relative_offset: u32,
    end_offset: u32,
    config_generation: u32,
    previous_value: u32,
    planned_value: u32,
    changed_byte_mask: u8,
};

pub const TransportIdentitySummary = struct {
    anchor: []const u8,
    magic_value: u32,
    version: u32,
    device_id: u32,
    vendor_id: u32,
    magic_matches: bool,
    version_supported: bool,
    device_present: bool,
    vendor_id_present: bool,
    requires_legacy_guest_page_size: bool,
};

pub const ProbePreflightSummary = struct {
    anchor: []const u8,
    magic_matches: bool,
    version_supported: bool,
    device_present: bool,
    vendor_id_present: bool,
    requires_legacy_guest_page_size: bool,
    legacy_guest_page_size_register_ready: bool,
    bounded_queue_register_window_ready: bool,
    interrupt_ack_ready: bool,
    ready_for_probe_handoff: bool,
};

pub const SelectedQueueReadinessSummary = struct {
    anchor: []const u8,
    selected_queue: u16,
    queue_num_max: u16,
    queue_num: u16,
    queue_ready: bool,
    queue_size_programmed: bool,
    queue_ready_for_handoff: bool,
};

pub const VirtioMmioLab = struct {
    const Self = @This();

    queue_num_max: [queue_capacity]u16 = [_]u16{0} ** queue_capacity,
    queue_num: [queue_capacity]u16 = [_]u16{0} ** queue_capacity,
    queue_ready: [queue_capacity]bool = [_]bool{false} ** queue_capacity,
    device_feature_words: [feature_word_capacity]u32 = [_]u32{0} ** feature_word_capacity,
    config_window: [config_window_capacity]u8 = [_]u8{0} ** config_window_capacity,
    pending_config_write: ?ConfigWritePlanSummary = null,
    configured_queue_count: usize = 0,
    config_window_size: usize = 0,
    selected_queue: u16 = 0,
    selected_device_feature_word: u32 = 0,
    status: u8 = 0,
    interrupt_status: u32 = 0,
    config_generation: u32 = 0,
    driver_features: u32 = 0,
    magic_value: u32 = mmio_magic_value,
    version: u32 = mmio_version_modern,
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
                .magic_value => self.magic_value,
                .version => self.version,
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

    pub fn planConfigWriteOffset(self: *Self, offset: u32, planned_value: u32) !ConfigWritePlanSummary {
        const relative_offset = try checkedConfigWindowOffset(offset);
        const start = try self.checkedConfigWordRange(relative_offset);
        const plan = ConfigWritePlanSummary{
            .anchor = descriptor().anchor,
            .absolute_offset = offset,
            .relative_offset = relative_offset,
            .config_generation = self.config_generation,
            .previous_value = readLittleU32(self.config_window[start .. start + 4]),
            .planned_value = planned_value,
        };
        self.pending_config_write = plan;
        return plan;
    }

    pub fn configWriteDispositionSummary(self: *const Self) !ConfigWriteDispositionSummary {
        const plan = self.pending_config_write orelse return error.ConfigWritePlanUnavailable;
        return .{
            .anchor = plan.anchor,
            .absolute_offset = plan.absolute_offset,
            .relative_offset = plan.relative_offset,
            .end_offset = plan.absolute_offset + 4,
            .config_generation = plan.config_generation,
            .previous_value = plan.previous_value,
            .planned_value = plan.planned_value,
            .changed_byte_mask = computeChangedByteMask(plan.previous_value, plan.planned_value),
        };
    }

    pub fn transportIdentitySummary(self: *const Self) TransportIdentitySummary {
        return .{
            .anchor = descriptor().anchor,
            .magic_value = self.magic_value,
            .version = self.version,
            .device_id = self.device_id,
            .vendor_id = self.vendor_id,
            .magic_matches = self.magic_value == mmio_magic_value,
            .version_supported = self.version == mmio_version_legacy or self.version == mmio_version_modern,
            .device_present = self.device_id != 0,
            .vendor_id_present = self.vendor_id != 0,
            .requires_legacy_guest_page_size = self.version == mmio_version_legacy,
        };
    }

    pub fn probePreflightSummary(self: *const Self) ProbePreflightSummary {
        const identity = self.transportIdentitySummary();
        const legacy_guest_page_size_register_ready = guest_page_size_register_offset == 0x028;
        const bounded_queue_register_window_ready = self.configured_queue_count != 0 and
            @intFromEnum(Register.queue_num_max) == 0x034 and
            @intFromEnum(Register.queue_num) == 0x038 and
            @intFromEnum(Register.queue_ready) == 0x044;
        const interrupt_ack_ready = @intFromEnum(Register.interrupt_status) == 0x060 and
            interrupt_ack_register_offset == 0x064 and
            supported_interrupt_bits == (queue_interrupt_bit | config_interrupt_bit);

        return .{
            .anchor = identity.anchor,
            .magic_matches = identity.magic_matches,
            .version_supported = identity.version_supported,
            .device_present = identity.device_present,
            .vendor_id_present = identity.vendor_id_present,
            .requires_legacy_guest_page_size = identity.requires_legacy_guest_page_size,
            .legacy_guest_page_size_register_ready = legacy_guest_page_size_register_ready,
            .bounded_queue_register_window_ready = bounded_queue_register_window_ready,
            .interrupt_ack_ready = interrupt_ack_ready,
            .ready_for_probe_handoff = identity.magic_matches and
                identity.version_supported and
                identity.device_present and
                identity.vendor_id_present and
                (!identity.requires_legacy_guest_page_size or legacy_guest_page_size_register_ready) and
                bounded_queue_register_window_ready and
                interrupt_ack_ready,
        };
    }

    pub fn selectedQueueReadinessSummary(self: *const Self) !SelectedQueueReadinessSummary {
        const queue_index = try self.checkedQueueIndex(self.selected_queue);
        const queue_num_max = self.queue_num_max[queue_index];
        const queue_num = self.queue_num[queue_index];
        const queue_ready = self.queue_ready[queue_index];

        return .{
            .anchor = descriptor().anchor,
            .selected_queue = self.selected_queue,
            .queue_num_max = queue_num_max,
            .queue_num = queue_num,
            .queue_ready = queue_ready,
            .queue_size_programmed = queue_num != 0,
            .queue_ready_for_handoff = queue_num != 0 and queue_ready,
        };
    }

    pub fn stageConfigBytes(self: *Self, bytes: []const u8) !void {
        if (bytes.len > config_window_capacity) return error.ConfigWindowTooLarge;
        @memset(self.config_window[0..], 0);
        @memcpy(self.config_window[0..bytes.len], bytes);
        self.config_window_size = bytes.len;
    }

    pub fn seedTransportIdentity(self: *Self, magic_value: u32, version: u32, device_id: u32, vendor_id: u32) void {
        self.magic_value = magic_value;
        self.version = version;
        self.device_id = device_id;
        self.vendor_id = vendor_id;
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
        self.pending_config_write = null;
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

fn computeChangedByteMask(previous_value: u32, planned_value: u32) u8 {
    var mask: u8 = 0;
    for (0..4) |index| {
        const shift: u5 = @intCast(index * 8);
        const previous_byte: u8 = @truncate(previous_value >> shift);
        const planned_byte: u8 = @truncate(planned_value >> shift);
        if (previous_byte != planned_byte) {
            mask |= @as(u8, 1) << @intCast(index);
        }
    }
    return mask;
}

fn boolToU32(value: bool) u32 {
    return if (value) 1 else 0;
}

test "phase10 virtio mmio config-generation bumps clear stale planned config writes" {
    var device = try VirtioMmioLab.init(56, &[_]u16{ 8, 16 });

    try device.stageConfigBytes(&[_]u8{
        0x78, 0x56, 0x34, 0x12,
        0xef, 0xcd, 0xab, 0x90,
    });
    device.bumpConfigGeneration();

    const original = try device.readConfigOffset(mmio_window_bytes + 4);
    const plan = try device.planConfigWriteOffset(mmio_window_bytes + 4, 0x1122_3344);
    try std.testing.expectEqual(@as(u32, 1), plan.config_generation);
    try std.testing.expectEqual(plan, device.pending_config_write.?);

    device.bumpConfigGeneration();
    try std.testing.expectEqual(@as(?ConfigWritePlanSummary, null), device.pending_config_write);

    const unchanged = try device.readConfigOffset(mmio_window_bytes + 4);
    try std.testing.expectEqual(original.value, unchanged.value);
    try std.testing.expectEqual(@as(u32, 2), unchanged.config_generation);

    const refreshed = try device.planConfigWriteOffset(mmio_window_bytes + 4, 0x5566_7788);
    try std.testing.expectEqual(@as(u32, 2), refreshed.config_generation);
    try std.testing.expectEqual(original.value, refreshed.previous_value);
    try std.testing.expectEqual(@as(u32, 0x5566_7788), refreshed.planned_value);
}

test "phase10 virtio mmio summarizes config-write disposition without mutating config space" {
    var device = try VirtioMmioLab.init(57, &[_]u16{ 8, 16 });

    try device.stageConfigBytes(&[_]u8{
        0x78, 0x56, 0x34, 0x12,
        0xef, 0xcd, 0xab, 0x90,
    });
    device.bumpConfigGeneration();

    try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteDispositionSummary());

    _ = try device.planConfigWriteOffset(mmio_window_bytes + 4, 0x90ab_1200);
    const disposition = try device.configWriteDispositionSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", disposition.anchor);
    try std.testing.expectEqual(mmio_window_bytes + 4, disposition.absolute_offset);
    try std.testing.expectEqual(@as(u32, 4), disposition.relative_offset);
    try std.testing.expectEqual(mmio_window_bytes + 8, disposition.end_offset);
    try std.testing.expectEqual(@as(u32, 1), disposition.config_generation);
    try std.testing.expectEqual(@as(u32, 0x90ab_cdef), disposition.previous_value);
    try std.testing.expectEqual(@as(u32, 0x90ab_1200), disposition.planned_value);
    try std.testing.expectEqual(@as(u8, 0b0011), disposition.changed_byte_mask);

    _ = try device.planConfigWriteOffset(mmio_window_bytes + 4, 0x90ab_cdef);
    const same_value = try device.configWriteDispositionSummary();
    try std.testing.expectEqual(@as(u8, 0), same_value.changed_byte_mask);

    const config_summary = try device.readConfigOffset(mmio_window_bytes + 4);
    try std.testing.expectEqual(@as(u32, 0x90ab_cdef), config_summary.value);
    try std.testing.expectEqual(@as(u32, 1), config_summary.config_generation);

    device.bumpConfigGeneration();
    try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteDispositionSummary());
}

test "phase10 virtio mmio exposes a transport identity summary before lifecycle work" {
    var device = try VirtioMmioLab.init(58, &[_]u16{ 8, 16 });

    device.seedTransportIdentity(mmio_magic_value, mmio_version_legacy, 58, default_vendor_id);
    var summary = device.transportIdentitySummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, mmio_magic_value), summary.magic_value);
    try std.testing.expectEqual(@as(u32, mmio_version_legacy), summary.version);
    try std.testing.expectEqual(@as(u32, 58), summary.device_id);
    try std.testing.expectEqual(@as(u32, default_vendor_id), summary.vendor_id);
    try std.testing.expect(summary.magic_matches);
    try std.testing.expect(summary.version_supported);
    try std.testing.expect(summary.device_present);
    try std.testing.expect(summary.vendor_id_present);
    try std.testing.expect(summary.requires_legacy_guest_page_size);

    device.vendor_id = 0;
    device.device_id = 0;
    summary = device.transportIdentitySummary();
    try std.testing.expect(!summary.device_present);
    try std.testing.expect(!summary.vendor_id_present);
}

test "phase10 virtio mmio summarizes selected-queue readiness before transport handoff" {
    var device = try VirtioMmioLab.init(59, &[_]u16{ 8, 16 });

    var summary = try device.selectedQueueReadinessSummary();
    try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.c", summary.anchor);
    try std.testing.expectEqual(@as(u16, 0), summary.selected_queue);
    try std.testing.expectEqual(@as(u16, 8), summary.queue_num_max);
    try std.testing.expectEqual(@as(u16, 0), summary.queue_num);
    try std.testing.expect(!summary.queue_ready);
    try std.testing.expect(!summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_num, 8);
    summary = try device.selectedQueueReadinessSummary();
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_ready, 1);
    summary = try device.selectedQueueReadinessSummary();
    try std.testing.expect(summary.queue_ready);
    try std.testing.expect(summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_sel, 1);
    summary = try device.selectedQueueReadinessSummary();
    try std.testing.expectEqual(@as(u16, 1), summary.selected_queue);
    try std.testing.expectEqual(@as(u16, 16), summary.queue_num_max);
    try std.testing.expectEqual(@as(u16, 0), summary.queue_num);
    try std.testing.expect(!summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_ready_for_handoff);
}
