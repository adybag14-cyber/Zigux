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

test "confdata bridge strips escaped control-sequence backslashes in parsed summary state" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_TEXT="line\nindent\tmark\bslot\fform\rend"
        \\CONFIG_NEXT="tail"
        \\# CONFIG_DEBUG is not set
        \\
    ;

    var summary = try bridge.parseConfig(allocator, input);
    defer bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_TEXT", summary.entries[0].name);
    try std.testing.expectEqualStrings("string", @tagName(summary.entries[0].kind));
    try std.testing.expectEqualStrings("linenindenttmarkbslotfformrend", summary.entries[0].value);

    try std.testing.expectEqualStrings("CONFIG_NEXT", summary.entries[1].name);
    try std.testing.expectEqualStrings("tail", summary.entries[1].value);

    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[2].name);
    try std.testing.expectEqualStrings("unset", @tagName(summary.entries[2].kind));
    try std.testing.expectEqualStrings("n", summary.entries[2].value);
}

test "confdata bridge emits stripped escaped control-sequence text in json output" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_TEXT="line\nindent\tmark\bslot\fform\rend"
        \\CONFIG_NEXT="tail"
        \\# CONFIG_DEBUG is not set
        \\
    ;

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_TEXT\",\"kind\":\"string\",\"value\":\"linenindenttmarkbslotfformrend\"},{\"name\":\"CONFIG_NEXT\",\"kind\":\"string\",\"value\":\"tail\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}
