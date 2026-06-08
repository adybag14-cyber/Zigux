const std = @import("std");
const genksyms_crc = @import("genksyms_crc.zig");

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

test "genksyms CRC escapes visible vertical tab before NUL tail" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    const input = "alpha\x0bbeta" ++ [_]u8{0} ++ "hidden\x0btail\nnext\n";
    try genksyms_crc.runGenksymsCrc(input, &capture);

    try std.testing.expectEqualStrings(
        "{\"cases\":[{\"input\":\"alpha\\u000bbeta\",\"crc_hex\":\"0x695cd00b\"},{\"input\":\"next\",\"crc_hex\":\"0x042f103c\"}]}\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "tail") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "0x389fc0fa") == null);
}
