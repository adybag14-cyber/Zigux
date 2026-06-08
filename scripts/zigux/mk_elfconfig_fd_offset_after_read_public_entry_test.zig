const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const elf32_ident = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const elf64_ident = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const invalid_class_ident = [_]u8{ 0x7f, 'E', 'L', 'F', 0xff, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const not_elf_ident = [_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

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

fn writeCaseFile(
    temp_dir: *std.testing.TmpDir,
    name: []const u8,
    first_ident: []const u8,
    tail: []const u8,
) !std.Io.File {
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, name, .{ .read = true });
    try file.writePositionalAll(io, first_ident, 0);
    try file.writePositionalAll(io, tail, first_ident.len);
    return file;
}

fn runFdCase(file: std.Io.File) !struct { code: u8, stdout: Capture, stderr: Capture } {
    var stdout = try Capture.init(std.testing.allocator);
    errdefer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    errdefer stderr.deinit();

    const code = try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    return .{ .code = code, .stdout = stdout, .stderr = stderr };
}

fn expectRemainingTail(file: std.Io.File, expected_tail: []const u8) !void {
    var actual_tail: [64]u8 = undefined;
    const read_len = try std.posix.read(file.handle, actual_tail[0..]);
    try std.testing.expectEqual(expected_tail.len, read_len);
    try std.testing.expectEqualSlices(u8, expected_tail, actual_tail[0..read_len]);

    const eof_len = try std.posix.read(file.handle, actual_tail[0..]);
    try std.testing.expectEqual(@as(usize, 0), eof_len);
}

test "fd-backed ELF32 success leaves trailing ELF64 ident unread" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const file = try writeCaseFile(&temp_dir, "elf32-then-elf64.bin", &elf32_ident, &elf64_ident);
    defer file.close(std.testing.io);

    var result = try runFdCase(file);
    defer result.stdout.deinit();
    defer result.stderr.deinit();

    try std.testing.expectEqual(@as(u8, 0), result.code);
    try std.testing.expectEqualStrings(elfclass32_define, result.stdout.list.items);
    try std.testing.expectEqualStrings("", result.stderr.list.items);
    try expectRemainingTail(file, &elf64_ident);
}

test "fd-backed invalid class leaves valid ELF32 tail unread" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const file = try writeCaseFile(&temp_dir, "invalid-then-elf32.bin", &invalid_class_ident, &elf32_ident);
    defer file.close(std.testing.io);

    var result = try runFdCase(file);
    defer result.stdout.deinit();
    defer result.stderr.deinit();

    try std.testing.expectEqual(@as(u8, 1), result.code);
    try std.testing.expectEqualStrings("", result.stdout.list.items);
    try std.testing.expectEqualStrings("", result.stderr.list.items);
    try expectRemainingTail(file, &elf32_ident);
}

test "fd-backed non-ELF leaves invalid-class tail unread" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const file = try writeCaseFile(&temp_dir, "not-elf-then-invalid.bin", &not_elf_ident, &invalid_class_ident);
    defer file.close(std.testing.io);

    var result = try runFdCase(file);
    defer result.stdout.deinit();
    defer result.stderr.deinit();

    try std.testing.expectEqual(@as(u8, 1), result.code);
    try std.testing.expectEqualStrings("", result.stdout.list.items);
    try std.testing.expectEqualStrings("Error: not ELF\n", result.stderr.list.items);
    try expectRemainingTail(file, &invalid_class_ident);
}
