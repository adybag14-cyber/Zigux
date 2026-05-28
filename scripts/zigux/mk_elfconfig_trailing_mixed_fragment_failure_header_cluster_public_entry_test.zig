const std = @import("std");
const mk = @import("mk_elfconfig.zig");

const elf32_header = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const elf64_header = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const invalid_class_header = [_]u8{ 0x7f, 'E', 'L', 'F', 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const not_elf_header = [_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

const trailing_fragment = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0 };
const failure_fragment = [_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1 };

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

    const exit_code = try mk.runMkElfconfig(bytes, &stdout, &stderr);
    try std.testing.expectEqual(expected_exit, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "first elf32 header wins over trailing mixed fragment failure header cluster" {
    const stdin_bytes = elf32_header ++ trailing_fragment ++ invalid_class_header ++ elf64_header;
    try expectRun(&stdin_bytes, 0, "#define KERNEL_ELFCLASS ELFCLASS32\n", "");
}

test "first elf64 header wins over trailing mixed fragment failure header cluster" {
    const stdin_bytes = elf64_header ++ failure_fragment ++ not_elf_header ++ elf32_header;
    try expectRun(&stdin_bytes, 0, "#define KERNEL_ELFCLASS ELFCLASS64\n", "");
}

test "leading invalid-class outcome ignores trailing mixed fragment failure header cluster" {
    const stdin_bytes = invalid_class_header ++ trailing_fragment ++ not_elf_header ++ elf64_header;
    try expectRun(&stdin_bytes, 1, "", "");
}

test "leading non-elf outcome ignores trailing mixed fragment failure header cluster" {
    const stdin_bytes = not_elf_header ++ failure_fragment ++ invalid_class_header ++ elf32_header;
    try expectRun(&stdin_bytes, 1, "", "Error: not ELF\n");
}
