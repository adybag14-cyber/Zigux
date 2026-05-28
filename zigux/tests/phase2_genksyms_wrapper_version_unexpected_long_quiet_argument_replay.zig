const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectUnexpectedLongQuietArgumentFailure(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--quiet", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper version-prefixed exact unexpected long quiet arguments preserve version count" {
    try expectUnexpectedLongQuietArgumentFailure(&.{ "--version", "--quiet=extra" }, 1);
    try expectUnexpectedLongQuietArgumentFailure(&.{ "-V", "--quiet=extra" }, 1);
}

test "phase2 genksyms wrapper version-prefixed abbreviated unexpected long quiet arguments stay canonical" {
    try expectUnexpectedLongQuietArgumentFailure(&.{ "--ver", "--qui=extra" }, 1);
    try expectUnexpectedLongQuietArgumentFailure(&.{ "-V", "--qui=extra" }, 1);
}
