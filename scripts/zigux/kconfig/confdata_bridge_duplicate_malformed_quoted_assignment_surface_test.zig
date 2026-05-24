const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const malformed_duplicate_input =
    \\CONFIG_ALPHA="stable"
    \\CONFIG_ALPHA="unterminated
    \\# CONFIG_DEBUG is not set
    \\CONFIG_DEBUG="broken
    \\CONFIG_GAMMA="still-broken
    \\CONFIG_SUFFIX="zigux"tail
    \\CONFIG_BETA=y
    \\
;

const expected_json =
    "{\"counts\":{\"set\":3,\"unset\":1},\"entries\":[" ++
    "{\"name\":\"CONFIG_ALPHA\",\"kind\":\"string\",\"value\":\"stable\"}," ++
    "{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"}," ++
    "{\"name\":\"CONFIG_SUFFIX\",\"kind\":\"string\",\"value\":\"zigux\"}," ++
    "{\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"y\"}]}\n";

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 256), .allocator = allocator };
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

test "confdata bridge standalone malformed duplicate summary keeps prior state" {
    const allocator = std.testing.allocator;
    var summary = try confdata_bridge.parseConfig(allocator, malformed_duplicate_input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 4), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("stable", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[1].name);
    try std.testing.expectEqualStrings("n", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_SUFFIX", summary.entries[2].name);
    try std.testing.expectEqualStrings("zigux", summary.entries[2].value);
    try std.testing.expectEqualStrings("CONFIG_BETA", summary.entries[3].name);
    try std.testing.expectEqualStrings("y", summary.entries[3].value);
}

test "confdata bridge standalone malformed duplicate json keeps prior state" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator, malformed_duplicate_input, &capture);
    try std.testing.expectEqualStrings(expected_json, capture.list.items);
}
