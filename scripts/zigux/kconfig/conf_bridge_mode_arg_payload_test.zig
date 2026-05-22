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

    pub fn writeAll(self: *Capture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "conf bridge keeps defconfig mode args that contain equals on the argv payload path" {
    var capture = try Capture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "arm64",
        .mode_arg = "arch/x86/configs/debug=1_defconfig",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"defconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--defconfig\",\"arch/x86/configs/debug=1_defconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\"out/.config\"}}\n",
        capture.list.items,
    );
}

test "conf bridge keeps silent-prefixed savedefconfig mode args distinct from bridge options" {
    var capture = try Capture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "arch/arm64/Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .mode_arg = "silent=debug_defconfig",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"savedefconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--savedefconfig\",\"silent=debug_defconfig\",\"arch/arm64/Kconfig\"],\"env\":{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\".config\"}}\n",
        capture.list.items,
    );
}

test "conf bridge keeps silent-prefixed savedefconfig mode args distinct from a separate silent bridge flag" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "arch/arm64/Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .silent = true,
        .mode_arg = "silent=debug_defconfig",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"savedefconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--savedefconfig\",\"silent=debug_defconfig\",\"arch/arm64/Kconfig\"],\"env\":{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\".config\"}}\n",
        capture.list.items,
    );
}
