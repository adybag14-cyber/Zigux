const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

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

    pub fn print(self: *TestCapture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }
};

test "confdata bridge trims only the first line UTF-8 BOM on public JSON surface" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "\xef\xbb\xbfCONFIG_FIRST=y\n" ++
            "\xef\xbb\xbfCONFIG_LATE=m\n" ++
            "CONFIG_AFTER=\"kept\"\n" ++
            "# CONFIG_DEBUG is not set\n",
        &capture,
    );

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"unset\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_FIRST\",\"kind\":\"tristate\",\"value\":\"y\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_AFTER\",\"kind\":\"string\",\"value\":\"kept\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_LATE") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\ufeff") == null);
}
