const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elf64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";

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

fn expectRun(input: []const u8, expected_stdout: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "public entry ignores noisy non-class ident bytes for ELF32" {
    const input = [_]u8{
        0x7f, 'E',  'L',  'F',  1,    0xff, 0x00, 0x7f,
        0x80, 0x55, 0xaa, 0x13, 0x37, 0xc0, 0xde, 0x5a,
        0x7f, 'E',  'L',  'F',  2,    1,    1,    0,
    };

    try expectRun(&input, elf32_define);
}

test "public entry ignores noisy non-class ident bytes for ELF64" {
    const input = [_]u8{
        0x7f, 'E',  'L',  'F',  2,    0x00, 0xff, 0x81,
        0x44, 0x33, 0x22, 0x11, 0xfe, 0xed, 0xfa, 0xce,
        0x7f, 'E',  'L',  'F',  1,    1,    1,    0,
    };

    try expectRun(&input, elf64_define);
}
