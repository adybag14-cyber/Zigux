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

test "phase2 conf bridge escapes defconfig mode argument before kconfig" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "arm64",
        .mode_arg = "arch/arm64/configs/board \\\"debug\\\"\\\\path defconfig",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"defconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--defconfig\",\"arch/arm64/configs/board \\\\\\\"debug\\\\\\\"\\\\\\\\path defconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\"out/.config\"}}\n",
        capture.list.items,
    );
}

test "phase2 conf bridge escapes savedefconfig mode argument before kconfig" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .mode_arg = "out/defconfigs/zigux \\\"release\\\"\\\\trimmed",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"savedefconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--savedefconfig\",\"out/defconfigs/zigux \\\\\\\"release\\\\\\\"\\\\\\\\trimmed\",\"Kconfig\"],\"env\":{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\".config\"}}\n",
        capture.list.items,
    );
}
