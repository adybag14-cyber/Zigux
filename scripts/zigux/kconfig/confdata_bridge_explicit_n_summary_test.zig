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

test "confdata bridge keeps explicit n assignments set after unset transitions" {
    const allocator = std.testing.allocator;
    var summary = try confdata_bridge.parseConfig(allocator,
        \\CONFIG_ALPHA=y
        \\# CONFIG_ALPHA is not set
        \\CONFIG_ALPHA=n
        \\CONFIG_BETA=m
        \\# CONFIG_BETA is not set
        \\CONFIG_BETA=n
        \\# CONFIG_DEBUG is not set
        \\
    );
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("tristate", summary.entries[0].kind.text());
    try std.testing.expectEqualStrings("n", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_BETA", summary.entries[1].name);
    try std.testing.expectEqualStrings("tristate", summary.entries[1].kind.text());
    try std.testing.expectEqualStrings("n", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[2].name);
    try std.testing.expectEqualStrings("unset", summary.entries[2].kind.text());
    try std.testing.expectEqualStrings("n", summary.entries[2].value);
}

test "confdata bridge emits explicit n assignments as tristate values in json summaries" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator,
        \\CONFIG_ALPHA=y
        \\# CONFIG_ALPHA is not set
        \\CONFIG_ALPHA=n
        \\CONFIG_BETA=m
        \\# CONFIG_BETA is not set
        \\CONFIG_BETA=n
        \\# CONFIG_DEBUG is not set
        \\
    , &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"n\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"n\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}
