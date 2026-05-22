const std = @import("std");
const bridge = @import("confdata_bridge.zig");

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

test "confdata bridge emitted json ignores malformed unset comment lines" {
    const allocator = std.testing.allocator;
    const input =
        "CONFIG_ALPHA=y\n" ++
        "# CONFIG_ALPHA extra is not set\n" ++
        "# CONFIG_DEBUG is not set trailing\n" ++
        "# CONFIG_DEBUG is not set\n" ++
        "CONFIG_NAME=\"zigux\"\n" ++
        "# CONFIG_NAME extra is not set\n";

    var capture = try Capture.init(allocator, 256);
    defer capture.deinit();

    try bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_NAME\",\"kind\":\"string\",\"value\":\"zigux\"}]}\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "trailing") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "extra") == null);
}

test "confdata bridge malformed unset comments do not clobber later visible states" {
    const allocator = std.testing.allocator;
    const input =
        "CONFIG_SWITCH=\"kept\"\n" ++
        "# CONFIG_SWITCH extra is not set\n" ++
        "CONFIG_SWITCH=9\n" ++
        "# CONFIG_FINAL is not set trailing\n" ++
        "# CONFIG_FINAL is not set\n";

    var summary = try bridge.parseConfig(allocator, input);
    defer bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_SWITCH", summary.entries[0].name);
    try std.testing.expectEqualStrings("value", summary.entries[0].kind.text());
    try std.testing.expectEqualStrings("9", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_FINAL", summary.entries[1].name);
    try std.testing.expectEqualStrings("unset", summary.entries[1].kind.text());
    try std.testing.expectEqualStrings("n", summary.entries[1].value);
}
