const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectMissingShortDumpTypesFailure(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("T", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper version-prefixed exact missing short dump-types failures preserve version count" {
    try expectMissingShortDumpTypesFailure(&.{
        "--version",
        "-T",
    }, 1);
    try expectMissingShortDumpTypesFailure(&.{
        "-V",
        "-T",
    }, 1);
}

test "phase2 genksyms wrapper abbreviated and clustered version prefixes preserve missing short dump-types failures" {
    try expectMissingShortDumpTypesFailure(&.{
        "--ver",
        "-T",
    }, 1);
    try expectMissingShortDumpTypesFailure(&.{
        "-VT",
    }, 1);
}
