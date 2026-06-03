const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 64),
            .allocator = allocator,
        };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *@This(), bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }
};

fn expectTruncated(input: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    try std.testing.expectEqual(mk_elfconfig.Outcome.truncated, mk_elfconfig.classify(input));
    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("Error: input truncated\n", stderr.list.items);
}

test "public entry treats every short prefix as truncated" {
    const input = [_]u8{
        0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0,
    };

    var len: usize = 0;
    while (len <= input.len) : (len += 1) {
        try expectTruncated(input[0..len]);
    }
}

test "public entry checks length before magic and class" {
    const almost_elf64 = [_]u8{
        0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0,
    };
    try expectTruncated(&almost_elf64);

    const almost_invalid_class = [_]u8{
        0x7f, 'E', 'L', 'F', 3, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0,
    };
    try expectTruncated(&almost_invalid_class);

    const almost_not_elf = [_]u8{
        0, 'E', 'L', 'F', 1, 1, 1, 0,
        0, 0,   0,   0,   0, 0, 0,
    };
    try expectTruncated(&almost_not_elf);
}
