const std = @import("std");
const bridge = @import("./conf_bridge.zig");

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

test "conf bridge emits oldconfig packet without mode-specific env leakage" {
    var capture = try Capture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .oldconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "x86_64",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"oldconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--oldconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\"out/.config\"}}\n",
        capture.list.items,
    );
}

test "conf bridge emits olddefconfig packet without mode-specific env leakage" {
    var capture = try Capture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .olddefconfig,
        .kconfig = "Kconfig",
        .config = "build/.config",
        .arch = "arm64",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"olddefconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--olddefconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\"build/.config\"}}\n",
        capture.list.items,
    );
}
