const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 192),
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

test "confdata bridge ignores malformed unset comments with extra tokens in summary output" {
    const allocator = std.testing.allocator;
    var summary = try confdata_bridge.parseConfig(allocator,
        \\CONFIG_ALPHA=y
        \\# CONFIG_ALPHA extra is not set
        \\# CONFIG_DEBUG is not set trailing
        \\# CONFIG_BAD-NAME is not set
        \\# CONFIG_TAB\t is not set
        \\CONFIG_VALUE=7
        \\
    );
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("tristate", @tagName(summary.entries[0].kind));
    try std.testing.expectEqualStrings("y", summary.entries[0].value);

    try std.testing.expectEqualStrings("CONFIG_VALUE", summary.entries[1].name);
    try std.testing.expectEqualStrings("value", @tagName(summary.entries[1].kind));
    try std.testing.expectEqualStrings("7", summary.entries[1].value);
}

test "confdata bridge emits no unset entries for malformed unset comments with extra tokens" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_ALPHA=y
        \\# CONFIG_ALPHA extra is not set
        \\# CONFIG_DEBUG is not set trailing
        \\# CONFIG_BAD-NAME is not set
        \\# CONFIG_TAB\t is not set
        \\CONFIG_VALUE=7
        \\
    ;

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_VALUE\",\"kind\":\"value\",\"value\":\"7\"}]}\n",
        capture.list.items,
    );
}
