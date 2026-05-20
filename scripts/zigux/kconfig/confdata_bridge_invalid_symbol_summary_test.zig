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

test "confdata bridge summary drops malformed CONFIG symbol names" {
    var capture = try Capture.init(std.testing.allocator, 384);
    defer capture.deinit();

    try bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_=y\n" ++
            "# CONFIG_ is not set\n" ++
            "CONFIG_BAD-NAME=m\n" ++
            "CONFIG.BAD=7\n" ++
            "CONFIG_TAB\t=y\n" ++
            "CONFIG_VALID=m\n" ++
            "CONFIG_PATH=\"drivers\\\\zigux\"\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_VALID\",\"kind\":\"tristate\",\"value\":\"m\"},{\"name\":\"CONFIG_PATH\",\"kind\":\"string\",\"value\":\"drivers\\\\zigux\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge summary ignores malformed unset comments and keeps valid neighbors" {
    var capture = try Capture.init(std.testing.allocator, 416);
    defer capture.deinit();

    try bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_ALPHA=y\n" ++
            "# CONFIG_ALPHA extra is not set\n" ++
            "# CONFIG_DEBUG is not set trailing\n" ++
            "# CONFIG_BAD-NAME is not set\n" ++
            "# BROKEN_DEBUG is not set\n" ++
            "# CONFIG_TRACE is not set\n" ++
            "CONFIG_MODE=\"safe\"\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_TRACE\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_MODE\",\"kind\":\"string\",\"value\":\"safe\"}]}\n",
        capture.list.items,
    );
}
