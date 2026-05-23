const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 320),
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

test "escaped quoted strings stay decoded in summary state and re-escaped in emitted json" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_BANNER=\"zigux \\\"bridge\\\"\"\n" ++
            "CONFIG_PATH=\"drivers\\\\zigux\"\n" ++
            "CONFIG_SUFFIX=\"zigux\"tail\n" ++
            "CONFIG_EMPTY=\"\"\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":4,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_BANNER\",\"kind\":\"string\",\"value\":\"zigux \\\"bridge\\\"\"},{\"name\":\"CONFIG_PATH\",\"kind\":\"string\",\"value\":\"drivers\\\\zigux\"},{\"name\":\"CONFIG_SUFFIX\",\"kind\":\"string\",\"value\":\"zigux\"},{\"name\":\"CONFIG_EMPTY\",\"kind\":\"string\",\"value\":\"\"}]}\n",
        capture.list.items,
    );
}
