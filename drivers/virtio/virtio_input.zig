const std = @import("std");

pub const queue_capacity: usize = 2;
pub const max_descriptor_count: u16 = 1024;
pub const static_event_buffer_capacity: u16 = 64;
pub const config_bitmap_capacity: usize = 8;
pub const config_bitmap_bit_capacity: usize = 1024;

pub const event_queue_index: u16 = 0;
pub const status_queue_index: u16 = 1;

pub const bus_virtual: u16 = 0x06;
pub const ev_msc: u16 = 0x04;
pub const msc_timestamp: u16 = 0x05;

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

    fn copyInto(buffer: []u8, source: []const u8) usize {
        const copy_len = @min(buffer.len, source.len);
        @memcpy(buffer[0..copy_len], source[0..copy_len]);
        return copy_len;
    }
};