const std = @import("std");
const genksyms_crc = @import("genksyms_crc.zig");

fn Capture(comptime capacity: usize) type {
    return struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        pub fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
                .allocator = allocator,
            };
        }

        pub fn deinit(self: *@This()) void {
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

test "runGenksymsCrc escapes quoted paths and low control bytes in JSON output" {
    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();

    try genksyms_crc.runGenksymsCrc("quoted \"symbol\"\tpath\\\\name\nctrl \x08\x0c\x01end\n", &capture);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"quoted \\\"symbol\\\"\\tpath\\\\\\\\name\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"input\":\"ctrl \\b\\f\\u0001end\"") != null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, '\t') == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, '\x08') == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, '\x0c') == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, '\x01') == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "\"crc_hex\"") == 2);
}
