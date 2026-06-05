const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";

const Capture = struct {
    bytes: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{ .bytes = try std.ArrayList(u8).initCapacity(allocator, 64) };
    }

    fn deinit(self: *Capture, allocator: std.mem.Allocator) void {
        self.bytes.deinit(allocator);
    }

    pub fn writeAll(self: *Capture, bytes: []const u8) !void {
        try self.bytes.appendSlice(std.testing.allocator, bytes);
    }
};

fn expectFdElf32(input: []const u8) !void {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "elf32_fd_input.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, input, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit(std.testing.allocator);
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit(std.testing.allocator);

    const exit_code = try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(elf32_define, stdout.bytes.items);
    try std.testing.expectEqualStrings("", stderr.bytes.items);
}

test "fd public entry accepts exact ELF32 ident at EOF" {
    const input = [_]u8{
        0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    };

    try expectFdElf32(&input);
}

test "fd public entry keeps exact ELF32 authority before later ELF64 bytes" {
    const input = [_]u8{
        0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
        0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    };

    try expectFdElf32(&input);
}

test "fd public entry keeps exact ELF32 authority before later invalid class" {
    const input = [_]u8{
        0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
        0x7f, 'E', 'L', 'F', 0, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    };

    try expectFdElf32(&input);
}
