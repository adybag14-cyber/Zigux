const std = @import("std");
const fixdep = @import("fixdep.zig");

const fixture_root = "zigux/tests/fixtures/fixdep/";

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 1024),
            .allocator = allocator,
        };
    }

    fn deinit(self: *Capture) void {
        self.list.deinit(self.allocator);
    }

    pub fn print(self: *Capture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }

    pub fn flush(_: *Capture) !void {}
};

test "sample multi-target fixture replays through public fixdep entry" {
    const allocator = std.testing.allocator;

    const expected = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        fixture_root ++ "sample_multi_target_expected.txt",
        allocator,
        .limited(16 * 1024),
    );
    defer allocator.free(expected);

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        allocator,
        std.testing.io,
        &capture,
        fixture_root ++ "sample_multi_target.d",
        "module/sample2.o",
        "clang -Iinclude -DZIGUX_MULTI -c zigux/tests/fixtures/fixdep/sample2.c -o module/sample2.o",
    );

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "module/sample2.o: $(deps_module/sample2.o)") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "module/sample2.d") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "include/generated/autoconf.h") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "ZIGUX_HASH") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "ZIGUX_SHARED") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "ZIGUX_SECOND") != null);
}
