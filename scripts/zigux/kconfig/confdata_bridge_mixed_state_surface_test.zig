const std = @import("std");
const bridge = @import("./confdata_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 320),
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
    \\CONFIG_ALPHA="stable"
    \\# CONFIG_ALPHA is not set
    \\CONFIG_ALPHA=
    \\CONFIG_ALPHA="broken
    \\CONFIG_ALPHA=y
    \\# CONFIG_BETA is not set
    \\# CONFIG_BETA is not set
    \\CONFIG_BETA=""
    \\CONFIG_BETA="unterminated
    \\# CONFIG_GAMMA is not set
    \\CONFIG_GAMMA="broken
    \\CONFIG_DELTA=
    \\# CONFIG_DELTA is not set
    \\CONFIG_DELTA=7
    \\
;

test "confdata bridge mixed-state surface keeps only the last valid state per symbol" {
    const allocator = std.testing.allocator;
    var summary = try bridge.parseConfig(allocator, input);
    defer bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 4), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("tristate", @tagName(summary.entries[0].kind));
    try std.testing.expectEqualStrings("y", summary.entries[0].value);

    try std.testing.expectEqualStrings("CONFIG_BETA", summary.entries[1].name);
    try std.testing.expectEqualStrings("string", @tagName(summary.entries[1].kind));
    try std.testing.expectEqualStrings("", summary.entries[1].value);

    try std.testing.expectEqualStrings("CONFIG_GAMMA", summary.entries[2].name);
    try std.testing.expectEqualStrings("unset", @tagName(summary.entries[2].kind));
    try std.testing.expectEqualStrings("n", summary.entries[2].value);

    try std.testing.expectEqualStrings("CONFIG_DELTA", summary.entries[3].name);
    try std.testing.expectEqualStrings("value", @tagName(summary.entries[3].kind));
    try std.testing.expectEqualStrings("7", summary.entries[3].value);
}

test "confdata bridge mixed-state surface emits the same final visible states in json" {
    const allocator = std.testing.allocator;
    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"string\",\"value\":\"\"},{\"name\":\"CONFIG_GAMMA\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_DELTA\",\"kind\":\"value\",\"value\":\"7\"}]}\n",
        capture.list.items,
    );
}
