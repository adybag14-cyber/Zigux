const std = @import("std");
const mk = @import("mk_elfconfig.zig");

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

test "fd-backed trailing not-ELF input does not silently skip forward to the hidden 32-bit ELF header" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "not_elf_hidden_elf32_no_skip.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &[_]u8{
        0x00, 'E',  'L',  'F',  1,    1,   1,   0,
        0,    0,    0,    0,    0,    0,   0,   0,
        0xaa, 0xbb, 0xcc, 0xdd, 0x7f, 'E', 'L', 'F',
        1,    1,    1,    0,    0,    0,   0,   0,
        0,    0,    0,    0,
    }, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    _ = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    stdout.reset();
    stderr.reset();

    const second_exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), second_exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
    try expectCursor(file, 32);
}

test "fd-backed trailing not-ELF input does not silently skip forward to the hidden 64-bit ELF header" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "not_elf_hidden_elf64_no_skip.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &[_]u8{
        0x00, 'E',  'L',  'F',  1,    1,   1,   0,
        0,    0,    0,    0,    0,    0,   0,   0,
        0xaa, 0xbb, 0xcc, 0xdd, 0x7f, 'E', 'L', 'F',
        2,    1,    1,    0,    0,    0,   0,   0,
        0,    0,    0,    0,
    }, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    _ = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    stdout.reset();
    stderr.reset();

    const second_exit_code = try mk.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), second_exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
    try expectCursor(file, 32);
}
