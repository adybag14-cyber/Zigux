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

test "confdata bridge preserves final unterminated value-line carriage return in public summary" {
    const allocator = std.testing.allocator;
    const input = "CONFIG_COUNT=7\r";

    var summary = try bridge.parseConfig(allocator, input);
    defer bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_COUNT", summary.entries[0].name);
    try std.testing.expectEqualStrings("value", summary.entries[0].kind.text());
    try std.testing.expectEqualStrings("7\r", summary.entries[0].value);

    var capture = try Capture.init(allocator, 160);
    defer capture.deinit();

    try bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_COUNT\",\"kind\":\"value\",\"value\":\"7\\r\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge ignores trailing-carriage-return unset comments in public summary output" {
    const allocator = std.testing.allocator;
    const input = "CONFIG_ALPHA=y\n" ++
        "CONFIG_NAME=\"zigux\"\n" ++
        "CONFIG_COUNT=7\n" ++
        "# CONFIG_DEBUG is not set\r";

    var summary = try bridge.parseConfig(allocator, input);
    defer bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("tristate", summary.entries[0].kind.text());
    try std.testing.expectEqualStrings("y", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_NAME", summary.entries[1].name);
    try std.testing.expectEqualStrings("string", summary.entries[1].kind.text());
    try std.testing.expectEqualStrings("zigux", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_COUNT", summary.entries[2].name);
    try std.testing.expectEqualStrings("value", summary.entries[2].kind.text());
    try std.testing.expectEqualStrings("7", summary.entries[2].value);

    var capture = try Capture.init(allocator, 224);
    defer capture.deinit();

    try bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_NAME\",\"kind\":\"string\",\"value\":\"zigux\"},{\"name\":\"CONFIG_COUNT\",\"kind\":\"value\",\"value\":\"7\"}]}\n",
        capture.list.items,
    );
}
