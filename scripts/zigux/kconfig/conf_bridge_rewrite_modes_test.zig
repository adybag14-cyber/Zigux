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

    pub fn writeAll(self: *Capture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

fn expectNoModeSpecificEnv(output: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_ALLCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_AUTOHEADER\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_NOSILENTUPDATE\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_PROBABILITY\"") == null);
}

test "conf bridge rewrite modes emit canonical argv and env" {
    const cases = [_]struct {
        mode: bridge.Mode,
        mode_text: []const u8,
        mode_flag: []const u8,
        kconfig: []const u8,
        config: []const u8,
        arch: []const u8,
    }{
        .{
            .mode = .yes2modconfig,
            .mode_text = "yes2modconfig",
            .mode_flag = "--yes2modconfig",
            .kconfig = "Kconfig",
            .config = "rewrite/.config",
            .arch = "x86",
        },
        .{
            .mode = .mod2yesconfig,
            .mode_text = "mod2yesconfig",
            .mode_flag = "--mod2yesconfig",
            .kconfig = "Kconfig.promote",
            .config = "promote/.config",
            .arch = "arm64",
        },
        .{
            .mode = .mod2noconfig,
            .mode_text = "mod2noconfig",
            .mode_flag = "--mod2noconfig",
            .kconfig = "arch/riscv/Kconfig",
            .config = "demote/.config",
            .arch = "riscv64",
        },
    };

    inline for (cases) |case| {
        var capture = try Capture.init(std.testing.allocator, 224);
        defer capture.deinit();

        try bridge.runConfBridge(&capture, .{
            .mode = case.mode,
            .kconfig = case.kconfig,
            .config = case.config,
            .arch = case.arch,
        });

        const expected_argv = try std.fmt.allocPrint(
            std.testing.allocator,
            "\"argv\":[\"scripts/kconfig/conf\",\"{s}\",\"{s}\"]",
            .{ case.mode_flag, case.kconfig },
        );
        defer std.testing.allocator.free(expected_argv);
        const expected_mode = try std.fmt.allocPrint(std.testing.allocator, "\"mode\":\"{s}\"", .{case.mode_text});
        defer std.testing.allocator.free(expected_mode);
        const expected_config = try std.fmt.allocPrint(std.testing.allocator, "\"KCONFIG_CONFIG\":\"{s}\"", .{case.config});
        defer std.testing.allocator.free(expected_config);
        const expected_arch = try std.fmt.allocPrint(std.testing.allocator, "\"ARCH\":\"{s}\"", .{case.arch});
        defer std.testing.allocator.free(expected_arch);

        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, expected_argv) != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, expected_mode) != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, expected_config) != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, expected_arch) != null);
        try expectNoModeSpecificEnv(capture.list.items);
    }
}
