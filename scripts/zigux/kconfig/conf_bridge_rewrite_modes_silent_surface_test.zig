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

test "standalone conf bridge rewrite modes keep silent ahead of mode and omit unrelated env" {
    const rewrite_cases = [_]struct {
        mode: conf_bridge.Mode,
        mode_json: []const u8,
        flag: []const u8,
        config: []const u8,
    }{
        .{ .mode = .yes2modconfig, .mode_json = "\"mode\":\"yes2modconfig\"", .flag = "\"--yes2modconfig\"", .config = "rewrite/.config" },
        .{ .mode = .mod2yesconfig, .mode_json = "\"mode\":\"mod2yesconfig\"", .flag = "\"--mod2yesconfig\"", .config = "promote/.config" },
        .{ .mode = .mod2noconfig, .mode_json = "\"mode\":\"mod2noconfig\"", .flag = "\"--mod2noconfig\"", .config = "demote/.config" },
    };

    inline for (rewrite_cases) |case| {
        var capture = try TestCapture.init(std.testing.allocator, 256);
        defer capture.deinit();

        try conf_bridge.runConfBridge(&capture, .{
            .mode = case.mode,
            .kconfig = "Kconfig",
            .config = case.config,
            .arch = "x86",
            .silent = true,
        });

        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, case.mode_json) != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",") != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, case.flag) != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, case.config) != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"x86\"") != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"allconfig_fallbacks\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_AUTOCONFIG\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_AUTOHEADER\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_NOSILENTUPDATE\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_SEED\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_PROBABILITY\"") == null);
    }
}

test "standalone conf bridge rewrite mode surface stays distinct under silent output" {
    const yes2mod = conf_bridge.Mode.parse("yes2modconfig").?;
    const mod2yes = conf_bridge.Mode.parse("mod2yesconfig").?;
    const mod2no = conf_bridge.Mode.parse("mod2noconfig").?;

    try std.testing.expectEqualStrings("yes2modconfig", yes2mod.text());
    try std.testing.expectEqualStrings("--yes2modconfig", yes2mod.flag());
    try std.testing.expectEqualStrings("mod2yesconfig", mod2yes.text());
    try std.testing.expectEqualStrings("--mod2yesconfig", mod2yes.flag());
    try std.testing.expectEqualStrings("mod2noconfig", mod2no.text());
    try std.testing.expectEqualStrings("--mod2noconfig", mod2no.flag());
    try std.testing.expect(yes2mod != mod2yes);
    try std.testing.expect(mod2yes != mod2no);
    try std.testing.expect(yes2mod != mod2no);
}
