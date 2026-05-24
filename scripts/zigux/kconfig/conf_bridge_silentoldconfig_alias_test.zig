const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

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

test "conf bridge standalone silentoldconfig alias keeps syncconfig packet" {
    const mode = conf_bridge.Mode.parse("silentoldconfig").?;
    try std.testing.expectEqual(conf_bridge.Mode.syncconfig, mode);
    try std.testing.expectEqualStrings("syncconfig", mode.text());
    try std.testing.expectEqualStrings("--syncconfig", mode.flag());

    var capture = try TestCapture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = mode,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "x86_64",
        .silent = true,
        .nosilentupdate = "1",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"syncconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--syncconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_NOSILENTUPDATE\":\"1\"") != null);
}
