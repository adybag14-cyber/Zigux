const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    bytes: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) Capture {
        return .{
            .allocator = allocator,
            .bytes = std.ArrayList(u8).empty,
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

fn expectContains(packet: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, packet, needle) != null);
}

fn expectAbsent(packet: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, packet, needle) == null);
}

test "standalone conf bridge keeps newconfig silent packets minimal" {
    const cases = [_]struct {
        mode: conf_bridge.Mode,
        mode_marker: []const u8,
        flag: []const u8,
        config: []const u8,
        arch: []const u8,
    }{
        .{
            .mode = .listnewconfig,
            .mode_marker = "\"mode\":\"listnewconfig\"",
            .flag = "\"--listnewconfig\"",
            .config = "out/list.config",
            .arch = "x86_64",
        },
        .{
            .mode = .helpnewconfig,
            .mode_marker = "\"mode\":\"helpnewconfig\"",
            .flag = "\"--helpnewconfig\"",
            .config = "out/help.config",
            .arch = "riscv64",
        },
    };

    inline for (cases) |case| {
        var capture = Capture.init(std.testing.allocator);
        defer capture.deinit();

        try conf_bridge.runConfBridge(&capture, .{
            .mode = case.mode,
            .kconfig = "Kconfig",
            .config = case.config,
            .arch = case.arch,
            .silent = true,
        });

        const packet = capture.bytes.items;
        try expectContains(packet, case.mode_marker);
        try expectContains(packet, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",");
        try expectContains(packet, case.flag);
        try expectContains(packet, "\"Kconfig\"");
        try expectContains(packet, case.config);
        try expectContains(packet, case.arch);

        try expectAbsent(packet, "\"KCONFIG_ALLCONFIG\"");
        try expectAbsent(packet, "\"allconfig_fallbacks\"");
        try expectAbsent(packet, "\"KCONFIG_AUTOCONFIG\"");
        try expectAbsent(packet, "\"KCONFIG_AUTOHEADER\"");
        try expectAbsent(packet, "\"KCONFIG_NOSILENTUPDATE\"");
        try expectAbsent(packet, "\"KCONFIG_SEED\"");
        try expectAbsent(packet, "\"KCONFIG_PROBABILITY\"");
    }
}
