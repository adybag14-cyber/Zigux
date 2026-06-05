const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

fn expectInvalidFailure(args: []const []const u8, expected_option: []const u8, expected_versions: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_versions, failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedInvalidOptionFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "invalid long option after delayed positionals preserves earlier versions" {
    const args = [_][]const u8{
        "leftover.c",
        "--version",
        "rightover.h",
        "--unknown",
    };

    try expectInvalidFailure(&args, "--unknown", 1);
}

test "invalid short cluster after delayed positional reports offending flag" {
    const args = [_][]const u8{
        "leftover.c",
        "-VVx",
    };

    try expectInvalidFailure(&args, "x", 2);
}

test "required option data after positionals does not mask later invalid short option" {
    const args = [_][]const u8{
        "leftover.c",
        "--reference",
        "--unknown-is-data",
        "-VZ",
    };

    try expectInvalidFailure(&args, "Z", 1);
}
