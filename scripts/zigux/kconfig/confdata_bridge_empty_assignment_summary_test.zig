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

test "confdata bridge keeps explicit empty assignments distinct from quoted empty strings in emitted json" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        \\CONFIG_EMPTY=
        \\CONFIG_QUOTED=""
        \\# CONFIG_SWITCH is not set
        \\CONFIG_SWITCH=
        \\
    ,
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_EMPTY\",\"kind\":\"value\",\"value\":\"\"},{\"name\":\"CONFIG_QUOTED\",\"kind\":\"string\",\"value\":\"\"},{\"name\":\"CONFIG_SWITCH\",\"kind\":\"value\",\"value\":\"\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge keeps later explicit empty assignments over earlier quoted duplicates in emitted json" {
    var capture = try Capture.init(std.testing.allocator, 256);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        \\CONFIG_DUPLICATE=""
        \\CONFIG_DUPLICATE=
        \\CONFIG_NEIGHBOR=7
        \\
    ,
        &capture,
    );

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_DUPLICATE\",\"kind\":\"value\",\"value\":\"\"},{\"name\":\"CONFIG_NEIGHBOR\",\"kind\":\"value\",\"value\":\"7\"}]}\n",
        capture.list.items,
    );
}
