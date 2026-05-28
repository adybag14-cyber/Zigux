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

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "conf bridge listnewconfig surface emits plain public packet without config side effects" {
    var capture = try TestCapture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .listnewconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "x86_64",
        .silent = true,
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"listnewconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--listnewconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\"out/.config\"}}\n",
        capture.list.items,
    );
    try expectAbsent(capture.list.items, "KCONFIG_ALLCONFIG");
    try expectAbsent(capture.list.items, "KCONFIG_AUTOCONFIG");
    try expectAbsent(capture.list.items, "KCONFIG_AUTOHEADER");
}
