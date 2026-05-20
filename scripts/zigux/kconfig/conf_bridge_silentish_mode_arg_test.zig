const std = @import("std");
const conf_bridge = @import("./conf_bridge.zig");

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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "conf bridge keeps silent-shaped defconfig mode argument distinct from silent flag" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "arm64",
        .silent = true,
        .mode_arg = "silent=debug\\\\profile\\\".defconfig",
    });

    try expectContains(capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--defconfig\"");
    try expectContains(capture.list.items, "\"silent=debug");
    try expectContains(capture.list.items, "profile\\\\");
    try expectContains(capture.list.items, "\\\".defconfig\"");
    try std.testing.expect(std.mem.count(u8, capture.list.items, "\"--silent\"") == 1);
    try expectContains(capture.list.items, "\"ARCH\":\"arm64\"");
}

test "conf bridge keeps silent-shaped savedefconfig path in argv without adding silent flag" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .mode_arg = "silent=trim\\\\artifact\\\".config",
    });

    try expectContains(capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--savedefconfig\"");
    try expectContains(capture.list.items, "\"silent=trim");
    try expectContains(capture.list.items, "artifact\\\\");
    try expectContains(capture.list.items, "\\\".config\"");
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--silent\"") == null);
    try expectContains(capture.list.items, "\"KCONFIG_CONFIG\":\".config\"");
}
