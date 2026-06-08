const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass32: u8 = 1;
const elfclass64: u8 = 2;
const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const not_elf_text = "Error: not ELF\n";

const elf32_ident = [_]u8{
    0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0,
    0,    0,   0,   0,   0,          0, 0, 0,
};
const elf64_ident = [_]u8{
    0x7f, 'E', 'L', 'F', elfclass64, 1, 1, 0,
    0,    0,   0,   0,   0,          0, 0, 0,
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

fn magicMismatchIdent(magic_index: usize) [16]u8 {
    var ident = elf32_ident;
    switch (magic_index) {
        0 => ident[0] = 0,
        1 => ident[1] = 'X',
        2 => ident[2] = 'X',
        3 => ident[3] = 'X',
        else => unreachable,
    }
    return ident;
}

fn expectFdOutcome(
    input: []const u8,
    expected_exit_code: u8,
    expected_stdout: []const u8,
    expected_stderr: []const u8,
) !void {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();

    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "mk_elfconfig_input.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, input, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(expected_exit_code, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "fd-backed magic byte mismatches report not ELF" {
    for (0..4) |magic_index| {
        const ident = magicMismatchIdent(magic_index);
        try expectFdOutcome(&ident, 1, "", not_elf_text);
    }
}

test "fd-backed bad first magic ident remains authoritative before a later valid ident" {
    const bad_ident = magicMismatchIdent(2);
    var input: [32]u8 = undefined;
    @memcpy(input[0..16], &bad_ident);
    @memcpy(input[16..32], &elf64_ident);

    try expectFdOutcome(&input, 1, "", not_elf_text);
}

test "fd-backed exact magic controls select ELF class output" {
    try expectFdOutcome(&elf32_ident, 0, elfclass32_define, "");
    try expectFdOutcome(&elf64_ident, 0, elfclass64_define, "");
}
