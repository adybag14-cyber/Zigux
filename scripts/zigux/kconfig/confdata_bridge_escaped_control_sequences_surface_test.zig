const std = @import("std");
const bridge = @import("confdata_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
        };
    }

    fn deinit(self: *TestCapture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *TestCapture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *TestCapture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }

    pub fn print(self: *TestCapture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }
};

test "confdata bridge escaped control-sequence surface keeps stripped parsed state" {
    var summary = try bridge.parseConfig(std.testing.allocator,
        \\CONFIG_ESCAPED="line\n\tend"
        \\CONFIG_LABEL="keep"
        \\# CONFIG_DEBUG is not set
        \\
    );
    defer bridge.deinitSummary(std.testing.allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ESCAPED", summary.entries[0].name);
    try std.testing.expectEqualStrings("linentend", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_LABEL", summary.entries[1].name);
    try std.testing.expectEqualStrings("keep", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[2].name);
    try std.testing.expectEqualStrings("n", summary.entries[2].value);
}

test "confdata bridge escaped control-sequence surface emits stripped duplicate on json output" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try bridge.runConfdataBridge(std.testing.allocator,
        \\CONFIG_ESCAPED="older"
        \\CONFIG_ESCAPED="line\n\tend"
        \\CONFIG_OTHER=value
        \\# CONFIG_DEBUG is not set
        \\
    , &capture);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"unset\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_ESCAPED\",\"kind\":\"string\",\"value\":\"linentend\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_OTHER\",\"kind\":\"value\",\"value\":\"value\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "line\\\\n\\\\tend") == null);
}
