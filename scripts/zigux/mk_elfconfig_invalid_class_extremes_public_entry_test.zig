const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf_magic = [_]u8{ 0x7f, 'E', 'L', 'F' };
const elfclass32: u8 = 1;
const elfclass64: u8 = 2;

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

fn elfIdent(class: u8) [16]u8 {
    return .{ elf_magic[0], elf_magic[1], elf_magic[2], elf_magic[3], class, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
}

fn expectInvalidClassFirstHeader(class: u8, trailing_header_class: u8) !void {
    const leading_header = elfIdent(class);
    const trailing_header = elfIdent(trailing_header_class);
    var input: [leading_header.len + 7 + trailing_header.len + 5]u8 = undefined;
    var cursor: usize = 0;

    @memcpy(input[cursor..][0..leading_header.len], &leading_header);
    cursor += leading_header.len;

    @memcpy(input[cursor..][0..7], "padding");
    cursor += 7;

    @memcpy(input[cursor..][0..trailing_header.len], &trailing_header);
    cursor += trailing_header.len;

    @memcpy(input[cursor..][0..5], "trail");

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(&input, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "public entry rejects zero ELF class before trailing ELF32" {
    try expectInvalidClassFirstHeader(0, elfclass32);
}

test "public entry rejects zero ELF class before trailing ELF64" {
    try expectInvalidClassFirstHeader(0, elfclass64);
}

test "public entry rejects max ELF class before trailing ELF32" {
    try expectInvalidClassFirstHeader(255, elfclass32);
}

test "public entry rejects max ELF class before trailing ELF64" {
    try expectInvalidClassFirstHeader(255, elfclass64);
}
