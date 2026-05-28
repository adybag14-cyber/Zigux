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

test "standalone conf bridge allyesconfig explicit override stays distinct from sentinel" {
    var sentinel_capture = try Capture.init(std.testing.allocator, 224);
    defer sentinel_capture.deinit();

    try bridge.runConfBridge(&sentinel_capture, .{
        .mode = .allyesconfig,
        .kconfig = "Kconfig",
        .config = "yes/.config",
        .arch = "arm64",
    });

    try std.testing.expect(std.mem.indexOf(u8, sentinel_capture.list.items, "\"mode\":\"allyesconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, sentinel_capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--allyesconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, sentinel_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, sentinel_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"board-yes.config\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, sentinel_capture.list.items, "\"allconfig_fallbacks\":[\"allyes.config\",\"all.config\"]") != null);

    var override_capture = try Capture.init(std.testing.allocator, 224);
    defer override_capture.deinit();

    try bridge.runConfBridge(&override_capture, .{
        .mode = .allyesconfig,
        .kconfig = "Kconfig",
        .config = "yes/.config",
        .arch = "arm64",
        .silent = true,
        .allconfig = "board-yes.config",
    });

    try std.testing.expect(std.mem.indexOf(u8, override_capture.list.items, "\"mode\":\"allyesconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, override_capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--allyesconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, override_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"board-yes.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, override_capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, override_capture.list.items, "\"allconfig_fallbacks\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, override_capture.list.items, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, override_capture.list.items, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, override_capture.list.items, "\"KCONFIG_PROBABILITY\"") == null);
}
