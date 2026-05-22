const std = @import("std");
const bridge = @import("conf_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator, capacity: usize) !@This() {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
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

fn expectNoModeArgumentLeaks(output: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_ALLCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_AUTOHEADER\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_NOSILENTUPDATE\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_PROBABILITY\"") == null);
}

test "conf bridge defconfig keeps path-shaped mode argument before Kconfig" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "x86_64",
        .mode_arg = "arch/x86/configs/silent_debug=1_defconfig",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"defconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--defconfig\",\"arch/x86/configs/silent_debug=1_defconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"out/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"x86_64\"") != null);
    try expectNoModeArgumentLeaks(capture.list.items);
}

test "conf bridge savedefconfig keeps silent ahead of a silent-prefixed output path" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "arm64",
        .silent = true,
        .mode_arg = "silent.save",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"savedefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--savedefconfig\",\"silent.save\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\".config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"arm64\"") != null);
    try expectNoModeArgumentLeaks(capture.list.items);
}
