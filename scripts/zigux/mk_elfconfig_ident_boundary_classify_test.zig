const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const Outcome = mk_elfconfig.Outcome;
const ei_nident: usize = 16;
const elfclass32: u8 = 1;
const elfclass64: u8 = 2;

fn elfHeader(class: u8) [ei_nident]u8 {
    return [_]u8{ 0x7f, 'E', 'L', 'F', class, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
}

fn nonElfHeader() [ei_nident]u8 {
    var header = elfHeader(elfclass32);
    header[0] = 0;
    return header;
}

fn expectClassifies(expected: Outcome, bytes: []const u8) !void {
    try std.testing.expectEqual(expected, mk_elfconfig.classify(bytes));
}

test "classify keeps every prefix below EI_NIDENT truncated" {
    const success_shaped = elfHeader(elfclass32);
    const bad_magic = nonElfHeader();
    const bad_class = elfHeader(0);

    for (0..ei_nident) |len| {
        try expectClassifies(.truncated, success_shaped[0..len]);
        try expectClassifies(.truncated, bad_magic[0..len]);
        try expectClassifies(.truncated, bad_class[0..len]);
    }
}

test "classify reaches magic and class only at the exact ident boundary" {
    const elf32 = elfHeader(elfclass32);
    const elf64 = elfHeader(elfclass64);
    const bad_magic = nonElfHeader();
    const bad_class = elfHeader(255);

    try expectClassifies(.elf32, &elf32);
    try expectClassifies(.elf64, &elf64);
    try expectClassifies(.not_elf, &bad_magic);
    try expectClassifies(.invalid_class, &bad_class);
}

test "classify ignores trailing bytes after the first ident" {
    const first_elf32 = elfHeader(elfclass32);
    const first_elf64 = elfHeader(elfclass64);
    const first_bad_magic = nonElfHeader();
    const first_bad_class = elfHeader(3);
    const later_elf64 = elfHeader(elfclass64);
    const later_bad_magic = nonElfHeader();

    var elf32_then_bad_magic: [ei_nident * 2]u8 = undefined;
    @memcpy(elf32_then_bad_magic[0..ei_nident], &first_elf32);
    @memcpy(elf32_then_bad_magic[ei_nident..], &later_bad_magic);
    try expectClassifies(.elf32, &elf32_then_bad_magic);

    var elf64_then_bad_class: [ei_nident * 2]u8 = undefined;
    @memcpy(elf64_then_bad_class[0..ei_nident], &first_elf64);
    @memcpy(elf64_then_bad_class[ei_nident..], &first_bad_class);
    try expectClassifies(.elf64, &elf64_then_bad_class);

    var bad_magic_then_elf64: [ei_nident * 2]u8 = undefined;
    @memcpy(bad_magic_then_elf64[0..ei_nident], &first_bad_magic);
    @memcpy(bad_magic_then_elf64[ei_nident..], &later_elf64);
    try expectClassifies(.not_elf, &bad_magic_then_elf64);

    var bad_class_then_elf64: [ei_nident * 2]u8 = undefined;
    @memcpy(bad_class_then_elf64[0..ei_nident], &first_bad_class);
    @memcpy(bad_class_then_elf64[ei_nident..], &later_elf64);
    try expectClassifies(.invalid_class, &bad_class_then_elf64);
}
