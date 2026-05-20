const std = @import("std");
const bridge = @import("confdata_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 192),
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

test "confdata bridge malformed unset comments keep valid neighboring summary entries" {
    const allocator = std.testing.allocator;
    const input =
        "CONFIG_ALPHA=y\n" ++
        "# CONFIG_ALPHA extra is not set\n" ++
        "# CONFIG_DEBUG is not set\n" ++
        "# CONFIG_DEBUG is not set trailing\n" ++
        "# CONFIG_BAD-NAME is not set\n" ++
        "# CONFIG_TAB\x09 is not set\n" ++
        "CONFIG_STRING=\"zigux\"\n" ++
        "CONFIG_VALUE=7\n";

    var summary = try bridge.parseConfig(allocator, input);
    defer bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 4), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("tristate", @tagName(summary.entries[0].kind));
    try std.testing.expectEqualStrings("y", summary.entries[0].value);

    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[1].name);
    try std.testing.expectEqualStrings("unset", @tagName(summary.entries[1].kind));
    try std.testing.expectEqualStrings("n", summary.entries[1].value);

    try std.testing.expectEqualStrings("CONFIG_STRING", summary.entries[2].name);
    try std.testing.expectEqualStrings("string", @tagName(summary.entries[2].kind));
    try std.testing.expectEqualStrings("zigux", summary.entries[2].value);

    try std.testing.expectEqualStrings("CONFIG_VALUE", summary.entries[3].name);
    try std.testing.expectEqualStrings("value", @tagName(summary.entries[3].kind));
    try std.testing.expectEqualStrings("7", summary.entries[3].value);
}

test "confdata bridge malformed unset comments stay absent from emitted json" {
    const allocator = std.testing.allocator;
    const input =
        "CONFIG_ALPHA=y\n" ++
        "# CONFIG_ALPHA extra is not set\n" ++
        "# CONFIG_DEBUG is not set\n" ++
        "# CONFIG_DEBUG is not set trailing\n" ++
        "# CONFIG_BAD-NAME is not set\n" ++
        "# CONFIG_TAB\x09 is not set\n" ++
        "CONFIG_STRING=\"zigux\"\n" ++
        "CONFIG_VALUE=7\n";

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try bridge.runConfdataBridge(allocator, input, &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_STRING\",\"kind\":\"string\",\"value\":\"zigux\"},{\"name\":\"CONFIG_VALUE\",\"kind\":\"value\",\"value\":\"7\"}]}\n",
        capture.list.items,
    );
}
