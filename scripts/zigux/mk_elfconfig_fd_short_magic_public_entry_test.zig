const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

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

fn expectFdTruncated(name: []const u8, bytes: []const u8) !void {
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
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("Error: input truncated\n", stderr.list.items);
}

test "fd-backed short magic prefix is truncated before ELF magic classification" {
    try expectFdTruncated("short_magic_prefix.bin", &[_]u8{ 0x7f, 'E', 'L' });
}

test "fd-backed short non-ELF prefix is still truncated before magic mismatch" {
    try expectFdTruncated("short_non_elf_prefix.bin", &[_]u8{ 0x00, 'E', 'L' });
}
