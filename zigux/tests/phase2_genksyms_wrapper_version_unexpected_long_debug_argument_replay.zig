const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectUnexpectedLongDebugArgumentFailure(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--debug", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper version-prefixed exact unexpected long debug arguments preserve version count" {
    try expectUnexpectedLongDebugArgumentFailure(&.{ "--version", "--debug=extra" }, 1);
    try expectUnexpectedLongDebugArgumentFailure(&.{ "-V", "--debug=extra" }, 1);
}

test "phase2 genksyms wrapper abbreviated version prefixes preserve exact unexpected long debug arguments" {
    try expectUnexpectedLongDebugArgumentFailure(&.{ "--ver", "--debug=extra" }, 1);
    try expectUnexpectedLongDebugArgumentFailure(&.{ "-V", "--debug=extra" }, 1);
}
