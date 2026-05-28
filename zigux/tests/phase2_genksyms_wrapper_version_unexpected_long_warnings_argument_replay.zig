const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectUnexpectedLongWarningsArgumentFailure(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--warnings", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper version-prefixed exact unexpected long warnings arguments preserve version count" {
    try expectUnexpectedLongWarningsArgumentFailure(&.{ "--version", "--warnings=extra" }, 1);
    try expectUnexpectedLongWarningsArgumentFailure(&.{ "-V", "--warnings=extra" }, 1);
}

test "phase2 genksyms wrapper version-prefixed abbreviated unexpected long warnings arguments stay canonical" {
    try expectUnexpectedLongWarningsArgumentFailure(&.{ "--ver", "--warn=extra" }, 1);
    try expectUnexpectedLongWarningsArgumentFailure(&.{ "-V", "--warn=extra" }, 1);
}
