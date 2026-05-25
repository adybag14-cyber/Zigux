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

test "confdata bridge standalone malformed quoted values keep only valid visible state" {
    const allocator = std.testing.allocator;
    var summary = try bridge.parseConfig(
        allocator,
        "CONFIG_ALPHA=y\n" ++
            "CONFIG_BROKEN=\"unterminated\n" ++
            "CONFIG_BROKEN=7\n" ++
            "# CONFIG_DEBUG is not set\n" ++
            "CONFIG_GAMMA=\"still-broken\n",
    );
    defer bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("tristate", @tagName(summary.entries[0].kind));
    try std.testing.expectEqualStrings("y", summary.entries[0].value);

    try std.testing.expectEqualStrings("CONFIG_BROKEN", summary.entries[1].name);
    try std.testing.expectEqualStrings("value", @tagName(summary.entries[1].kind));
    try std.testing.expectEqualStrings("7", summary.entries[1].value);

    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[2].name);
    try std.testing.expectEqualStrings("unset", @tagName(summary.entries[2].kind));
    try std.testing.expectEqualStrings("n", summary.entries[2].value);
}

test "confdata bridge standalone malformed quoted values stay out of emitted json" {
    const allocator = std.testing.allocator;
    var capture = try Capture.init(allocator, 224);
    defer capture.deinit();

    try bridge.runConfdataBridge(
        allocator,
        "CONFIG_ALPHA=y\n" ++
            "CONFIG_BROKEN=\"unterminated\n" ++
            "CONFIG_BROKEN=7\n" ++
            "# CONFIG_DEBUG is not set\n" ++
            "CONFIG_GAMMA=\"still-broken\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_BROKEN\",\"kind\":\"value\",\"value\":\"7\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}
