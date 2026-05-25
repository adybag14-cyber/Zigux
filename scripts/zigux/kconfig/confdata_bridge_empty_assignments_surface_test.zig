const std = @import("std");
const bridge = @import("./confdata_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
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
    \\CONFIG_EMPTY=
    \\CONFIG_QUOTED=""
    \\# CONFIG_SWITCH is not set
    \\CONFIG_SWITCH=
    \\
;

test "confdata bridge empty assignments stay distinct from quoted empty strings on the summary surface" {
    const allocator = std.testing.allocator;
    var summary = try bridge.parseConfig(allocator, input);
    defer bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_EMPTY", summary.entries[0].name);
    try std.testing.expectEqualStrings("value", @tagName(summary.entries[0].kind));
    try std.testing.expectEqualStrings("", summary.entries[0].value);

    try std.testing.expectEqualStrings("CONFIG_QUOTED", summary.entries[1].name);
    try std.testing.expectEqualStrings("string", @tagName(summary.entries[1].kind));
    try std.testing.expectEqualStrings("", summary.entries[1].value);

    try std.testing.expectEqualStrings("CONFIG_SWITCH", summary.entries[2].name);
    try std.testing.expectEqualStrings("value", @tagName(summary.entries[2].kind));
    try std.testing.expectEqualStrings("", summary.entries[2].value);
}

test "confdata bridge empty assignments stay distinct from quoted empty strings in json output" {
    const allocator = std.testing.allocator;
    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_EMPTY\",\"kind\":\"value\",\"value\":\"\"},{\"name\":\"CONFIG_QUOTED\",\"kind\":\"string\",\"value\":\"\"},{\"name\":\"CONFIG_SWITCH\",\"kind\":\"value\",\"value\":\"\"}]}\n",
        capture.list.items,
    );
}
