const std = @import("std");

const confdata = @import("confdata_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator, capacity: usize) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
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

test "confdata bridge omits embedded NUL suffix bytes on the public json surface" {
    var capture = try TestCapture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try confdata.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_ALPHA=value\x00shadow\n" ++
            "CONFIG_BETA=\"keep\"\n" ++
            "# CONFIG_DEBUG is not set\n",
        &capture,
    );

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"unset\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"value\",\"value\":\"value\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_BETA\",\"kind\":\"string\",\"value\":\"keep\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "shadow") == null);
}

test "confdata bridge preserves bytes before an embedded NUL while keeping adjacent entries visible" {
    var summary = try confdata.parseConfig(
        std.testing.allocator,
        "CONFIG_ALPHA=value\r\x00shadow\n" ++
            "CONFIG_BETA=y\n",
    );
    defer confdata.deinitSummary(std.testing.allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("value\r", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_BETA", summary.entries[1].name);
    try std.testing.expectEqualStrings("y", summary.entries[1].value);
}

test "confdata bridge lets an embedded-NUL duplicate replace the prior visible value without keeping the suffix" {
    var summary = try confdata.parseConfig(
        std.testing.allocator,
        "CONFIG_ALPHA=stable\n" ++
            "CONFIG_ALPHA=value\x00shadow\n" ++
            "CONFIG_BETA=m\n",
    );
    defer confdata.deinitSummary(std.testing.allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("value", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_BETA", summary.entries[1].name);
    try std.testing.expectEqualStrings("m", summary.entries[1].value);
}
