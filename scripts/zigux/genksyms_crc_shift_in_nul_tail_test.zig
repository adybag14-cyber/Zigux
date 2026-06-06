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

test "runGenksymsCrc escapes shift-in before NUL and hides hidden tail" {
    var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, 64);
    defer input.deinit(std.testing.allocator);
    try input.appendSlice(std.testing.allocator, "alpha");
    try input.append(std.testing.allocator, 0x0f);
    try input.appendSlice(std.testing.allocator, "visible");
    try input.append(std.testing.allocator, 0);
    try input.appendSlice(std.testing.allocator, "hidden");
    try input.append(std.testing.allocator, 0x0f);
    try input.appendSlice(std.testing.allocator, "tail\nnext\n");

    const visible = input.items[0.."alpha\x0fvisible".len];

    var capture = try Capture(192).init(std.testing.allocator);
    defer capture.deinit();
    try genksyms_crc.runGenksymsCrc(input.items, &capture);

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "{{\"cases\":[{{\"input\":\"alpha\\u000fvisible\",\"crc_hex\":\"0x{x:0>8}\"}},{{\"input\":\"next\",\"crc_hex\":\"0x{x:0>8}\"}}]}}\n",
        .{ genksyms_crc.crc32(visible), genksyms_crc.crc32("next") },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "hidden") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "tail") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u000f") != null);
}
