const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

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

test "confdata bridge emits embedded NUL bounded summary output" {
    const input =
        "CONFIG_ALPHA=y\x00hidden_alpha\n" ++
        "CONFIG_PATH=\"drivers\\\\zigux\"\x00ignored_tail\n" ++
        "# CONFIG_DEBUG is not set\x00ghost_comment\n" ++
        "CONFIG_EMPTY=\x00hidden_empty\n";

    var capture = try TestCapture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator, input, &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_PATH\",\"kind\":\"string\",\"value\":\"drivers\\\\zigux\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_EMPTY\",\"kind\":\"value\",\"value\":\"\"}]}\n",
        capture.list.items,
    );

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden_alpha") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "ignored_tail") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "ghost_comment") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden_empty") == null);
}
