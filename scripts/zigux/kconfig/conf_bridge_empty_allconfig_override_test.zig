const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
            .allocator = allocator,
        };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *@This(), bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *@This(), byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "allnoconfig explicit empty allconfig override suppresses the sentinel path" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .allnoconfig,
        .kconfig = "Kconfig",
        .config = "mini/.config",
        .arch = "arm64",
        .silent = true,
        .allconfig = "",
    });

    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--allnoconfig\",\"Kconfig\"]",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_ALLCONFIG\":\"\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_ALLCONFIG\":\"1\"",
    ) == null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_NOSILENTUPDATE\"",
    ) == null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_SEED\"",
    ) == null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_PROBABILITY\"",
    ) == null);
}

test "allyesconfig explicit empty allconfig override stays distinct from the implicit sentinel" {
    var implicit_capture = try Capture.init(std.testing.allocator);
    defer implicit_capture.deinit();

    try conf_bridge.runConfBridge(&implicit_capture, .{
        .mode = .allyesconfig,
        .kconfig = "Kconfig",
        .config = "yes/.config",
        .arch = "x86_64",
    });

    try std.testing.expect(std.mem.indexOf(
        u8,
        implicit_capture.list.items,
        "\"KCONFIG_ALLCONFIG\":\"1\"",
    ) != null);

    var explicit_capture = try Capture.init(std.testing.allocator);
    defer explicit_capture.deinit();

    try conf_bridge.runConfBridge(&explicit_capture, .{
        .mode = .allyesconfig,
        .kconfig = "Kconfig",
        .config = "yes/.config",
        .arch = "x86_64",
        .allconfig = "",
    });

    try std.testing.expect(std.mem.indexOf(
        u8,
        explicit_capture.list.items,
        "\"KCONFIG_ALLCONFIG\":\"\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        explicit_capture.list.items,
        "\"KCONFIG_ALLCONFIG\":\"1\"",
    ) == null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        explicit_capture.list.items,
        "\"KCONFIG_CONFIG\":\"yes/.config\"",
    ) != null);
}
