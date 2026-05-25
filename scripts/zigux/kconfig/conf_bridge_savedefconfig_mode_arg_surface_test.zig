const std = @import("std");
const bridge = @import("conf_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator, capacity: usize) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
            .allocator = allocator,
        };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *@This(), text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *@This(), byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "conf bridge keeps savedefconfig silent-prefixed mode arg in argv payload position" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .mode_arg = "silent=debug_defconfig",
    });

    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"argv\":[\"scripts/kconfig/conf\",\"--savedefconfig\",\"silent=debug_defconfig\",\"Kconfig\"]",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"mode\":\"savedefconfig\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"--silent\"",
    ) == null);
}

test "conf bridge json escapes savedefconfig mode arg without mutating argv ordering" {
    var capture = try Capture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "Kcon\"fig",
        .config = ".con\\fig",
        .arch = "arm64",
        .mode_arg = "silent=debug\\\"cfg\\\\tail\\n\\t\x01",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"savedefconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--savedefconfig\",\"silent=debug\\\\\\\"cfg\\\\\\\\tail\\\\n\\\\t\\u0001\",\"Kcon\\\"fig\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\".con\\\\fig\"}}\n",
        capture.list.items,
    );
}
