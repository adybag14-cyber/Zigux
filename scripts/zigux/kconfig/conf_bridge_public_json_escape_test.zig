const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    bytes: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .allocator = allocator,
            .bytes = try std.ArrayList(u8).initCapacity(allocator, 512),
        };
    }

    fn deinit(self: *Capture) void {
        self.bytes.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, text: []const u8) !void {
        try self.bytes.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.bytes.append(self.allocator, byte);
    }
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "conf bridge public surface json-escapes request-controlled strings" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "arch/zigux/Kconfig\nnext",
        .config = "out/quote\"slash\\.config",
        .arch = "rv\t64",
        .allconfig = "allrandom\x01.config",
        .probability = "10\n20",
    });

    const output = capture.bytes.items;
    try expectContains(output, "\"mode\":\"randconfig\"");
    try expectContains(output, "\"arch/zigux/Kconfig\\nnext\"");
    try expectContains(output, "\"KCONFIG_CONFIG\":\"out/quote\\\"slash\\\\.config\"");
    try expectContains(output, "\"ARCH\":\"rv\\t64\"");
    try expectContains(output, "\"KCONFIG_ALLCONFIG\":\"allrandom\\u0001.config\"");
    try expectContains(output, "\"KCONFIG_PROBABILITY\":\"10\\n20\"");
    try expectAbsent(output, "arch/zigux/Kconfig\nnext");
    try expectAbsent(output, "rv\t64");
    try expectAbsent(output, "allrandom\x01.config");
}

test "conf bridge escapes defconfig mode argument before kconfig path" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .mode_arg = "arch/x86/configs/debug\"\\defconfig",
    });

    const output = capture.bytes.items;
    try expectContains(output, "\"argv\":[\"scripts/kconfig/conf\",\"--defconfig\",\"arch/x86/configs/debug\\\"\\\\defconfig\",\"Kconfig\"]");
    try expectAbsent(output, "debug\"\\defconfig");
}
