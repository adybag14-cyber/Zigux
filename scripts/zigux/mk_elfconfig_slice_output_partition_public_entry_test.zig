const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
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

fn expectRun(
    input: []const u8,
    expected_exit: u8,
    expected_stdout: []const u8,
    expected_stderr: []const u8,
) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
    try std.testing.expectEqual(expected_exit, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "slice public entry keeps success output on stdout only" {
    try expectRun(&[_]u8{
        0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    }, 0, elfclass32_define, "");
    try expectRun(&[_]u8{
        0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    }, 0, elfclass64_define, "");
}

test "slice public entry keeps diagnostics on stderr only" {
    try expectRun(&[_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0 }, 1, "", truncated_text);
    try expectRun(&[_]u8{
        0, 'E', 'L', 'F', 1, 1, 1, 0,
        0, 0,   0,   0,   0, 0, 0, 0,
    }, 1, "", not_elf_text);
}

test "slice public entry leaves invalid class silent" {
    try expectRun(&[_]u8{
        0x7f, 'E', 'L', 'F', 0xff, 1, 1, 0,
        0,    0,   0,   0,   0,    0, 0, 0,
    }, 1, "", "");
}

test "slice public entry output channels follow the first ident" {
    const elf64_tail = [_]u8{
        0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    };
    const not_elf_tail = [_]u8{
        0, 'E', 'L', 'F', 1, 1, 1, 0,
        0, 0,   0,   0,   0, 0, 0, 0,
    };
    const invalid_tail = [_]u8{
        0x7f, 'E', 'L', 'F', 0, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    };

    const elf32_then_not_elf = [_]u8{
        0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    } ++ not_elf_tail;
    const not_elf_then_elf64 = not_elf_tail ++ elf64_tail;
    const invalid_then_elf64 = invalid_tail ++ elf64_tail;

    try expectRun(&elf32_then_not_elf, 0, elfclass32_define, "");
    try expectRun(&not_elf_then_elf64, 1, "", not_elf_text);
    try expectRun(&invalid_then_elf64, 1, "", "");
}
