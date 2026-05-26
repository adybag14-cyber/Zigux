const std = @import("std");
const bridge = @import("conf_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator, capacity: usize) !@This() {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
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

test "conf bridge keeps silent syncconfig argv ordering with syncconfig-only env" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "riscv64",
        .silent = true,
        .nosilentupdate = "1",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"syncconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--syncconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"riscv64\",\"KCONFIG_CONFIG\":\"out/.config\",\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\",\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\",\"KCONFIG_NOSILENTUPDATE\":\"1\"}}\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_PROBABILITY\"") == null);
}

test "conf bridge escapes silent syncconfig nosilentupdate payload without leaking randconfig env" {
    var capture = try Capture.init(std.testing.allocator, 384);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "arch/riscv/Kconfig",
        .config = "sync/.config",
        .arch = "x86_64",
        .silent = true,
        .nosilentupdate = "line\nnext\rpath\t\x01",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"syncconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--syncconfig\",\"arch/riscv/Kconfig\"],\"env\":{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\"sync/.config\",\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\",\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\",\"KCONFIG_NOSILENTUPDATE\":\"line\\nnext\\rpath\\t\\u0001\"}}\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_PROBABILITY\"") == null);
}
