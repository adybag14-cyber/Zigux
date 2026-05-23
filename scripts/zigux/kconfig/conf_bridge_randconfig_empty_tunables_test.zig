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

test "conf bridge omits empty randconfig tunables while keeping explicit empty allconfig" {
    var capture = try TestCapture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "rand/.config",
        .arch = "x86_64",
        .silent = true,
        .allconfig = "",
        .seed = null,
        .probability = null,
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--randconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_PROBABILITY\"") == null);
}

test "conf bridge omits empty randconfig tunables while keeping the default sentinel" {
    var capture = try TestCapture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "rand/.config",
        .arch = "arm64",
        .seed = null,
        .probability = null,
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"randconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_PROBABILITY\"") == null);
}
