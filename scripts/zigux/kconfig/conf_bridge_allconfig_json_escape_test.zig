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

test "conf bridge escapes quoted and backslashed allconfig override in allnoconfig output" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .allnoconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "arm64",
        .allconfig = "mini\\\"quoted\\\\path",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"allnoconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--allnoconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\"out/.config\",\"KCONFIG_ALLCONFIG\":\"mini\\\\\\\"quoted\\\\\\\\path\"}}\n",
        capture.list.items,
    );
}

test "conf bridge keeps escaped allyesconfig allconfig override without sentinel fallback" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .allyesconfig,
        .kconfig = "Kconfig",
        .config = "yes/.config",
        .arch = "x86_64",
        .allconfig = "yes\\\"pack\\\\path",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"allyesconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"yes\\\\\\\"pack\\\\\\\\path\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
}
