const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

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
    expected_stdout: []const u8,
    expected_stderr: []const u8,
    expected_exit_code: u8,
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

test "slice public entry reports truncation before magic or class interpretation" {
    const cases = [_][]const u8{
        &[_]u8{},
        &[_]u8{0x00},
        &[_]u8{ 0x00, 'E', 'L', 'F', 1 },
        &[_]u8{ 0x7f, 'E', 'L', 'F', 0 },
        &[_]u8{ 0x7f, 'E', 'L', 'F', 3 },
        &[_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 },
        &[_]u8{ 0x00, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 },
    };

    for (cases) |input| {
        try expectRun(input, "", "Error: input truncated\n", 1);
    }
}

test "slice public entry changes behavior exactly at complete ident boundary" {
    try expectRun(
        &[_]u8{ 0x00, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        "",
        "Error: not ELF\n",
        1,
    );
    try expectRun(
        &[_]u8{ 0x7f, 'E', 'L', 'F', 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        "",
        "",
        1,
    );
    try expectRun(
        &[_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        "#define KERNEL_ELFCLASS ELFCLASS32\n",
        "",
        0,
    );
    try expectRun(
        &[_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        "#define KERNEL_ELFCLASS ELFCLASS64\n",
        "",
        0,
    );
}
