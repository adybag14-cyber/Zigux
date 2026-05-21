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

test "conf bridge silentoldconfig alias emits canonical syncconfig packet" {
    const mode = bridge.Mode.parse("silentoldconfig").?;
    try std.testing.expectEqual(bridge.Mode.syncconfig, mode);

    var capture = try TestCapture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = mode,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "riscv64",
        .nosilentupdate = "1",
    });

    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"mode\":\"syncconfig\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"argv\":[\"scripts/kconfig/conf\",\"--syncconfig\",\"Kconfig\"]",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_NOSILENTUPDATE\":\"1\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "silentoldconfig",
    ) == null);
}

test "conf bridge silentoldconfig alias still omits empty nosilentupdate" {
    const mode = bridge.Mode.parse("silentoldconfig").?;
    try std.testing.expectEqualStrings("syncconfig", mode.text());
    try std.testing.expectEqualStrings("--syncconfig", mode.flag());

    var capture = try TestCapture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = mode,
        .kconfig = "Kconfig",
        .config = "build/.config",
        .arch = "arm64",
        .nosilentupdate = "",
    });

    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"mode\":\"syncconfig\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"argv\":[\"scripts/kconfig/conf\",\"--syncconfig\",\"Kconfig\"]",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_CONFIG\":\"build/.config\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"ARCH\":\"arm64\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_NOSILENTUPDATE\"",
    ) == null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"--silent\"",
    ) == null);
}
