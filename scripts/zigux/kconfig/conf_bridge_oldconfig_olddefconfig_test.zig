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

    pub fn writeAll(self: *Capture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "conf bridge emits oldconfig and olddefconfig without mode-specific env leakage" {
    const allocator = std.testing.allocator;

    var oldconfig_capture = try Capture.init(allocator, 192);
    defer oldconfig_capture.deinit();

    try conf_bridge.runConfBridge(&oldconfig_capture, .{
        .mode = .oldconfig,
        .kconfig = "Kconfig",
        .config = "refresh/.config",
        .arch = "x86",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"oldconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--oldconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"x86\",\"KCONFIG_CONFIG\":\"refresh/.config\"}}\n",
        oldconfig_capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, oldconfig_capture.list.items, "\"KCONFIG_ALLCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, oldconfig_capture.list.items, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, oldconfig_capture.list.items, "\"KCONFIG_SEED\"") == null);

    var olddefconfig_capture = try Capture.init(allocator, 192);
    defer olddefconfig_capture.deinit();

    try conf_bridge.runConfBridge(&olddefconfig_capture, .{
        .mode = .olddefconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"olddefconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--olddefconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\".config\"}}\n",
        olddefconfig_capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, olddefconfig_capture.list.items, "\"KCONFIG_ALLCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, olddefconfig_capture.list.items, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, olddefconfig_capture.list.items, "\"KCONFIG_NOSILENTUPDATE\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, olddefconfig_capture.list.items, "\"KCONFIG_PROBABILITY\"") == null);
}

test "conf bridge keeps silent before oldconfig and olddefconfig mode flags" {
    const allocator = std.testing.allocator;

    var oldconfig_capture = try Capture.init(allocator, 224);
    defer oldconfig_capture.deinit();

    try conf_bridge.runConfBridge(&oldconfig_capture, .{
        .mode = .oldconfig,
        .kconfig = "Kconfig",
        .config = "refresh/.config",
        .arch = "x86",
        .silent = true,
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"oldconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--oldconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"x86\",\"KCONFIG_CONFIG\":\"refresh/.config\"}}\n",
        oldconfig_capture.list.items,
    );

    var olddefconfig_capture = try Capture.init(allocator, 224);
    defer olddefconfig_capture.deinit();

    try conf_bridge.runConfBridge(&olddefconfig_capture, .{
        .mode = .olddefconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .silent = true,
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"olddefconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--olddefconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\".config\"}}\n",
        olddefconfig_capture.list.items,
    );
}
