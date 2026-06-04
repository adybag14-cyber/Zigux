const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    bytes: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .allocator = allocator,
            .bytes = try std.ArrayList(u8).initCapacity(allocator, 256),
        };
    }

    fn deinit(self: *Capture) void {
        self.bytes.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, text: []const u8) !void {
        try self.bytes.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.bytes.append(self.allocator, byte);
    }
};

test "syncconfig nosilentupdate public surface json-escapes value bytes" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "riscv64",
        .nosilentupdate = "quote\"slash\\line\nlow\x01",
    });

    const output = capture.bytes.items;
    try std.testing.expect(std.mem.indexOf(u8, output, "\"mode\":\"syncconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_NOSILENTUPDATE\":\"quote\\\"slash\\\\line\\nlow\\u0001\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_PROBABILITY\"") == null);
}
