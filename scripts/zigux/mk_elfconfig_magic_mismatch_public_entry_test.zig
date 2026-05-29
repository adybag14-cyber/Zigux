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

fn expectNotElf(input: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("Error: not ELF\n", stderr.list.items);
}

test "public entry rejects each full-length ELF magic mismatch" {
    const mismatches = [_]struct {
        offset: usize,
        replacement: u8,
    }{
        .{ .offset = 0, .replacement = 0x00 },
        .{ .offset = 1, .replacement = 'e' },
        .{ .offset = 2, .replacement = 'l' },
        .{ .offset = 3, .replacement = 'f' },
    };

    for (mismatches) |mismatch| {
        var header = [_]u8{
            0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
            0,    0,   0,   0,   0, 0, 0, 0,
        };
        header[mismatch.offset] = mismatch.replacement;

        try expectNotElf(&header);
    }
}

test "public entry keeps magic mismatch authoritative over later valid ELF ident" {
    const input = [_]u8{
        0x00, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
        0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    };

    try expectNotElf(&input);
}
