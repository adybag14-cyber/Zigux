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

test "conf bridge escapes mode argument and core request fields in json output" {
    var capture = try Capture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig\\\"arm64",
        .config = "out\\\\debug\\\"/.config",
        .arch = "arm64\\\\\\\"virt",
        .mode_arg = "arch/\\\"arm64\\\"\\\\configs\\\\mini_defconfig",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"defconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--defconfig\",\"arch/\\\\\\\"arm64\\\\\\\"\\\\\\\\configs\\\\\\\\mini_defconfig\",\"Kconfig\\\\\\\"arm64\"],\"env\":{\"ARCH\":\"arm64\\\\\\\\\\\\\\\"virt\",\"KCONFIG_CONFIG\":\"out\\\\\\\\debug\\\\\\\"/.config\"}}\n",
        capture.list.items,
    );
}

test "conf bridge escapes core request fields without mode argument" {
    var capture = try Capture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .listnewconfig,
        .kconfig = "arch/Kconfig\\\"quoted",
        .config = "tmp\\\\lists\\\"/.config",
        .arch = "x86_64\\\"vm",
        .silent = true,
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"listnewconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--listnewconfig\",\"arch/Kconfig\\\\\\\"quoted\"],\"env\":{\"ARCH\":\"x86_64\\\\\\\"vm\",\"KCONFIG_CONFIG\":\"tmp\\\\\\\\lists\\\\\\\"/.config\"}}\n",
        capture.list.items,
    );
}
