const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const Outcome = mk_elfconfig.Outcome;

fn expectClassifies(expected: Outcome, bytes: []const u8) !void {
    try std.testing.expectEqual(expected, mk_elfconfig.classify(bytes));
}

test "classify treats short buffers as truncated before magic or class checks" {
    try expectClassifies(.truncated, "");
    try expectClassifies(.truncated, "\x7fELF");
    try expectClassifies(.truncated, "not an ELF file");
    try expectClassifies(.truncated, "\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00");
}

test "classify only accepts the exact ELF magic prefix after length passes" {
    const wrong_first_byte = [_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const wrong_second_byte = [_]u8{ 0x7f, 'e', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const wrong_third_byte = [_]u8{ 0x7f, 'E', 'l', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const wrong_fourth_byte = [_]u8{ 0x7f, 'E', 'L', 'f', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

    try expectClassifies(.not_elf, &wrong_first_byte);
    try expectClassifies(.not_elf, &wrong_second_byte);
    try expectClassifies(.not_elf, &wrong_third_byte);
    try expectClassifies(.not_elf, &wrong_fourth_byte);
}

test "classify maps only ELFCLASS32 and ELFCLASS64 to success outcomes" {
    const elf32 = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const elf64 = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const class_none = [_]u8{ 0x7f, 'E', 'L', 'F', 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const class_future = [_]u8{ 0x7f, 'E', 'L', 'F', 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const class_max = [_]u8{ 0x7f, 'E', 'L', 'F', 0xff, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

    try expectClassifies(.elf32, &elf32);
    try expectClassifies(.elf64, &elf64);
    try expectClassifies(.invalid_class, &class_none);
    try expectClassifies(.invalid_class, &class_future);
    try expectClassifies(.invalid_class, &class_max);
}
