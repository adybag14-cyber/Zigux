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

test "standalone confdata mid-line nul truncates poisoned assignment suffix" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_ALPHA=y\x00CONFIG_ALPHA=m\n" ++
            "CONFIG_BETA=7\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[" ++
            "{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"}," ++
            "{\"name\":\"CONFIG_BETA\",\"kind\":\"value\",\"value\":\"7\"}" ++
            "]}\n",
        capture.list.items,
    );
}

test "standalone confdata mid-line nul ignores hidden unset replay" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_DEBUG=m\x00# CONFIG_DEBUG is not set\n" ++
            "# CONFIG_VISIBLE is not set\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":1},\"entries\":[" ++
            "{\"name\":\"CONFIG_DEBUG\",\"kind\":\"tristate\",\"value\":\"m\"}," ++
            "{\"name\":\"CONFIG_VISIBLE\",\"kind\":\"unset\",\"value\":\"n\"}" ++
            "]}\n",
        capture.list.items,
    );
}
