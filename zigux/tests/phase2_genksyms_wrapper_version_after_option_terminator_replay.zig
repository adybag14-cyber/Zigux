const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectTerminatedVersionData(
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

test "phase2 genksyms wrapper treats long version after option terminator as request data" {
    try expectTerminatedVersionData(&.{
        "--",
        "--version",
        "--ver",
        "input.c",
    }, 0, 0);
}

test "phase2 genksyms wrapper stops parsing clustered version flags after option terminator" {
    try expectTerminatedVersionData(&.{
        "-d",
        "--",
        "-VV",
        "-Vd",
    }, 0, 1);
}

test "phase2 genksyms wrapper only counts version flags before option terminator" {
    try expectTerminatedVersionData(&.{
        "--version",
        "-d",
        "--",
        "--version",
        "-VV",
    }, 1, 1);
}
