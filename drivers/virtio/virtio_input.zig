const std = @import("std");

pub const max_descriptor_count: u16 = 1024;
pub const static_event_buffer_capacity: u16 = 64;
pub const config_bitmap_capacity: usize = 8;
pub const config_bitmap_bit_capacity: usize = 1024;
pub const abs_info_capacity: usize = 16;

pub const event_queue_index: u16 = 0;
pub const status_queue_index: u16 = 1;

pub const bus_virtual: u16 = 0x06;
pub const ev_abs: u8 = 0x03;
pub const ev_msc: u16 = 0x04;
pub const msc_timestamp: u16 = 0x05;
pub const abs_mt_slot: u16 = 0x2f;

pub const ConfigSelect = enum(u8) {
    unset = 0x00,
    id_name = 0x01,
    id_serial = 0x02,
    id_devids = 0x03,
    prop_bits = 0x10,
    ev_bits = 0x11,
    abs_info = 0x12,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_lab_validation: bool,
    touches_transport_mmio: bool,
    touches_dma_paths: bool,
};

pub const DeviceIds = struct {
    bustype: u16 = bus_virtual,
    vendor: u16 = 0,
    product: u16 = 0,
    version: u16 = 0,
};

pub const ConfigSnapshot = struct {
    anchor: []const u8,
    name: []const u8,
    serial: []const u8,
    phys: []const u8,
    ids: DeviceIds,
};

pub const QueuePlanSummary = struct {
    anchor: []const u8,
    event_queue_index: u16,
    status_queue_index: u16,
    event_descriptor_count: u16,
    status_descriptor_count: u16,
    queued_event_buffer_count: u16,
    ready: bool,
};

pub const RefillEventBuffersSummary = struct {
    anchor: []const u8,
    available_event_buffer_count: u16,
    queued_event_buffer_count_before: u16,
    queued_event_buffer_count_after: u16,
};

pub const StatusSendSummary = struct {
    anchor: []const u8,
    queue_index: u16,
    event_type: u16,
    code: u16,
    value: i32,
    sent: bool,
    suppressed_msc_timestamp: bool,
    queued_status_count: usize,
    suppressed_status_count: usize,
};

pub const StatusDrainSummary = struct {
    anchor: []const u8,
    completed_status_count: usize,
    pending_status_count_before: usize,
    pending_status_count_after: usize,
    suppressed_status_count: usize,
    ready: bool,
};

pub const AbsInfo = struct {
    minimum: i32,
    maximum: i32,
    fuzz: i32 = 0,
    flat: i32 = 0,
    resolution: i32 = 0,
};

pub const MultitouchSlotPlanSummary = struct {
    anchor: []const u8,
    abs_code: u16,
    advertised_slot_max: u16,
    planned_slot_count: u16,
    multitouch_enabled: bool,
};

pub const RegistrationBlocker = enum {
    event_queue_unconfigured,
    status_queue_unconfigured,
    event_buffers_unfilled,
    device_not_ready,
    capability_setup_incomplete,
    multitouch_slots_unplanned,
};

pub const RegistrationPreflightSummary = struct {
    anchor: []const u8,
    queue_plan_ready: bool,
    device_ready: bool,
    capability_setup_ready: bool,
    multitouch_slots_ready: bool,
    blocker: ?RegistrationBlocker,
    ready_for_registration: bool,
};

pub const QueueCallbackPreflightBlocker = enum {
    event_queue_unconfigured,
    status_queue_unconfigured,
    event_buffers_unfilled,
    device_not_ready,
};

pub const QueueCallbackPreflightSummary = struct {
    anchor: []const u8,
    event_queue_configured: bool,
    status_queue_configured: bool,
    queued_event_buffer_count: u16,
    event_buffers_ready: bool,
    device_ready: bool,
    blocker: ?QueueCallbackPreflightBlocker,
    ready_for_queue_callbacks: bool,
};

pub const ProbePreflightBlocker = enum {
    identity_incomplete,
    event_queue_unconfigured,
    status_queue_unconfigured,
    event_buffers_unfilled,
    device_not_ready,
    capability_setup_incomplete,
    multitouch_slots_unplanned,
};

pub const ProbePreflightSummary = struct {
    anchor: []const u8,
    identity_ready: bool,
    queue_plan_ready: bool,
    device_ready: bool,
    capability_setup_ready: bool,
    multitouch_slots_ready: bool,
    blocker: ?ProbePreflightBlocker,
    ready_for_probe_handoff: bool,
};

pub const TeardownObservationSummary = struct {
    anchor: []const u8,
    name: []const u8,
    serial: []const u8,
    phys: []const u8,
    ids: DeviceIds,
    event_queue_was_configured: bool,
    status_queue_was_configured: bool,
    queued_event_buffer_count: u16,
    queued_status_count: usize,
    suppressed_status_count: usize,
    ready_before_reset: bool,
    multitouch_was_enabled: bool,
    planned_multitouch_slots: u16,
    preserves_identity: bool,
    clears_runtime_state: bool,
    clears_capability_state: bool,
};

pub const VirtioInputLab = struct {
    const Self = @This();
    const ConfigBitmapBitSet = std.StaticBitSet(config_bitmap_bit_capacity);
    const ConfigBitmapRecord = struct {
        active: bool = false,
        select: ConfigSelect = .unset,
        subsel: u8 = 0,
        supported_bits: ConfigBitmapBitSet = ConfigBitmapBitSet.initEmpty(),
    };
    const AbsInfoRecord = struct {
        active: bool = false,
        abs_code: u16 = 0,
        metadata: AbsInfo = .{
            .minimum = 0,
            .maximum = 0,
        },
    };

    name_buffer: [64]u8 = [_]u8{0} ** 64,
    name_len: usize = 0,
    serial_buffer: [64]u8 = [_]u8{0} ** 64,
    serial_len: usize = 0,
    phys_buffer: [64]u8 = [_]u8{0} ** 64,
    phys_len: usize = 0,
    ids: DeviceIds = .{},
    event_descriptor_count: u16 = 0,
    status_descriptor_count: u16 = 0,
    queued_event_buffer_count: u16 = 0,
    queued_status_count: usize = 0,
    suppressed_status_count: usize = 0,
    config_bitmap_count: usize = 0,
    config_bitmaps: [config_bitmap_capacity]ConfigBitmapRecord = [_]ConfigBitmapRecord{ConfigBitmapRecord{}} ** config_bitmap_capacity,
    abs_info_count: usize = 0,
    abs_info_records: [abs_info_capacity]AbsInfoRecord = [_]AbsInfoRecord{AbsInfoRecord{}} ** abs_info_capacity,
    ready: bool = false,
    multitouch_enabled: bool = false,
    planned_multitouch_slots: u16 = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "virtio_input_lab",
            .anchor = "drivers/virtio/virtio_input.c",
            .provides_lab_validation = true,
            .touches_transport_mmio = false,
            .touches_dma_paths = false,
        };
    }

    pub fn init(
        name: []const u8,
        serial: []const u8,
        device_index: u16,
        ids: ?DeviceIds,
    ) !Self {
        var self = Self{};
        self.ids = ids orelse DeviceIds{};
        self.name_len = copyInto(&self.name_buffer, name);
        self.serial_len = copyInto(&self.serial_buffer, serial);
        const phys = try std.fmt.bufPrint(&self.phys_buffer, "virtio{d}/input0", .{device_index});
        self.phys_len = phys.len;
        return self;
    }

    pub fn reset(self: *Self) void {
        self.event_descriptor_count = 0;
        self.status_descriptor_count = 0;
        self.queued_event_buffer_count = 0;
        self.queued_status_count = 0;
        self.suppressed_status_count = 0;
        self.config_bitmap_count = 0;
        self.config_bitmaps = [_]ConfigBitmapRecord{ConfigBitmapRecord{}} ** config_bitmap_capacity;
        self.abs_info_count = 0;
        self.abs_info_records = [_]AbsInfoRecord{AbsInfoRecord{}} ** abs_info_capacity;
        self.ready = false;
        self.multitouch_enabled = false;
        self.planned_multitouch_slots = 0;
    }

    pub fn configSnapshot(self: *const Self) ConfigSnapshot {
        return .{
            .anchor = descriptor().anchor,
            .name = self.name_buffer[0..self.name_len],
            .serial = self.serial_buffer[0..self.serial_len],
            .phys = self.phys_buffer[0..self.phys_len],
            .ids = self.ids,
        };
    }

    pub fn configureEventQueue(self: *Self, descriptor_count: u16) !void {
        if (self.event_descriptor_count != 0) return error.EventQueueAlreadyConfigured;
        try validateDescriptorCount(descriptor_count);
        self.event_descriptor_count = descriptor_count;
    }

    pub fn configureStatusQueue(self: *Self, descriptor_count: u16) !void {
        if (self.status_descriptor_count != 0) return error.StatusQueueAlreadyConfigured;
        try validateDescriptorCount(descriptor_count);
        self.status_descriptor_count = descriptor_count;
    }

    pub fn fillEventBuffers(self: *Self) !QueuePlanSummary {
        if (self.event_descriptor_count == 0) return error.EventQueueNotConfigured;
        if (self.status_descriptor_count == 0) return error.StatusQueueNotConfigured;
        self.queued_event_buffer_count = @min(self.event_descriptor_count, static_event_buffer_capacity);
        return try self.queuePlanSummary();
    }

    pub fn refillEventBuffers(self: *Self, available_count: u16) !RefillEventBuffersSummary {
        if (self.event_descriptor_count == 0) return error.EventQueueNotConfigured;
        if (self.status_descriptor_count == 0) return error.StatusQueueNotConfigured;
        const before = self.queued_event_buffer_count;
        const after = @min(self.event_descriptor_count, before + available_count);
        self.queued_event_buffer_count = after;
        return .{
            .anchor = descriptor().anchor,
            .available_event_buffer_count = available_count,
            .queued_event_buffer_count_before = before,
            .queued_event_buffer_count_after = after,
        };
    }

    pub fn markReady(self: *Self) !void {
        if (self.event_descriptor_count == 0) return error.EventQueueNotConfigured;
        if (self.status_descriptor_count == 0) return error.StatusQueueNotConfigured;
        if (self.queued_event_buffer_count == 0) return error.EventBuffersUnfilled;
        self.ready = true;
    }

    pub fn setMultitouch(self: *Self, enabled: bool) void {
        self.multitouch_enabled = enabled;
    }

    pub fn configureConfigBitmap(
        self: *Self,
        select: ConfigSelect,
        subsel: u8,
        supported_bits: []const u16,
    ) !void {
        if (select != .prop_bits and select != .ev_bits) {
            return error.UnsupportedConfigBitmapSelect;
        }
        if (supported_bits.len == 0) return error.EmptyConfigBitmap;
        if (self.findConfigBitmapIndex(select, subsel) != null) return error.ConfigBitmapAlreadyConfigured;

        const record = try self.allocateConfigBitmapRecord();
        record.* = .{
            .active = true,
            .select = select,
            .subsel = subsel,
            .supported_bits = ConfigBitmapBitSet.initEmpty(),
        };

        for (supported_bits) |bit| {
            if (bit >= config_bitmap_bit_capacity) return error.ConfigBitmapBitOutOfRange;
            if (record.supported_bits.isSet(bit)) return error.ConfigBitmapBitDuplicate;
            record.supported_bits.set(bit);
        }
    }

    pub fn configureAbsInfo(self: *Self, abs_code: u16, metadata: AbsInfo) !void {
        if (metadata.minimum > metadata.maximum) return error.AbsInfoRangeInvalid;
        if (self.findAbsInfoIndex(abs_code) != null) return error.AbsInfoAlreadyConfigured;

        const record = try self.allocateAbsInfoRecord();
        record.* = .{
            .active = true,
            .abs_code = abs_code,
            .metadata = metadata,
        };
    }

    pub fn planMultitouchSlots(self: *Self) !MultitouchSlotPlanSummary {
        const index = self.findAbsInfoIndex(abs_mt_slot) orelse return error.MultitouchSlotAbsInfoNotConfigured;
        const record = self.abs_info_records[index];
        if (record.metadata.minimum < 0) return error.MultitouchSlotMinimumNegative;
        if (record.metadata.maximum < record.metadata.minimum) return error.MultitouchSlotCountInvalid;

        const slot_count_i64 = @as(i64, record.metadata.maximum) - @as(i64, record.metadata.minimum) + 1;
        if (slot_count_i64 <= 0) return error.MultitouchSlotCountInvalid;

        self.multitouch_enabled = true;
        self.planned_multitouch_slots = @intCast(slot_count_i64);

        return .{
            .anchor = descriptor().anchor,
            .abs_code = abs_mt_slot,
            .advertised_slot_max = @intCast(record.metadata.maximum),
            .planned_slot_count = self.planned_multitouch_slots,
            .multitouch_enabled = self.multitouch_enabled,
        };
    }

    pub fn queuePlanSummary(self: *const Self) !QueuePlanSummary {
        if (self.event_descriptor_count == 0) return error.EventQueueNotConfigured;
        if (self.status_descriptor_count == 0) return error.StatusQueueNotConfigured;

        return .{
            .anchor = descriptor().anchor,
            .event_queue_index = event_queue_index,
            .status_queue_index = status_queue_index,
            .event_descriptor_count = self.event_descriptor_count,
            .status_descriptor_count = self.status_descriptor_count,
            .queued_event_buffer_count = self.queued_event_buffer_count,
            .ready = self.ready,
        };
    }

    pub fn sendStatus(self: *Self, event_type: u16, code: u16, value: i32) !StatusSendSummary {
        if (self.status_descriptor_count == 0) return error.StatusQueueNotConfigured;
        if (!self.ready) return error.DeviceNotReady;

        const suppressed = self.multitouch_enabled and event_type == ev_msc and code == msc_timestamp;
        if (suppressed) {
            self.suppressed_status_count += 1;
        } else {
            self.queued_status_count += 1;
        }

        return .{
            .anchor = descriptor().anchor,
            .queue_index = status_queue_index,
            .event_type = event_type,
            .code = code,
            .value = value,
            .sent = !suppressed,
            .suppressed_msc_timestamp = suppressed,
            .queued_status_count = self.queued_status_count,
            .suppressed_status_count = self.suppressed_status_count,
        };
    }

    pub fn drainStatusQueue(self: *Self, completed_count: usize) !StatusDrainSummary {
        if (self.status_descriptor_count == 0) return error.StatusQueueNotConfigured;
        const before = self.queued_status_count;
        if (completed_count > before) return error.StatusCompletionCountExceedsQueued;

        self.queued_status_count -= completed_count;
        return .{
            .anchor = descriptor().anchor,
            .completed_status_count = completed_count,
            .pending_status_count_before = before,
            .pending_status_count_after = self.queued_status_count,
            .suppressed_status_count = self.suppressed_status_count,
            .ready = self.ready,
        };
    }

    pub fn registrationPreflightSummary(self: *const Self) RegistrationPreflightSummary {
        const queue_plan_ready = self.event_descriptor_count != 0 and self.status_descriptor_count != 0 and self.queued_event_buffer_count != 0;
        const capability_setup_ready = self.hasAbsCapability(abs_mt_slot) and self.findAbsInfoIndex(abs_mt_slot) != null;
        const multitouch_slots_ready = self.planned_multitouch_slots != 0;

        const blocker: ?RegistrationBlocker = if (self.event_descriptor_count == 0)
            .event_queue_unconfigured
        else if (self.status_descriptor_count == 0)
            .status_queue_unconfigured
        else if (self.queued_event_buffer_count == 0)
            .event_buffers_unfilled
        else if (!self.ready)
            .device_not_ready
        else if (!capability_setup_ready)
            .capability_setup_incomplete
        else if (!multitouch_slots_ready)
            .multitouch_slots_unplanned
        else
            null;

        return .{
            .anchor = descriptor().anchor,
            .queue_plan_ready = queue_plan_ready,
            .device_ready = self.ready,
            .capability_setup_ready = capability_setup_ready,
            .multitouch_slots_ready = multitouch_slots_ready,
            .blocker = blocker,
            .ready_for_registration = blocker == null,
        };
    }

    pub fn queueCallbackPreflightSummary(self: *const Self) QueueCallbackPreflightSummary {
        const event_queue_configured = self.event_descriptor_count != 0;
        const status_queue_configured = self.status_descriptor_count != 0;
        const event_buffers_ready = self.queued_event_buffer_count != 0;

        const blocker: ?QueueCallbackPreflightBlocker = if (!event_queue_configured)
            .event_queue_unconfigured
        else if (!status_queue_configured)
            .status_queue_unconfigured
        else if (!event_buffers_ready)
            .event_buffers_unfilled
        else if (!self.ready)
            .device_not_ready
        else
            null;

        return .{
            .anchor = descriptor().anchor,
            .event_queue_configured = event_queue_configured,
            .status_queue_configured = status_queue_configured,
            .queued_event_buffer_count = self.queued_event_buffer_count,
            .event_buffers_ready = event_buffers_ready,
            .device_ready = self.ready,
            .blocker = blocker,
            .ready_for_queue_callbacks = blocker == null,
        };
    }

    pub fn probePreflightSummary(self: *const Self) ProbePreflightSummary {
        const registration = self.registrationPreflightSummary();
        const identity_ready = self.name_len != 0 and self.phys_len != 0;

        const blocker: ?ProbePreflightBlocker = if (!identity_ready)
            .identity_incomplete
        else if (self.event_descriptor_count == 0)
            .event_queue_unconfigured
        else if (self.status_descriptor_count == 0)
            .status_queue_unconfigured
        else if (self.queued_event_buffer_count == 0)
            .event_buffers_unfilled
        else if (!registration.capability_setup_ready)
            .capability_setup_incomplete
        else if (!registration.multitouch_slots_ready)
            .multitouch_slots_unplanned
        else if (!self.ready)
            .device_not_ready
        else
            null;

        return .{
            .anchor = descriptor().anchor,
            .identity_ready = identity_ready,
            .queue_plan_ready = registration.queue_plan_ready,
            .device_ready = registration.device_ready,
            .capability_setup_ready = registration.capability_setup_ready,
            .multitouch_slots_ready = registration.multitouch_slots_ready,
            .blocker = blocker,
            .ready_for_probe_handoff = blocker == null,
        };
    }

    pub fn teardownObservationSummary(self: *const Self) TeardownObservationSummary {
        const clears_runtime_state = self.event_descriptor_count != 0 or
            self.status_descriptor_count != 0 or
            self.queued_event_buffer_count != 0 or
            self.queued_status_count != 0 or
            self.suppressed_status_count != 0 or
            self.ready or
            self.multitouch_enabled or
            self.planned_multitouch_slots != 0;
        const clears_capability_state = self.config_bitmap_count != 0 or
            self.abs_info_count != 0 or
            self.planned_multitouch_slots != 0;

        return .{
            .anchor = descriptor().anchor,
            .name = self.name_buffer[0..self.name_len],
            .serial = self.serial_buffer[0..self.serial_len],
            .phys = self.phys_buffer[0..self.phys_len],
            .ids = self.ids,
            .event_queue_was_configured = self.event_descriptor_count != 0,
            .status_queue_was_configured = self.status_descriptor_count != 0,
            .queued_event_buffer_count = self.queued_event_buffer_count,
            .queued_status_count = self.queued_status_count,
            .suppressed_status_count = self.suppressed_status_count,
            .ready_before_reset = self.ready,
            .multitouch_was_enabled = self.multitouch_enabled,
            .planned_multitouch_slots = self.planned_multitouch_slots,
            .preserves_identity = true,
            .clears_runtime_state = clears_runtime_state,
            .clears_capability_state = clears_capability_state,
        };
    }

    fn validateDescriptorCount(descriptor_count: u16) !void {
        if (descriptor_count == 0) return error.EmptyDescriptorCount;
        if (descriptor_count > max_descriptor_count) return error.DescriptorCountTooLarge;
        if (!std.math.isPowerOfTwo(descriptor_count)) return error.DescriptorCountMustBePowerOfTwo;
    }

    fn allocateConfigBitmapRecord(self: *Self) !*ConfigBitmapRecord {
        for (&self.config_bitmaps) |*record| {
            if (record.active) continue;
            self.config_bitmap_count += 1;
            return record;
        }
        return error.ConfigBitmapCapacityExceeded;
    }

    fn findConfigBitmapIndex(self: *const Self, select: ConfigSelect, subsel: u8) ?usize {
        for (self.config_bitmaps, 0..) |record, index| {
            if (!record.active) continue;
            if (record.select == select and record.subsel == subsel) return index;
        }
        return null;
    }

    fn allocateAbsInfoRecord(self: *Self) !*AbsInfoRecord {
        for (&self.abs_info_records) |*record| {
            if (record.active) continue;
            self.abs_info_count += 1;
            return record;
        }
        return error.AbsInfoCapacityExceeded;
    }

    fn findAbsInfoIndex(self: *const Self, abs_code: u16) ?usize {
        for (self.abs_info_records, 0..) |record, index| {
            if (!record.active) continue;
            if (record.abs_code == abs_code) return index;
        }
        return null;
    }

    fn hasAbsCapability(self: *const Self, bit: u16) bool {
        if (bit >= config_bitmap_bit_capacity) return false;
        const index = self.findConfigBitmapIndex(.ev_bits, ev_abs) orelse return false;
        return self.config_bitmaps[index].supported_bits.isSet(bit);
    }

    fn copyInto(buffer: []u8, source: []const u8) usize {
        const copy_len = @min(buffer.len, source.len);
        @memcpy(buffer[0..copy_len], source[0..copy_len]);
        return copy_len;
    }
};

test "phase10 virtio input teardown summary keeps device ids explicit across reset" {
    const ids = DeviceIds{
        .vendor = 0x1af4,
        .product = 0x1052,
        .version = 7,
    };
    var device = try VirtioInputLab.init("virtio-touch", "teardown-ids", 12, ids);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();
    _ = try device.sendStatus(0x02, 0x01, 9);

    const before_reset = device.teardownObservationSummary();
    try std.testing.expectEqualDeep(ids, before_reset.ids);
    try std.testing.expect(before_reset.preserves_identity);
    try std.testing.expect(before_reset.clears_runtime_state);

    device.reset();

    const after_reset = device.teardownObservationSummary();
    try std.testing.expectEqualDeep(ids, after_reset.ids);
    try std.testing.expect(after_reset.preserves_identity);
    try std.testing.expect(!after_reset.clears_runtime_state);
    try std.testing.expect(!after_reset.clears_capability_state);
}
