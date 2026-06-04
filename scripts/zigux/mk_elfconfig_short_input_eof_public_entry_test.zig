const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const truncated_text = "Error: input truncated\n";
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

test "public entry reports truncation for every short ELF-looking prefix length" {
    const full_elf64 = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

    for (0..full_elf64.len) |len| {
        try std.testing.expectEqual(mk_elfconfig.Outcome.truncated, mk_elfconfig.classify(full_elf64[0..len]));
        try expectRun(full_elf64[0..len], 1, "", truncated_text);
    }

    try expectRun(&full_elf64, 0, elfclass64_define, "");
}

test "public entry keeps truncation ahead of bad magic before full ident" {
    const short_bad_magic = [_]u8{ 0, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 };

    try std.testing.expectEqual(mk_elfconfig.Outcome.truncated, mk_elfconfig.classify(&short_bad_magic));
    try expectRun(&short_bad_magic, 1, "", truncated_text);
}

test "public entry keeps truncation ahead of invalid class before full ident" {
    const short_invalid_class = [_]u8{ 0x7f, 'E', 'L', 'F', 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 };

    try std.testing.expectEqual(mk_elfconfig.Outcome.truncated, mk_elfconfig.classify(&short_invalid_class));
    try expectRun(&short_invalid_class, 1, "", truncated_text);
}
