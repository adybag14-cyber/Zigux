const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    bytes: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .allocator = allocator,
            .bytes = try std.ArrayList(u8).initCapacity(allocator, 256),
        };
    }

    fn deinit(self: *Capture) void {
        self.bytes.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, text: []const u8) !void {
        try self.bytes.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.bytes.append(self.allocator, byte);
    }

    pub fn print(self: *Capture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.bytes.appendSlice(self.allocator, rendered);
    }
};

test "confdata public json surface strips first-line utf8 bom from symbol names" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "\xef\xbb\xbfCONFIG_FIRST=y\nCONFIG_SECOND=m\n",
        &capture,
    );

    const output = capture.bytes.items;
    try std.testing.expect(std.mem.indexOf(u8, output, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"unset\":0") != null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"name\":\"CONFIG_FIRST\",\"kind\":\"tristate\",\"value\":\"y\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"name\":\"CONFIG_SECOND\",\"kind\":\"tristate\",\"value\":\"m\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\xef\xbb\xbfCONFIG_FIRST") == null);
}
