const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass32: u8 = 1;
const elfclass64: u8 = 2;
const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
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

fn elfIdent(class: u8) [16]u8 {
    return .{ 0x7f, 'E', 'L', 'F', class, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
}

fn runFd(bytes: []const u8) !struct { exit_code: u8, stdout: Capture, stderr: Capture } {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();

    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "input.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, bytes, 0);

    var stdout = try Capture.init(std.testing.allocator);
    errdefer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    errdefer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    return .{ .exit_code = exit_code, .stdout = stdout, .stderr = stderr };
}

test "fd-backed full-header magic mismatches report not ELF at each magic byte" {
    const mismatch_bytes = [_]u8{ 0x00, 'e', 'l', 'x' };

    for (mismatch_bytes, 0..) |replacement, index| {
        var header = elfIdent(elfclass64);
        header[index] = replacement;

        var result = try runFd(&header);
        defer result.stdout.deinit();
        defer result.stderr.deinit();

        try std.testing.expectEqual(@as(u8, 1), result.exit_code);
        try std.testing.expectEqualStrings("", result.stdout.list.items);
        try std.testing.expectEqualStrings(not_elf_text, result.stderr.list.items);
    }
}

test "fd-backed magic mismatch does not scan later valid ELF ident" {
    var bad_first = elfIdent(elfclass64);
    bad_first[0] = 0;
    const later_elf32 = elfIdent(elfclass32);
    const payload = bad_first ++ later_elf32;

    var result = try runFd(&payload);
    defer result.stdout.deinit();
    defer result.stderr.deinit();

    try std.testing.expectEqual(@as(u8, 1), result.exit_code);
    try std.testing.expectEqualStrings("", result.stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, result.stderr.list.items);
}

test "fd-backed exact ELF32 remains a success control for magic mismatch witness" {
    const header = elfIdent(elfclass32);

    var result = try runFd(&header);
    defer result.stdout.deinit();
    defer result.stderr.deinit();

    try std.testing.expectEqual(@as(u8, 0), result.exit_code);
    try std.testing.expectEqualStrings(elfclass32_define, result.stdout.list.items);
    try std.testing.expectEqualStrings("", result.stderr.list.items);
}
