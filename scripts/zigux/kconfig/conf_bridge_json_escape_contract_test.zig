const std = @import("std");
const bridge = @import("conf_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator, capacity: usize) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
            .allocator = allocator,
        };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *@This(), text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *@This(), byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "conf bridge escapes syncconfig request fields in end-to-end json output" {
    var capture = try Capture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kcon\"fig\\path\n\t\x01",
        .config = ".con\\fig\"\x01",
        .arch = "arm\"64\t",
        .silent = true,
        .nosilentupdate = "keep\nquiet\t\x01",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"syncconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--syncconfig\",\"Kcon\\\"fig\\\\path\\n\\t\\u0001\"],\"env\":{\"ARCH\":\"arm\\\"64\\t\",\"KCONFIG_CONFIG\":\".con\\\\fig\\\"\\u0001\",\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\",\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\",\"KCONFIG_NOSILENTUPDATE\":\"keep\\nquiet\\t\\u0001\"}}\n",
        capture.list.items,
    );
}

test "conf bridge escapes randconfig override fields including seed without adding syncconfig env" {
    var capture = try Capture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "rand/.config",
        .arch = "x86_64",
        .silent = true,
        .allconfig = "all\"rand\\path",
        .seed = "seed\"mix\\\n\t\x01",
        .probability = "15:25\t\x01",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"randconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--randconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\"rand/.config\",\"KCONFIG_ALLCONFIG\":\"all\\\"rand\\\\path\",\"KCONFIG_SEED\":\"seed\\\"mix\\\\\\n\\t\\u0001\",\"KCONFIG_PROBABILITY\":\"15:25\\t\\u0001\"}}\n",
        capture.list.items,
    );

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_AUTOHEADER\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_NOSILENTUPDATE\"") == null);
}

test "conf bridge escapes defconfig mode argument in end-to-end json output" {
    var capture = try Capture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kcon\"fig",
        .config = "out/.config",
        .arch = "arm64",
        .mode_arg = "arch/arm64/configs/def\"\\\n\t\x01",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"defconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--defconfig\",\"arch/arm64/configs/def\\\"\\\\\\n\\t\\u0001\",\"Kcon\\\"fig\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\"out/.config\"}}\n",
        capture.list.items,
    );
}
