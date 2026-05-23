const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 224),
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

test "confdata bridge ignores embedded NUL suffix bytes in standalone summary output" {
    const allocator = std.testing.allocator;
    const input =
        "CONFIG_ALPHA=\"seed\"\x00ignored_suffix\n" ++
        "CONFIG_COUNT=42\x00garbage\n" ++
        "# CONFIG_DEBUG is not set\x00trailing_comment\n" ++
        "CONFIG_ALPHA=\"final\"\x00later_noise\n";

    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("string", summary.entries[0].kind.text());
    try std.testing.expectEqualStrings("final", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_COUNT", summary.entries[1].name);
    try std.testing.expectEqualStrings("value", summary.entries[1].kind.text());
    try std.testing.expectEqualStrings("42", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[2].name);
    try std.testing.expectEqualStrings("unset", summary.entries[2].kind.text());
    try std.testing.expectEqualStrings("n", summary.entries[2].value);

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"string\",\"value\":\"final\"},{\"name\":\"CONFIG_COUNT\",\"kind\":\"value\",\"value\":\"42\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}
