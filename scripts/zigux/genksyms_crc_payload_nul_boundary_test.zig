const std = @import("std");
const genksyms_crc = @import("genksyms_crc.zig");

const c_line_payload_len = 4095;

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

test "genksyms CRC truncates long C payload chunks at an embedded NUL" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, c_line_payload_len + 6);
    defer input.deinit(std.testing.allocator);

    const visible = "long-prefix";
    const hidden = "hidden-long-tail";
    try input.appendSlice(std.testing.allocator, visible);
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, hidden);
    try input.appendNTimes(std.testing.allocator, 'z', c_line_payload_len - visible.len - 1 - hidden.len);
    try input.appendSlice(std.testing.allocator, "\nnext\n");

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();
    try genksyms_crc.runGenksymsCrc(input.items, &capture);

    try std.testing.expectEqualStrings(
        "{\"cases\":[{\"input\":\"long-prefix\",\"crc_hex\":\"0xd333660b\"},{\"input\":\"next\",\"crc_hex\":\"0x042f103c\"}]}\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden-long-tail") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "0xd8a8dda4") == null);
    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, capture.list.items, "crc_hex"));
}
