const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf32_header = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const elf64_header = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const not_elf_header = [_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const invalid_class_header = [_]u8{ 0x7f, 'E', 'L', 'F', 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const truncated_header = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 };

const Case = struct {
    input: []const u8,
    exit_code: u8,
    stdout: []const u8,
    stderr: []const u8,
};

const cases = [_]Case{
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
        .input = &truncated_header,
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
};

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

fn expectRun(case: Case) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(case.input, &stdout, &stderr);

    try std.testing.expectEqual(case.exit_code, exit_code);
    try std.testing.expectEqualStrings(case.stdout, stdout.list.items);
    try std.testing.expectEqualStrings(case.stderr, stderr.list.items);
}

test "runMkElfconfig produces identical isolated captures across repeated calls" {
    for (cases) |case| {
        try expectRun(case);
        try expectRun(case);
    }
}

test "mixed repeated public-entry calls do not leak previous output" {
    const sequence = [_]usize{ 0, 3, 1, 4, 2, 0, 4, 3 };

    for (sequence) |index| {
        try expectRun(cases[index]);
    }
}

test "first complete ident remains authoritative across repeated overlong calls" {
    const tail = elf64_header ++ not_elf_header ++ invalid_class_header;

    for (cases) |case| {
        if (case.input.len < 16) continue;

        const payload = case.input[0..16].* ++ tail;
        try expectRun(.{
            .input = &payload,
            .exit_code = case.exit_code,
            .stdout = case.stdout,
            .stderr = case.stderr,
        });
        try expectRun(.{
            .input = &payload,
            .exit_code = case.exit_code,
            .stdout = case.stdout,
            .stderr = case.stderr,
        });
    }
}
