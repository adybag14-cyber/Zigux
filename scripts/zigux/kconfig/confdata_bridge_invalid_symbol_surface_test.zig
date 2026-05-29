const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const TestCapture = struct {
    list: std.ArrayList(u8) = .empty,

    fn deinit(self: *TestCapture) void {
        self.list.deinit(std.testing.allocator);
    }

    pub fn writeAll(self: *TestCapture, bytes: []const u8) !void {
        try self.list.appendSlice(std.testing.allocator, bytes);
    }

    pub fn writeByte(self: *TestCapture, byte: u8) !void {
        try self.list.append(std.testing.allocator, byte);
    }

    pub fn print(self: *TestCapture, comptime format: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(std.testing.allocator, format, args);
        defer std.testing.allocator.free(rendered);
        try self.writeAll(rendered);
    }
};

test "standalone confdata json surface ignores invalid CONFIG symbol names" {
    var capture = TestCapture{};
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator,
        "CONFIG_VALID=y\n" ++
            "CONFIG_BAD-DASH=m\n" ++
            "# CONFIG_BAD.DOT is not set\n" ++
            "CONFIG_BAD SPACE=7\n" ++
            "CONFIG_OK_2=\"kept\"\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[" ++
            "{\"name\":\"CONFIG_VALID\",\"kind\":\"tristate\",\"value\":\"y\"}," ++
            "{\"name\":\"CONFIG_OK_2\",\"kind\":\"string\",\"value\":\"kept\"}" ++
            "]}\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "BAD-DASH") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "BAD.DOT") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "BAD SPACE") == null);
}
