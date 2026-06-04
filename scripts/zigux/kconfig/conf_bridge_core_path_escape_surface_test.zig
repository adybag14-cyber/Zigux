const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
        };
    }

    fn deinit(self: *TestCapture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *TestCapture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *TestCapture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNoRawControlBytesExceptFinalNewline(output: []const u8) !void {
    for (output, 0..) |byte, index| {
        if (byte < 0x20) {
            try std.testing.expect(byte == '\n' and index + 1 == output.len);
        }
    }
}

test "conf bridge escapes core path fields in emitted json" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "Kconfig\"dir\\child\nmenu\troot\r\x01",
        .config = "out/.config\"debug\\next\ncfg\tleaf\r\x02",
        .arch = "x86_64\"lab\\arch\nvariant\tcr\r\x03",
        .mode_arg = "arch/x86/configs/debug\"path\\save\nleaf\tcr\r\x04",
        .silent = true,
    });

    try expectContains(capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--savedefconfig\"");
    try expectContains(capture.list.items, "arch/x86/configs/debug\\\"path\\\\save\\nleaf\\tcr\\r\\u0004");
    try expectContains(capture.list.items, "Kconfig\\\"dir\\\\child\\nmenu\\troot\\r\\u0001");
    try expectContains(capture.list.items, "\"KCONFIG_CONFIG\":\"out/.config\\\"debug\\\\next\\ncfg\\tleaf\\r\\u0002\"");
    try expectContains(capture.list.items, "\"ARCH\":\"x86_64\\\"lab\\\\arch\\nvariant\\tcr\\r\\u0003\"");
    try expectNoRawControlBytesExceptFinalNewline(capture.list.items);
}
