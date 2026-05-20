const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

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

test "confdata bridge emits uppercase tristates in json summaries" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator,
        \\CONFIG_ALPHA=Y
        \\CONFIG_BETA=M
        \\CONFIG_DEBUG=N
        \\
    , &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"Y\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"M\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"tristate\",\"value\":\"N\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge keeps uppercase tristate duplicates across prior states" {
    const input =
        \\# CONFIG_ALPHA is not set
        \\CONFIG_ALPHA=Y
        \\CONFIG_BETA=7
        \\CONFIG_BETA=M
        \\CONFIG_GAMMA=\"quoted\"
        \\CONFIG_GAMMA=N
        \\
    ;

    const allocator = std.testing.allocator;
    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("Y", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_BETA", summary.entries[1].name);
    try std.testing.expectEqualStrings("M", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_GAMMA", summary.entries[2].name);
    try std.testing.expectEqualStrings("N", summary.entries[2].value);

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"Y\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"M\"},{\"name\":\"CONFIG_GAMMA\",\"kind\":\"tristate\",\"value\":\"N\"}]}\n",
        capture.list.items,
    );
}
