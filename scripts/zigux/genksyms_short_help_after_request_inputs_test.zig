const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

fn expectHelpVersionCount(args: []const []const u8, expected_version_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(expected_version_count, version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedHelpCommand,
    }
}

test "genksyms bridge treats short help after positional request input as help" {
    const args = [_][]const u8{
        "leftover.c",
        "-h",
    };

    try expectHelpVersionCount(&args, 0);
}

test "genksyms bridge treats short help after lone dash request input as help" {
    const args = [_][]const u8{
        "-",
        "-h",
    };

    try expectHelpVersionCount(&args, 0);
}

test "genksyms bridge preserves version side effects before request short help" {
    const separated_args = [_][]const u8{
        "--version",
        "leftover.c",
        "-h",
    };
    const clustered_args = [_][]const u8{
        "leftover.c",
        "-Vh",
    };

    try expectHelpVersionCount(&separated_args, 1);
    try expectHelpVersionCount(&clustered_args, 1);
}

test "genksyms bridge keeps required-option short help lookalikes as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--reference",
        "-h",
        "-T",
        "-h",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("-h", request.reference_files[0]);
                try testing.expectEqualStrings("-h", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
