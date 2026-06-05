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

fn expectFdRun(
    name: []const u8,
    bytes: []const u8,
    expected_exit: u8,
    expected_stdout: []const u8,
    expected_stderr: []const u8,
) !void {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, name, .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, bytes, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(expected_exit, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "fd public entry keeps success output on stdout only" {
    try expectFdRun(
        "elf32_with_error_tail.bin",
        &[_]u8{
            0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
            0,    0,   0,   0,   0, 0, 0, 0,
            0x00, 'E', 'L', 'F', 1, 1, 1, 0,
        },
        0,
        elfclass32_define,
        "",
    );
    try expectFdRun(
        "elf64_with_silent_tail.bin",
        &[_]u8{
            0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
            0,    0,   0,   0,   0, 0, 0, 0,
            0x7f, 'E', 'L', 'F', 9, 1, 1, 0,
        },
        0,
        elfclass64_define,
        "",
    );
}

test "fd public entry keeps diagnostics on stderr only" {
    try expectFdRun(
        "truncated_fd_input.bin",
        &[_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0 },
        1,
        "",
        truncated_text,
    );
    try expectFdRun(
        "not_elf_fd_input.bin",
        &[_]u8{
            0x00, 'E', 'L', 'F', 1, 1, 1, 0,
            0,    0,   0,   0,   0, 0, 0, 0,
            0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
        },
        1,
        "",
        not_elf_text,
    );
}

test "fd public entry keeps invalid class silent on both streams" {
    try expectFdRun(
        "invalid_class_with_success_tail.bin",
        &[_]u8{
            0x7f, 'E', 'L', 'F', 0, 1, 1, 0,
            0,    0,   0,   0,   0, 0, 0, 0,
            0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
        },
        1,
        "",
        "",
    );
    try expectFdRun(
        "invalid_high_class_with_error_tail.bin",
        &[_]u8{
            0x7f, 'E', 'L', 'F', 255, 1, 1, 0,
            0,    0,   0,   0,   0,   0, 0, 0,
            0x00, 'E', 'L', 'F', 1,   1, 1, 0,
        },
        1,
        "",
        "",
    );
}
