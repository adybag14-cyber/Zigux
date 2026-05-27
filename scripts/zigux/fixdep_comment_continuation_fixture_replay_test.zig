const std = @import("std");
const fixdep = @import("fixdep.zig");

const fixture_depfile = "zigux/tests/fixtures/fixdep/sample_comment_continuation.d";
const fixture_expected = "zigux/tests/fixtures/fixdep/sample_comment_continuation_expected.txt";
const fixture_target = "sample_comment_continuation.o";
const fixture_cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_comment_continuation_source.c -o sample_comment_continuation.o";

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 1024),
            .allocator = allocator,
        };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }

    pub fn flush(self: *@This()) !void {
        _ = self;
    }
};

test "runFixdep replays the committed comment-continuation fixture output" {
    const expected = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        fixture_expected,
        std.testing.allocator,
        .limited(std.math.maxInt(usize)),
    );
    defer std.testing.allocator.free(expected);

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        fixture_depfile,
        fixture_target,
        fixture_cmdline,
    );

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
