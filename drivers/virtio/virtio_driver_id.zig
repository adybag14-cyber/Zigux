const std = @import("std");

pub const any_id: u32 = 0xffff_ffff;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_lab_validation: bool,
    touches_transport_mmio: bool,
};

pub const RegistrationIdentitySummary = struct {
    anchor: []const u8,
    device_index: u32,
    device_id: u32,
    vendor_id: u32,
    device_name: []const u8,
    modalias: []const u8,
};

pub const DriverIdMatchRule = struct {
    device_id: u32,
    vendor_id: u32,
};

pub const DriverIdMatchSummary = struct {
    anchor: []const u8,
    device_id: u32,
    vendor_id: u32,
    candidate_count: usize,
    matched: bool,
    matched_rule_index: ?usize,
    matched_device_any: bool,
    matched_vendor_any: bool,
};

pub const VirtioDriverIdMatcher = struct {
    const Self = @This();

    device_index: u32,
    device_id: u32,
    vendor_id: u32,
    device_name_buffer: [32]u8,
    device_name_len: usize,
    modalias_buffer: [32]u8,
    modalias_len: usize,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "virtio_driver_id_matcher_lab",
            .anchor = "drivers/virtio/virtio.c",
            .provides_lab_validation = true,
            .touches_transport_mmio = false,
        };
    }

    pub fn init(device_index: u32, device_id: u32, vendor_id: u32) !Self {
        var self = Self{
            .device_index = device_index,
            .device_id = device_id,
            .vendor_id = vendor_id,
            .device_name_buffer = [_]u8{0} ** 32,
            .device_name_len = 0,
            .modalias_buffer = [_]u8{0} ** 32,
            .modalias_len = 0,
        };

        self.device_name_len = try formatInto(
            self.device_name_buffer[0..],
            "virtio{}",
            .{device_index},
        );
        self.modalias_len = try formatInto(
            self.modalias_buffer[0..],
            "virtio:d{x:0>8}v{x:0>8}",
            .{ device_id, vendor_id },
        );
        return self;
    }

    pub fn registrationSummary(self: *const Self) RegistrationIdentitySummary {
        return .{
            .anchor = descriptor().anchor,
            .device_index = self.device_index,
            .device_id = self.device_id,
            .vendor_id = self.vendor_id,
            .device_name = self.device_name_buffer[0..self.device_name_len],
            .modalias = self.modalias_buffer[0..self.modalias_len],
        };
    }

    pub fn driverIdMatchSummary(
        self: *const Self,
        rules: []const DriverIdMatchRule,
    ) DriverIdMatchSummary {
        for (rules, 0..) |rule, index| {
            const device_matches = rule.device_id == self.device_id or rule.device_id == any_id;
            if (!device_matches) continue;

            const vendor_matches = rule.vendor_id == self.vendor_id or rule.vendor_id == any_id;
            if (!vendor_matches) continue;

            return .{
                .anchor = descriptor().anchor,
                .device_id = self.device_id,
                .vendor_id = self.vendor_id,
                .candidate_count = rules.len,
                .matched = true,
                .matched_rule_index = index,
                .matched_device_any = rule.device_id == any_id,
                .matched_vendor_any = rule.vendor_id == any_id,
            };
        }

        return .{
            .anchor = descriptor().anchor,
            .device_id = self.device_id,
            .vendor_id = self.vendor_id,
            .candidate_count = rules.len,
            .matched = false,
            .matched_rule_index = null,
            .matched_device_any = false,
            .matched_vendor_any = false,
        };
    }

    fn formatInto(buffer: []u8, comptime fmt: []const u8, args: anytype) !usize {
        const rendered = try std.fmt.bufPrint(buffer, fmt, args);
        return rendered.len;
    }
};