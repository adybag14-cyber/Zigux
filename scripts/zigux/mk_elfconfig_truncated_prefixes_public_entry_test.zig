const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const truncated_text = "Error: input truncated\n";

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

fn expectRun(
    input: []const u8,
    expected_exit_code: u8,
    expected_stdout: []const u8,
    expected_stderr: []const u8,
) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
    try std.testing.expectEqual(expected_exit_code, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "truncated ELF prefixes remain truncated through public entry" {
    const cases = [_][]const u8{
        &[_]u8{},
        &[_]u8{0x7f},
        &[_]u8{ 0x7f, 'E' },
        &[_]u8{ 0x7f, 'E', 'L' },
        &[_]u8{ 0x7f, 'E', 'L', 'F' },
        &[_]u8{ 0x7f, 'E', 'L', 'F', 1 },
        &[_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 },
    };

    for (cases) |input| {
        try expectRun(input, 1, "", truncated_text);
    }
}

test "exact ident length is the public entry boundary" {
    try expectRun(
        &[_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        0,
        elfclass32_define,
        "",
    );
    try expectRun(
        &[_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        0,
        elfclass64_define,
        "",
    );
}
