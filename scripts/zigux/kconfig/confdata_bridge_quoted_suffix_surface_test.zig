const std = @import("std");
const bridge = @import("confdata_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator, capacity: usize) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
        };
    }

    fn deinit(self: *TestCapture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *TestCapture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *TestCapture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }

    pub fn print(self: *TestCapture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "standalone confdata bridge quoted suffix surface trims trailing junk and keeps sibling entries visible" {
    var capture = try TestCapture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try bridge.runConfdataBridge(std.testing.allocator,
        \\CONFIG_ALPHA="zigux"suffix
        \\CONFIG_BETA=42
        \\# CONFIG_DEBUG is not set
        \\
    , &capture);

    try expectContains(capture.list.items, "\"counts\":{\"set\":2,\"unset\":1}");
    try expectContains(capture.list.items, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"string\",\"value\":\"zigux\"");
    try expectContains(capture.list.items, "\"name\":\"CONFIG_BETA\",\"kind\":\"value\",\"value\":\"42\"");
    try expectContains(capture.list.items, "\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"");
    try expectAbsent(capture.list.items, "suffix");
}

test "standalone confdata bridge quoted suffix duplicate surface keeps the later trimmed value only" {
    var capture = try TestCapture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try bridge.runConfdataBridge(std.testing.allocator,
        \\CONFIG_ALPHA="stable"
        \\CONFIG_ALPHA="fresh"tail
        \\CONFIG_NOTE=value
        \\
    , &capture);

    try expectContains(capture.list.items, "\"counts\":{\"set\":2,\"unset\":0}");
    try expectContains(capture.list.items, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"string\",\"value\":\"fresh\"");
    try expectContains(capture.list.items, "\"name\":\"CONFIG_NOTE\",\"kind\":\"value\",\"value\":\"value\"");
    try expectAbsent(capture.list.items, "\"value\":\"stable\"");
    try expectAbsent(capture.list.items, "tail");
}
