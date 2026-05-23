const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 320),
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

test "conf bridge standalone proof escapes quoted and backslashed allconfig override in json output" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .allnoconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "arm64",
        .allconfig = "mini\\\"quoted\\\\path",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"allnoconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--allnoconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\"out/.config\",\"KCONFIG_ALLCONFIG\":\"mini\\\\\\\"quoted\\\\\\\\path\"}}\n",
        capture.list.items,
    );
}
