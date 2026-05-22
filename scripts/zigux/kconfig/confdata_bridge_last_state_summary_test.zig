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

test "confdata bridge standalone proof keeps only final set states in summary output" {
    const allocator = std.testing.allocator;
    const input =
        \\# CONFIG_ALPHA is not set
        \\CONFIG_ALPHA="enabled"
        \\CONFIG_BETA=m
        \\# CONFIG_BETA is not set
        \\CONFIG_BETA=7
        \\
    ;

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"string\",\"value\":\"enabled\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"value\",\"value\":\"7\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge standalone proof keeps duplicate unset state counted once" {
    const allocator = std.testing.allocator;
    const input =
        \\# CONFIG_REPEAT is not set
        \\# CONFIG_REPEAT is not set
        \\CONFIG_KEEP=7
        \\
    ;

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_REPEAT\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_KEEP\",\"kind\":\"value\",\"value\":\"7\"}]}\n",
        capture.list.items,
    );
}
