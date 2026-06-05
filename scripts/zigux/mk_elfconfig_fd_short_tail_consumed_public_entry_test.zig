const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass32: u8 = 1;
const elfclass64: u8 = 2;
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

fn runFromOffset(path: []const u8, bytes: []const u8, offset: u64) !struct {
    exit_code: u8,
    stdout: []const u8,
    stderr: []const u8,
    remaining: []const u8,
} {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, path, .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, bytes, 0);
    const seek_result = std.os.linux.lseek(file.handle, @intCast(offset), std.os.linux.SEEK.SET);
    try std.testing.expectEqual(offset, seek_result);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr);

    var remaining_buffer: [32]u8 = undefined;
    const remaining_len = try std.posix.read(file.handle, &remaining_buffer);

    return .{
        .exit_code = exit_code,
        .stdout = try std.testing.allocator.dupe(u8, stdout.list.items),
        .stderr = try std.testing.allocator.dupe(u8, stderr.list.items),
        .remaining = try std.testing.allocator.dupe(u8, remaining_buffer[0..remaining_len]),
    };
}

fn expectTruncatedAndConsumed(result: anytype) !void {
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);
    defer std.testing.allocator.free(result.remaining);

    try std.testing.expectEqual(@as(u8, 1), result.exit_code);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(truncated_text, result.stderr);
    try std.testing.expectEqualStrings("", result.remaining);
}

test "fd-backed short tail after valid header is consumed at EOF" {
    const bytes = [_]u8{
        0x7f, 'E', 'L', 'F', elfclass64, 1, 1, 0,
        0,    0,   0,   0,   0,          0, 0, 0,
        0x7f, 'E', 'L',
    };

    try expectTruncatedAndConsumed(try runFromOffset("valid_then_short_tail.bin", &bytes, 16));
}

test "fd-backed short tail after invalid class is consumed at EOF" {
    const bytes = [_]u8{
        0x7f, 'E', 'L', 'F', 0xff,       1, 1, 0,
        0,    0,   0,   0,   0,          0, 0, 0,
        0x7f, 'E', 'L', 'F', elfclass32,
    };

    try expectTruncatedAndConsumed(try runFromOffset("invalid_then_short_tail.bin", &bytes, 16));
}

test "fd-backed full non-ELF at tail is not treated as truncated" {
    const bytes = [_]u8{
        0x7f, 'E', 'L', 'F', elfclass64, 1, 1, 0,
        0,    0,   0,   0,   0,          0, 0, 0,
        'n',  'o', 't', '!', elfclass32, 1, 1, 0,
        0,    0,   0,   0,   0,          0, 0, 0,
    };

    const result = try runFromOffset("valid_then_non_elf_tail.bin", &bytes, 16);
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);
    defer std.testing.allocator.free(result.remaining);

    try std.testing.expectEqual(@as(u8, 1), result.exit_code);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(not_elf_text, result.stderr);
    try std.testing.expectEqualStrings("", result.remaining);
}
