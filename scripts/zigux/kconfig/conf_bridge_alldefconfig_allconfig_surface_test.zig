const std = @import("std");
const bridge = @import("conf_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator, capacity: usize) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
        };
    }

    fn deinit(self: *TestCapture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *TestCapture, text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *TestCapture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "standalone conf bridge alldefconfig keeps explicit allconfig override on public surface" {
    var capture = try TestCapture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .alldefconfig,
        .kconfig = "Kconfig",
        .config = "build/.config",
        .arch = "arm64",
        .allconfig = "configs/mini-all.config",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"alldefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--alldefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"configs/mini-all.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"allconfig_fallbacks\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"arm64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"build/.config\"") != null);
}

test "standalone conf bridge alldefconfig escapes explicit allconfig override text" {
    var capture = try TestCapture.init(std.testing.allocator, 384);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .alldefconfig,
        .kconfig = "Kconfig",
        .config = "build/.config",
        .arch = "arm64",
        .allconfig = "configs/mini\"all\\\\set
next",
        .silent = true,
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--alldefconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"configs/mini\\\"all\\\\\\\\set\\nnext\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"allconfig_fallbacks\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_PROBABILITY\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_NOSILENTUPDATE\"") == null);
}
