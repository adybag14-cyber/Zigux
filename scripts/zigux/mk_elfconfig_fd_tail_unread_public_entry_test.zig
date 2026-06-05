const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass32: u8 = 1;
const elfclass64: u8 = 2;
const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
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

const FdTailCase = struct {
    name: []const u8,
    header: [16]u8,
    expected_exit: u8,
    expected_stdout: []const u8,
    expected_stderr: []const u8,
};

fn expectFdEntryLeavesTailUnread(case: FdTailCase) !void {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();

    const io = std.testing.io;
    const tail = "zigux-tail-remains-owned-by-caller";
    const file = try temp_dir.dir.createFile(io, case.name, .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, &case.header, 0);
    try file.writePositionalAll(io, tail, case.header.len);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(case.expected_exit, exit_code);
    try std.testing.expectEqualStrings(case.expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(case.expected_stderr, stderr.list.items);

    var remaining: [tail.len]u8 = undefined;
    const read_count = try std.posix.read(file.handle, &remaining);
    try std.testing.expectEqual(tail.len, read_count);
    try std.testing.expectEqualStrings(tail, remaining[0..read_count]);

    var eof_probe: [1]u8 = undefined;
    try std.testing.expectEqual(@as(usize, 0), try std.posix.read(file.handle, &eof_probe));
}

test "fd public entry leaves caller tail unread after success and failure classifications" {
    const cases = [_]FdTailCase{
        .{
            .name = "elf32_tail.bin",
            .header = .{ 0x7f, 'E', 'L', 'F', elfclass32, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
            .expected_exit = 0,
            .expected_stdout = elfclass32_define,
            .expected_stderr = "",
        },
        .{
            .name = "elf64_tail.bin",
            .header = .{ 0x7f, 'E', 'L', 'F', elfclass64, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
            .expected_exit = 0,
            .expected_stdout = elfclass64_define,
            .expected_stderr = "",
        },
        .{
            .name = "not_elf_tail.bin",
            .header = .{ 0x00, 'E', 'L', 'F', elfclass32, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
            .expected_exit = 1,
            .expected_stdout = "",
            .expected_stderr = not_elf_text,
        },
        .{
            .name = "invalid_class_tail.bin",
            .header = .{ 0x7f, 'E', 'L', 'F', 0xff, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
            .expected_exit = 1,
            .expected_stdout = "",
            .expected_stderr = "",
        },
    };

    for (cases) |case| {
        try expectFdEntryLeavesTailUnread(case);
    }
}
