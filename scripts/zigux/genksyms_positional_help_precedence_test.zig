const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectHelpVersionCount(args: []const []const u8, expected: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(expected, version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedHelpCommand,
    }
}

test "genksyms help still wins after delayed positional args" {
    const short_args = [_][]const u8{
        "leftover.c",
        "-V",
        "-h",
    };
    try expectHelpVersionCount(&short_args, 1);

    const long_args = [_][]const u8{
        "leftover.c",
        "--ver",
        "--help",
    };
    try expectHelpVersionCount(&long_args, 1);
}

test "genksyms abbreviated help still wins after delayed positional args" {
    const args = [_][]const u8{
        "leftover.c",
        "--version",
        "--hel",
    };
    try expectHelpVersionCount(&args, 1);
}

test "genksyms terminator protects help-looking positional tail" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "leftover.c",
        "--",
        "--help",
        "-h",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 5), request.rendered_args.len);
                try testing.expectEqualStrings("-V", request.rendered_args[0]);
                try testing.expectEqualStrings("leftover.c", request.rendered_args[1]);
                try testing.expectEqualStrings("--", request.rendered_args[2]);
                try testing.expectEqualStrings("--help", request.rendered_args[3]);
                try testing.expectEqualStrings("-h", request.rendered_args[4]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
