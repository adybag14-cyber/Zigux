const std = @import("std");
const bridge = @import("conf_bridge.zig");

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

test "conf bridge escapes explicit allconfig overrides in json output" {
    var capture = try TestCapture.init(std.testing.allocator, 384);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .allnoconfig,
        .kconfig = "arch/\"quoted\"/Kconfig",
        .config = "out/quoted\\path/.config",
        .arch = "arm64\\quoted",
        .allconfig = "mini\\\"quoted\\\\path",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"allnoconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--allnoconfig\",\"arch/\\\"quoted\\\"/Kconfig\"],\"env\":{\"ARCH\":\"arm64\\\\quoted\",\"KCONFIG_CONFIG\":\"out/quoted\\\\path/.config\",\"KCONFIG_ALLCONFIG\":\"mini\\\\\\\"quoted\\\\\\\\path\"}}\n",
        capture.list.items,
    );
}
