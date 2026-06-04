const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elf64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
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

fn expectRun(input: []const u8, expected_stdout: []const u8, expected_stderr: []const u8, expected_code: u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
    try std.testing.expectEqual(expected_code, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

fn validIdent(class: u8, byte15: u8) [16]u8 {
    return .{ 0x7f, 'E', 'L', 'F', class, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, byte15 };
}

test "public entry treats the sixteenth byte as the ident boundary" {
    const elf32_ident = validIdent(1, 0xa5);
    const elf64_ident = validIdent(2, 0x5a);

    try std.testing.expectEqual(mk_elfconfig.Outcome.truncated, mk_elfconfig.classify(elf32_ident[0..15]));
    try expectRun(elf32_ident[0..15], "", truncated_text, 1);
    try expectRun(&elf32_ident, elf32_define, "", 0);

    try std.testing.expectEqual(mk_elfconfig.Outcome.truncated, mk_elfconfig.classify(elf64_ident[0..15]));
    try expectRun(elf64_ident[0..15], "", truncated_text, 1);
    try expectRun(&elf64_ident, elf64_define, "", 0);
}

test "public entry ignores valid ELF tails after a complete invalid-class ident" {
    const invalid_ident = validIdent(0xfe, 0x11);
    const elf32_tail = validIdent(1, 0x22);
    const elf64_tail = validIdent(2, 0x33);

    var input = invalid_ident ++ elf32_tail ++ elf64_tail;
    try std.testing.expectEqual(mk_elfconfig.Outcome.invalid_class, mk_elfconfig.classify(&input));
    try expectRun(&input, "", "", 1);
}

test "public entry ignores failure-shaped tails after a complete valid ident" {
    const elf32_ident = validIdent(1, 0x44);
    const elf64_ident = validIdent(2, 0x55);
    const invalid_tail = validIdent(0, 0x66);
    const non_elf_tail = [_]u8{ 0, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

    var elf32_input = elf32_ident ++ invalid_tail ++ non_elf_tail;
    try std.testing.expectEqual(mk_elfconfig.Outcome.elf32, mk_elfconfig.classify(&elf32_input));
    try expectRun(&elf32_input, elf32_define, "", 0);

    var elf64_input = elf64_ident ++ non_elf_tail ++ invalid_tail;
    try std.testing.expectEqual(mk_elfconfig.Outcome.elf64, mk_elfconfig.classify(&elf64_input));
    try expectRun(&elf64_input, elf64_define, "", 0);
}

test "public entry ignores success-shaped tails after a complete non-ELF ident" {
    const non_elf_ident = [_]u8{ 0, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const elf32_tail = validIdent(1, 0x77);
    const elf64_tail = validIdent(2, 0x88);

    var input = non_elf_ident ++ elf32_tail ++ elf64_tail;
    try std.testing.expectEqual(mk_elfconfig.Outcome.not_elf, mk_elfconfig.classify(&input));
    try expectRun(&input, "", not_elf_text, 1);
}
