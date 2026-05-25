const std = @import("std");
const conf_bridge = @import("./conf_bridge.zig");

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

test "conf bridge keeps the allconfig sentinel on only the legacy allconfig modes" {
    const cases = [_]struct {
        mode: conf_bridge.Mode,
        expect_sentinel: bool,
    }{
        .{ .mode = .allnoconfig, .expect_sentinel = true },
        .{ .mode = .allyesconfig, .expect_sentinel = true },
        .{ .mode = .allmodconfig, .expect_sentinel = false },
        .{ .mode = .alldefconfig, .expect_sentinel = true },
    };

    inline for (cases) |case| {
        var capture = try Capture.init(std.testing.allocator, 192);
        defer capture.deinit();

        try conf_bridge.runConfBridge(&capture, .{
            .mode = case.mode,
            .kconfig = "Kconfig",
            .config = "out/.config",
            .arch = "arm64",
        });

        const has_sentinel = std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") != null;
        try std.testing.expectEqual(case.expect_sentinel, has_sentinel);
    }
}

test "conf bridge keeps explicit allconfig overrides distinct from the sentinel" {
    var empty_override = try Capture.init(std.testing.allocator, 192);
    defer empty_override.deinit();

    try conf_bridge.runConfBridge(&empty_override, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "mod/.config",
        .arch = "arm",
        .allconfig = "",
    });

    try std.testing.expect(std.mem.indexOf(u8, empty_override.list.items, "\"KCONFIG_ALLCONFIG\":\"\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, empty_override.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);

    var path_override = try Capture.init(std.testing.allocator, 224);
    defer path_override.deinit();

    try conf_bridge.runConfBridge(&path_override, .{
        .mode = .alldefconfig,
        .kconfig = "Kconfig",
        .config = "def/.config",
        .arch = "x86_64",
        .allconfig = "mini-all.config",
    });

    try std.testing.expect(std.mem.indexOf(u8, path_override.list.items, "\"KCONFIG_ALLCONFIG\":\"mini-all.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, path_override.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
}
