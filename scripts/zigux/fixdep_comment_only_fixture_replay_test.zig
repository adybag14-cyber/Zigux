const std = @import("std");
const fixdep = @import("fixdep.zig");

const depfile_path = "zigux/tests/fixtures/fixdep/sample_comment_only.d";
const expected_stdout_path = "zigux/tests/fixtures/fixdep/sample_comment_only_expected.txt";
const target = "sample_comment_only.o";
const cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only.o";

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
            .allocator = allocator,
        };
    }

    pub fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }

    pub fn flush(_: *@This()) !void {}
};

test "runFixdep keeps the shipped comment-only fixture stdout before the no-target failure" {
    const expected_stdout = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        expected_stdout_path,
        std.testing.allocator,
        .limited(4 * 1024),
    );
    defer std.testing.allocator.free(expected_stdout);

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try std.testing.expectError(
        error.NoTargets,
        fixdep.runFixdep(
            std.testing.allocator,
            std.testing.io,
            &capture,
            depfile_path,
            target,
            cmdline,
        ),
    );

    try std.testing.expectEqualStrings(expected_stdout, capture.list.items);
}
