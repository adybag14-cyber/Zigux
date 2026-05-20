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

test "conf bridge keeps defconfig mode arguments containing equals in argv" {
    var capture = try TestCapture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "x86_64",
        .mode_arg = "arch/x86/configs/debug=1_defconfig",
    });

    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"argv\":[\"scripts/kconfig/conf\",\"--defconfig\",\"arch/x86/configs/debug=1_defconfig\",\"Kconfig\"]",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_ALLCONFIG\"",
    ) == null);
}

test "conf bridge keeps savedefconfig mode arguments containing equals distinct from silent" {
    var capture = try TestCapture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "arm64",
        .silent = true,
        .mode_arg = "out/silent=release.config",
    });

    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--savedefconfig\",\"out/silent=release.config\",\"Kconfig\"]",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_CONFIG\":\".config\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_ALLCONFIG\"",
    ) == null);
}
