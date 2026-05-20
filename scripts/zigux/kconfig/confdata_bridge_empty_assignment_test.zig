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

test "confdata bridge summary keeps explicit empty assignments distinct from quoted empty strings" {
    var capture = try Capture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try bridge.runConfdataBridge(std.testing.allocator,
        \\CONFIG_EMPTY=
        \\CONFIG_QUOTED=""
        \\
    , &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_EMPTY\",\"kind\":\"value\",\"value\":\"\"},{\"name\":\"CONFIG_QUOTED\",\"kind\":\"string\",\"value\":\"\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge summary keeps the latest explicit empty assignment across quoted and unset transitions" {
    var capture = try Capture.init(std.testing.allocator, 384);
    defer capture.deinit();

    try bridge.runConfdataBridge(std.testing.allocator,
        \\# CONFIG_ALPHA is not set
        \\CONFIG_ALPHA=
        \\CONFIG_BETA=""
        \\CONFIG_BETA=
        \\
    , &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"value\",\"value\":\"\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"value\",\"value\":\"\"}]}\n",
        capture.list.items,
    );
}
