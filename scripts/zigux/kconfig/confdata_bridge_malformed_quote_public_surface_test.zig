const std = @import("std");

const confdata = @import("confdata_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
        };
    }

    fn deinit(self: *Capture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
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

test "public confdata bridge ignores malformed quoted assignments without dropping neighbors" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata.runConfdataBridge(std.testing.allocator,
        \\CONFIG_ALPHA="stable"
        \\CONFIG_BROKEN="unterminated
        \\CONFIG_ALPHA="still-broken
        \\CONFIG_MID=m
        \\# CONFIG_OFF is not set
        \\CONFIG_OFF="broken
        \\CONFIG_TAIL=42
        \\
    , &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"string\",\"value\":\"stable\"},{\"name\":\"CONFIG_MID\",\"kind\":\"tristate\",\"value\":\"m\"},{\"name\":\"CONFIG_OFF\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_TAIL\",\"kind\":\"value\",\"value\":\"42\"}]}\n",
        capture.list.items,
    );
}
