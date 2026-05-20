const std = @import("std");
const confdata_bridge = @import("./confdata_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator, capacity: usize) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
            .allocator = allocator,
        };
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

test "confdata bridge keeps prior valid entries when later quoted duplicates are malformed" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_ALPHA=\"stable\"\n" ++
            "CONFIG_ALPHA=\"unterminated\n" ++
            "# CONFIG_DEBUG is not set\n" ++
            "CONFIG_DEBUG=\"broken\n" ++
            "CONFIG_BETA=y\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"string\",\"value\":\"stable\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"y\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge keeps earlier unset and string states when malformed quoted duplicates follow" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "# CONFIG_DELTA is not set\n" ++
            "CONFIG_DELTA=\"broken\n" ++
            "CONFIG_PATH=\"drivers\\\\zigux\"\n" ++
            "CONFIG_PATH=\"still-broken\n" ++
            "CONFIG_EPSILON=7\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_DELTA\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_PATH\",\"kind\":\"string\",\"value\":\"drivers\\\\zigux\"},{\"name\":\"CONFIG_EPSILON\",\"kind\":\"value\",\"value\":\"7\"}]}\n",
        capture.list.items,
    );
}
