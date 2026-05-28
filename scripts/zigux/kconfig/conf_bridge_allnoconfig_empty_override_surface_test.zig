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

test "standalone conf bridge allnoconfig empty override stays distinct from sentinel" {
    var sentinel_capture = try Capture.init(std.testing.allocator, 224);
    defer sentinel_capture.deinit();

    try bridge.runConfBridge(&sentinel_capture, .{
        .mode = .allnoconfig,
        .kconfig = "Kconfig",
        .config = "none/.config",
        .arch = "arm64",
    });

    try std.testing.expect(std.mem.indexOf(u8, sentinel_capture.list.items, "\"mode\":\"allnoconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, sentinel_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, sentinel_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, sentinel_capture.list.items, "\"allconfig_fallbacks\":[\"allno.config\",\"all.config\"]") != null);

    var explicit_empty_capture = try Capture.init(std.testing.allocator, 224);
    defer explicit_empty_capture.deinit();

    try bridge.runConfBridge(&explicit_empty_capture, .{
        .mode = .allnoconfig,
        .kconfig = "Kconfig",
        .config = "none/.config",
        .arch = "arm64",
        .allconfig = "",
    });

    try std.testing.expect(std.mem.indexOf(u8, explicit_empty_capture.list.items, "\"mode\":\"allnoconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_empty_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_empty_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_empty_capture.list.items, "\"allconfig_fallbacks\":[\"allno.config\",\"all.config\"]") != null);

    var path_capture = try Capture.init(std.testing.allocator, 192);
    defer path_capture.deinit();

    try bridge.runConfBridge(&path_capture, .{
        .mode = .allnoconfig,
        .kconfig = "Kconfig",
        .config = "none/.config",
        .arch = "arm64",
        .allconfig = "mini-all.config",
    });

    try std.testing.expect(std.mem.indexOf(u8, path_capture.list.items, "\"mode\":\"allnoconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, path_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"mini-all.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, path_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, path_capture.list.items, "\"allconfig_fallbacks\"") == null);
}
