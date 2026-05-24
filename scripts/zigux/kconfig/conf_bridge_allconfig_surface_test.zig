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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "conf bridge emits implicit KCONFIG_ALLCONFIG only for sentinel modes" {
    const sentinel_cases = [_]struct {
        mode: bridge.Mode,
        config: []const u8,
        arch: []const u8,
    }{
        .{ .mode = .allnoconfig, .config = "none/.config", .arch = "arm64" },
        .{ .mode = .allyesconfig, .config = "yes/.config", .arch = "arm64" },
        .{ .mode = .alldefconfig, .config = "build/.config", .arch = "arm64" },
    };

    inline for (sentinel_cases) |case| {
        var capture = try Capture.init(std.testing.allocator, 192);
        defer capture.deinit();

        try bridge.runConfBridge(&capture, .{
            .mode = case.mode,
            .kconfig = "Kconfig",
            .config = case.config,
            .arch = case.arch,
        });

        try expectContains(capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"");
    }
}

test "conf bridge omits KCONFIG_ALLCONFIG for optional modes without override" {
    var allmodconfig_capture = try Capture.init(std.testing.allocator, 192);
    defer allmodconfig_capture.deinit();

    try bridge.runConfBridge(&allmodconfig_capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "mod/.config",
        .arch = "arm",
    });

    try expectNotContains(allmodconfig_capture.list.items, "\"KCONFIG_ALLCONFIG\"");

    var randconfig_capture = try Capture.init(std.testing.allocator, 256);
    defer randconfig_capture.deinit();

    try bridge.runConfBridge(&randconfig_capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "rand/.config",
        .arch = "x86_64",
        .seed = "0xC0FFEE",
        .probability = "15:25",
    });

    try expectContains(randconfig_capture.list.items, "\"KCONFIG_SEED\":\"0xC0FFEE\"");
    try expectContains(randconfig_capture.list.items, "\"KCONFIG_PROBABILITY\":\"15:25\"");
    try expectNotContains(randconfig_capture.list.items, "\"KCONFIG_ALLCONFIG\"");
}

test "conf bridge explicit KCONFIG_ALLCONFIG override suppresses sentinel" {
    const override_cases = [_]struct {
        mode: bridge.Mode,
        config: []const u8,
        arch: []const u8,
        allconfig: []const u8,
        expected_fragment: []const u8,
    }{
        .{
            .mode = .allnoconfig,
            .config = "none/.config",
            .arch = "arm64",
            .allconfig = "mini-all.config",
            .expected_fragment = "\"KCONFIG_ALLCONFIG\":\"mini-all.config\"",
        },
        .{
            .mode = .allyesconfig,
            .config = "yes/.config",
            .arch = "arm64",
            .allconfig = "",
            .expected_fragment = "\"KCONFIG_ALLCONFIG\":\"\"",
        },
        .{
            .mode = .alldefconfig,
            .config = "build/.config",
            .arch = "arm64",
            .allconfig = "mini-all.config",
            .expected_fragment = "\"KCONFIG_ALLCONFIG\":\"mini-all.config\"",
        },
        .{
            .mode = .allmodconfig,
            .config = "mod/.config",
            .arch = "arm",
            .allconfig = "",
            .expected_fragment = "\"KCONFIG_ALLCONFIG\":\"\"",
        },
        .{
            .mode = .randconfig,
            .config = "rand/.config",
            .arch = "x86_64",
            .allconfig = "allrandom.config",
            .expected_fragment = "\"KCONFIG_ALLCONFIG\":\"allrandom.config\"",
        },
    };

    inline for (override_cases) |case| {
        var capture = try Capture.init(std.testing.allocator, 256);
        defer capture.deinit();

        try bridge.runConfBridge(&capture, .{
            .mode = case.mode,
            .kconfig = "Kconfig",
            .config = case.config,
            .arch = case.arch,
            .allconfig = case.allconfig,
        });

        try expectContains(capture.list.items, case.expected_fragment);
        try expectNotContains(capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"");
    }
}
