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

test "standalone conf bridge allmodconfig default packet omits allconfig override state" {
    var capture = try Capture.init(std.testing.allocator, 192);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "build/.config",
        .arch = "x86_64",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"allmodconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--allmodconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\"build/.config\"}}\n",
        capture.list.items,
    );
}

test "standalone conf bridge allmodconfig explicit empty override keeps empty env value and fallbacks" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .allmodconfig,
        .kconfig = "arch/Kconfig",
        .config = ".config.mod",
        .arch = "arm64",
        .silent = true,
        .allconfig = "",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"allmodconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--allmodconfig\",\"arch/Kconfig\"],\"allconfig_fallbacks\":[\"allmod.config\",\"all.config\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\".config.mod\",\"KCONFIG_ALLCONFIG\":\"\"}}\n",
        capture.list.items,
    );
}
