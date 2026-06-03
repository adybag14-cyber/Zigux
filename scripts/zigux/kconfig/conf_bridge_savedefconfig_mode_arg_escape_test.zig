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

test "standalone savedefconfig mode argument json escaping stays exact" {
    var capture = try TestCapture.init(std.testing.allocator, 384);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .mode_arg = "out/save\"quote\\slash\tline\ncarriage\rbyte\x01_defconfig",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"savedefconfig\"," ++
            "\"argv\":[\"scripts/kconfig/conf\",\"--savedefconfig\"," ++
            "\"out/save\\\"quote\\\\slash\\tline\\ncarriage\\rbyte\\u0001_defconfig\"," ++
            "\"Kconfig\"],\"env\":{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\".config\"}}\n",
        capture.list.items,
    );
}
