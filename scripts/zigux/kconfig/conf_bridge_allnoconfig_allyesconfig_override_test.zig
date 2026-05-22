const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

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

test "allnoconfig explicit allconfig override stays escaped and suppresses sentinel" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .allnoconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "arm64",
        .silent = true,
        .allconfig = "configs/\\\"quoted\\\"\\\\bridge",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"allnoconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--allnoconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\"out/.config\",\"KCONFIG_ALLCONFIG\":\"configs/\\\\\\\"quoted\\\\\\\"\\\\\\\\bridge\"}}\n",
        capture.list.items,
    );
}

test "allyesconfig explicit empty allconfig override stays distinct from implicit sentinel" {
    var implicit_capture = try Capture.init(std.testing.allocator, 192);
    defer implicit_capture.deinit();

    try conf_bridge.runConfBridge(&implicit_capture, .{
        .mode = .allyesconfig,
        .kconfig = "Kconfig",
        .config = "yes/.config",
        .arch = "x86_64",
    });

    try std.testing.expect(std.mem.indexOf(u8, implicit_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);

    var explicit_capture = try Capture.init(std.testing.allocator, 192);
    defer explicit_capture.deinit();

    try conf_bridge.runConfBridge(&explicit_capture, .{
        .mode = .allyesconfig,
        .kconfig = "Kconfig",
        .config = "yes/.config",
        .arch = "x86_64",
        .allconfig = "",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"allyesconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--allyesconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\"yes/.config\",\"KCONFIG_ALLCONFIG\":\"\"}}\n",
        explicit_capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, explicit_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_capture.list.items, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_capture.list.items, "\"KCONFIG_SEED\"") == null);
}
