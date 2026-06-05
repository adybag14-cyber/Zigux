const std = @import("std");

const crc = @import("genksyms_crc.zig");

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

fn expectCase(capture: []const u8, input: []const u8) !usize {
    const input_marker = try std.fmt.allocPrint(std.testing.allocator, "\"input\":\"{s}\"", .{input});
    defer std.testing.allocator.free(input_marker);
    const crc_marker = try std.fmt.allocPrint(std.testing.allocator, "\"crc_hex\":\"0x{x:0>8}\"", .{crc.crc32(input)});
    defer std.testing.allocator.free(crc_marker);

    const input_index = std.mem.indexOf(u8, capture, input_marker) orelse return error.MissingInput;
    const crc_index = std.mem.indexOf(u8, capture, crc_marker) orelse return error.MissingCrc;
    try std.testing.expect(crc_index > input_index);
    return input_index;
}

test "runGenksymsCrc truncates a final EOF record at NUL" {
    var capture = try Capture(256).init(std.testing.allocator);
    defer capture.deinit();

    try crc.runGenksymsCrc("int\nunsigned long\x00hidden eof suffix", &capture);

    const int_index = try expectCase(capture.list.items, "int");
    const eof_index = try expectCase(capture.list.items, "unsigned long");

    try std.testing.expect(int_index < eof_index);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "suffix") == null);
    try std.testing.expect(std.mem.count(u8, capture.list.items, "crc_hex") == 2);
}
