const std = @import("std");
const bridge = @import("confdata_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator, capacity: usize) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
        };
    }

    fn deinit(self: *TestCapture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *TestCapture, text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
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

test "confdata bridge ignores malformed unset comments in emitted json summaries" {
    var capture = try TestCapture.init(std.testing.allocator, 192);
    defer capture.deinit();

    try bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_ALPHA=y\n" ++
            "# CONFIG_ALPHA extra is not set\n" ++
            "# CONFIG_DEBUG is not set trailing\n" ++
            "# CONFIG_BAD-NAME is not set\n" ++
            "# CONFIG_TAB\t is not set\n" ++
            "CONFIG_BETA=\"zigux\"\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"string\",\"value\":\"zigux\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge keeps valid unset entries beside malformed unset comments" {
    var capture = try TestCapture.init(std.testing.allocator, 192);
    defer capture.deinit();

    try bridge.runConfdataBridge(
        std.testing.allocator,
        "# CONFIG_DEBUG is not set\n" ++
            "# CONFIG_DEBUG is not set trailing\n" ++
            "# CONFIG_BAD-NAME is not set\n" ++
            "CONFIG_ALPHA=m\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"m\"}]}\n",
        capture.list.items,
    );
}
