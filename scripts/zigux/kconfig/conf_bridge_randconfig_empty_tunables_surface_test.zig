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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "conf bridge omits empty randconfig tunables on public env surface" {
    var capture = try Capture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "rand/.config",
        .arch = "x86_64",
        .seed = null,
        .probability = null,
    });

    try expectContains(capture.list.items, "\"mode\":\"randconfig\"");
    try expectContains(capture.list.items, "\"ARCH\":\"x86_64\"");
    try expectContains(capture.list.items, "\"KCONFIG_CONFIG\":\"rand/.config\"");
    try expectNotContains(capture.list.items, "\"KCONFIG_ALLCONFIG\"");
    try expectNotContains(capture.list.items, "\"allconfig_fallbacks\"");
    try expectNotContains(capture.list.items, "\"KCONFIG_SEED\"");
    try expectNotContains(capture.list.items, "\"KCONFIG_PROBABILITY\"");
}

test "conf bridge keeps explicit empty randconfig allconfig while omitting empty tunables on public env surface" {
    var capture = try Capture.init(std.testing.allocator, 288);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "rand/.config",
        .arch = "x86_64",
        .allconfig = "",
        .seed = null,
        .probability = null,
    });

    try expectContains(capture.list.items, "\"mode\":\"randconfig\"");
    try expectContains(capture.list.items, "\"KCONFIG_ALLCONFIG\":\"\"");
    try expectContains(capture.list.items, "\"allconfig_fallbacks\":[\"allrandom.config\",\"all.config\"]");
    try expectNotContains(capture.list.items, "\"KCONFIG_SEED\"");
    try expectNotContains(capture.list.items, "\"KCONFIG_PROBABILITY\"");
}
