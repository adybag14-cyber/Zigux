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

test "conf bridge frontend modes emit canonical argv and env" {
    var oldask_capture = try Capture.init(std.testing.allocator, 192);
    defer oldask_capture.deinit();

    try bridge.runConfBridge(&oldask_capture, .{
        .mode = .oldaskconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "x86_64",
    });

    try std.testing.expect(std.mem.indexOf(
        u8,
        oldask_capture.list.items,
        "\"argv\":[\"scripts/kconfig/conf\",\"--oldaskconfig\",\"Kconfig\"]",
    ) != null);
    try std.testing.expect(std.mem.indexOf(u8, oldask_capture.list.items, "\"mode\":\"oldaskconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, oldask_capture.list.items, "\"KCONFIG_CONFIG\":\"out/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, oldask_capture.list.items, "\"ARCH\":\"x86_64\"") != null);
    try expectNoModeSpecificEnv(oldask_capture.list.items);

    var listnew_capture = try Capture.init(std.testing.allocator, 224);
    defer listnew_capture.deinit();

    try bridge.runConfBridge(&listnew_capture, .{
        .mode = .listnewconfig,
        .kconfig = "Kconfig.debug",
        .config = "configs/list/.config",
        .arch = "riscv64",
        .silent = true,
    });

    try std.testing.expect(std.mem.indexOf(
        u8,
        listnew_capture.list.items,
        "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--listnewconfig\",\"Kconfig.debug\"]",
    ) != null);
    try std.testing.expect(std.mem.indexOf(u8, listnew_capture.list.items, "\"mode\":\"listnewconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, listnew_capture.list.items, "\"KCONFIG_CONFIG\":\"configs/list/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, listnew_capture.list.items, "\"ARCH\":\"riscv64\"") != null);
    try expectNoModeSpecificEnv(listnew_capture.list.items);

    var help_capture = try Capture.init(std.testing.allocator, 192);
    defer help_capture.deinit();

    try bridge.runConfBridge(&help_capture, .{
        .mode = .helpnewconfig,
        .kconfig = "arch/arm64/Kconfig",
        .config = ".config",
        .arch = "arm64",
    });

    try std.testing.expect(std.mem.indexOf(
        u8,
        help_capture.list.items,
        "\"argv\":[\"scripts/kconfig/conf\",\"--helpnewconfig\",\"arch/arm64/Kconfig\"]",
    ) != null);
    try std.testing.expect(std.mem.indexOf(u8, help_capture.list.items, "\"mode\":\"helpnewconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, help_capture.list.items, "\"KCONFIG_CONFIG\":\".config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, help_capture.list.items, "\"ARCH\":\"arm64\"") != null);
    try expectNoModeSpecificEnv(help_capture.list.items);
}
