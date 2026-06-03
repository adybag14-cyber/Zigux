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

test "standalone defconfig mode argument escapes json sensitive paths" {
    var capture = try TestCapture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig\nroot",
        .config = "out/\x01.config",
        .arch = "arm64\rtest",
        .mode_arg = "arch/arm64/configs/vendor\"debug\\path\tprofile",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"defconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--defconfig\",\"arch/arm64/configs/vendor\\\"debug\\\\path\\tprofile\",\"Kconfig\\nroot\"],\"env\":{\"ARCH\":\"arm64\\rtest\",\"KCONFIG_CONFIG\":\"out/\\u0001.config\"}}\n",
        capture.list.items,
    );
}
