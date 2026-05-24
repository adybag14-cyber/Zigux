const std = @import("std");
const bridge = @import("./conf_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 192),
            .allocator = allocator,
        };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *@This(), bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *@This(), byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "conf bridge keeps explicit empty allmodconfig override distinct from sentinel" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "mod/.config",
        .arch = "arm",
        .allconfig = "",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"allmodconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--allmodconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"arm\",\"KCONFIG_CONFIG\":\"mod/.config\",\"KCONFIG_ALLCONFIG\":\"\"}}\n",
        capture.list.items,
    );
}

test "conf bridge falls back to allmodconfig sentinel without override" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "mod/.config",
        .arch = "arm",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"allmodconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--allmodconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"arm\",\"KCONFIG_CONFIG\":\"mod/.config\",\"KCONFIG_ALLCONFIG\":\"1\"}}\n",
        capture.list.items,
    );
}
