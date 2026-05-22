const std = @import("std");
const bridge = @import("conf_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator, capacity: usize) !Capture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
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

fn expectNoNonAllmodconfigEnv(output: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_AUTOHEADER\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_NOSILENTUPDATE\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_PROBABILITY\"") == null);
}

fn expectAllmodconfigSentinelPacket(config_path: []const u8, arch: []const u8, silent: bool) !void {
    var capture = try Capture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = config_path,
        .arch = arch,
        .silent = silent,
    });

    const expected_argv = if (silent)
        "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--allmodconfig\",\"Kconfig\"]"
    else
        "\"argv\":[\"scripts/kconfig/conf\",\"--allmodconfig\",\"Kconfig\"]";

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"allmodconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, expected_argv) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, config_path) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, arch) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"\"") == null);
    try expectNoNonAllmodconfigEnv(capture.list.items);
}

test "conf bridge allmodconfig emits implicit sentinel packet" {
    try expectAllmodconfigSentinelPacket("mod/.config", "arm", false);
}

test "conf bridge allmodconfig keeps sentinel with silent ahead of mode flag" {
    try expectAllmodconfigSentinelPacket("out/allmod.config", "arm64", true);
}
