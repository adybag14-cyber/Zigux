const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

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
    return .{
        0x7f, 'E', 'L', 'F', class, 1, 1, 0,
        0,    0,   0,   0,   0,     0, 0, 0,
    };
}

fn expectRun(input: []const u8, expected_exit: u8, expected_stdout: []const u8, expected_stderr: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);

    try std.testing.expectEqual(expected_exit, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "slice-backed public entry rejects each full-header magic-byte mismatch" {
    const valid_elf32 = elfIdent(1);

    var index: usize = 0;
    while (index < 4) : (index += 1) {
        var header = valid_elf32;
        header[index] ^= 0xff;

        try std.testing.expectEqual(mk_elfconfig.Outcome.not_elf, mk_elfconfig.classify(&header));
        try expectRun(&header, 1, "", not_elf_text);
    }
}

test "slice-backed magic mismatch keeps first complete ident authoritative" {
    const valid_elf32 = elfIdent(1);

    var bad_first = valid_elf32;
    bad_first[0] = 0;

    const bad_then_valid = bad_first ++ valid_elf32;

    try std.testing.expectEqual(mk_elfconfig.Outcome.not_elf, mk_elfconfig.classify(&bad_then_valid));
    try expectRun(&bad_then_valid, 1, "", not_elf_text);
}

test "slice-backed exact valid magic remains the success control" {
    const valid_elf32 = elfIdent(1);

    try std.testing.expectEqual(mk_elfconfig.Outcome.elf32, mk_elfconfig.classify(&valid_elf32));
    try expectRun(&valid_elf32, 0, elfclass32_define, "");
}
