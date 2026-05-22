const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const Request = conf_bridge.Request;
const runConfBridge = conf_bridge.runConfBridge;

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

fn expectAbsent(buffer: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, buffer, needle) == null);
}

test "conf bridge rewrite modes emit canonical argv and env packets" {
    const cases = [_]struct {
        mode: conf_bridge.Mode,
        mode_text: []const u8,
        mode_flag: []const u8,
        config: []const u8,
    }{
        .{
            .mode = .yes2modconfig,
            .mode_text = "yes2modconfig",
            .mode_flag = "--yes2modconfig",
            .config = "rewrite/.config",
        },
        .{
            .mode = .mod2yesconfig,
            .mode_text = "mod2yesconfig",
            .mode_flag = "--mod2yesconfig",
            .config = "promote/.config",
        },
        .{
            .mode = .mod2noconfig,
            .mode_text = "mod2noconfig",
            .mode_flag = "--mod2noconfig",
            .config = "demote/.config",
        },
    };

    inline for (cases) |case| {
        var capture = try Capture.init(std.testing.allocator, 224);
        defer capture.deinit();

        try runConfBridge(&capture, .{
            .mode = case.mode,
            .kconfig = "Kconfig",
            .config = case.config,
            .arch = "x86",
        });

        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"tool\":\"scripts/kconfig/conf\"") != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"" ++ case.mode_text ++ "\"") != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"" ++ case.mode_flag ++ "\",\"Kconfig\"]") != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"x86\"") != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"" ++ case.config ++ "\"") != null);

        try expectAbsent(capture.list.items, "\"KCONFIG_ALLCONFIG\"");
        try expectAbsent(capture.list.items, "\"KCONFIG_AUTOCONFIG\"");
        try expectAbsent(capture.list.items, "\"KCONFIG_AUTOHEADER\"");
        try expectAbsent(capture.list.items, "\"KCONFIG_NOSILENTUPDATE\"");
        try expectAbsent(capture.list.items, "\"KCONFIG_SEED\"");
        try expectAbsent(capture.list.items, "\"KCONFIG_PROBABILITY\"");
    }
}

test "conf bridge rewrite modes keep silent ahead of the mode flag" {
    var capture = try Capture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .mod2yesconfig,
        .kconfig = "Kconfig",
        .config = "promote/.config",
        .arch = "x86",
        .silent = true,
    });

    try std.testing.expect(
        std.mem.indexOf(
            u8,
            capture.list.items,
            "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--mod2yesconfig\",\"Kconfig\"]",
        ) != null,
    );
    try expectAbsent(capture.list.items, "\"KCONFIG_ALLCONFIG\"");
}
