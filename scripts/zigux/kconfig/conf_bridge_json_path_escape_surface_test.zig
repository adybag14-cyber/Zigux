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

test "standalone conf bridge escapes core path and arch strings" {
    var capture = try TestCapture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .olddefconfig,
        .kconfig = "boards/\"quoted\"\\Kconfig\n",
        .config = "out/debug\t.config",
        .arch = "x86_64\x01test",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"olddefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--olddefconfig\",\"boards/\\\"quoted\\\"\\\\Kconfig\\n\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"x86_64\\u0001test\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"out/debug\\t.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\"") == null);
}
