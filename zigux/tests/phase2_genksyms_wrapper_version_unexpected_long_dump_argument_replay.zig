const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectUnexpectedLongDumpArgumentFailure(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--dump", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper version-prefixed exact unexpected long dump arguments preserve version count" {
    try expectUnexpectedLongDumpArgumentFailure(&.{ "--version", "--dump=extra" }, 1);
    try expectUnexpectedLongDumpArgumentFailure(&.{ "-V", "--dump=extra" }, 1);
}

test "phase2 genksyms wrapper abbreviated version prefixes preserve exact unexpected long dump arguments" {
    try expectUnexpectedLongDumpArgumentFailure(&.{ "--ver", "--dump=extra" }, 1);
    try expectUnexpectedLongDumpArgumentFailure(&.{ "-V", "--dump=extra" }, 1);
}
