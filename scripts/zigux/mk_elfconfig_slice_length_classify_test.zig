const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf32_ident = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const elf64_ident = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const invalid_class_ident = [_]u8{ 0x7f, 'E', 'L', 'F', 255, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const non_elf_ident = [_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

test "classify treats fifteen bytes as truncated even when the prefix is otherwise ELF32" {
    try std.testing.expectEqual(
        mk_elfconfig.Outcome.truncated,
        mk_elfconfig.classify(elf32_ident[0..15]),
    );
}

test "classify accepts the exact sixteenth byte as the slice-backed boundary" {
    try std.testing.expectEqual(
        mk_elfconfig.Outcome.elf32,
        mk_elfconfig.classify(&elf32_ident),
    );
}

test "classify ignores bytes after a complete ELF64 ident" {
    const bytes = elf64_ident ++ non_elf_ident ++ [_]u8{ 0, 1, 2, 3 };
    try std.testing.expectEqual(
        mk_elfconfig.Outcome.elf64,
        mk_elfconfig.classify(&bytes),
    );
}

test "classify keeps a complete non-ELF first ident authoritative before later ELF bytes" {
    const bytes = non_elf_ident ++ elf64_ident;
    try std.testing.expectEqual(
        mk_elfconfig.Outcome.not_elf,
        mk_elfconfig.classify(&bytes),
    );
}

test "classify keeps invalid class authoritative before later valid ELF32 bytes" {
    const bytes = invalid_class_ident ++ elf32_ident;
    try std.testing.expectEqual(
        mk_elfconfig.Outcome.invalid_class,
        mk_elfconfig.classify(&bytes),
    );
}

test "classify still reports truncated for a non-empty prefix shorter than EI_NIDENT" {
    const short_prefix = [_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 };
    try std.testing.expectEqual(
        mk_elfconfig.Outcome.truncated,
        mk_elfconfig.classify(&short_prefix),
    );
}
