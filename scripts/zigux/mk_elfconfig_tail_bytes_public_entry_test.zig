const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elf64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const not_elf_text = "Error: not ELF\n";

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

fn expectRun(input: []const u8, expected_code: u8, expected_stdout: []const u8, expected_stderr: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit(std.testing.allocator);
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit(std.testing.allocator);

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
    try std.testing.expectEqual(expected_code, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.bytes.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.bytes.items);
}

test "public entry ignores extra bytes after ELF32 ident" {
    const input = [_]u8{
        0x7f, 'E', 'L', 'F', 1, 1,    1,    0,
        0,    0,   0,   0,   0, 0,    0,    0,
        0x00, 'E', 'L', 'F', 2, 0xff, 0xee, 0xdd,
    };

    try std.testing.expectEqual(mk_elfconfig.Outcome.elf32, mk_elfconfig.classify(input[0..16]));
    try expectRun(&input, 0, elf32_define, "");
}

test "public entry ignores extra bytes after ELF64 ident" {
    const input = [_]u8{
        0x7f, 'E', 'L', 'F', 2, 1,    1,    0,
        0,    0,   0,   0,   0, 0,    0,    0,
        0x7f, 'E', 'L', 'F', 1, 0xaa, 0xbb, 0xcc,
    };

    try std.testing.expectEqual(mk_elfconfig.Outcome.elf64, mk_elfconfig.classify(input[0..16]));
    try expectRun(&input, 0, elf64_define, "");
}

test "public entry ignores rescuing bytes after bad first ident" {
    const input = [_]u8{
        0x00, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
        0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    };

    try std.testing.expectEqual(mk_elfconfig.Outcome.not_elf, mk_elfconfig.classify(input[0..16]));
    try expectRun(&input, 1, "", not_elf_text);
}

test "public entry ignores rescuing bytes after invalid first class" {
    const input = [_]u8{
        0x7f, 'E', 'L', 'F', 0, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
        0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    };

    try std.testing.expectEqual(mk_elfconfig.Outcome.invalid_class, mk_elfconfig.classify(input[0..16]));
    try expectRun(&input, 1, "", "");
}
