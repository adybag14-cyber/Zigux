const std = @import("std");
const mk = @import("mk_elfconfig.zig");

const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const truncated_text = "Error: input truncated\n";
const not_elf_text = "Error: not ELF\n";

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 64),
            .allocator = allocator,
        };
    }

    pub fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn reset(self: *@This()) void {
        self.list.clearRetainingCapacity();
    }

    pub fn writeAll(self: *@This(), bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }
};

fn expectCursor(file: anytype, expected: usize) !void {
    try std.testing.expectEqual(
        @as(usize, expected),
        std.os.linux.lseek(file.handle, 0, std.posix.SEEK.CUR),
    );
}

test "fd-backed trailing 32-bit ELF input leaves only a truncated tail after the hidden same-class header is consumed" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "elf32_trailing_same_class_tail.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &[_]u8{
        0x7f, 'E',  'L',  'F',  1,   1,   1,   0,
        0,    0,    0,    0,    0,   0,   0,   0,
        0xaa, 0xbb, 0xcc, 0x7f, 'E', 'L', 'F', 1,
        1,    1,    0,    0,    0,   0,   0,   0,
        0,    0,    0,
    }, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const first_exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), first_exit_code);
    try std.testing.expectEqualStrings(elfclass32_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
    try expectCursor(file, 16);

    stdout.reset();
    stderr.reset();
    const second_exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), second_exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
    try expectCursor(file, 32);

    stdout.reset();
    stderr.reset();
    const third_exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), third_exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
    try expectCursor(file, 35);
}

test "fd-backed trailing 64-bit ELF input leaves only a truncated tail after the hidden same-class header is consumed" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "elf64_trailing_same_class_tail.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &[_]u8{
        0x7f, 'E',  'L',  'F',  2,   1,   1,   0,
        0,    0,    0,    0,    0,   0,   0,   0,
        0xaa, 0xbb, 0xcc, 0x7f, 'E', 'L', 'F', 2,
        1,    1,    0,    0,    0,   0,   0,   0,
        0,    0,    0,
    }, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const first_exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), first_exit_code);
    try std.testing.expectEqualStrings(elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
    try expectCursor(file, 16);

    stdout.reset();
    stderr.reset();
    const second_exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), second_exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
    try expectCursor(file, 32);

    stdout.reset();
    stderr.reset();
    const third_exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), third_exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
    try expectCursor(file, 35);
}

test "fd-backed trailing not-ELF input leaves only a truncated tail after the hidden same-class header is consumed" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "not_elf_trailing_same_class_tail.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &[_]u8{
        0x00, 'E',  'L',  'F',  1,   1,   1,   0,
        0,    0,    0,    0,    0,   0,   0,   0,
        0xaa, 0xbb, 0xcc, 0x00, 'E', 'L', 'F', 1,
        1,    1,    0,    0,    0,   0,   0,   0,
        0,    0,    0,
    }, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const first_exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), first_exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
    try expectCursor(file, 16);

    stdout.reset();
    stderr.reset();
    const second_exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), second_exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
    try expectCursor(file, 32);

    stdout.reset();
    stderr.reset();
    const third_exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), third_exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
    try expectCursor(file, 35);
}
