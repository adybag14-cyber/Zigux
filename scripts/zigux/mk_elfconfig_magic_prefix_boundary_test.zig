const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass32: u8 = 1;
const elfclass64: u8 = 2;
const truncated_text = "Error: input truncated\n";
const not_elf_text = "Error: not ELF\n";

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

fn expectRun(input: []const u8, expected_stderr: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);

    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "short ELF magic prefix is truncated before magic mismatch handling" {
    try expectRun(&[_]u8{ 0x7f, 'E', 'L' }, truncated_text);
}

test "full header with only first three magic bytes is not ELF" {
    try expectRun(&[_]u8{
        0x7f, 'E', 'L', 'X', elfclass64, 1, 1, 0,
        0,    0,   0,   0,   0,          0, 0, 0,
    }, not_elf_text);
}

test "leading byte before a valid header is not skipped or scanned" {
    try expectRun(&[_]u8{
        0, 0x7f, 'E', 'L', 'F', elfclass32, 1, 1,
        0, 0,    0,   0,   0,   0,          0, 0,
        0,
    }, not_elf_text);
}
