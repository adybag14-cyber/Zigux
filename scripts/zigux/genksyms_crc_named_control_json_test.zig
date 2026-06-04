const std = @import("std");
const genksyms_crc = @import("./genksyms_crc.zig");

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

    pub fn print(self: *Capture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "runGenksymsCrc uses named JSON escapes for backspace and form feed" {
    const record = "pre" ++ [_]u8{0x08} ++ "mid" ++ [_]u8{0x0c} ++ "tail";

    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, record.len + 1);
    defer input.deinit(std.testing.allocator);
    try input.appendSlice(std.testing.allocator, record);
    try input.append(std.testing.allocator, '\n');

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();
    try genksyms_crc.runGenksymsCrc(input.items, &capture);

    const expected_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{genksyms_crc.crc32(record)});
    defer std.testing.allocator.free(expected_crc);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"pre\\bmid\\ftail\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, expected_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u0008") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u000c") == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0x08) == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0x0c) == null);
}
