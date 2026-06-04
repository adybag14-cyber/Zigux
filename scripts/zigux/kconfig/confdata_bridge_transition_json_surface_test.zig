const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    bytes: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .allocator = allocator,
            .bytes = try std.ArrayList(u8).initCapacity(allocator, 512),
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

test "confdata bridge json keeps first symbol slot while emitting final transition state" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator,
        \\CONFIG_ALPHA=y
        \\CONFIG_BETA=m
        \\# CONFIG_ALPHA is not set
        \\CONFIG_ALPHA=M
        \\# CONFIG_BETA is not set
    , &capture);

    try std.testing.expect(std.mem.indexOf(u8, capture.bytes.items, "\"counts\":{\"set\":1,\"unset\":1}") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.bytes.items, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.bytes.items, "\"name\":\"CONFIG_BETA\",\"kind\":\"unset\",\"value\":\"n\"") != null);

    const alpha_index = std.mem.indexOf(u8, capture.bytes.items, "\"name\":\"CONFIG_ALPHA\"").?;
    const beta_index = std.mem.indexOf(u8, capture.bytes.items, "\"name\":\"CONFIG_BETA\"").?;
    try std.testing.expect(alpha_index < beta_index);
}
