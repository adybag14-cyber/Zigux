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

test "phase2 conf bridge keeps allmodconfig sentinel separate from explicit empty override" {
    var implicit_capture = try Capture.init(std.testing.allocator, 192);
    defer implicit_capture.deinit();

    try conf_bridge.runConfBridge(&implicit_capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "mod/.config",
        .arch = "arm",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"allmodconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--allmodconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"arm\",\"KCONFIG_CONFIG\":\"mod/.config\",\"KCONFIG_ALLCONFIG\":\"1\"}}\n",
        implicit_capture.list.items,
    );

    var explicit_capture = try Capture.init(std.testing.allocator, 192);
    defer explicit_capture.deinit();

    try conf_bridge.runConfBridge(&explicit_capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "mod/.config",
        .arch = "arm",
        .allconfig = "",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"allmodconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--allmodconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"arm\",\"KCONFIG_CONFIG\":\"mod/.config\",\"KCONFIG_ALLCONFIG\":\"\"}}\n",
        explicit_capture.list.items,
    );
}
