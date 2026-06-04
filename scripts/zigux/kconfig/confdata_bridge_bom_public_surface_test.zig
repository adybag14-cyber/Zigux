const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
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

test "confdata bridge public json keeps mid-file bom from becoming a config symbol" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_FIRST=y\n" ++
            "\xef\xbb\xbfCONFIG_SECOND=m\n" ++
            "CONFIG_THIRD=7\n",
        &capture,
    );

    try expectContains(capture.list.items, "\"set\":2");
    try expectContains(capture.list.items, "\"unset\":0");
    try expectContains(capture.list.items, "\"name\":\"CONFIG_FIRST\",\"kind\":\"tristate\",\"value\":\"y\"");
    try expectContains(capture.list.items, "\"name\":\"CONFIG_THIRD\",\"kind\":\"value\",\"value\":\"7\"");
    try expectAbsent(capture.list.items, "CONFIG_SECOND");
    try expectAbsent(capture.list.items, "\xef\xbb\xbfCONFIG_SECOND");
}
