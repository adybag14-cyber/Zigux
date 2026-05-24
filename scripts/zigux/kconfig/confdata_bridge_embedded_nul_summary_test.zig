const std = @import("std");
const bridge = @import("confdata_bridge.zig");

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

test "confdata bridge emitted json truncates lines at embedded NUL bytes" {
    const allocator = std.testing.allocator;
    const input =
        "CONFIG_ALPHA=y\x00suffix_noise\n" ++
        "CONFIG_BETA=\"zigux\"\x00trailing_bytes\n" ++
        "# CONFIG_DEBUG is not set\x00ignored_tail\n" ++
        "CONFIG_COUNT=7\r\x00garbage\n";

    var capture = try Capture.init(allocator, 256);
    defer capture.deinit();

    try bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"string\",\"value\":\"zigux\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_COUNT\",\"kind\":\"value\",\"value\":\"7\\r\"}]}\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "suffix_noise") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "trailing_bytes") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "ignored_tail") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "garbage") == null);
}

test "confdata bridge embedded NUL truncation keeps only the last visible duplicate state" {
    const allocator = std.testing.allocator;
    const input =
        "CONFIG_SWITCH=\"kept\"\x00ignored\n" ++
        "# CONFIG_SWITCH is not set\x00ignored_tail\n" ++
        "CONFIG_SWITCH=9\n" ++
        "# CONFIG_FINAL is not set\x00noise\n";

    var summary = try bridge.parseConfig(allocator, input);
    defer bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_SWITCH", summary.entries[0].name);
    try std.testing.expectEqualStrings("value", summary.entries[0].kind.text());
    try std.testing.expectEqualStrings("9", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_FINAL", summary.entries[1].name);
    try std.testing.expectEqualStrings("unset", summary.entries[1].kind.text());
    try std.testing.expectEqualStrings("n", summary.entries[1].value);
}
