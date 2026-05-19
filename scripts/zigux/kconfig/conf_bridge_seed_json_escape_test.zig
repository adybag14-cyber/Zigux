const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

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

test "conf bridge preserves JSON escaping for randconfig seed text" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "x86_64",
        .seed = "seed\\\"branch\\\\path",
        .probability = "10:20",
    });

    try std.testing.expect(
        std.mem.indexOf(
            u8,
            capture.list.items,
            "\"KCONFIG_SEED\":\"seed\\\\\\\"branch\\\\\\\\path\"",
        ) != null,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            capture.list.items,
            "\"KCONFIG_PROBABILITY\":\"10:20\"",
        ) != null,
    );
}

test "conf bridge omits empty randconfig seed while keeping sibling env fields" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "x86_64",
        .allconfig = "mini.config",
        .probability = "15:25",
    });

    try std.testing.expect(
        std.mem.indexOf(
            u8,
            capture.list.items,
            "\"KCONFIG_SEED\"",
        ) == null,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            capture.list.items,
            "\"KCONFIG_ALLCONFIG\":\"mini.config\"",
        ) != null,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            capture.list.items,
            "\"KCONFIG_PROBABILITY\":\"15:25\"",
        ) != null,
    );
}
