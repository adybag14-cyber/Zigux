const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator, capacity: usize) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
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

test "confdata bridge preserves trailing backslashes and ignores later malformed quoted duplicates" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_PATH="drivers\\\\"
        \\CONFIG_PATH="unterminated
        \\CONFIG_BANNER="zigux \\\"bridge\\\""suffix
        \\# CONFIG_DEBUG is not set
        \\
    ;

    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_PATH", summary.entries[0].name);
    try std.testing.expectEqualStrings("drivers\\\\", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_BANNER", summary.entries[1].name);
    try std.testing.expectEqualStrings("zigux \\\"bridge\\\"", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[2].name);
    try std.testing.expectEqualStrings("n", summary.entries[2].value);
}

test "confdata bridge emits preserved trailing backslashes and suffix-trimmed strings in json output" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_PATH="drivers\\\\"
        \\CONFIG_PATH="unterminated
        \\CONFIG_BANNER="zigux \\\"bridge\\\""suffix
        \\# CONFIG_DEBUG is not set
        \\
    ;

    var capture = try Capture.init(allocator, 256);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"unset\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_PATH\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"value\":\"drivers\\\\\\\\\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_BANNER\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"value\":\"zigux \\\\\\\"bridge\\\\\\\"\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_DEBUG\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"kind\":\"unset\"") != null);
}
