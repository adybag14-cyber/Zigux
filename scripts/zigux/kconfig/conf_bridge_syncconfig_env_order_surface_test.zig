const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 384),
        };
    }

    fn deinit(self: *Capture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

fn expectBefore(packet: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, packet, earlier) orelse return error.MissingEarlierNeedle;
    const later_index = std.mem.indexOf(u8, packet, later) orelse return error.MissingLaterNeedle;
    try std.testing.expect(earlier_index < later_index);
}

test "standalone conf bridge syncconfig silent env order surface" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "riscv64",
        .silent = true,
        .nosilentupdate = "1",
    });

    const packet = capture.list.items;
    const expected =
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"syncconfig\"," ++
        "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--syncconfig\",\"Kconfig\"]," ++
        "\"env\":{\"ARCH\":\"riscv64\",\"KCONFIG_CONFIG\":\"out/.config\"," ++
        "\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\"," ++
        "\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"," ++
        "\"KCONFIG_NOSILENTUPDATE\":\"1\"}}\n";

    try std.testing.expectEqualStrings(expected, packet);
    try expectBefore(packet, "\"--silent\"", "\"--syncconfig\"");
    try expectBefore(packet, "\"KCONFIG_AUTOCONFIG\"", "\"KCONFIG_AUTOHEADER\"");
    try expectBefore(packet, "\"KCONFIG_AUTOHEADER\"", "\"KCONFIG_NOSILENTUPDATE\"");
    try std.testing.expect(std.mem.indexOf(u8, packet, "\"KCONFIG_ALLCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, packet, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, packet, "\"KCONFIG_PROBABILITY\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, packet, "\"allconfig_fallbacks\"") == null);
}
