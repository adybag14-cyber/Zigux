const std = @import("std");
const bridge = @import("conf_bridge.zig");

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

    pub fn writeAll(self: *TestCapture, text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *TestCapture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "conf bridge allmodconfig emits implicit allconfig sentinel" {
    var capture = try TestCapture.init(std.testing.allocator, 192);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "arm64",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--allmodconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
}

test "conf bridge allmodconfig keeps explicit empty allconfig override distinct from omission" {
    var capture = try TestCapture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "arm64",
        .allconfig = "",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"allmodconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--allmodconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\"out/.config\",\"KCONFIG_ALLCONFIG\":\"\"}}\n",
        capture.list.items,
    );
}

test "conf bridge allmodconfig escapes explicit allconfig override in json output" {
    var capture = try TestCapture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "arm64",
        .allconfig = "mini\\\"quoted\\\\path",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"allmodconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--allmodconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\"out/.config\",\"KCONFIG_ALLCONFIG\":\"mini\\\\\\\"quoted\\\\\\\\path\"}}\n",
        capture.list.items,
    );
}
