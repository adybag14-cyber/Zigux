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

test "conf bridge syncconfig preserves silent ordering and nosilentupdate output" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "arch/arm64/Kconfig",
        .config = "build/.config",
        .arch = "arm64",
        .silent = true,
        .nosilentupdate = "1",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"syncconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--syncconfig\",\"arch/arm64/Kconfig\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\"build/.config\",\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\",\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\",\"KCONFIG_NOSILENTUPDATE\":\"1\"}}\n",
        capture.list.items,
    );
}

test "conf bridge syncconfig omits empty nosilentupdate while keeping auto files" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "out/sync.config",
        .arch = "riscv64",
        .nosilentupdate = "",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"syncconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--syncconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"riscv64\",\"KCONFIG_CONFIG\":\"out/sync.config\",\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\",\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"}}\n",
        capture.list.items,
    );
}
