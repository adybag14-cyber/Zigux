const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectVersionedAmbiguousLongFailure(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .ambiguous_option => |option| try testing.expectEqualStrings("--d", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedAmbiguousLongFailure,
    }
}

test "phase2 genksyms wrapper keeps exact version before ambiguous long failure" {
    try expectVersionedAmbiguousLongFailure(
        &.{
            "--version",
            "--d",
        },
        1,
    );
}

test "phase2 genksyms wrapper keeps abbreviated version before ambiguous long failure" {
    try expectVersionedAmbiguousLongFailure(
        &.{
            "--ver",
            "--d",
        },
        1,
    );
}
