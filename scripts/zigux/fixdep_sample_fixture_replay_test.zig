const std = @import("std");
const fixdep = @import("fixdep.zig");

const depfile_path = "zigux/tests/fixtures/fixdep/sample.d";
const expected_path = "zigux/tests/fixtures/fixdep/sample_expected.txt";
const target = "sample.o";
const cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample.o";

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 1024),
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

test "runFixdep matches the shipped baseline sample fixture replay" {
    const expected = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        expected_path,
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(expected);

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        target,
        cmdline,
    );

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
