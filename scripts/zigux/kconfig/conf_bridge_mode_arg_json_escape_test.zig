const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator, capacity: usize) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
            .allocator = allocator,
        };
    }

    pub fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *@This(), bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *@This(), byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "conf bridge defconfig mode arg stays escaped in json argv output" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "arm64",
        .mode_arg = "arch/x86/configs/quoted\\\"path\\\\debug_defconfig",
    });

    try std.testing.expect(
        std.mem.indexOf(
            u8,
            capture.list.items,
            "\"argv\":[\"scripts/kconfig/conf\",\"--defconfig\",\"arch/x86/configs/quoted\\\\\\\"path\\\\\\\\debug_defconfig\",\"Kconfig\"]",
        ) != null,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"out/.config\"") != null);
}

test "conf bridge savedefconfig mode arg stays escaped in json argv output" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .mode_arg = "silent=debug\\\"\\\\defconfig",
    });

    try std.testing.expect(
        std.mem.indexOf(
            u8,
            capture.list.items,
            "\"argv\":[\"scripts/kconfig/conf\",\"--savedefconfig\",\"silent=debug\\\\\\\"\\\\\\\\defconfig\",\"Kconfig\"]",
        ) != null,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"x86_64\"") != null);
}
