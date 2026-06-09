const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass32: u8 = 1;
const elfclass64: u8 = 2;
const truncated_text = "Error: input truncated\n";
const not_elf_text = "Error: not ELF\n";
const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";

const elf32_ident = [_]u8{
    0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0,
    0,    0,   0,   0,   0,          0, 0, 0,
};

const elf64_ident = [_]u8{
    0x7f, 'E', 'L', 'F', elfclass64, 1, 1, 0,
    0,    0,   0,   0,   0,          0, 0, 0,
};

const invalid_ident = [_]u8{
    0x7f, 'E', 'L', 'F', 0xff, 1, 1, 0,
    0,    0,   0,   0,   0,    0, 0, 0,
};

const not_elf_ident = [_]u8{
    0x00, 'E', 'L', 'F', elfclass64, 1, 1, 0,
    0,    0,   0,   0,   0,          0, 0, 0,
};

const noisy_elf64_ident = [_]u8{
    0x7f, 'E',  'L',  'F',  elfclass64, 2,    3,    0xaa,
    0xbb, 0xcc, 0xdd, 0xee, 0xf0,       0x11, 0x22, 0x33,
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

fn expectSliceAndFdAgree(
    input: []const u8,
    expected_exit: u8,
    expected_stdout: []const u8,
    expected_stderr: []const u8,
) !void {
    var slice_stdout = try Capture.init(std.testing.allocator);
    defer slice_stdout.deinit();
    var slice_stderr = try Capture.init(std.testing.allocator);
    defer slice_stderr.deinit();

    const slice_exit = try mk_elfconfig.runMkElfconfig(input, &slice_stdout, &slice_stderr);

    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "input.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, input, 0);

    var fd_stdout = try Capture.init(std.testing.allocator);
    defer fd_stdout.deinit();
    var fd_stderr = try Capture.init(std.testing.allocator);
    defer fd_stderr.deinit();

    const fd_exit = try mk_elfconfig.runMkElfconfigFromFd(file.handle, &fd_stdout, &fd_stderr);

    try std.testing.expectEqual(slice_exit, fd_exit);
    try std.testing.expectEqualStrings(slice_stdout.list.items, fd_stdout.list.items);
    try std.testing.expectEqualStrings(slice_stderr.list.items, fd_stderr.list.items);

    try std.testing.expectEqual(expected_exit, slice_exit);
    try std.testing.expectEqualStrings(expected_stdout, slice_stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, slice_stderr.list.items);
}

test "slice and fd public entries agree on canonical outcomes" {
    try expectSliceAndFdAgree(&elf32_ident, 0, elfclass32_define, "");
    try expectSliceAndFdAgree(&elf64_ident, 0, elfclass64_define, "");
    try expectSliceAndFdAgree(elf32_ident[0..8], 1, "", truncated_text);
    try expectSliceAndFdAgree(&not_elf_ident, 1, "", not_elf_text);
    try expectSliceAndFdAgree(&invalid_ident, 1, "", "");
}

test "slice and fd public entries agree on first ident authority" {
    const elf32_then_not_elf = elf32_ident ++ not_elf_ident;
    const elf64_then_invalid = elf64_ident ++ invalid_ident;
    const invalid_then_elf64 = invalid_ident ++ elf64_ident;
    const not_elf_then_elf32 = not_elf_ident ++ elf32_ident;

    try expectSliceAndFdAgree(&elf32_then_not_elf, 0, elfclass32_define, "");
    try expectSliceAndFdAgree(&elf64_then_invalid, 0, elfclass64_define, "");
    try expectSliceAndFdAgree(&invalid_then_elf64, 1, "", "");
    try expectSliceAndFdAgree(&not_elf_then_elf32, 1, "", not_elf_text);
}

test "slice and fd public entries agree on metadata noise and short prefixes" {
    try expectSliceAndFdAgree(&noisy_elf64_ident, 0, elfclass64_define, "");

    var prefix: [15]u8 = undefined;
    @memcpy(&prefix, elf64_ident[0..15]);
    try expectSliceAndFdAgree(&prefix, 1, "", truncated_text);
}
