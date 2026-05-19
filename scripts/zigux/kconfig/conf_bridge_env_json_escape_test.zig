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

test "conf bridge preserves JSON escaping for randconfig env overrides" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "x86_64",
        .allconfig = "seed\"path\\branch",
        .probability = "15:25\\\"quoted",
    });

    try std.testing.expect(
        std.mem.indexOf(
            u8,
            capture.list.items,
            "\"KCONFIG_ALLCONFIG\":\"seed\\\"path\\\\branch\"",
        ) != null,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            capture.list.items,
            "\"KCONFIG_PROBABILITY\":\"15:25\\\\\\\"quoted\"",
        ) != null,
    );
}

test "conf bridge preserves JSON escaping for syncconfig nosilentupdate" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "riscv64",
        .nosilentupdate = "need\"quiet\\later",
    });

    try std.testing.expect(
        std.mem.indexOf(
            u8,
            capture.list.items,
            "\"KCONFIG_NOSILENTUPDATE\":\"need\\\"quiet\\\\later\"",
        ) != null,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            capture.list.items,
            "\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\"",
        ) != null,
    );
}
