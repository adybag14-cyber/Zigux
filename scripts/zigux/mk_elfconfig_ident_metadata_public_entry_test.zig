const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 96),
            .allocator = allocator,
        };
    }

    fn deinit(self: *Capture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }
};

fn expectRun(
    input: []const u8,
    expected_exit: u8,
    expected_stdout: []const u8,
    expected_stderr: []const u8,
) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
    try std.testing.expectEqual(expected_exit, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "ELF32 accepts unusual non-class ident metadata bytes" {
    const header = [_]u8{
        0x7f, 'E',  'L',  'F',
        1,    0xff, 0x00, 0x7f,
        0x80, 0x01, 0xfe, 0x55,
        0xaa, 0x10, 0x20, 0x30,
    };

    try std.testing.expectEqual(mk_elfconfig.Outcome.elf32, mk_elfconfig.classify(&header));
    try expectRun(&header, 0, "#define KERNEL_ELFCLASS ELFCLASS32\n", "");
}

test "ELF64 accepts unusual non-class ident metadata bytes" {
    const header = [_]u8{
        0x7f, 'E',  'L',  'F',
        2,    0x00, 0xff, 0x42,
        0x99, 0x11, 0x22, 0x33,
        0x44, 0x55, 0x66, 0x77,
    };

    try std.testing.expectEqual(mk_elfconfig.Outcome.elf64, mk_elfconfig.classify(&header));
    try expectRun(&header, 0, "#define KERNEL_ELFCLASS ELFCLASS64\n", "");
}

test "invalid class ignores metadata that otherwise looks conventional" {
    const header = [_]u8{
        0x7f, 'E', 'L', 'F',
        0,    1,   1,   0,
        0,    0,   0,   0,
        0,    0,   0,   0,
    };

    try std.testing.expectEqual(mk_elfconfig.Outcome.invalid_class, mk_elfconfig.classify(&header));
    try expectRun(&header, 1, "", "");
}

test "metadata bytes after EI_CLASS cannot repair non-ELF magic" {
    const header = [_]u8{
        0x7f, 'E', 'X', 'F',
        2,    1,   1,   0,
        0,    0,   0,   0,
        0,    0,   0,   0,
    };

    try std.testing.expectEqual(mk_elfconfig.Outcome.not_elf, mk_elfconfig.classify(&header));
    try expectRun(&header, 1, "", "Error: not ELF\n");
}
