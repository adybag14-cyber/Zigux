const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms");

fn expectVersionTerminatorRequest(
    args: []const []const u8,
    expected_version_arg: []const u8,
    expected_version_count: usize,
) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(expected_version_count, request.version_count);
                try testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try testing.expectEqualStrings(expected_version_arg, request.rendered_args[0]);
                try testing.expectEqualStrings("--", request.rendered_args[1]);
                try testing.expectEqualStrings("--leftover", request.rendered_args[2]);
                try testing.expectEqualStrings("positional", request.rendered_args[3]);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expectEqual(@as(?[]const u8, null), request.dump_types_file);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "pure long version before explicit terminator becomes request with side effect" {
    const args = [_][]const u8{
        "--version",
        "--",
        "--leftover",
        "positional",
    };

    try expectVersionTerminatorRequest(&args, "--version", 1);
}

test "abbreviated long version before explicit terminator becomes request with side effect" {
    const args = [_][]const u8{
        "--ver",
        "--",
        "--leftover",
        "positional",
    };

    try expectVersionTerminatorRequest(&args, "--ver", 1);
}

test "repeated short version cluster before explicit terminator keeps both side effects" {
    const args = [_][]const u8{
        "-VV",
        "--",
        "--leftover",
        "positional",
    };

    try expectVersionTerminatorRequest(&args, "-VV", 2);
}
