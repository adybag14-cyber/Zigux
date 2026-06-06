const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf32_header = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const elf64_header = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const invalid_class_header = [_]u8{ 0x7f, 'E', 'L', 'F', 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const not_elf_header = [_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

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

fn expectRun(bytes: []const u8, expected_exit: u8, expected_stdout: []const u8, expected_stderr: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(bytes, &stdout, &stderr);
    try std.testing.expectEqual(expected_exit, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "slice-backed public entry keeps first ident authoritative before trailing bytes" {
    const elf32_then_elf64 = elf32_header ++ elf64_header;
    try expectRun(
        &elf32_then_elf64,
        0,
        "#define KERNEL_ELFCLASS ELFCLASS32\n",
        "",
    );

    const elf64_then_not_elf = elf64_header ++ not_elf_header;
    try expectRun(
        &elf64_then_not_elf,
        0,
        "#define KERNEL_ELFCLASS ELFCLASS64\n",
        "",
    );

    const invalid_class_then_elf32 = invalid_class_header ++ elf32_header;
    try expectRun(
        &invalid_class_then_elf32,
        1,
        "",
        "",
    );

    const not_elf_then_elf64 = not_elf_header ++ elf64_header;
    try expectRun(
        &not_elf_then_elf64,
        1,
        "",
        "Error: not ELF\n",
    );
}
