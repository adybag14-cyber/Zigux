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

test "confdata bridge preserves a final unterminated carriage return value in summary and json" {
    const allocator = std.testing.allocator;
    const input = "CONFIG_DECIMAL=7\r";

    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_DECIMAL", summary.entries[0].name);
    try std.testing.expectEqualStrings("7\r", summary.entries[0].value);

    var capture = try Capture.init(allocator, 128);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_DECIMAL\",\"kind\":\"value\",\"value\":\"7\\r\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge ignores a final unterminated unset comment with carriage return while preserving neighbors" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_ALPHA=y
        \\CONFIG_LABEL=\"zigux\"
        \\# CONFIG_DEBUG is not set\r
    ;

    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("y", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_LABEL", summary.entries[1].name);
    try std.testing.expectEqualStrings("zigux", summary.entries[1].value);

    var capture = try Capture.init(allocator, 192);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_LABEL\",\"kind\":\"string\",\"value\":\"zigux\"}]}\n",
        capture.list.items,
    );
}
