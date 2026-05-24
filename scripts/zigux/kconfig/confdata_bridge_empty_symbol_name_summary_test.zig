const std = @import("std");
const bridge = @import("confdata_bridge.zig");

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

    pub fn writeAll(self: *TestCapture, text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
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

test "confdata bridge parseConfig ignores empty CONFIG symbol names" {
    const allocator = std.testing.allocator;
    var summary = try bridge.parseConfig(allocator,
        \\CONFIG_=y
        \\# CONFIG_ is not set
        \\CONFIG_VALID=m
        \\
    );
    defer bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_VALID", summary.entries[0].name);
    try std.testing.expectEqualStrings("m", summary.entries[0].value);
}

test "confdata bridge runConfdataBridge omits empty CONFIG symbol names from JSON output" {
    var capture = try TestCapture.init(std.testing.allocator, 160);
    defer capture.deinit();

    try bridge.runConfdataBridge(std.testing.allocator,
        \\CONFIG_=y
        \\# CONFIG_ is not set
        \\CONFIG_VALID=m
        \\
    , &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_VALID\",\"kind\":\"tristate\",\"value\":\"m\"}]}\n",
        capture.list.items,
    );
}
