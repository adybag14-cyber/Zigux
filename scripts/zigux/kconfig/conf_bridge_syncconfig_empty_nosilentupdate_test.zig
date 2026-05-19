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

test "conf bridge omits empty syncconfig nosilentupdate while keeping escaped core env fields" {
    var capture = try Capture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig\\\"sync\\\\root",
        .config = "out\\\"sync\\\\.config",
        .arch = "arm64\\\"debug\\\\stage",
        .nosilentupdate = "",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"syncconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--syncconfig\",\"Kconfig\\\\\\\"sync\\\\\\\\root\"],\"env\":{\"ARCH\":\"arm64\\\\\\\"debug\\\\\\\\stage\",\"KCONFIG_CONFIG\":\"out\\\\\\\"sync\\\\\\\\.config\",\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\",\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"}}\n",
        capture.list.items,
    );
}

test "conf bridge treats empty and absent syncconfig nosilentupdate the same" {
    var explicit_empty = try Capture.init(std.testing.allocator, 512);
    defer explicit_empty.deinit();

    try conf_bridge.runConfBridge(&explicit_empty, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig\\\"sync\\\\root",
        .config = "out\\\"sync\\\\.config",
        .arch = "arm64\\\"debug\\\\stage",
        .nosilentupdate = "",
    });

    var absent = try Capture.init(std.testing.allocator, 512);
    defer absent.deinit();

    try conf_bridge.runConfBridge(&absent, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig\\\"sync\\\\root",
        .config = "out\\\"sync\\\\.config",
        .arch = "arm64\\\"debug\\\\stage",
    });

    try std.testing.expectEqualStrings(absent.list.items, explicit_empty.list.items);
    try std.testing.expect(std.mem.indexOf(u8, explicit_empty.list.items, "\"KCONFIG_NOSILENTUPDATE\"") == null);
}
