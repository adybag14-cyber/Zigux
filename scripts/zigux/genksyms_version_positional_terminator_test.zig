const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

fn expectVersionPositionalTerminatorRequest(
    args: []const []const u8,
    expected_rendered: []const []const u8,
    expected_version_count: usize,
) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(expected_version_count, request.version_count);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, expected_rendered, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "version before terminator flushes deferred positional arguments" {
    const args = [_][]const u8{
        "input.c",
        "-V",
        "--",
        "--debug",
        "after.symref",
    };
    const expected_rendered = [_][]const u8{
        "-V",
        "--",
        "input.c",
        "--debug",
        "after.symref",
    };

    try expectVersionPositionalTerminatorRequest(&args, &expected_rendered, 1);
}

test "mixed versions before terminator preserve earlier positional ordering" {
    const args = [_][]const u8{
        "first.c",
        "--ver",
        "second.h",
        "-VV",
        "--",
        "-r",
        "ignored.symref",
    };
    const expected_rendered = [_][]const u8{
        "--ver",
        "-VV",
        "--",
        "first.c",
        "second.h",
        "-r",
        "ignored.symref",
    };

    try expectVersionPositionalTerminatorRequest(&args, &expected_rendered, 3);
}
