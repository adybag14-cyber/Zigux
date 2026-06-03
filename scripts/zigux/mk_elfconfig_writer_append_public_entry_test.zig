const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator, prefix: []const u8) !@This() {
        var list = try std.ArrayList(u8).initCapacity(allocator, 128);
        try list.appendSlice(allocator, prefix);
        return .{
            .list = list,
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

fn expectAppendedRun(
    input: []const u8,
    expected_exit_code: u8,
    stdout_prefix: []const u8,
    stderr_prefix: []const u8,
    expected_stdout: []const u8,
    expected_stderr: []const u8,
) !void {
    var stdout = try Capture.init(std.testing.allocator, stdout_prefix);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator, stderr_prefix);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
    try std.testing.expectEqual(expected_exit_code, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "public entry appends ELF success output to existing stdout" {
    const elf32_header = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    try expectAppendedRun(
        &elf32_header,
        0,
        "stdout-prefix\n",
        "stderr-prefix\n",
        "stdout-prefix\n#define KERNEL_ELFCLASS ELFCLASS32\n",
        "stderr-prefix\n",
    );

    const elf64_header = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    try expectAppendedRun(
        &elf64_header,
        0,
        "already-written:",
        "",
        "already-written:#define KERNEL_ELFCLASS ELFCLASS64\n",
        "",
    );
}

test "public entry appends failure diagnostics to existing stderr" {
    const truncated_prefix = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0 };
    try expectAppendedRun(
        &truncated_prefix,
        1,
        "",
        "stderr-prefix\n",
        "",
        "stderr-prefix\nError: input truncated\n",
    );

    const not_elf_header = [_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    try expectAppendedRun(
        &not_elf_header,
        1,
        "stdout-prefix\n",
        "diagnostic:",
        "stdout-prefix\n",
        "diagnostic:Error: not ELF\n",
    );
}

test "public entry invalid class preserves both existing writers silently" {
    const invalid_class_header = [_]u8{ 0x7f, 'E', 'L', 'F', 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    try expectAppendedRun(
        &invalid_class_header,
        1,
        "stdout-prefix\n",
        "stderr-prefix\n",
        "stdout-prefix\n",
        "stderr-prefix\n",
    );
}
