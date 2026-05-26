const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

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

test "confdata bridge utf8 bom surface trims only the first config line" {
    const allocator = std.testing.allocator;
    var summary = try confdata_bridge.parseConfig(
        allocator,
        "\xef\xbb\xbfCONFIG_ALPHA=y\n" ++
            "CONFIG_NAME=\"zigux\"\n" ++
            "# CONFIG_DEBUG is not set\n",
    );
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("tristate", summary.entries[0].kind.text());
    try std.testing.expectEqualStrings("y", summary.entries[0].value);

    try std.testing.expectEqualStrings("CONFIG_NAME", summary.entries[1].name);
    try std.testing.expectEqualStrings("string", summary.entries[1].kind.text());
    try std.testing.expectEqualStrings("zigux", summary.entries[1].value);

    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[2].name);
    try std.testing.expectEqualStrings("unset", summary.entries[2].kind.text());
    try std.testing.expectEqualStrings("n", summary.entries[2].value);
}

test "confdata bridge utf8 bom surface emits bom-free json summary" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "\xef\xbb\xbfCONFIG_ALPHA=y\n" ++
            "CONFIG_NAME=\"zigux\"\n" ++
            "# CONFIG_DEBUG is not set\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_NAME\",\"kind\":\"string\",\"value\":\"zigux\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\xef\xbb\xbf") == null);
}
