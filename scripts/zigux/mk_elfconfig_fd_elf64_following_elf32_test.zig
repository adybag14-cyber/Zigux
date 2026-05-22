const std = @import("std");
const mk = @import("mk_elfconfig.zig");

const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";

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

test "fd-backed exact 64-bit ELF header leaves a following 32-bit ELF header for the next call" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "elf64_then_elf32.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &[_]u8{
        0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
        0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
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
    try std.testing.expectEqual(@as(u8, 0), second_exit_code);
    try std.testing.expectEqualStrings(elfclass32_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
    try expectCursor(file, 32);
}
