const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf_magic = [_]u8{ 0x7f, 'E', 'L', 'F' };
const elfclass32: u8 = 1;
const elfclass64: u8 = 2;

fn baseHeader(class: u8) [16]u8 {
    return .{ 0x7f, 'E', 'L', 'F', class, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
}

fn corruptMagic(index: usize, replacement: u8, class: u8) [16]u8 {
    var header = baseHeader(class);
    header[index] = replacement;
    return header;
}

test "classify rejects each corrupted ELF magic byte before using ELFCLASS32" {
    const replacements = [_]u8{ 0x00, 'e', 'l', 'f' };
    inline for (0..elf_magic.len) |index| {
        const header = corruptMagic(index, replacements[index], elfclass32);
        try std.testing.expectEqual(mk_elfconfig.Outcome.not_elf, mk_elfconfig.classify(&header));
    }
}

test "classify rejects each corrupted ELF magic byte before using ELFCLASS64" {
    const replacements = [_]u8{ 0xff, 'X', 'x', '!' };
    inline for (0..elf_magic.len) |index| {
        const header = corruptMagic(index, replacements[index], elfclass64);
        try std.testing.expectEqual(mk_elfconfig.Outcome.not_elf, mk_elfconfig.classify(&header));
    }
}

test "classify rejects exact magic bytes in the wrong positions" {
    const headers = [_][16]u8{
        .{ 'E', 0x7f, 'L', 'F', elfclass32, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        .{ 0x7f, 'L', 'E', 'F', elfclass32, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        .{ 0x7f, 'E', 'F', 'L', elfclass32, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
    };
    for (headers) |header| {
        try std.testing.expectEqual(mk_elfconfig.Outcome.not_elf, mk_elfconfig.classify(&header));
    }
}

test "classify reaches class only after exact magic bytes match" {
    const elf32_header = baseHeader(elfclass32);
    const elf64_header = baseHeader(elfclass64);
    var invalid_class_header = baseHeader(0);

    try std.testing.expectEqual(mk_elfconfig.Outcome.elf32, mk_elfconfig.classify(&elf32_header));
    try std.testing.expectEqual(mk_elfconfig.Outcome.elf64, mk_elfconfig.classify(&elf64_header));
    try std.testing.expectEqual(mk_elfconfig.Outcome.invalid_class, mk_elfconfig.classify(&invalid_class_header));

    invalid_class_header[0] = 0;
    try std.testing.expectEqual(mk_elfconfig.Outcome.not_elf, mk_elfconfig.classify(&invalid_class_header));
}
