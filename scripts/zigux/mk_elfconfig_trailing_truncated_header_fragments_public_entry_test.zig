const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf_magic = [_]u8{ 0x7f, 'E', 'L', 'F' };
const elfclass32: u8 = 1;
const elfclass64: u8 = 2;
const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const truncated_text = "Error: input truncated\n";

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

fn expectRun(input: []const u8, expected_exit: u8, expected_stdout: []const u8, expected_stderr: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
    try std.testing.expectEqual(expected_exit, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "public entry keeps ELF32 first header before trailing truncated ELF64 fragment" {
    try expectRun(&[_]u8{
        elf_magic[0], elf_magic[1], elf_magic[2], elf_magic[3], elfclass32, 1, 1, 0,
        0,            0,            0,            0,            0,          0, 0, 0,
        elf_magic[0], elf_magic[1], elf_magic[2], elf_magic[3], elfclass64, 1, 1,
    }, 0, elfclass32_define, "");
}

test "public entry keeps ELF64 first header before trailing truncated ELF32 fragment" {
    try expectRun(&[_]u8{
        elf_magic[0], elf_magic[1], elf_magic[2], elf_magic[3], elfclass64, 1, 1, 0,
        0,            0,            0,            0,            0,          0, 0, 0,
        elf_magic[0], elf_magic[1], elf_magic[2], elf_magic[3], elfclass32,
    }, 0, elfclass64_define, "");
}

test "public entry keeps invalid class first header before trailing truncated valid fragment" {
    try expectRun(&[_]u8{
        elf_magic[0], elf_magic[1], elf_magic[2], elf_magic[3], 3,          1, 1, 0,
        0,            0,            0,            0,            0,          0, 0, 0,
        elf_magic[0], elf_magic[1], elf_magic[2], elf_magic[3], elfclass32, 1,
    }, 1, "", "");
}

test "public entry reports truncated first fragment before later valid-looking fragment" {
    try expectRun(&[_]u8{
        elf_magic[0], elf_magic[1], elf_magic[2], elf_magic[3], elfclass32, 1, 1,
        elf_magic[0], elf_magic[1], elf_magic[2], elf_magic[3], elfclass64, 1, 1,
        0,
    }, 1, "", truncated_text);
}
