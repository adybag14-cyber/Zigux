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

fn expectConversionModePacket(mode: conf_bridge.Mode, mode_text: []const u8, mode_flag: []const u8, config: []const u8) !void {
    var capture = try TestCapture.init(std.testing.allocator, 192);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = mode,
        .kconfig = "Kconfig",
        .config = config,
        .arch = "x86_64",
    });

    var expected_packet_buffer: [192]u8 = undefined;
    const expected_packet = try std.fmt.bufPrint(
        &expected_packet_buffer,
        "{{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"{s}\",\"argv\":[\"scripts/kconfig/conf\",\"{s}\",\"Kconfig\"],\"env\":{{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\"{s}\"}}}}\n",
        .{ mode_text, mode_flag, config },
    );

    try std.testing.expectEqualStrings(expected_packet, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_ALLCONFIG") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_SEED") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_PROBABILITY") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_AUTOCONFIG") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_AUTOHEADER") == null);
}

test "standalone conf bridge conversion modes keep minimal argv and env surface" {
    try expectConversionModePacket(.yes2modconfig, "yes2modconfig", "--yes2modconfig", "rewrite/.config");
    try expectConversionModePacket(.mod2yesconfig, "mod2yesconfig", "--mod2yesconfig", "promote/.config");
    try expectConversionModePacket(.mod2noconfig, "mod2noconfig", "--mod2noconfig", "demote/.config");
}
