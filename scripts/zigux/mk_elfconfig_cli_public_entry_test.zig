const std = @import("std");

const case_count = 5;

const elf32 = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const elf64_with_tail = [_]u8{
    0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
    0,    0,   0,   0,   0, 0, 0, 0,
    0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
};
const truncated_elf_prefix = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 };
const not_elf = [_]u8{ 'Z', 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const invalid_class = [_]u8{ 0x7f, 'E', 'L', 'F', 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

test "CLI shard keeps the canonical stdin cases visible" {
    const cases = [_][]const u8{
        &elf32,
        &elf64_with_tail,
        &truncated_elf_prefix,
        &not_elf,
        &invalid_class,
    };

    try std.testing.expectEqual(@as(usize, case_count), cases.len);
}

test "CLI shard includes exact fixed-header and trailing-byte inputs" {
    try std.testing.expectEqual(@as(usize, 16), elf32.len);
    try std.testing.expectEqual(@as(usize, 24), elf64_with_tail.len);
    try std.testing.expectEqual(@as(usize, 15), truncated_elf_prefix.len);
    try std.testing.expectEqual(@as(u8, 2), elf64_with_tail[4]);
    try std.testing.expectEqual(@as(u8, 1), elf64_with_tail[20]);
}
