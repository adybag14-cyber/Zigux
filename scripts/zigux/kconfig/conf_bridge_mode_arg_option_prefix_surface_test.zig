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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "defconfig mode argument preserves embedded bridge option prefixes as path text" {
    var capture = try TestCapture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig",
        .config = "build/.config",
        .arch = "x86_64",
        .mode_arg = "arch/x86/configs/allconfig=mini/seed=7/probability=20_defconfig",
    });

    try expectContains(capture.list.items, "\"mode\":\"defconfig\"");
    try expectContains(capture.list.items, "\"--defconfig\",\"arch/x86/configs/allconfig=mini/seed=7/probability=20_defconfig\",\"Kconfig\"");
    try expectContains(capture.list.items, "\"KCONFIG_CONFIG\":\"build/.config\"");
    try expectMissing(capture.list.items, "\"KCONFIG_ALLCONFIG\"");
    try expectMissing(capture.list.items, "\"KCONFIG_SEED\"");
    try expectMissing(capture.list.items, "\"KCONFIG_PROBABILITY\"");
}

test "savedefconfig mode argument preserves nosilentupdate-looking path text" {
    var capture = try TestCapture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "arm64",
        .mode_arg = "configs/nosilentupdate=1/saved.config",
        .silent = true,
    });

    try expectContains(capture.list.items, "\"mode\":\"savedefconfig\"");
    try expectContains(capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--savedefconfig\",\"configs/nosilentupdate=1/saved.config\",\"Kconfig\"]");
    try expectContains(capture.list.items, "\"ARCH\":\"arm64\"");
    try expectMissing(capture.list.items, "\"KCONFIG_NOSILENTUPDATE\"");
}
