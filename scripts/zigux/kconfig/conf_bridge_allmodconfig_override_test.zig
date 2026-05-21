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

test "conf bridge keeps explicit empty allmodconfig override distinct from sentinel with silent flag" {
    var capture = try TestCapture.init(std.testing.allocator, 192);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "mod/.config",
        .arch = "arm64",
        .silent = true,
        .allconfig = "",
    });

    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--allmodconfig\",\"Kconfig\"]",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_ALLCONFIG\":\"\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_ALLCONFIG\":\"1\"",
    ) == null);
}

test "conf bridge json escapes quoted allmodconfig override text without falling back to sentinel" {
    var capture = try TestCapture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "mod/.config",
        .arch = "x86_64",
        .silent = true,
        .allconfig = "configs/mini-\\\"set\\\"\\\\overlay",
    });

    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--allmodconfig\",\"Kconfig\"]",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_ALLCONFIG\":\"configs/mini-\\\\\\\"set\\\\\\\"\\\\\\\\overlay\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_ALLCONFIG\":\"1\"",
    ) == null);
}
