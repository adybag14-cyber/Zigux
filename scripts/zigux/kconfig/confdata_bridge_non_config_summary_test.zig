const std = @import("std");
const bridge = @import("confdata_bridge.zig");

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

test "confdata bridge summary ignores non-CONFIG assignments and comments" {
    var capture = try Capture.init(std.testing.allocator, 384);
    defer capture.deinit();

    try bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_ALPHA=y\n" ++
            "BROKEN_ENTRY=1\n" ++
            "# BROKEN_DEBUG is not set\n" ++
            "not-even-kconfig\n" ++
            "CONFIG_NAME=\"zigux\"\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_NAME\",\"kind\":\"string\",\"value\":\"zigux\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge summary keeps valid state transitions beside ignored non-CONFIG lines" {
    var capture = try Capture.init(std.testing.allocator, 448);
    defer capture.deinit();

    try bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_ALPHA=y\n" ++
            "BROKEN_ENTRY=1\n" ++
            "# CONFIG_TRACE is not set\n" ++
            "not-even-kconfig\n" ++
            "CONFIG_MODE=\"safe\"\n" ++
            "# BROKEN_DEBUG is not set\n" ++
            "CONFIG_LEVEL=7\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_TRACE\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_MODE\",\"kind\":\"string\",\"value\":\"safe\"},{\"name\":\"CONFIG_LEVEL\",\"kind\":\"value\",\"value\":\"7\"}]}\n",
        capture.list.items,
    );
}
