const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

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

test "confdata bridge preserves explicit empty states after malformed quoted duplicates" {
    const allocator = std.testing.allocator;
    var capture = try Capture.init(allocator, 256);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        allocator,
        \\CONFIG_EMPTY=
        \\CONFIG_QUOTED=""
        \\CONFIG_EMPTY="unterminated
        \\CONFIG_QUOTED="broken
        \\CONFIG_FINAL=y
        \\
    ,
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_EMPTY\",\"kind\":\"value\",\"value\":\"\"},{\"name\":\"CONFIG_QUOTED\",\"kind\":\"string\",\"value\":\"\"},{\"name\":\"CONFIG_FINAL\",\"kind\":\"tristate\",\"value\":\"y\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge keeps explicit empty assignment after unset and malformed quoted replay" {
    const allocator = std.testing.allocator;
    var capture = try Capture.init(allocator, 224);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        allocator,
        \\# CONFIG_SWITCH is not set
        \\CONFIG_SWITCH=
        \\CONFIG_FLAG=m
        \\CONFIG_SWITCH="broken
        \\
    ,
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_SWITCH\",\"kind\":\"value\",\"value\":\"\"},{\"name\":\"CONFIG_FLAG\",\"kind\":\"tristate\",\"value\":\"m\"}]}\n",
        capture.list.items,
    );
}
