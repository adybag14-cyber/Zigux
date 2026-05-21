const std = @import("std");
const bridge = @import("conf_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator, capacity: usize) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
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

fn expectNoRewriteModeLeaks(output: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_ALLCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_AUTOHEADER\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_NOSILENTUPDATE\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_PROBABILITY\"") == null);
}

fn expectRewritePacket(
    mode: bridge.Mode,
    mode_text: []const u8,
    mode_flag: []const u8,
    config_path: []const u8,
    arch: []const u8,
    silent: bool,
) !void {
    var capture = try Capture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = mode,
        .kconfig = "Kconfig",
        .config = config_path,
        .arch = arch,
        .silent = silent,
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, mode_text) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, mode_flag) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, config_path) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, arch) != null);

    const expected_argv = if (silent)
        try std.fmt.allocPrint(std.testing.allocator, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"{s}\",\"Kconfig\"]", .{mode_flag})
    else
        try std.fmt.allocPrint(std.testing.allocator, "\"argv\":[\"scripts/kconfig/conf\",\"{s}\",\"Kconfig\"]", .{mode_flag});
    defer std.testing.allocator.free(expected_argv);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, expected_argv) != null);
    try expectNoRewriteModeLeaks(capture.list.items);
}

test "conf bridge rewrite modes emit canonical argv and env packets" {
    try expectRewritePacket(.yes2modconfig, "\"mode\":\"yes2modconfig\"", "--yes2modconfig", "rewrite/.config", "x86", false);
    try expectRewritePacket(.mod2yesconfig, "\"mode\":\"mod2yesconfig\"", "--mod2yesconfig", "promote/.config", "x86", false);
    try expectRewritePacket(.mod2noconfig, "\"mode\":\"mod2noconfig\"", "--mod2noconfig", "demote/.config", "x86", false);
}

test "conf bridge rewrite modes keep silent ahead of the mode flag without extra env" {
    try expectRewritePacket(.yes2modconfig, "\"mode\":\"yes2modconfig\"", "--yes2modconfig", "rewrite/.config", "x86", true);
    try expectRewritePacket(.mod2yesconfig, "\"mode\":\"mod2yesconfig\"", "--mod2yesconfig", "promote/.config", "x86", true);
    try expectRewritePacket(.mod2noconfig, "\"mode\":\"mod2noconfig\"", "--mod2noconfig", "demote/.config", "x86", true);
}
