const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectVersionedRequestAfterTerminator(
    args: []const []const u8,
    expected_version_count: usize,
    expected_debug_level: usize,
) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(expected_version_count, request.version_count);
                try testing.expectEqual(expected_debug_level, request.debug_level);
                try testing.expectEqualSlices([]const u8, args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper keeps version side effects before explicit option terminator" {
    try expectVersionedRequestAfterTerminator(&.{
        "--version",
        "--",
        "--leftover",
        "-d",
    }, 1, 0);
}

test "phase2 genksyms wrapper keeps abbreviated and clustered versions before option terminator" {
    try expectVersionedRequestAfterTerminator(&.{
        "--ver",
        "-VV",
        "--",
        "input.c",
    }, 3, 0);
}

test "phase2 genksyms wrapper stops parsing debug flags after option terminator" {
    try expectVersionedRequestAfterTerminator(&.{
        "-Vd",
        "--",
        "-d",
        "--debug",
    }, 1, 1);
}
