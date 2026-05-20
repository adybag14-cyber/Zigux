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

test "confdata bridge emits quoted values without trailing suffix bytes in json summaries" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator,
        \\CONFIG_BANNER="zigux \"bridge\""suffix_bytes
        \\CONFIG_PATH="drivers\\zigux"tail
        \\# CONFIG_DEBUG is not set
        \\
    , &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_BANNER\",\"kind\":\"string\",\"value\":\"zigux \\\"bridge\\\"\"},{\"name\":\"CONFIG_PATH\",\"kind\":\"string\",\"value\":\"drivers\\\\zigux\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge keeps quoted suffix duplicates on the final decoded value" {
    const input =
        \\# CONFIG_ALPHA is not set
        \\CONFIG_ALPHA="enabled"value_tail
        \\CONFIG_BETA=7
        \\CONFIG_BETA="final path"ignored
        \\CONFIG_GAMMA="still here"extra
        \\
    ;

    const allocator = std.testing.allocator;
    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("string", summary.entries[0].kind.text());
    try std.testing.expectEqualStrings("enabled", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_BETA", summary.entries[1].name);
    try std.testing.expectEqualStrings("string", summary.entries[1].kind.text());
    try std.testing.expectEqualStrings("final path", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_GAMMA", summary.entries[2].name);
    try std.testing.expectEqualStrings("string", summary.entries[2].kind.text());
    try std.testing.expectEqualStrings("still here", summary.entries[2].value);

    var capture = try Capture.init(allocator, 256);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"string\",\"value\":\"enabled\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"string\",\"value\":\"final path\"},{\"name\":\"CONFIG_GAMMA\",\"kind\":\"string\",\"value\":\"still here\"}]}\n",
        capture.list.items,
    );
}
