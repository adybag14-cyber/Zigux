const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator, capacity: usize) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
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

fn expectContains(output: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, output, needle) != null);
}

fn expectNotContains(output: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, output, needle) == null);
}

test "standalone conf bridge escapes explicit allconfig override without fallback list" {
    var capture = try TestCapture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .allyesconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "x86_64",
        .allconfig = "configs/quoted\\\"path\\tab.config",
    });

    try expectContains(capture.list.items, "\"mode\":\"allyesconfig\"");
    try expectContains(capture.list.items, "\"--allyesconfig\"");
    try expectContains(capture.list.items, "\"KCONFIG_ALLCONFIG\":\"configs/quoted\\\\\\\"path\\\\tab.config\"");
    try expectNotContains(capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"");
    try expectNotContains(capture.list.items, "\"allconfig_fallbacks\"");
}

test "standalone conf bridge keeps escaped explicit allconfig separate from randconfig tunables" {
    var capture = try TestCapture.init(std.testing.allocator, 360);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "rand/.config",
        .arch = "arm64",
        .allconfig = "profiles/rand\ncustom.config",
        .probability = "10:20:70",
    });

    try expectContains(capture.list.items, "\"mode\":\"randconfig\"");
    try expectContains(capture.list.items, "\"KCONFIG_ALLCONFIG\":\"profiles/rand\\ncustom.config\"");
    try expectContains(capture.list.items, "\"KCONFIG_PROBABILITY\":\"10:20:70\"");
    try expectNotContains(capture.list.items, "\"allconfig_fallbacks\"");
}
