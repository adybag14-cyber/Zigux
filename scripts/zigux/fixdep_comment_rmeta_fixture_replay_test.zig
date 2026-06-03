const std = @import("std");
const fixdep = @import("fixdep.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
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

test "comment-continuation rmeta dependency remains no-parse" {
    const allocator = std.testing.allocator;
    const depfile_name = "zigux_fixdep_comment_rmeta_fixture_replay.d";
    const rmeta_name = "zigux_fixdep_comment_rmeta_fixture_replay_source.rmeta";
    const so_name = "zigux_fixdep_comment_rmeta_fixture_replay_dep.so";
    const target = "sample_comment_continuation.o";
    const cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_comment_continuation_source.c -o sample_comment_continuation.o";

    try std.Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = depfile_name,
        .data =
        \\# rustc note \
        \\continues across lines \
        \\until the first real newline
        \\sample_comment_continuation.o: zigux_fixdep_comment_rmeta_fixture_replay_source.rmeta \
        \\ zigux_fixdep_comment_rmeta_fixture_replay_dep.so
        \\
        ,
    });
    defer std.Io.Dir.cwd().deleteFile(std.testing.io, depfile_name) catch {};

    try std.Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = rmeta_name,
        .data = "CONFIG_ZIGUX_COMMENT_RMETA_SHOULD_NOT_PARSE\n",
    });
    defer std.Io.Dir.cwd().deleteFile(std.testing.io, rmeta_name) catch {};

    try std.Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = so_name,
        .data = "CONFIG_ZIGUX_COMMENT_SO_SHOULD_NOT_PARSE\n",
    });
    defer std.Io.Dir.cwd().deleteFile(std.testing.io, so_name) catch {};

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        allocator,
        std.testing.io,
        &capture,
        depfile_name,
        target,
        cmdline,
    );

    try std.testing.expectEqualStrings(
        "savedcmd_sample_comment_continuation.o := clang -c zigux/tests/fixtures/fixdep/sample_comment_continuation_source.c -o sample_comment_continuation.o\n\n" ++
            "source_sample_comment_continuation.o := zigux_fixdep_comment_rmeta_fixture_replay_source.rmeta\n\n" ++
            "deps_sample_comment_continuation.o := \\\n" ++
            "  zigux_fixdep_comment_rmeta_fixture_replay_dep.so \\\n" ++
            "\n" ++
            "sample_comment_continuation.o: $(deps_sample_comment_continuation.o)\n\n" ++
            "$(deps_sample_comment_continuation.o):\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "comment/rmeta/should/not/parse") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "comment/so/should/not/parse") == null);
}
