const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf32_ident = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const elf64_ident = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const invalid_class_ident = [_]u8{ 0x7f, 'E', 'L', 'F', 9, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const not_elf_ident = [_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elf64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
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

fn appendIdent(bytes: *std.ArrayList(u8), ident: []const u8) !void {
    try bytes.appendSlice(std.testing.allocator, ident);
}

fn runFdCase(name: []const u8, input: []const u8, expected_stdout: []const u8, expected_stderr: []const u8, expected_exit: u8) !void {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, name, .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, input, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(expected_exit, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "fd-backed first ELF32 ident ignores later success and failure shaped tails" {
    var bytes = try std.ArrayList(u8).initCapacity(std.testing.allocator, 64);
    defer bytes.deinit(std.testing.allocator);
    try appendIdent(&bytes, &elf32_ident);
    try appendIdent(&bytes, &elf64_ident);
    try appendIdent(&bytes, &not_elf_ident);
    try appendIdent(&bytes, &invalid_class_ident);

    try runFdCase("first_elf32_tail.bin", bytes.items, elf32_define, "", 0);
}

test "fd-backed first ELF64 ident ignores later ELF32 and non-ELF tails" {
    var bytes = try std.ArrayList(u8).initCapacity(std.testing.allocator, 48);
    defer bytes.deinit(std.testing.allocator);
    try appendIdent(&bytes, &elf64_ident);
    try appendIdent(&bytes, &elf32_ident);
    try appendIdent(&bytes, &not_elf_ident);

    try runFdCase("first_elf64_tail.bin", bytes.items, elf64_define, "", 0);
}

test "fd-backed invalid first class stays silent despite later valid ELF64" {
    var bytes = try std.ArrayList(u8).initCapacity(std.testing.allocator, 32);
    defer bytes.deinit(std.testing.allocator);
    try appendIdent(&bytes, &invalid_class_ident);
    try appendIdent(&bytes, &elf64_ident);

    try runFdCase("first_invalid_tail.bin", bytes.items, "", "", 1);
}

test "fd-backed non-ELF first ident reports not ELF despite later valid ELF32" {
    var bytes = try std.ArrayList(u8).initCapacity(std.testing.allocator, 32);
    defer bytes.deinit(std.testing.allocator);
    try appendIdent(&bytes, &not_elf_ident);
    try appendIdent(&bytes, &elf32_ident);

    try runFdCase("first_not_elf_tail.bin", bytes.items, "", not_elf_text, 1);
}
