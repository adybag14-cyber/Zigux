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

    pub fn writeAll(self: *Capture, text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "conf bridge oldaskconfig emits canonical interactive packet" {
    var capture = try Capture.init(std.testing.allocator, 160);
    defer capture.deinit();

    try bridge.runConfBridge(&capture, .{
        .mode = .oldaskconfig,
        .kconfig = "Kconfig",
        .config = "build/.config",
        .arch = "x86_64",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"oldaskconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--oldaskconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\"build/.config\"}}\n",
        capture.list.items,
    );
}

test "conf bridge interactive discovery modes preserve silent and mode ordering" {
    var list_capture = try Capture.init(std.testing.allocator, 192);
    defer list_capture.deinit();

    try bridge.runConfBridge(&list_capture, .{
        .mode = .listnewconfig,
        .kconfig = "arch/Kconfig",
        .config = ".config.list",
        .arch = "arm64",
        .silent = true,
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"listnewconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--listnewconfig\",\"arch/Kconfig\"],\"env\":{\"ARCH\":\"arm64\",\"KCONFIG_CONFIG\":\".config.list\"}}\n",
        list_capture.list.items,
    );

    var help_capture = try Capture.init(std.testing.allocator, 192);
    defer help_capture.deinit();

    try bridge.runConfBridge(&help_capture, .{
        .mode = .helpnewconfig,
        .kconfig = "Kconfig.debug",
        .config = "out/help.config",
        .arch = "riscv64",
        .silent = true,
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"helpnewconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--helpnewconfig\",\"Kconfig.debug\"],\"env\":{\"ARCH\":\"riscv64\",\"KCONFIG_CONFIG\":\"out/help.config\"}}\n",
        help_capture.list.items,
    );
}
