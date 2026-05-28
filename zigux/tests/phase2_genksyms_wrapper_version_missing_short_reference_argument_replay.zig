const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectMissingShortReferenceFailure(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("r", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper version-prefixed exact missing short reference failures preserve version count" {
    try expectMissingShortReferenceFailure(&.{
        "--version",
        "-r",
    }, 1);
    try expectMissingShortReferenceFailure(&.{
        "-V",
        "-r",
    }, 1);
}

test "phase2 genksyms wrapper abbreviated and clustered version prefixes preserve missing short reference failures" {
    try expectMissingShortReferenceFailure(&.{
        "--ver",
        "-r",
    }, 1);
    try expectMissingShortReferenceFailure(&.{
        "-Vr",
    }, 1);
}
