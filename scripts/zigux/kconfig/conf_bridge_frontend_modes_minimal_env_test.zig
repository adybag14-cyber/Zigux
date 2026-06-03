const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
        };
    }

    fn deinit(self: *TestCapture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *TestCapture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *TestCapture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

fn expectFrontendModeHasMinimalEnv(mode: conf_bridge.Mode, mode_text: []const u8, flag: []const u8) !void {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = mode,
        .kconfig = "Kconfig",
        .config = "front/.config",
        .arch = "x86_64",
        .silent = true,
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, mode_text) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, flag) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--silent\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"front/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"x86_64\"") != null);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_ALLCONFIG") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "allconfig_fallbacks") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_AUTOCONFIG") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_AUTOHEADER") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_NOSILENTUPDATE") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_SEED") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_PROBABILITY") == null);
}

test "standalone frontend modes keep env minimal" {
    try expectFrontendModeHasMinimalEnv(.oldaskconfig, "\"mode\":\"oldaskconfig\"", "\"--oldaskconfig\"");
    try expectFrontendModeHasMinimalEnv(.listnewconfig, "\"mode\":\"listnewconfig\"", "\"--listnewconfig\"");
    try expectFrontendModeHasMinimalEnv(.helpnewconfig, "\"mode\":\"helpnewconfig\"", "\"--helpnewconfig\"");
}
