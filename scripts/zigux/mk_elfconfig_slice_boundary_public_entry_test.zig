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
    stdin_bytes: []const u8,
    expected_exit: u8,
    expected_stdout: []const u8,
    expected_stderr: []const u8,
) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(stdin_bytes, &stdout, &stderr);
    try std.testing.expectEqual(expected_exit, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "runMkElfconfig ignores bytes before caller slice" {
    const storage = [_]u8{
        0x7f, 'E',  'L',  'F',  3,    0xaa, 0xbb, 0xcc,
        0xdd, 0xee, 0xff, 0x11, 0x22, 0x33, 0x44, 0x55,
        0x7f, 'E',  'L',  'F',  1,    1,    1,    0,
        0,    0,    0,    0,    0,    0,    0,    0,
    };

    try expectRun(
        storage[16..32],
        0,
        "#define KERNEL_ELFCLASS ELFCLASS32\n",
        "",
    );
}

test "runMkElfconfig ignores bytes after caller slice" {
    const storage = [_]u8{
        0x7f, 'E',  'L',  'F',  2,    1,    1,    0,
        0,    0,    0,    0,    0,    0,    0,    0,
        0x7f, 'E',  'L',  'F',  3,    0xaa, 0xbb, 0xcc,
        0xdd, 0xee, 0xff, 0x11, 0x22, 0x33, 0x44, 0x55,
    };

    try expectRun(
        storage[0..16],
        0,
        "#define KERNEL_ELFCLASS ELFCLASS64\n",
        "",
    );
}

test "runMkElfconfig reports truncated caller slice despite valid following bytes" {
    const storage = [_]u8{
        0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    };

    try expectRun(
        storage[0..15],
        1,
        "",
        "Error: input truncated\n",
    );
}

test "runMkElfconfig starts classification at caller slice offset" {
    const storage = [_]u8{
        0xaa, 0xbb, 0xcc, 0xdd,
        0x7f, 'E',  'L',  'F',
        1,    1,    1,    0,
        0,    0,    0,    0,
        0,    0,    0,    0,
    };

    try expectRun(
        storage[4..20],
        0,
        "#define KERNEL_ELFCLASS ELFCLASS32\n",
        "",
    );
}
