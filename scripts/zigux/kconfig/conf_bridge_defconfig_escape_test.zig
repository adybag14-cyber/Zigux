const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 512),
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

test "defconfig request escapes mode argument and environment payloads" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig\nroot",
        .config = "out/.config\r",
        .arch = "x86\t64",
        .silent = true,
        .mode_arg = "arch/x86/configs/zigux\"debug\\path\tdefconfig",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"defconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--defconfig\",\"arch/x86/configs/zigux\\\"debug\\\\path\\tdefconfig\",\"Kconfig\\nroot\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"x86\\t64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"out/.config\\r\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"allconfig_fallbacks\"") == null);
}
