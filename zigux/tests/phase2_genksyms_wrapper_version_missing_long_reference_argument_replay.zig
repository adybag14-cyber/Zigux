const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectMissingLongReferenceFailure(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("--reference", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper version-prefixed exact missing long reference failures preserve version count" {
    try expectMissingLongReferenceFailure(&.{
        "--version",
        "--reference",
    }, 1);
    try expectMissingLongReferenceFailure(&.{
        "-V",
        "--reference",
    }, 1);
}

test "phase2 genksyms wrapper abbreviated version prefixes preserve missing long reference failures" {
    try expectMissingLongReferenceFailure(&.{
        "--ver",
        "--ref",
    }, 1);
    try expectMissingLongReferenceFailure(&.{
        "-V",
        "--ref",
    }, 1);
}
