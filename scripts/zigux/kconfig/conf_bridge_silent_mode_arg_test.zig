const std = @import("std");
const bridge = @import("conf_bridge.zig");

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

test "conf bridge keeps silent-prefixed savedefconfig path as argv mode argument" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .mode_arg = "silent=debug_defconfig",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"savedefconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--savedefconfig\",\"silent=debug_defconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\".config\"}}\n",
        capture.list.items,
    );
}

test "conf bridge keeps silent-prefixed savedefconfig path distinct from silent bridge option" {
    var capture = try Capture.init(std.testing.allocator, 384);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "arch/Kconfig",
        .config = "out/.config",
        .arch = "arm64",
        .silent = true,
        .mode_arg = "silent=mini_defconfig",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"savedefconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--savedefconfig\",\"silent=mini_defconfig\",\"arch/Kconfig\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\"out/.config\"}}\n",
        capture.list.items,
    );
}
