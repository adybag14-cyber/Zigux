const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 512),
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

test "standalone syncconfig escapes paths and nosilentupdate while preserving silent argv order" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "arch/zigux/Kconfig\\\"bridge",
        .config = "out/.config\\nphase2",
        .arch = "x86_64\\tzigux",
        .silent = true,
        .nosilentupdate = "stamp\\tphase2\\nready",
    });

    const expected =
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"syncconfig\"," ++
        "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--syncconfig\",\"arch/zigux/Kconfig\\\\\\\"bridge\"]," ++
        "\"env\":{\"ARCH\":\"x86_64\\\\tzigux\",\"KCONFIG_CONFIG\":\"out/.config\\\\nphase2\"," ++
        "\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\"," ++
        "\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"," ++
        "\"KCONFIG_NOSILENTUPDATE\":\"stamp\\\\tphase2\\\\nready\"}}\n";

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--silent\",\"--syncconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\"") == null);
}
