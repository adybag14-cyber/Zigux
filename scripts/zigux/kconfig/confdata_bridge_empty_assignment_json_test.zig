const std = @import("std");
const confdata_bridge = @import("./confdata_bridge.zig");

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

test "confdata bridge keeps explicit empty assignments distinct from quoted empty strings" {
    const input =
        \\CONFIG_EMPTY=
        \\CONFIG_QUOTED_EMPTY=""
        \\# CONFIG_DEBUG is not set
        \\
    ;

    const allocator = std.testing.allocator;
    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_EMPTY", summary.entries[0].name);
    try std.testing.expectEqual(.value, summary.entries[0].kind);
    try std.testing.expectEqualStrings("", summary.entries[0].value);

    try std.testing.expectEqualStrings("CONFIG_QUOTED_EMPTY", summary.entries[1].name);
    try std.testing.expectEqual(.string, summary.entries[1].kind);
    try std.testing.expectEqualStrings("", summary.entries[1].value);

    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[2].name);
    try std.testing.expectEqual(.unset, summary.entries[2].kind);
    try std.testing.expectEqualStrings("n", summary.entries[2].value);
}

test "confdata bridge emits distinct json for explicit empty and quoted empty assignments" {
    const input =
        \\CONFIG_EMPTY=
        \\CONFIG_QUOTED_EMPTY=""
        \\# CONFIG_DEBUG is not set
        \\
    ;

    const allocator = std.testing.allocator;
    var capture = try Capture.init(allocator, 192);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_EMPTY\",\"kind\":\"value\",\"value\":\"\"},{\"name\":\"CONFIG_QUOTED_EMPTY\",\"kind\":\"string\",\"value\":\"\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}
