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

test "syncconfig nosilentupdate escapes quoted and backslashed values on the json env surface" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "riscv64",
        .nosilentupdate = "quoted\\path\"tail",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"syncconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--syncconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"riscv64\",\"KCONFIG_CONFIG\":\"out/.config\",\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\",\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\",\"KCONFIG_NOSILENTUPDATE\":\"quoted\\\\path\\\"tail\"}}\n",
        capture.list.items,
    );
}

test "syncconfig nosilentupdate escape path stays distinct from the silent argv flag" {
    var capture = try Capture.init(std.testing.allocator, 352);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "sync/.config",
        .arch = "x86_64",
        .silent = true,
        .nosilentupdate = "silent\\\"toggle",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--syncconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_NOSILENTUPDATE\":\"silent\\\\\\\"toggle\"") != null);
}
