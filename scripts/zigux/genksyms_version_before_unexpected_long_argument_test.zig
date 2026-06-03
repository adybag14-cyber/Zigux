const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectUnexpectedLongArgument(
    args: []const []const u8,
    expected_option: []const u8,
    expected_versions: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_versions, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| {
                    try testing.expectEqualStrings(expected_option, option);
                },
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedUnexpectedArgumentFailure,
    }
}

test "version side effects survive unexpected inline long option arguments" {
    try expectUnexpectedLongArgument(
        &.{ "--version", "--help=usage.txt" },
        "--help",
        1,
    );

    try expectUnexpectedLongArgument(
        &.{ "--ver", "--quiet=false" },
        "--quiet",
        1,
    );

    try expectUnexpectedLongArgument(
        &.{ "-VV", "--dump=defs.sym" },
        "--dump",
        2,
    );
}
