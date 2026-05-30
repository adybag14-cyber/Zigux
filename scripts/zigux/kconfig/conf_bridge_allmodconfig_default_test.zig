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

test "allmodconfig default path does not synthesize allconfig sentinel" {
    var capture = try TestCapture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "mod/.config",
        .arch = "arm",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"allmodconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--allmodconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"allconfig_fallbacks\"") == null);
}
