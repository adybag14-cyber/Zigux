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

test "conf bridge escapes low control bytes in defconfig request fields" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .defconfig,
        .mode_arg = "arch/arm64/configs/mini\x01defconfig",
        .kconfig = "Kconfig\nmain",
        .config = "out/.config\rshadow",
        .arch = "arm64\tdebug",
    });

    try expectContains(capture.list.items, "\"--defconfig\",\"arch/arm64/configs/mini\\u0001defconfig\",\"Kconfig\\nmain\"]");
    try expectContains(capture.list.items, "\"ARCH\":\"arm64\\tdebug\"");
    try expectContains(capture.list.items, "\"KCONFIG_CONFIG\":\"out/.config\\rshadow\"");
}

test "conf bridge escapes low control bytes in allconfig override" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .allnoconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "arm64",
        .allconfig = "mini\x08all\x0cconfig",
    });

    try expectContains(capture.list.items, "\"KCONFIG_ALLCONFIG\":\"mini\\ball\\fconfig\"");
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
}

test "conf bridge escapes low control bytes in syncconfig nosilentupdate" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "riscv64",
        .nosilentupdate = "keep\x01\nquiet",
    });

    try expectContains(capture.list.items, "\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\"");
    try expectContains(capture.list.items, "\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"");
    try expectContains(capture.list.items, "\"KCONFIG_NOSILENTUPDATE\":\"keep\\u0001\\nquiet\"");
}

test "conf bridge escapes low control bytes in randconfig probability override" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "rand/.config",
        .arch = "x86_64",
        .probability = "10\x0b20",
    });

    try expectContains(capture.list.items, "\"KCONFIG_PROBABILITY\":\"10\\u000b20\"");
}
