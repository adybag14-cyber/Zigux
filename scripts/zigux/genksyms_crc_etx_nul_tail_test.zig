const std = @import("std");
const genksyms_crc = @import("genksyms_crc.zig");

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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectCrcPresent(output: []const u8, input: []const u8) !void {
    const expected_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{genksyms_crc.crc32(input)},
    );
    defer std.testing.allocator.free(expected_crc);
    try expectContains(output, expected_crc);
}

fn expectCrcAbsent(output: []const u8, input: []const u8) !void {
    const hidden_crc = try std.fmt.allocPrint(
        std.testing.allocator,
        "0x{x:0>8}",
        .{genksyms_crc.crc32(input)},
    );
    defer std.testing.allocator.free(hidden_crc);
    try expectAbsent(output, hidden_crc);
}

test "runGenksymsCrc escapes visible ETX while hiding embedded NUL tail" {
    var output = try Capture(256).init(std.testing.allocator);
    defer output.deinit();

    const visible = "alpha\x03visible";
    const hidden = "hidden\x03tail";
    const input = visible ++ "\x00" ++ hidden ++ "\nnext\n";

    try genksyms_crc.runGenksymsCrc(input, &output);

    try expectContains(output.list.items, "\"input\":\"alpha\\u0003visible\"");
    try expectAbsent(output.list.items, "hidden");
    try expectAbsent(output.list.items, "\\u0003tail");
    try expectContains(output.list.items, "\"input\":\"next\"");

    try expectCrcPresent(output.list.items, visible);
    try expectCrcPresent(output.list.items, "next");
    try expectCrcAbsent(output.list.items, hidden);
}
