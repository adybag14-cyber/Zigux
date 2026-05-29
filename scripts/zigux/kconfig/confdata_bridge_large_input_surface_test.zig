const std = @import("std");

const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) Capture {
        return .{
            .allocator = allocator,
            .list = .empty,
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
        try self.writeAll(rendered);
    }
};

test "standalone confdata bridge keeps tail entries after large ignored prefix" {
    const allocator = std.testing.allocator;

    var input = try std.ArrayList(u8).initCapacity(allocator, (1024 * 1024) + 160);
    defer input.deinit(allocator);

    try input.appendSlice(allocator, "# ");
    try input.appendNTimes(allocator, 'x', (1024 * 1024) + 64);
    try input.append(allocator, '\n');
    try input.appendSlice(allocator,
        \\CONFIG_TAIL="large-input"
        \\# CONFIG_DROP is not set
        \\
    );
    try std.testing.expect(input.items.len > 1024 * 1024);

    var capture = Capture.init(allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input.items, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_TAIL\",\"kind\":\"string\",\"value\":\"large-input\"},{\"name\":\"CONFIG_DROP\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}
