const std = @import("std");
const genksyms_crc = @import("./genksyms_crc.zig");

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

fn crcHex(allocator: std.mem.Allocator, input: []const u8) ![]const u8 {
    return std.fmt.allocPrint(allocator, "0x{x:0>8}", .{genksyms_crc.crc32(input)});
}

test "runGenksymsCrc starts each output packet from fresh state" {
    var first = try Capture(192).init(std.testing.allocator);
    defer first.deinit();
    try genksyms_crc.runGenksymsCrc("int\nstruct device\n", &first);

    var second = try Capture(96).init(std.testing.allocator);
    defer second.deinit();
    try genksyms_crc.runGenksymsCrc("char\n", &second);

    const first_int_crc = try crcHex(std.testing.allocator, "int");
    defer std.testing.allocator.free(first_int_crc);
    const first_struct_crc = try crcHex(std.testing.allocator, "struct device");
    defer std.testing.allocator.free(first_struct_crc);
    const second_char_crc = try crcHex(std.testing.allocator, "char");
    defer std.testing.allocator.free(second_char_crc);

    try std.testing.expect(std.mem.indexOf(u8, first.list.items, "\"input\":\"int\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, first.list.items, "\"input\":\"struct device\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, first.list.items, first_int_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, first.list.items, first_struct_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, first.list.items, second_char_crc) == null);

    try std.testing.expect(std.mem.indexOf(u8, second.list.items, "\"input\":\"char\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, second.list.items, second_char_crc) != null);
    try std.testing.expect(std.mem.indexOf(u8, second.list.items, "\"input\":\"int\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, second.list.items, "\"input\":\"struct device\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, second.list.items, first_int_crc) == null);
    try std.testing.expect(std.mem.indexOf(u8, second.list.items, first_struct_crc) == null);
    try std.testing.expect(std.mem.count(u8, second.list.items, "crc_hex") == 1);
    try std.testing.expect(std.mem.startsWith(
        u8,
        second.list.items,
        "{\"cases\":[{\"input\":\"char\",\"crc_hex\":\"0x",
    ));
}
