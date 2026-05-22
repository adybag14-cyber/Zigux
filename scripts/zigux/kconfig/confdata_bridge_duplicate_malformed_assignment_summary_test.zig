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

test "confdata bridge keeps prior visible states when later quoted duplicates are malformed" {
    var capture = try Capture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        \\CONFIG_ALPHA="stable"
        \\CONFIG_ALPHA="unterminated
        \\# CONFIG_DEBUG is not set
        \\CONFIG_DEBUG="broken
        \\CONFIG_GAMMA="still-broken
        \\CONFIG_BETA=y
        \\# CONFIG_DELTA is not set
        \\CONFIG_DELTA="broken
        \\CONFIG_EPSILON=7
        \\
    ,
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":2},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"string\",\"value\":\"stable\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_DELTA\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_EPSILON\",\"kind\":\"value\",\"value\":\"7\"}]}\n",
        capture.list.items,
    );
}
