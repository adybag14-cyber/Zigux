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

test "conf bridge standalone rewrite packets keep silent ahead of rewrite mode flag" {
    const cases = [_]struct {
        mode: conf_bridge.Mode,
        mode_json: []const u8,
        argv_json: []const u8,
        config: []const u8,
    }{
        .{
            .mode = .yes2modconfig,
            .mode_json = "\"mode\":\"yes2modconfig\"",
            .argv_json = "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--yes2modconfig\",\"Kconfig\"]",
            .config = "rewrite/.config",
        },
        .{
            .mode = .mod2yesconfig,
            .mode_json = "\"mode\":\"mod2yesconfig\"",
            .argv_json = "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--mod2yesconfig\",\"Kconfig\"]",
            .config = "promote/.config",
        },
        .{
            .mode = .mod2noconfig,
            .mode_json = "\"mode\":\"mod2noconfig\"",
            .argv_json = "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--mod2noconfig\",\"Kconfig\"]",
            .config = "demote/.config",
        },
    };

    inline for (cases) |case| {
        var capture = try TestCapture.init(std.testing.allocator, 224);
        defer capture.deinit();

        try conf_bridge.runConfBridge(&capture, .{
            .mode = case.mode,
            .kconfig = "Kconfig",
            .config = case.config,
            .arch = "x86",
            .silent = true,
        });

        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, case.mode_json) != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, case.argv_json) != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, case.config) != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"x86\"") != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_AUTOCONFIG\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_AUTOHEADER\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_NOSILENTUPDATE\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_SEED\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_PROBABILITY\"") == null);
    }
}

test "conf bridge standalone rewrite mode surface stays distinct" {
    const yes_to_mod = conf_bridge.Mode.parse("yes2modconfig").?;
    const mod_to_yes = conf_bridge.Mode.parse("mod2yesconfig").?;
    const mod_to_no = conf_bridge.Mode.parse("mod2noconfig").?;

    try std.testing.expectEqualStrings("yes2modconfig", yes_to_mod.text());
    try std.testing.expectEqualStrings("--yes2modconfig", yes_to_mod.flag());
    try std.testing.expectEqualStrings("mod2yesconfig", mod_to_yes.text());
    try std.testing.expectEqualStrings("--mod2yesconfig", mod_to_yes.flag());
    try std.testing.expectEqualStrings("mod2noconfig", mod_to_no.text());
    try std.testing.expectEqualStrings("--mod2noconfig", mod_to_no.flag());
    try std.testing.expect(yes_to_mod != mod_to_yes);
    try std.testing.expect(yes_to_mod != mod_to_no);
    try std.testing.expect(mod_to_yes != mod_to_no);
}
