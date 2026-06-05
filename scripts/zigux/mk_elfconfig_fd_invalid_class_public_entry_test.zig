const std = @import("std");

const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";

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

fn validHeader(class: u8) [16]u8 {
    return .{ 0x7f, 'E', 'L', 'F', class, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
}

fn expectFdRun(input: []const u8, expected_exit: u8, expected_stdout: []const u8, expected_stderr: []const u8) !void {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "input.bin", .{ .read = true });
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

test "fd-backed exact invalid class range exits silently" {
    const invalid_classes = [_]u8{ 0, 3, 4, 42, 127, 128, 200, 254, 255 };
    for (invalid_classes) |class| {
        const header = validHeader(class);
        try expectFdRun(&header, 1, "", "");
    }
}

test "fd-backed invalid class range stays between valid class boundaries" {
    const elf32 = validHeader(1);
    try expectFdRun(&elf32, 0, elfclass32_define, "");

    const zero_class = validHeader(0);
    try expectFdRun(&zero_class, 1, "", "");

    const high_class = validHeader(255);
    try expectFdRun(&high_class, 1, "", "");

    const elf64 = validHeader(2);
    try expectFdRun(&elf64, 0, elfclass64_define, "");
}
