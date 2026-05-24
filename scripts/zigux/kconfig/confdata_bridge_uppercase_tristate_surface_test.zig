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

test "confdata bridge canonicalizes uppercase tristate assignments in public json output" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_ALPHA=Y
        \\CONFIG_BETA=M
        \\CONFIG_DEBUG=N
        \\CONFIG_GAMMA=Ysuffix
        \\CONFIG_DELTA=M #comment
        \\CONFIG_EPSILON=N trailing
        \\
    ;

    var capture = try Capture.init(allocator, 384);
    defer capture.deinit();

    try bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":6,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"m\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"tristate\",\"value\":\"n\"},{\"name\":\"CONFIG_GAMMA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_DELTA\",\"kind\":\"tristate\",\"value\":\"m\"},{\"name\":\"CONFIG_EPSILON\",\"kind\":\"tristate\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}
