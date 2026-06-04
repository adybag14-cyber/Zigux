const std = @import("std");
const genksyms_crc = @import("genksyms_crc.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 192),
            .allocator = allocator,
        };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *@This(), bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }

    pub fn writeByte(self: *@This(), byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "runGenksymsCrc starts a clean packet after leading skipped chunks" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try genksyms_crc.runGenksymsCrc("\n\r\n\x00hidden\n\r\r\nint\nstruct device\n", &capture);

    try std.testing.expectEqualStrings(
        "{\"cases\":[{\"input\":\"int\",\"crc_hex\":\"0x1451dab1\"},{\"input\":\"struct device\",\"crc_hex\":\"0xa38c4517\"}]}\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "[,") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden") == null);
    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, capture.list.items, "crc_hex"));
}
