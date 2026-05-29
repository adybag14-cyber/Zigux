const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    bytes: std.ArrayList(u8),

    pub fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .allocator = allocator,
            .bytes = try std.ArrayList(u8).initCapacity(allocator, 128),
        };
    }

    pub fn deinit(self: *Capture) void {
        self.bytes.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, chunk: []const u8) !void {
        try self.bytes.appendSlice(self.allocator, chunk);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.bytes.append(self.allocator, byte);
    }

    pub fn print(self: *Capture, comptime format: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, format, args);
        defer self.allocator.free(rendered);
        try self.bytes.appendSlice(self.allocator, rendered);
    }
};

test "standalone ignored lines keep json packet empty" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator,
        \\# plain comment
        \\CONFIG_=empty-name
        \\CONFIG-BAD=y
        \\# CONFIG_DEBUG is not set extra
        \\CONFIG_QUOTED="unterminated
        \\
    , &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":0,\"unset\":0},\"entries\":[]}\n",
        capture.bytes.items,
    );
}

test "standalone ignored lines do not disturb surrounding entries" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator,
        \\CONFIG_ALPHA=y
        \\# plain comment
        \\CONFIG-BAD=m
        \\# CONFIG_STALE is not set extra
        \\CONFIG_MESSAGE="zigux"
        \\
    , &capture);

    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":0},\"entries\":[" ++
            "{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"}," ++
            "{\"name\":\"CONFIG_MESSAGE\",\"kind\":\"string\",\"value\":\"zigux\"}" ++
            "]}\n",
        capture.bytes.items,
    );
}

test "standalone ignored lines parse as a zero count summary" {
    var summary = try confdata_bridge.parseConfig(std.testing.allocator,
        \\CONFIG_=
        \\not a symbol
        \\# CONFIG_DEBUG is not set extra
        \\CONFIG_NAME="unterminated
        \\
    );
    defer confdata_bridge.deinitSummary(std.testing.allocator, &summary);

    try std.testing.expectEqual(@as(usize, 0), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 0), summary.entries.len);
}
