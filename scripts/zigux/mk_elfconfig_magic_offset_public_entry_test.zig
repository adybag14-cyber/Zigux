const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elf64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
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

fn expectRun(
    stdin_bytes: []const u8,
    expected_exit: u8,
    expected_stdout: []const u8,
    expected_stderr: []const u8,
) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(stdin_bytes, &stdout, &stderr);
    try std.testing.expectEqual(expected_exit, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "shifted ELF magic is not accepted as a header" {
    const shifted_magic = [_]u8{ 0, 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 };

    try std.testing.expectEqual(.not_elf, mk_elfconfig.classify(&shifted_magic));
    try expectRun(&shifted_magic, 1, "", not_elf_text);
}

test "tail-embedded ELF magic cannot override byte zero mismatch" {
    const embedded_magic = [_]u8{ 0x7f, 'X', 'E', 'L', 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0 };

    try std.testing.expectEqual(.not_elf, mk_elfconfig.classify(&embedded_magic));
    try expectRun(&embedded_magic, 1, "", not_elf_text);
}

test "trailing valid ELF header is ignored after a non-ELF first header" {
    const packet = [_]u8{
        0,    'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    };

    try std.testing.expectEqual(.not_elf, mk_elfconfig.classify(&packet));
    try expectRun(&packet, 1, "", not_elf_text);
}

test "byte-zero magic still uses EI_CLASS even when trailing bytes look valid" {
    const invalid_class_with_trailing_elf = [_]u8{
        0x7f, 'E', 'L', 'F', 0xff, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0x7f, 'E', 'L', 'F', 1,    1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    };

    try std.testing.expectEqual(.invalid_class, mk_elfconfig.classify(&invalid_class_with_trailing_elf));
    try expectRun(&invalid_class_with_trailing_elf, 1, "", "");
}

test "byte-zero ELF magic still emits normal success outputs" {
    const elf32 = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const elf64 = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

    try expectRun(&elf32, 0, elf32_define, "");
    try expectRun(&elf64, 0, elf64_define, "");
}
