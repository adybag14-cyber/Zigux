const std = @import("std");
const bridge = @import("confdata_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
            .allocator = allocator,
        };
    }

    pub fn deinit(self: *@This()) void {
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

test "confdata bridge trims BOM on first unset comment before later state updates" {
    const allocator = std.testing.allocator;
    const input =
        "\xef\xbb\xbf# CONFIG_ALPHA is not set\n" ++
        "CONFIG_BETA=\"kept\"\n" ++
        "CONFIG_ALPHA=y\n" ++
        "# CONFIG_ALPHA is not set\n" ++
        "CONFIG_GAMMA=9\r\n";

    var summary = try bridge.parseConfig(allocator, input);
    defer bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("n", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_BETA", summary.entries[1].name);
    try std.testing.expectEqualStrings("kept", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_GAMMA", summary.entries[2].name);
    try std.testing.expectEqualStrings("9", summary.entries[2].value);

    try std.testing.expect(std.mem.indexOfScalar(u8, summary.entries[0].name, '\xef') == null);
}

test "confdata bridge emits BOM trimmed json for first unset comment" {
    const allocator = std.testing.allocator;
    const input =
        "\xef\xbb\xbf# CONFIG_ALPHA is not set\n" ++
        "CONFIG_BETA=\"kept\"\n" ++
        "CONFIG_ALPHA=y\n" ++
        "# CONFIG_ALPHA is not set\n" ++
        "CONFIG_GAMMA=9\r\n";

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"string\",\"value\":\"kept\"},{\"name\":\"CONFIG_GAMMA\",\"kind\":\"value\",\"value\":\"9\"}]}\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, '\xef') == null);
}
