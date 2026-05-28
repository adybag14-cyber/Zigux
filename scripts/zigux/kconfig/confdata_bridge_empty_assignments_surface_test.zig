const std = @import("std");
const bridge = @import("confdata_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
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

test "standalone confdata bridge keeps explicit empty assignments distinct in json output" {
    var output = try Capture.init(std.testing.allocator);
    defer output.deinit();

    try bridge.runConfdataBridge(
        std.testing.allocator,
        \\CONFIG_EMPTY=
        \\CONFIG_QUOTED_EMPTY=""
        \\CONFIG_ALPHA=n
        \\# CONFIG_DEBUG is not set
        \\
    ,
        &output,
    );

    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"set\":3") != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"unset\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"name\":\"CONFIG_EMPTY\",\"kind\":\"value\",\"value\":\"\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"name\":\"CONFIG_QUOTED_EMPTY\",\"kind\":\"string\",\"value\":\"\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"") != null);
}

test "standalone confdata bridge keeps prior explicit value after malformed quoted duplicate" {
    var output = try Capture.init(std.testing.allocator);
    defer output.deinit();

    try bridge.runConfdataBridge(
        std.testing.allocator,
        \\CONFIG_ALPHA="stable"
        \\CONFIG_ALPHA="broken
        \\CONFIG_BETA=
        \\
    ,
        &output,
    );

    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"unset\":0") != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"string\",\"value\":\"stable\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"name\":\"CONFIG_BETA\",\"kind\":\"value\",\"value\":\"\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"broken") == null);
}
