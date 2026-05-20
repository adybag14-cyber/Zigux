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

test "confdata bridge keeps explicit n assignments distinct from unset markers in json summary" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_ALPHA=n\n" ++
            "# CONFIG_BETA is not set\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"n\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge preserves explicit n after replacing an earlier unset duplicate" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "# CONFIG_ALPHA is not set\n" ++
            "CONFIG_ALPHA=n\n" ++
            "CONFIG_GAMMA=y\n",
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"n\"},{\"name\":\"CONFIG_GAMMA\",\"kind\":\"tristate\",\"value\":\"y\"}]}\n",
        capture.list.items,
    );
}
