const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf32_header = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const elf64_header = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const invalid_class_header = [_]u8{ 0x7f, 'E', 'L', 'F', 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const not_elf_header = [_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const truncated_prefix = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0 };

const CallExpectation = struct {
    input: []const u8,
    exit_code: u8,
    stdout: []const u8,
    stderr: []const u8,
};

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 128),
            .allocator = allocator,
        };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    fn reset(self: *@This()) void {
        self.list.clearRetainingCapacity();
    }

    pub fn writeAll(self: *@This(), bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }
};

fn expectRepeatedRun(sequence: []const CallExpectation) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    for (sequence) |expected| {
        stdout.reset();
        stderr.reset();
        const exit_code = try mk_elfconfig.runMkElfconfig(expected.input, &stdout, &stderr);
        try std.testing.expectEqual(expected.exit_code, exit_code);
        try std.testing.expectEqualStrings(expected.stdout, stdout.list.items);
        try std.testing.expectEqualStrings(expected.stderr, stderr.list.items);
    }
}

test "repeated runMkElfconfig calls keep success outputs independent" {
    try expectRepeatedRun(&[_]CallExpectation{
        .{
            .input = &elf32_header,
            .exit_code = 0,
            .stdout = "#define KERNEL_ELFCLASS ELFCLASS32\n",
            .stderr = "",
        },
        .{
            .input = &elf64_header,
            .exit_code = 0,
            .stdout = "#define KERNEL_ELFCLASS ELFCLASS64\n",
            .stderr = "",
        },
        .{
            .input = &elf32_header,
            .exit_code = 0,
            .stdout = "#define KERNEL_ELFCLASS ELFCLASS32\n",
            .stderr = "",
        },
    });
}

test "repeated runMkElfconfig calls reset diagnostics between failures" {
    try expectRepeatedRun(&[_]CallExpectation{
        .{
            .input = &truncated_prefix,
            .exit_code = 1,
            .stdout = "",
            .stderr = "Error: input truncated\n",
        },
        .{
            .input = &not_elf_header,
            .exit_code = 1,
            .stdout = "",
            .stderr = "Error: not ELF\n",
        },
        .{
            .input = &invalid_class_header,
            .exit_code = 1,
            .stdout = "",
            .stderr = "",
        },
    });
}

test "repeated runMkElfconfig calls can recover after failures" {
    try expectRepeatedRun(&[_]CallExpectation{
        .{
            .input = &truncated_prefix,
            .exit_code = 1,
            .stdout = "",
            .stderr = "Error: input truncated\n",
        },
        .{
            .input = &elf64_header,
            .exit_code = 0,
            .stdout = "#define KERNEL_ELFCLASS ELFCLASS64\n",
            .stderr = "",
        },
        .{
            .input = &not_elf_header,
            .exit_code = 1,
            .stdout = "",
            .stderr = "Error: not ELF\n",
        },
        .{
            .input = &elf32_header,
            .exit_code = 0,
            .stdout = "#define KERNEL_ELFCLASS ELFCLASS32\n",
            .stderr = "",
        },
    });
}
