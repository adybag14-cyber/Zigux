const std = @import("std");
const bridge = @import("./confdata_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 192),
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

const input =
    "CONFIG_COUNT=7\r\x00suffix_noise\n" ++
    "CONFIG_ALPHA=y\n";

test "confdata bridge preserves carriage return before an embedded NUL in parsed summary state" {
    const allocator = std.testing.allocator;
    var summary = try bridge.parseConfig(allocator, input);
    defer bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_COUNT", summary.entries[0].name);
    try std.testing.expectEqualStrings("value", @tagName(summary.entries[0].kind));
    try std.testing.expectEqualStrings("7\r", summary.entries[0].value);

    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[1].name);
    try std.testing.expectEqualStrings("tristate", @tagName(summary.entries[1].kind));
    try std.testing.expectEqualStrings("y", summary.entries[1].value);
}

test "confdata bridge preserves carriage return before an embedded NUL in emitted json" {
    const allocator = std.testing.allocator;
    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_COUNT\",\"kind\":\"value\",\"value\":\"7\\r\"},{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"}]}\n",
        capture.list.items,
    );
}
