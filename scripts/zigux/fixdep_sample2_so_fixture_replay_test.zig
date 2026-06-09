const std = @import("std");
const Io = std.Io;
const fixdep = @import("fixdep.zig");

const fixture_dir = "zigux/tests/fixtures/fixdep/";

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 2048),
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

    pub fn flush(_: *@This()) !void {}
};

test "sample2 so fixture is retained but not parsed" {
    const allocator = std.testing.allocator;

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        allocator,
        std.testing.io,
        &capture,
        fixture_dir ++ "sample_multi_target.d",
        "module/sample2.o",
        "clang -Iinclude -DZIGUX_MULTI -c " ++ fixture_dir ++ "sample2.c -o module/sample2.o",
    );

    const expected = try Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        fixture_dir ++ "sample_multi_target_expected.txt",
        allocator,
        .limited(16 * 1024),
    );
    defer allocator.free(expected);

    const so_body = try Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        fixture_dir ++ "sample2.so",
        allocator,
        .limited(16 * 1024),
    );
    defer allocator.free(so_body);

    try std.testing.expect(std.mem.indexOf(u8, so_body, "ZIGUX_SAMPLE2_SO_NO_PARSE_SENTINEL") != null);
    try std.testing.expect(std.mem.indexOf(u8, so_body, "ZIGUX_SAMPLE2_SO_MODULE_SHOULD_NOT_PARSE") != null);
    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "sample2.so") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "ZIGUX_SAMPLE2_SO") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "include/generated/autoconf.h") == null);
}
