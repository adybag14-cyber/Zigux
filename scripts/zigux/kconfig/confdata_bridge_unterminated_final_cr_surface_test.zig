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

    pub fn writeAll(self: *TestCapture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "standalone confdata bridge preserves a trailing carriage return on the final unterminated value line" {
    var summary = try bridge.parseConfig(
        std.testing.allocator,
        "CONFIG_NAME=\"zigux\"\n" ++
            "# CONFIG_DEBUG is not set\n" ++
            "CONFIG_ALPHA=value\r",
    );
    defer bridge.deinitSummary(std.testing.allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_NAME", summary.entries[0].name);
    try std.testing.expectEqualStrings("string", @tagName(summary.entries[0].kind));
    try std.testing.expectEqualStrings("zigux", summary.entries[0].value);

    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[1].name);
    try std.testing.expectEqualStrings("unset", @tagName(summary.entries[1].kind));
    try std.testing.expectEqualStrings("n", summary.entries[1].value);

    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[2].name);
    try std.testing.expectEqualStrings("value", @tagName(summary.entries[2].kind));
    try std.testing.expectEqualStrings("value\r", summary.entries[2].value);
}

test "standalone confdata bridge json surface keeps the final carriage return escaped while preserving sibling entries" {
    var capture = try TestCapture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_NAME=\"zigux\"\n" ++
            "# CONFIG_DEBUG is not set\n" ++
            "CONFIG_ALPHA=value\r",
        &capture,
    );

    try expectContains(capture.list.items, "\"counts\":{\"set\":2,\"unset\":1}");
    try expectContains(capture.list.items, "\"name\":\"CONFIG_NAME\",\"kind\":\"string\",\"value\":\"zigux\"");
    try expectContains(capture.list.items, "\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"");
    try expectContains(capture.list.items, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"value\",\"value\":\"value\\r\"}");
}
