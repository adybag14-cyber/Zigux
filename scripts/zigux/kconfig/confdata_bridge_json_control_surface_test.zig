const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 512),
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

test "standalone confdata bridge json escapes generated entry values" {
    const input =
        "CONFIG_QUOTED=\"left\tright\"\n" ++
        "CONFIG_LOW=prefix" ++ [_]u8{0x1f} ++ "suffix\n" ++
        "CONFIG_SHORT=\"bell\x08form\x0c\"\n";

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator, input, &capture);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_QUOTED\",\"kind\":\"string\",\"value\":\"left\\tright\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_LOW\",\"kind\":\"value\",\"value\":\"prefix\\u001fsuffix\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_SHORT\",\"kind\":\"string\",\"value\":\"bell\\bform\\f\"") != null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, '\t') == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0x1f) == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0x08) == null);
    try std.testing.expect(std.mem.endsWith(u8, capture.list.items, "}\n"));
}
