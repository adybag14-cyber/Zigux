const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator) !@This() {
        return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 224), .allocator = allocator };
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

test "confdata bridge public surface ignores malformed unset comments" {
    const allocator = std.testing.allocator;
    const input =
        \\# CONFIG_ALPHA extra is not set
        \\CONFIG_ALPHA="enabled"
        \\# CONFIG_DEBUG is not set trailing
        \\# CONFIG_DEBUG is not set
        \\CONFIG_VALUE=7
        \\
    ;

    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqual(.string, summary.entries[0].kind);
    try std.testing.expectEqualStrings("enabled", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[1].name);
    try std.testing.expectEqual(.unset, summary.entries[1].kind);
    try std.testing.expectEqualStrings("n", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_VALUE", summary.entries[2].name);
    try std.testing.expectEqual(.value, summary.entries[2].kind);
    try std.testing.expectEqualStrings("7", summary.entries[2].value);
}

test "confdata bridge public json omits malformed unset comments while preserving valid state" {
    const input =
        \\# CONFIG_ALPHA extra is not set
        \\CONFIG_ALPHA="enabled"
        \\# CONFIG_DEBUG is not set trailing
        \\# CONFIG_DEBUG is not set
        \\CONFIG_VALUE=7
        \\
    ;

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator, input, &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"string\",\"value\":\"enabled\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_VALUE\",\"kind\":\"value\",\"value\":\"7\"}]}\n",
        capture.list.items,
    );
}
