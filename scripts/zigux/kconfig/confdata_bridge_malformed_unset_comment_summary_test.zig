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

test "confdata bridge ignores malformed unset comments without disturbing neighboring states" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_ALPHA=y
        \\# CONFIG_ALPHA extra is not set
        \\# CONFIG_DEBUG is not set trailing
        \\# CONFIG_TRACE is not set
        \\CONFIG_BETA="zigux"
        \\
    ;

    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("y", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_TRACE", summary.entries[1].name);
    try std.testing.expectEqualStrings("n", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_BETA", summary.entries[2].name);
    try std.testing.expectEqualStrings("zigux", summary.entries[2].value);
}

test "confdata bridge emits only valid neighbors after malformed unset comments" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_ALPHA=y
        \\# CONFIG_ALPHA extra is not set
        \\# CONFIG_DEBUG is not set trailing
        \\# CONFIG_TRACE is not set
        \\CONFIG_BETA="zigux"
        \\
    ;

    var capture = try Capture.init(allocator, 224);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_TRACE\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"string\",\"value\":\"zigux\"}]}\n",
        capture.list.items,
    );
}
