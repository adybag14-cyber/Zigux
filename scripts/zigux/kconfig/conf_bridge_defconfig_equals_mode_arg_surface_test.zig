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

test "standalone conf bridge defconfig keeps equals-bearing mode arg in argv" {
    var capture = try TestCapture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "arm64",
        .mode_arg = "arch/arm64/configs/debug=1_defconfig",
        .silent = true,
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"defconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--defconfig\",\"arch/arm64/configs/debug=1_defconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\"out/.config\"}}\n",
        capture.list.items,
    );
}

test "standalone conf bridge defconfig omits unrelated bridge env keys" {
    var capture = try TestCapture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .mode_arg = "arch/x86/configs/debug=1_defconfig",
        .silent = true,
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"allconfig_fallbacks\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_AUTOHEADER\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_NOSILENTUPDATE\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_PROBABILITY\"") == null);
}
