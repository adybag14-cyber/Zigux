const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "syncconfig nosilentupdate value is json escaped and syncconfig scoped" {
    var syncconfig_capture = try TestCapture.init(std.testing.allocator);
    defer syncconfig_capture.deinit();

    try conf_bridge.runConfBridge(&syncconfig_capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "riscv64",
        .silent = true,
        .nosilentupdate = "force\"regen\\next\n\t\x01",
    });

    const syncconfig_packet = syncconfig_capture.list.items;
    try expectContains(syncconfig_packet, "\"mode\":\"syncconfig\"");
    try expectContains(syncconfig_packet, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--syncconfig\",\"Kconfig\"]");
    try expectContains(syncconfig_packet, "\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\"");
    try expectContains(syncconfig_packet, "\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"");
    try expectContains(syncconfig_packet, "\"KCONFIG_NOSILENTUPDATE\":\"force\\\"regen\\\\next\\n\\t\\u0001\"");
    try expectMissing(syncconfig_packet, "\"KCONFIG_ALLCONFIG\"");
    try expectMissing(syncconfig_packet, "\"KCONFIG_SEED\"");
    try expectMissing(syncconfig_packet, "\"KCONFIG_PROBABILITY\"");

    var olddefconfig_capture = try TestCapture.init(std.testing.allocator);
    defer olddefconfig_capture.deinit();

    try conf_bridge.runConfBridge(&olddefconfig_capture, .{
        .mode = .olddefconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .nosilentupdate = "force\"regen\\next\n\t\x01",
    });

    const olddefconfig_packet = olddefconfig_capture.list.items;
    try expectContains(olddefconfig_packet, "\"mode\":\"olddefconfig\"");
    try expectMissing(olddefconfig_packet, "\"KCONFIG_NOSILENTUPDATE\"");
    try expectMissing(olddefconfig_packet, "\"KCONFIG_AUTOCONFIG\"");
    try expectMissing(olddefconfig_packet, "\"KCONFIG_AUTOHEADER\"");
}
