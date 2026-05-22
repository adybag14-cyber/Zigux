const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const TestCapture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator, initial_capacity: usize) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, initial_capacity),
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

test "confdata bridge trims first-line utf8 bom before parsing config symbols" {
    const allocator = std.testing.allocator;
    const input =
        "\xef\xbb\xbfCONFIG_ALPHA=y\n" ++
        "# CONFIG_DEBUG is not set\n";

    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("y", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[1].name);
    try std.testing.expectEqualStrings("n", summary.entries[1].value);
}

test "confdata bridge truncates each line at the first nul before parsing" {
    const allocator = std.testing.allocator;
    const input =
        "CONFIG_ALPHA=y\x00ignored\n" ++
        "CONFIG_NAME=\"zigux\"\x00tail\n" ++
        "# CONFIG_DEBUG is not set\x00suffix\n";

    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("y", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_NAME", summary.entries[1].name);
    try std.testing.expectEqualStrings("zigux", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[2].name);
    try std.testing.expectEqualStrings("n", summary.entries[2].value);

    var capture = try TestCapture.init(allocator, 192);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_NAME\",\"kind\":\"string\",\"value\":\"zigux\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}
