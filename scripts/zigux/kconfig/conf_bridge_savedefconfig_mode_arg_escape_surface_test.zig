const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

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

    pub fn writeAll(self: *TestCapture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *TestCapture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "standalone savedefconfig mode argument JSON escapes path bytes" {
    var capture = try TestCapture.init(std.testing.allocator, 384);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "x86_64",
        .mode_arg = "arch/x86/configs/save\"debug\\path\tdefconfig",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"savedefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--savedefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"arch/x86/configs/save\\\"debug\\\\path\\tdefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"Kconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"out/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"x86_64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--silent\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\"") == null);
}
