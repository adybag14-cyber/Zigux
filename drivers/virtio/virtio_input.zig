const std = @import("std");

pub const queue_capacity: usize = 2;
pub const max_descriptor_count: u16 = 1024;
pub const static_event_buffer_capacity: u16 = 64;
pub const config_bitmap_capacity: usize = 8;
pub const config_bitmap_bit_capacity: usize = 1024;
pub const abs_info_capacity: usize = 16;
pub const multitouch_slot_capacity: u16 = 32;

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
    supported_selects: [6]ConfigSelect,
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

pub const ConfigBitmapSummary = struct {
    anchor: []const u8,
    select: ConfigSelect,
    subsel: u8,
    supported_bit_count: usize,
    surfaces_selected_event_type: bool,
};

pub const AbsInfo = struct {
    minimum: i32,
    maximum: i32,
    fuzz: i32 = 0,
    flat: i32 = 0,
    resolution: i32 = 0,
};

pub const AbsInfoSummary = struct {
    anchor: []const u8,
    abs_code: u16,
    minimum: i32,
    maximum: i32,
    fuzz: i32,
    flat: i32,
    resolution: i32,
};

pub const CapabilitySetupSummary = struct {
    anchor: []const u8,
    property_bit_count: usize,
    staged_event_type_count: usize,
    staged_capability_count: usize,
    staged_abs_param_count: usize,
    stages_abs_params: bool,
};

pub const MultitouchSlotSummary = struct {
    anchor: []const u8,
    abs_code: u16,
    advertised_slot_max: u16,
    planned_slot_count: u16,
    multitouch_enabled: bool,
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

pub const VirtioInputLab = struct {
    const Self = @This();
    const ConfigBitmapBitSet = std.StaticBitSet(config_bitmap_bit_capacity);
    const ConfigBitmapRecord = struct {
        active: bool = false,
        select: ConfigSelect = .unset,
        subsel: u8 = 0,
        supported_bits: ConfigBitmapBitSet = ConfigBitmapBitSet.initEmpty(),
        surfaces_selected_event_type: bool = false,
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
    planned_multitouch_slots: u16 = 0,
    ready: bool = false,
    multitouch_enabled: bool = false,

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
        self.planned_multitouch_slots = 0;
        self.ready = false;
        self.multitouch_enabled = false;
    }

    pub fn configSnapshot(self: *const Self) ConfigSnapshot {
        return .{
            .anchor = descriptor().anchor,
            .name = self.name_buffer[0..self.name_len],
            .serial = self.serial_buffer[0..self.serial_len],
            .phys = self.phys_buffer[0..self.phys_len],
            .ids = self.ids,
            .supported_selects = .{
                .id_name,
                .id_serial,
                .id_devids,
                .prop_bits,
                .ev_bits,
                .abs_info,
            },
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
        self.queued_event_buffer_count = @min(self.event_descriptor_count, static_event_buffer_capacity);
        return try self.queuePlanSummary();
    }

    pub fn markReady(self: *Self) !void {
        if (self.event_descriptor_count == 0) return error.EventQueueNotConfigured;
        if (self.status_descriptor_count == 0) return error.StatusQueueNotConfigured;
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
            .surfaces_selected_event_type = select == .ev_bits,
        };

        for (supported_bits) |bit| {
            if (bit >= config_bitmap_bit_capacity) return error.ConfigBitmapBitOutOfRange;
            if (record.supported_bits.isSet(bit)) return error.ConfigBitmapBitDuplicate;
            record.supported_bits.set(bit);
        }
    }

    pub fn configBitmapSummary(self: *const Self, select: ConfigSelect, subsel: u8) !ConfigBitmapSummary {
        const index = self.findConfigBitmapIndex(select, subsel) orelse return error.ConfigBitmapNotConfigured;
        const record = self.config_bitmaps[index];
        return .{
            .anchor = descriptor().anchor,
            .select = record.select,
            .subsel = record.subsel,
            .supported_bit_count = record.supported_bits.count(),
            .surfaces_selected_event_type = record.surfaces_selected_event_type,
        };
    }

    pub fn configBitmapSupportsBit(self: *const Self, select: ConfigSelect, subsel: u8, bit: u16) !bool {
        if (bit >= config_bitmap_bit_capacity) return error.ConfigBitmapBitOutOfRange;

        const index = self.findConfigBitmapIndex(select, subsel) orelse return error.ConfigBitmapNotConfigured;
        return self.config_bitmaps[index].supported_bits.isSet(bit);
    }

    pub fn configureAbsInfo(self: *Self, abs_code: u16, metadata: AbsInfo) !void {
        if (metadata.minimum > metadata.maximum) return error.AbsInfoRangeInvalid;
        if (metadata.fuzz < 0) return error.AbsInfoNegativeFuzz;
        if (metadata.flat < 0) return error.AbsInfoNegativeFlat;
        if (metadata.resolution < 0) return error.AbsInfoNegativeResolution;
        if (self.findAbsInfoIndex(abs_code) != null) return error.AbsInfoAlreadyConfigured;

        const record = try self.allocateAbsInfoRecord();
        record.* = .{
            .active = true,
            .abs_code = abs_code,
            .metadata = metadata,
        };
    }

    pub fn absInfoSummary(self: *const Self, abs_code: u16) !AbsInfoSummary {
        const index = self.findAbsInfoIndex(abs_code) orelse return error.AbsInfoNotConfigured;
        const record = self.abs_info_records[index];
        return .{
            .anchor = descriptor().anchor,
            .abs_code = record.abs_code,
            .minimum = record.metadata.minimum,
            .maximum = record.metadata.maximum,
            .fuzz = record.metadata.fuzz,
            .flat = record.metadata.flat,
            .resolution = record.metadata.resolution,
        };
    }

    pub fn capabilitySetupSummary(self: *const Self) !CapabilitySetupSummary {
        var property_bit_count: usize = 0;
        var staged_event_type_count: usize = 0;
        var staged_capability_count: usize = 0;

        for (self.config_bitmaps) |record| {
            if (!record.active) continue;
            switch (record.select) {
                .prop_bits => {
                    property_bit_count += record.supported_bits.count();
                },
                .ev_bits => {
                    staged_event_type_count += 1;
                    staged_capability_count += record.supported_bits.count();
                },
                else => {},
            }
        }

        if (staged_event_type_count == 0) return error.CapabilityConfigNotConfigured;

        if (self.abs_info_count != 0) {
            const abs_index = self.findConfigBitmapIndex(.ev_bits, ev_abs) orelse return error.AbsCapabilitiesNotConfigured;
            const abs_bitmap = self.config_bitmaps[abs_index].supported_bits;
            for (self.abs_info_records) |record| {
                if (!record.active) continue;
                if (record.abs_code >= config_bitmap_bit_capacity) return error.AbsCodeOutOfRange;
                if (!abs_bitmap.isSet(record.abs_code)) return error.AbsAxisMissingCapabilityBit;
            }
        }

        return .{
            .anchor = descriptor().anchor,
            .property_bit_count = property_bit_count,
            .staged_event_type_count = staged_event_type_count,
            .staged_capability_count = staged_capability_count,
            .staged_abs_param_count = self.abs_info_count,
            .stages_abs_params = self.abs_info_count != 0,
        };
    }

    pub fn planMultitouchSlots(self: *Self) !MultitouchSlotSummary {
        const abs_index = self.findConfigBitmapIndex(.ev_bits, ev_abs) orelse return error.AbsCapabilitiesNotConfigured;
        const abs_bitmap = self.config_bitmaps[abs_index].supported_bits;
        if (!abs_bitmap.isSet(abs_mt_slot)) return error.MultitouchSlotCapabilityMissing;

        const slot_index = self.findAbsInfoIndex(abs_mt_slot) orelse return error.MultitouchSlotAbsInfoNotConfigured;
        const slot_metadata = self.abs_info_records[slot_index].metadata;
        if (slot_metadata.maximum < 0) return error.MultitouchSlotMaximumNegative;
        if (slot_metadata.minimum != 0) return error.MultitouchSlotMinimumMustBeZero;

        const advertised_slot_max: u16 = @intCast(slot_metadata.maximum);
        if (advertised_slot_max >= multitouch_slot_capacity) return error.MultitouchSlotCountTooLarge;

        self.planned_multitouch_slots = advertised_slot_max + 1;
        self.multitouch_enabled = true;

        return .{
            .anchor = descriptor().anchor,
            .abs_code = abs_mt_slot,
            .advertised_slot_max = advertised_slot_max,
            .planned_slot_count = self.planned_multitouch_slots,
            .multitouch_enabled = self.multitouch_enabled,
        };
    }

    pub fn queueCallbackPreflightSummary(self: *const Self) QueueCallbackPreflightSummary {
        const event_queue_configured = self.event_descriptor_count != 0;
        const status_queue_configured = self.status_descriptor_count != 0;
        const queued_event_buffer_count = self.queued_event_buffer_count;
        const event_buffers_ready = queued_event_buffer_count != 0;
        const device_ready = self.ready;

        const blocker: ?QueueCallbackPreflightBlocker = if (!event_queue_configured)
            .event_queue_unconfigured
        else if (!status_queue_configured)
            .status_queue_unconfigured
        else if (!event_buffers_ready)
            .event_buffers_unfilled
        else if (!device_ready)
            .device_not_ready
        else
            null;

        return .{
            .anchor = descriptor().anchor,
            .event_queue_configured = event_queue_configured,
            .status_queue_configured = status_queue_configured,
            .queued_event_buffer_count = queued_event_buffer_count,
            .event_buffers_ready = event_buffers_ready,
            .device_ready = device_ready,
            .blocker = blocker,
            .ready_for_queue_callbacks = blocker == null,
        };
    }

    pub fn registrationPreflightSummary(self: *const Self) RegistrationPreflightSummary {
        const queue_callback_preflight = self.queueCallbackPreflightSummary();
        const queue_plan_ready = queue_callback_preflight.event_queue_configured and
            queue_callback_preflight.status_queue_configured and
            queue_callback_preflight.event_buffers_ready;
        const device_ready = queue_callback_preflight.device_ready;
        const capability_setup_ready = self.capabilitySetupReady();
        const multitouch_slots_ready = !self.multitouchSlotsRequired() or self.planned_multitouch_slots != 0;

        const blocker: ?RegistrationBlocker = if (!queue_callback_preflight.event_queue_configured)
            .event_queue_unconfigured
        else if (!queue_callback_preflight.status_queue_configured)
            .status_queue_unconfigured
        else if (!queue_callback_preflight.event_buffers_ready)
            .event_buffers_unfilled
        else if (!device_ready)
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
            .device_ready = device_ready,
            .capability_setup_ready = capability_setup_ready,
            .multitouch_slots_ready = multitouch_slots_ready,
            .blocker = blocker,
            .ready_for_registration = blocker == null,
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

    pub fn drainStatusQueue(self: *Self, completed_status_count: usize) !StatusDrainSummary {
        if (self.status_descriptor_count == 0) return error.StatusQueueNotConfigured;
        if (completed_status_count == 0) return error.EmptyStatusCompletionCount;
        if (completed_status_count > self.queued_status_count) return error.StatusCompletionCountExceedsQueued;

        const pending_status_count_before = self.queued_status_count;
        self.queued_status_count -= completed_status_count;

        return .{
            .anchor = descriptor().anchor,
            .completed_status_count = completed_status_count,
            .pending_status_count_before = pending_status_count_before,
            .pending_status_count_after = self.queued_status_count,
            .suppressed_status_count = self.suppressed_status_count,
            .ready = self.ready,
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

    fn validateDescriptorCount(descriptor_count: u16) !void {
        if (descriptor_count == 0) return error.EmptyDescriptorCount;
        if (descriptor_count > max_descriptor_count) return error.DescriptorCountTooLarge;
        if (!std.math.isPowerOfTwo(descriptor_count)) return error.DescriptorCountMustBePowerOfTwo;
    }

    fn capabilitySetupReady(self: *const Self) bool {
        _ = self.capabilitySetupSummary() catch return false;
        return true;
    }

    fn multitouchSlotsRequired(self: *const Self) bool {
        const abs_index = self.findConfigBitmapIndex(.ev_bits, ev_abs) orelse return false;
        return self.config_bitmaps[abs_index].supported_bits.isSet(abs_mt_slot);
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

    fn copyInto(buffer: []u8, source: []const u8) usize {
        const copy_len = @min(buffer.len, source.len);
        @memcpy(buffer[0..copy_len], source[0..copy_len]);
        return copy_len;
    }
};