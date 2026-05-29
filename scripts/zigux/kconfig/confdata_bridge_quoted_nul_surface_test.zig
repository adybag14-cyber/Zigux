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

test "standalone confdata quoted nul drops unterminated visible string" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_TITLE=\"zig\x00ux\"\n" ++
            "CONFIG_AFTER=y\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":0},\"entries\":[" ++
            "{\"name\":\"CONFIG_AFTER\",\"kind\":\"tristate\",\"value\":\"y\"}" ++
            "]}\n",
        capture.list.items,
    );
}

test "standalone confdata quoted nul keeps closed string before hidden suffix" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_TITLE=\"zigux\"\x00CONFIG_TITLE=\"poison\"\n" ++
            "CONFIG_AFTER=m\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[" ++
            "{\"name\":\"CONFIG_TITLE\",\"kind\":\"string\",\"value\":\"zigux\"}," ++
            "{\"name\":\"CONFIG_AFTER\",\"kind\":\"tristate\",\"value\":\"m\"}" ++
            "]}\n",
        capture.list.items,
    );
}
