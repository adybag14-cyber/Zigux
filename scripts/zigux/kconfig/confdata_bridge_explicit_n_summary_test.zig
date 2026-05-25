const std = @import("std");
const bridge = @import("confdata_bridge.zig");

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

test "confdata bridge keeps explicit n distinct from unset markers in parsed summary" {
    const allocator = std.testing.allocator;
    const input =
        \\# CONFIG_ALPHA is not set
        \\CONFIG_ALPHA=n
        \\CONFIG_BETA=y
        \\# CONFIG_BETA is not set
        \\CONFIG_GAMMA="still-set"
        \\
    ;

    var summary = try bridge.parseConfig(allocator, input);
    defer bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("tristate", @tagName(summary.entries[0].kind));
    try std.testing.expectEqualStrings("n", summary.entries[0].value);

    try std.testing.expectEqualStrings("CONFIG_BETA", summary.entries[1].name);
    try std.testing.expectEqualStrings("unset", @tagName(summary.entries[1].kind));
    try std.testing.expectEqualStrings("n", summary.entries[1].value);

    try std.testing.expectEqualStrings("CONFIG_GAMMA", summary.entries[2].name);
    try std.testing.expectEqualStrings("string", @tagName(summary.entries[2].kind));
    try std.testing.expectEqualStrings("still-set", summary.entries[2].value);
}

test "confdata bridge emits explicit n distinctly in json summary output" {
    const allocator = std.testing.allocator;
    const input =
        \\# CONFIG_ALPHA is not set
        \\CONFIG_ALPHA=n
        \\CONFIG_BETA=y
        \\# CONFIG_BETA is not set
        \\CONFIG_GAMMA="still-set"
        \\
    ;

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"n\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_GAMMA\",\"kind\":\"string\",\"value\":\"still-set\"}]}\n",
        capture.list.items,
    );
}
