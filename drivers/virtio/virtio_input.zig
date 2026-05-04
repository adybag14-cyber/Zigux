const std = @import("std");
const registration_blocker = @import("virtio_input_registration_blocker");

pub const queue_capacity: usize = 2;
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

pub const MultitouchSlotPlanSummary = struct {
    anchor: []const u8,
    abs_code: u16,
    minimum: i32,
    maximum: i32,
    slot_count: usize,
    staged_abs_param_count: usize,
    initializes_slots: bool,
};

pub const TeardownPlanSummary = struct {
    anchor: []const u8,
    ready: bool,
    queued_event_buffer_count: u16,
    queued_status_count: usize,
    suppressed_status_count: usize,
    config_bitmap_count: usize,
    abs_info_count: usize,
    multitouch_enabled: bool,
    clears_queue_plan_on_reset: bool,
    clears_status_counters_on_reset: bool,
    clears_config_on_reset: bool,
    clears_abs_info_on_reset: bool,
    clears_multitouch_on_reset: bool,
    preserves_identity_strings: bool,
};

pub const RegistrationPreflightSummary = struct {
    anchor: []const u8,
    identity_ready: bool,
    staged_event_type_count: usize,
    staged_capability_count: usize,
    staged_abs_param_count: usize,
    multitouch_enabled: bool,
    multitouch_slot_intent: bool,
    multitouch_slot_required: bool,
    multitouch_slot_requirement_ready: bool,
    multitouch_slots_ready: bool,
    multitouch_slot_count: usize,
    ready_for_registration: bool,
};

pub const QueueCallbackPreflightSummary = struct {
    anchor: []const u8,
    event_queue_index: u16,
    status_queue_index: u16,
    queued_event_buffer_count: u16,
    event_buffers_ready: bool,
    status_queue_configured: bool,
    device_ready: bool,
    registration_ready: bool,
    ready_for_queue_callback: bool,
};

pub const ProbePreflightSummary = struct {
    anchor: []const u8,
    supported_select_count: usize,
    identity_ready: bool,
    capability_ready: bool,
    registration_ready: bool,
    event_queue_configured: bool,
    status_queue_configured: bool,
    event_buffers_ready: bool,
    device_ready: bool,
    ready_for_probe_handoff: bool,
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

    pub fn multitouchSlotPlanSummary(self: *const Self) !MultitouchSlotPlanSummary {
        const capability_summary = try self.capabilitySetupSummary();
        const slot_index = self.findAbsInfoIndex(abs_mt_slot) orelse return error.MultitouchSlotAbsInfoNotConfigured;
        const slot_record = self.abs_info_records[slot_index];

        if (slot_record.metadata.minimum < 0) return error.MultitouchSlotMinimumNegative;

        const slot_count_i64 = @as(i64, slot_record.metadata.maximum) - @as(i64, slot_record.metadata.minimum) + 1;
        if (slot_count_i64 <= 0) return error.MultitouchSlotCountInvalid;

        return .{
            .anchor = descriptor().anchor,
            .abs_code = slot_record.abs_code,
            .minimum = slot_record.metadata.minimum,
            .maximum = slot_record.metadata.maximum,
            .slot_count = @intCast(slot_count_i64),
            .staged_abs_param_count = capability_summary.staged_abs_param_count,
            .initializes_slots = true,
        };
    }

    pub fn teardownPlanSummary(self: *const Self) TeardownPlanSummary {
        return .{
            .anchor = descriptor().anchor,
            .ready = self.ready,
            .queued_event_buffer_count = self.queued_event_buffer_count,
            .queued_status_count = self.queued_status_count,
            .suppressed_status_count = self.suppressed_status_count,
            .config_bitmap_count = self.config_bitmap_count,
            .abs_info_count = self.abs_info_count,
            .multitouch_enabled = self.multitouch_enabled,
            .clears_queue_plan_on_reset = true,
            .clears_status_counters_on_reset = true,
            .clears_config_on_reset = true,
            .clears_abs_info_on_reset = true,
            .clears_multitouch_on_reset = true,
            .preserves_identity_strings = true,
        };
    }

    pub fn registrationPreflightSummary(self: *const Self) !RegistrationPreflightSummary {
        const capability_summary = try self.capabilitySetupSummary();
        const identity_ready = self.name_len != 0 and self.serial_len != 0 and self.phys_len != 0;

        const multitouch_slot_intent = self.findAbsInfoIndex(abs_mt_slot) != null;
        const multitouch_slot_required = self.multitouch_enabled;
        var multitouch_slots_ready = true;
        var multitouch_slot_requirement_ready = !multitouch_slot_required;
        var multitouch_slot_count: usize = 0;
        if (multitouch_slot_intent) {
            const slot_summary = try self.multitouchSlotPlanSummary();
            multitouch_slot_count = slot_summary.slot_count;
            multitouch_slots_ready = slot_summary.initializes_slots;
            multitouch_slot_requirement_ready = slot_summary.initializes_slots;
        }

        return .{
            .anchor = descriptor().anchor,
            .identity_ready = identity_ready,
            .staged_event_type_count = capability_summary.staged_event_type_count,
            .staged_capability_count = capability_summary.staged_capability_count,
            .staged_abs_param_count = capability_summary.staged_abs_param_count,
            .multitouch_enabled = self.multitouch_enabled,
            .multitouch_slot_intent = multitouch_slot_intent,
            .multitouch_slot_required = multitouch_slot_required,
            .multitouch_slot_requirement_ready = multitouch_slot_requirement_ready,
            .multitouch_slots_ready = multitouch_slots_ready,
            .multitouch_slot_count = multitouch_slot_count,
            .ready_for_registration = identity_ready and
                capability_summary.staged_capability_count != 0 and
                multitouch_slot_requirement_ready,
        };
    }

    pub fn queueCallbackPreflightSummary(self: *const Self) !QueueCallbackPreflightSummary {
        const registration_summary = try self.registrationPreflightSummary();
        const event_buffers_ready = self.queued_event_buffer_count != 0;
        const status_queue_configured = self.status_descriptor_count != 0;

        return .{
            .anchor = descriptor().anchor,
            .event_queue_index = event_queue_index,
            .status_queue_index = status_queue_index,
            .queued_event_buffer_count = self.queued_event_buffer_count,
            .event_buffers_ready = event_buffers_ready,
            .status_queue_configured = status_queue_configured,
            .device_ready = self.ready,
            .registration_ready = registration_summary.ready_for_registration,
            .ready_for_queue_callback = registration_summary.ready_for_registration and event_buffers_ready and status_queue_configured and self.ready,
        };
    }

    pub fn probePreflightSummary(self: *const Self) !ProbePreflightSummary {
        const snapshot = self.configSnapshot();
        const registration_summary = try self.registrationPreflightSummary();
        const queue_summary = try self.queueCallbackPreflightSummary();
        const event_queue_configured = self.event_descriptor_count != 0;

        return .{
            .anchor = descriptor().anchor,
            .supported_select_count = snapshot.supported_selects.len,
            .identity_ready = registration_summary.identity_ready,
            .capability_ready = registration_summary.staged_capability_count != 0,
            .registration_ready = registration_summary.ready_for_registration,
            .event_queue_configured = event_queue_configured,
            .status_queue_configured = queue_summary.status_queue_configured,
            .event_buffers_ready = queue_summary.event_buffers_ready,
            .device_ready = queue_summary.device_ready,
            .ready_for_probe_handoff = registration_summary.ready_for_registration and
                event_queue_configured and
                queue_summary.status_queue_configured and
                queue_summary.event_buffers_ready and
                queue_summary.device_ready,
        };
    }

    pub fn registrationBlockerSummary(self: *const Self) !registration_blocker.RegistrationBlockerSummary {
        const registration_summary = try self.registrationPreflightSummary();
        const queue_summary = try self.queueCallbackPreflightSummary();
        const probe_summary = try self.probePreflightSummary();

        return registration_blocker.summarize(.{
            .registration_preflight_ready = registration_summary.ready_for_registration,
            .queue_callback_ready = queue_summary.ready_for_queue_callback,
            .probe_handoff_ready = probe_summary.ready_for_probe_handoff,
        });
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