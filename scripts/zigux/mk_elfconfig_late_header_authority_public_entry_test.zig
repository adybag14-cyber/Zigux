const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";

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

test "late ELF-looking headers do not override first ELF class" {
    const first_elf32 = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const late_elf64 = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0xaa, 0xbb, 0xcc, 0xdd, 0, 0, 0, 0 };
    const late_invalid = [_]u8{ 0x7f, 'E', 'L', 'F', 9, 1, 1, 0, 0xee, 0xff, 0x11, 0x22, 0, 0, 0, 0 };
    const input = first_elf32 ++ late_elf64 ++ [_]u8{ 'i', 'g', 'n', 'o', 'r', 'e', 'd' } ++ late_invalid;

    try expectRun(&input, 0, elfclass32_define, "");
}

test "late valid ELF header cannot rescue an invalid first class" {
    const first_invalid = [_]u8{ 0x7f, 'E', 'L', 'F', 9, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const late_elf64 = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0xaa, 0xbb, 0xcc, 0xdd, 0, 0, 0, 0 };
    const late_elf32 = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0xee, 0xff, 0x11, 0x22, 0, 0, 0, 0 };
    const input = first_invalid ++ [_]u8{ 'p', 'a', 'd', 'd', 'i', 'n', 'g' } ++ late_elf64 ++ late_elf32;

    try expectRun(&input, 1, "", "");
}

test "late ELF header cannot rescue non-ELF first header" {
    const first_not_elf = [_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const late_elf64 = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0xaa, 0xbb, 0xcc, 0xdd, 0, 0, 0, 0 };
    const input = first_not_elf ++ [_]u8{ 'p', 'a', 'd', 'd', 'i', 'n', 'g' } ++ late_elf64;

    try expectRun(&input, 1, "", "Error: not ELF\n");
}
