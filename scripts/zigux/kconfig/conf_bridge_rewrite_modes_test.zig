const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator, capacity: usize) !@This() {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
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

test "conf bridge rewrite modes emit canonical argv and env" {
    const cases = [_]struct {
        mode: conf_bridge.Mode,
        mode_text: []const u8,
        mode_flag: []const u8,
        config: []const u8,
        arch: []const u8,
    }{
        .{
            .mode = .yes2modconfig,
            .mode_text = "yes2modconfig",
            .mode_flag = "--yes2modconfig",
            .config = "rewrite/yes2mod.config",
            .arch = "x86",
        },
        .{
            .mode = .mod2yesconfig,
            .mode_text = "mod2yesconfig",
            .mode_flag = "--mod2yesconfig",
            .config = "rewrite/mod2yes.config",
            .arch = "arm64",
        },
        .{
            .mode = .mod2noconfig,
            .mode_text = "mod2noconfig",
            .mode_flag = "--mod2noconfig",
            .config = "rewrite/mod2no.config",
            .arch = "riscv64",
        },
    };

    inline for (cases) |case| {
        var capture = try Capture.init(std.testing.allocator, 192);
        defer capture.deinit();

        try conf_bridge.runConfBridge(&capture, .{
            .mode = case.mode,
            .kconfig = "Kconfig",
            .config = case.config,
            .arch = case.arch,
        });

        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"tool\":\"scripts/kconfig/conf\"") != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, case.mode_text) != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, case.mode_flag) != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, case.config) != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, case.arch) != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_AUTOCONFIG\"") == null);
    }
}

test "conf bridge rewrite modes keep silent ahead of the mode flag" {
    var capture = try Capture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .mod2noconfig,
        .kconfig = "arch/zigux/Kconfig",
        .config = "rewrite/.config",
        .arch = "x86_64",
        .silent = true,
    });

    try std.testing.expect(
        std.mem.indexOf(
            u8,
            capture.list.items,
            "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--mod2noconfig\",\"arch/zigux/Kconfig\"]",
        ) != null,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"mod2noconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"rewrite/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"x86_64\"") != null);
}
