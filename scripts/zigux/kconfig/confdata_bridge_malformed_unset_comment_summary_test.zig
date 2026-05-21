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

test "confdata bridge emitted json ignores malformed unset comments and keeps valid neighbors" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    const input =
        \\CONFIG_ALPHA=y
        \\# CONFIG_ALPHA extra is not set
        \\# CONFIG_DEBUG is not set trailing
        \\# CONFIG_BAD-NAME is not set
    ++ "# CONFIG_TAB" ++ "\t" ++ " is not set\n" ++
        \\# CONFIG_GOOD is not set
        \\CONFIG_COUNT=7
        \\
    ;

    try confdata_bridge.runConfdataBridge(std.testing.allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_GOOD\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_COUNT\",\"kind\":\"value\",\"value\":\"7\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge malformed unset comments do not clobber later valid duplicate state" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_SWITCH=\"armed\"
        \\# CONFIG_SWITCH extra is not set
        \\# CONFIG_SWITCH is not set trailing
        \\CONFIG_SWITCH=7
        \\# CONFIG_FINAL is not set
        \\
    ;

    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_SWITCH", summary.entries[0].name);
    try std.testing.expectEqualStrings("value", summary.entries[0].kind.text());
    try std.testing.expectEqualStrings("7", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_FINAL", summary.entries[1].name);
    try std.testing.expectEqualStrings("unset", summary.entries[1].kind.text());
    try std.testing.expectEqualStrings("n", summary.entries[1].value);
}
