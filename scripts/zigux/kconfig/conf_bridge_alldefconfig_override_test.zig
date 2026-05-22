const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator, capacity: usize) !Capture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
        };
    }

    fn deinit(self: *Capture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "alldefconfig explicit allconfig override suppresses sentinel" {
    var implicit_capture = try Capture.init(std.testing.allocator, 192);
    defer implicit_capture.deinit();

    try conf_bridge.runConfBridge(&implicit_capture, .{
        .mode = .alldefconfig,
        .kconfig = "Kconfig",
        .config = "arch/.config",
        .arch = "arm64",
    });

    try std.testing.expect(std.mem.indexOf(u8, implicit_capture.list.items, "\"mode\":\"alldefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, implicit_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);

    var explicit_capture = try Capture.init(std.testing.allocator, 224);
    defer explicit_capture.deinit();

    try conf_bridge.runConfBridge(&explicit_capture, .{
        .mode = .alldefconfig,
        .kconfig = "Kconfig",
        .config = "arch/.config",
        .arch = "arm64",
        .silent = true,
        .allconfig = "",
    });

    try std.testing.expect(std.mem.indexOf(u8, explicit_capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--alldefconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_capture.list.items, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_capture.list.items, "\"KCONFIG_SEED\"") == null);
}

test "alldefconfig explicit allconfig override stays json escaped" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .alldefconfig,
        .kconfig = "Kconfig",
        .config = "arch/.config",
        .arch = "arm64",
        .silent = true,
        .allconfig = "configs/\"quoted\"\\\\bridge",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--alldefconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"configs/\\\"quoted\\\"\\\\\\\\bridge\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
}
