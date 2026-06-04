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

    pub fn writeAll(self: *TestCapture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *TestCapture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

fn expectSilentRewritePacket(
    mode: conf_bridge.Mode,
    mode_name: []const u8,
    mode_flag: []const u8,
    config_path: []const u8,
) !void {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = mode,
        .kconfig = "Kconfig",
        .config = config_path,
        .arch = "x86",
        .silent = true,
    });

    const expected_argv = try std.fmt.allocPrint(
        std.testing.allocator,
        "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"{s}\",\"Kconfig\"]",
        .{mode_flag},
    );
    defer std.testing.allocator.free(expected_argv);

    const expected_mode = try std.fmt.allocPrint(
        std.testing.allocator,
        "\"mode\":\"{s}\"",
        .{mode_name},
    );
    defer std.testing.allocator.free(expected_mode);

    const expected_config = try std.fmt.allocPrint(
        std.testing.allocator,
        "\"KCONFIG_CONFIG\":\"{s}\"",
        .{config_path},
    );
    defer std.testing.allocator.free(expected_config);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, expected_mode) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, expected_argv) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"x86\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, expected_config) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_ALLCONFIG") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_SEED") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_PROBABILITY") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_AUTOCONFIG") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_AUTOHEADER") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "KCONFIG_NOSILENTUPDATE") == null);
}

test "conf bridge emits silent rewrite mode packets without unrelated env entries" {
    try expectSilentRewritePacket(.yes2modconfig, "yes2modconfig", "--yes2modconfig", "rewrite/.config");
    try expectSilentRewritePacket(.mod2yesconfig, "mod2yesconfig", "--mod2yesconfig", "promote/.config");
    try expectSilentRewritePacket(.mod2noconfig, "mod2noconfig", "--mod2noconfig", "demote/.config");
}
