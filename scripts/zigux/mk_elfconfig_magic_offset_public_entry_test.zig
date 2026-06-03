const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

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

fn expectRun(input: []const u8, expected_exit_code: u8, expected_stdout: []const u8, expected_stderr: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);

    try std.testing.expectEqual(expected_exit_code, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "public entry rejects shifted magic with valid class-looking byte" {
    const input = [_]u8{ 0x00, 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 };

    try std.testing.expectEqual(.not_elf, mk_elfconfig.classify(&input));
    try expectRun(&input, 1, "", not_elf_text);
}

test "public entry keeps leading ELF32 authority before later shifted magic" {
    const input = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0x7f, 'E', 'L', 'F', 2, 1, 1, 0 };

    try std.testing.expectEqual(.elf32, mk_elfconfig.classify(&input));
    try expectRun(&input, 0, elfclass32_define, "");
}

test "public entry keeps leading ELF64 authority before later shifted magic" {
    const input = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0x7f, 'E', 'L', 'F', 1, 1, 1, 0 };

    try std.testing.expectEqual(.elf64, mk_elfconfig.classify(&input));
    try expectRun(&input, 0, elfclass64_define, "");
}
