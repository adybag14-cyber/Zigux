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

test "conf bridge emits explicit empty allnoconfig override instead of sentinel" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .allnoconfig,
        .kconfig = "Kconfig",
        .config = "none/.config",
        .arch = "arm64",
        .allconfig = "",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"allnoconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--allnoconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\"none/.config\",\"KCONFIG_ALLCONFIG\":\"\"}}\n",
        capture.list.items,
    );
}

test "conf bridge keeps explicit empty allyesconfig override distinct from implicit sentinel" {
    var explicit_empty = try Capture.init(std.testing.allocator, 320);
    defer explicit_empty.deinit();

    try bridge.runConfBridge(&explicit_empty, .{
        .mode = .allyesconfig,
        .kconfig = "Kconfig",
        .config = "yes/.config",
        .arch = "x86_64",
        .allconfig = "",
    });

    var implicit_sentinel = try Capture.init(std.testing.allocator, 320);
    defer implicit_sentinel.deinit();

    try bridge.runConfBridge(&implicit_sentinel, .{
        .mode = .allyesconfig,
        .kconfig = "Kconfig",
        .config = "yes/.config",
        .arch = "x86_64",
    });

    try std.testing.expect(!std.mem.eql(u8, explicit_empty.list.items, implicit_sentinel.list.items));
    try std.testing.expect(std.mem.indexOf(u8, explicit_empty.list.items, "\"KCONFIG_ALLCONFIG\":\"\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, implicit_sentinel.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
}
