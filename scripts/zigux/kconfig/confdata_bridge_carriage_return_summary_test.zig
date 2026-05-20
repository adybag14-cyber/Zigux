const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator, capacity: usize) !Capture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
        };
    }

    fn deinit(self: *Capture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }

    pub fn print(self: *Capture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }
};

test "confdata bridge preserves final unterminated carriage returns in json summaries" {
    const allocator = std.testing.allocator;
    const input = "CONFIG_DECIMAL=7\r";

    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_DECIMAL", summary.entries[0].name);
    try std.testing.expectEqualStrings("value", summary.entries[0].kind.text());
    try std.testing.expectEqualStrings("7\r", summary.entries[0].value);

    var capture = try Capture.init(allocator, 128);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_DECIMAL\",\"kind\":\"value\",\"value\":\"7\\r\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge ignores unterminated unset comments ending in carriage return" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_ALPHA=y
        \\# CONFIG_DEBUG is not set\r
    ;

    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("tristate", summary.entries[0].kind.text());
    try std.testing.expectEqualStrings("y", summary.entries[0].value);

    var capture = try Capture.init(allocator, 128);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"}]}\n",
        capture.list.items,
    );
}
