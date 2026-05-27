const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
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

test "standalone conf bridge allyesconfig distinguishes sentinel from explicit empty override" {
    var implicit_capture = try TestCapture.init(std.testing.allocator);
    defer implicit_capture.deinit();

    try conf_bridge.runConfBridge(&implicit_capture, .{
        .mode = .allyesconfig,
        .kconfig = "Kconfig",
        .config = "yes/.config",
        .arch = "arm64",
    });

    try std.testing.expect(std.mem.indexOf(u8, implicit_capture.list.items, "\"mode\":\"allyesconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, implicit_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, implicit_capture.list.items, "\"allconfig_fallbacks\":[\"allyes.config\",\"all.config\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, implicit_capture.list.items, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, implicit_capture.list.items, "\"KCONFIG_PROBABILITY\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, implicit_capture.list.items, "\"KCONFIG_NOSILENTUPDATE\"") == null);

    var explicit_capture = try TestCapture.init(std.testing.allocator);
    defer explicit_capture.deinit();

    try conf_bridge.runConfBridge(&explicit_capture, .{
        .mode = .allyesconfig,
        .kconfig = "Kconfig",
        .config = "yes/.config",
        .arch = "arm64",
        .silent = true,
        .allconfig = "",
    });

    try std.testing.expect(std.mem.indexOf(u8, explicit_capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--allyesconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_capture.list.items, "\"allconfig_fallbacks\":[\"allyes.config\",\"all.config\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_capture.list.items, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_capture.list.items, "\"KCONFIG_PROBABILITY\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_capture.list.items, "\"KCONFIG_NOSILENTUPDATE\"") == null);
}
