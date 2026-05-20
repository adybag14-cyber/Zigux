const std = @import("std");
const conf_bridge = @import("./conf_bridge.zig");

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

    pub fn writeAll(self: *@This(), text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *@This(), byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "conf bridge keeps explicit empty allyesconfig allconfig distinct from sentinel and silent flag" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .allyesconfig,
        .kconfig = "Kconfig",
        .config = "yes/.config",
        .arch = "arm64",
        .silent = true,
        .allconfig = "",
    });

    try expectContains(capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--allyesconfig\"");
    try expectContains(capture.list.items, "\"mode\":\"allyesconfig\"");
    try expectContains(capture.list.items, "\"KCONFIG_ALLCONFIG\":\"\"");
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "\"--silent\"") == 1);
    try expectContains(capture.list.items, "\"ARCH\":\"arm64\"");
}

test "conf bridge escapes allyesconfig allconfig override text without falling back to sentinel" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .allyesconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .allconfig = "yes\\\\path\\\"packet.config",
    });

    try expectContains(capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--allyesconfig\"");
    try expectContains(capture.list.items, "\"mode\":\"allyesconfig\"");
    try expectContains(capture.list.items, "\"KCONFIG_ALLCONFIG\":\"yes\\\\\\\\path\\\\\\\"packet.config\"");
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--silent\"") == null);
    try expectContains(capture.list.items, "\"KCONFIG_CONFIG\":\".config\"");
}
