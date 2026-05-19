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

test "confdata bridge trims a first-line BOM from unset markers before duplicate updates" {
    const allocator = std.testing.allocator;
    var summary = try confdata_bridge.parseConfig(
        allocator,
        "\xef\xbb\xbf# CONFIG_ALPHA is not set\r\n" ++
            "CONFIG_ALPHA=\"restored\"\r\n" ++
            "# CONFIG_DEBUG is not set\n",
    );
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("restored", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[1].name);
    try std.testing.expectEqualStrings("n", summary.entries[1].value);
}

test "confdata bridge emits BOM-prefixed unset markers as normal duplicate summaries" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "\xef\xbb\xbf# CONFIG_ALPHA is not set\r\n" ++
            "CONFIG_ALPHA=\"restored\"\r\n" ++
            "# CONFIG_DEBUG is not set\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"string\",\"value\":\"restored\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}
