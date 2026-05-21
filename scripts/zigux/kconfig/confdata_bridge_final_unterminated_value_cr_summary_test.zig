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

test "confdata bridge emits trailing carriage return for final unterminated value line" {
    var capture = try Capture.init(std.testing.allocator, 192);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_DECIMAL=7\r",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_DECIMAL\",\"kind\":\"value\",\"value\":\"7\\r\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge keeps final unterminated carriage-return value as the last visible duplicate" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_DECIMAL=5\n" ++
            "CONFIG_OTHER=y\n" ++
            "CONFIG_DECIMAL=7\r",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_DECIMAL\",\"kind\":\"value\",\"value\":\"7\\r\"},{\"name\":\"CONFIG_OTHER\",\"kind\":\"tristate\",\"value\":\"y\"}]}\n",
        capture.list.items,
    );
}
