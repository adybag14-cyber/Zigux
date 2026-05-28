const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectUnexpectedLongHelpArgumentFailure(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--help", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper version-prefixed exact unexpected long help arguments preserve version count" {
    try expectUnexpectedLongHelpArgumentFailure(&.{ "--version", "--help=extra" }, 1);
    try expectUnexpectedLongHelpArgumentFailure(&.{ "-V", "--help=extra" }, 1);
}

test "phase2 genksyms wrapper abbreviated version prefixes keep unexpected long help arguments canonical" {
    try expectUnexpectedLongHelpArgumentFailure(&.{ "--ver", "--hel=extra" }, 1);
    try expectUnexpectedLongHelpArgumentFailure(&.{ "-V", "--hel=extra" }, 1);
}
