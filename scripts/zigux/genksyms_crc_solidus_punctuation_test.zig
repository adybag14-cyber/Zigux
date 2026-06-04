const std = @import("std");
const gen = @import("./genksyms_crc.zig");

fn Capture(comptime capacity: usize) type {
    return struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
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
}

test "runGenksymsCrc leaves solidus and punctuation records literal while hashing raw bytes" {
    const slash_record = "path/to-symbol+field[3]";
    const punctuation_record = "question?colon:semi;comma,equals=star*paren()";
    const input = slash_record ++ "\n" ++ punctuation_record ++ "\n";

    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();

    try gen.runGenksymsCrc(input, &capture);

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "{{\"cases\":[{{\"input\":\"{s}\",\"crc_hex\":\"0x{x:0>8}\"}},{{\"input\":\"{s}\",\"crc_hex\":\"0x{x:0>8}\"}}]}}\n",
        .{ slash_record, gen.crc32(slash_record), punctuation_record, gen.crc32(punctuation_record) },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\/") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, slash_record) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, punctuation_record) != null);
}
