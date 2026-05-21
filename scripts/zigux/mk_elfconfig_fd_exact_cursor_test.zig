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

test "fd-backed exact empty input leaves the cursor at zero" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "empty_exact.bin", .{ .read = true });
    defer file.close(io);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
    try expectCursor(file, 0);
}

test "fd-backed exact truncated input leaves the cursor at the truncated byte count" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "truncated_exact.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &[_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0 }, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
    try expectCursor(file, 8);
}

test "fd-backed one-byte-short input leaves the cursor at fifteen bytes" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "near_full_exact.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &[_]u8{
        0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0,
    }, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
    try expectCursor(file, 15);
}

test "fd-backed exact 32-bit ELF input leaves the cursor at the full header" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "elf32_exact.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &[_]u8{
        0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    }, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(elfclass32_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
    try expectCursor(file, 16);
}

test "fd-backed exact 64-bit ELF input leaves the cursor at the full header" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "elf64_exact.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &[_]u8{
        0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    }, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
    try expectCursor(file, 16);
}

test "fd-backed exact invalid-class input leaves the cursor at the full header" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "invalid_class_exact.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &[_]u8{
        0x7f, 'E', 'L', 'F', 3, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    }, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
    try expectCursor(file, 16);
}

test "fd-backed exact non-ELF input leaves the cursor at the full header" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "not_elf_exact.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &[_]u8{
        0x00, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    }, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
    try expectCursor(file, 16);
}

test "fd-backed exact non-ELF input with trailing bytes still leaves the cursor at the full header" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "not_elf_exact_trailing.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &[_]u8{
        0x00, 'E',  'L',  'F',  1, 1, 1, 0,
        0,    0,    0,    0,    0, 0, 0, 0,
        0xaa, 0xbb, 0xcc, 0xdd,
    }, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
    try expectCursor(file, 16);
}
