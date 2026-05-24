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

test "confdata bridge canonicalizes uppercase tristates during parsing" {
    const allocator = std.testing.allocator;
    var summary = try confdata_bridge.parseConfig(allocator,
        \\CONFIG_ALPHA=Y
        \\CONFIG_BETA=M # comment
        \\CONFIG_DEBUG=N trailing
        \\CONFIG_VALUE=7
        \\
    );
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 4), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 4), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqual(.tristate, summary.entries[0].kind);
    try std.testing.expectEqualStrings("y", summary.entries[0].value);

    try std.testing.expectEqualStrings("CONFIG_BETA", summary.entries[1].name);
    try std.testing.expectEqual(.tristate, summary.entries[1].kind);
    try std.testing.expectEqualStrings("m", summary.entries[1].value);

    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[2].name);
    try std.testing.expectEqual(.tristate, summary.entries[2].kind);
    try std.testing.expectEqualStrings("n", summary.entries[2].value);

    try std.testing.expectEqualStrings("CONFIG_VALUE", summary.entries[3].name);
    try std.testing.expectEqual(.value, summary.entries[3].kind);
    try std.testing.expectEqualStrings("7", summary.entries[3].value);
}

test "confdata bridge emits lowercase tristates for uppercase inputs" {
    const allocator = std.testing.allocator;
    var capture = try Capture.init(allocator, 224);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator,
        \\CONFIG_ALPHA=Y
        \\CONFIG_BETA=Msuffix
        \\CONFIG_DEBUG=N trailing
        \\
    , &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"m\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"tristate\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}
