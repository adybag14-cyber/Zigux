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

fn expectRewriteModePacket(
    mode: bridge.Mode,
    kconfig: []const u8,
    config: []const u8,
    arch: []const u8,
    expected_flag: []const u8,
) !void {
    var capture = try Capture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = mode,
        .kconfig = kconfig,
        .config = config,
        .arch = arch,
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, expected_flag) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, kconfig) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, config) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, arch) != null);
    try expectNoModeSpecificEnv(capture.list.items);
}

test "conf bridge rewrite modes emit canonical argv and env" {
    try expectRewriteModePacket(
        .yes2modconfig,
        "Kconfig",
        "rewrite/.config",
        "x86",
        "\"argv\":[\"scripts/kconfig/conf\",\"--yes2modconfig\",\"Kconfig\"]",
    );
    try expectRewriteModePacket(
        .mod2yesconfig,
        "arch/arm64/Kconfig",
        "promote/.config",
        "arm64",
        "\"argv\":[\"scripts/kconfig/conf\",\"--mod2yesconfig\",\"arch/arm64/Kconfig\"]",
    );
    try expectRewriteModePacket(
        .mod2noconfig,
        "drivers/net/Kconfig",
        "demote/.config",
        "riscv64",
        "\"argv\":[\"scripts/kconfig/conf\",\"--mod2noconfig\",\"drivers/net/Kconfig\"]",
    );
}
