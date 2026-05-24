const std = @import("std");
const bridge = @import("confdata_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 224), .allocator = allocator };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *@This(), bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *@This(), byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }

    pub fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }
};

test "confdata bridge surface omits embedded NUL suffix bytes from emitted json" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_ALPHA=y\x00suffix_noise\n" ++
            "CONFIG_BETA=\"zigux\"\x00trailing_bytes\n" ++
            "CONFIG_COUNT=42\x00garbage\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"string\",\"value\":\"zigux\"},{\"name\":\"CONFIG_COUNT\",\"kind\":\"value\",\"value\":\"42\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge surface preserves carriage return before embedded NUL in emitted json" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_COUNT=7\r\x00suffix_noise\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_COUNT\",\"kind\":\"value\",\"value\":\"7\\r\"}]}\n",
        capture.list.items,
    );
}
