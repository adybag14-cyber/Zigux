const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

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

test "standalone confdata bridge duplicate symbols keep first visible order with final state" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator,
        \\CONFIG_ALPHA=y
        \\CONFIG_BETA=m
        \\# CONFIG_ALPHA is not set
        \\CONFIG_GAMMA="tail"
        \\CONFIG_BETA=7
        \\
    , &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[" ++
            "{\"name\":\"CONFIG_ALPHA\",\"kind\":\"unset\",\"value\":\"n\"}," ++
            "{\"name\":\"CONFIG_BETA\",\"kind\":\"value\",\"value\":\"7\"}," ++
            "{\"name\":\"CONFIG_GAMMA\",\"kind\":\"string\",\"value\":\"tail\"}" ++
            "]}\n",
        capture.list.items,
    );
}
