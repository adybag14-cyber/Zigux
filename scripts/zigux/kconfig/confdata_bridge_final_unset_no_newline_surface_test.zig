const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
            .allocator = allocator,
        };
    }

    fn deinit(self: *Capture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
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

test "standalone final unset without trailing newline stays visible" {
    const input =
        "CONFIG_ALPHA=y\n" ++
        "CONFIG_BETA=m\n" ++
        "# CONFIG_ALPHA is not set";

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator, input, &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"m\"}]}\n",
        capture.list.items,
    );
}

test "standalone final unset without trailing newline can be superseded before eof" {
    const input =
        "# CONFIG_GAMMA is not set\n" ++
        "CONFIG_GAMMA=7\n" ++
        "# CONFIG_DELTA is not set";

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator, input, &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_GAMMA\",\"kind\":\"value\",\"value\":\"7\"},{\"name\":\"CONFIG_DELTA\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}
