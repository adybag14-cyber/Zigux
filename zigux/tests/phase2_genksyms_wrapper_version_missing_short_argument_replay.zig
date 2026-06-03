const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectMissingShortArgumentAfterVersions(
    args: []const []const u8,
    expected_version_count: usize,
    expected_option: []const u8,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedMissingOptionArgumentFailure,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}

test "phase2 genksyms wrapper preserves exact version before missing short reference argument" {
    const args = [_][]const u8{
        "--version",
        "-r",
    };

    try expectMissingShortArgumentAfterVersions(&args, 1, "r");
}

test "phase2 genksyms wrapper preserves abbreviated version before missing short dump-types argument" {
    const args = [_][]const u8{
        "--ver",
        "-T",
    };

    try expectMissingShortArgumentAfterVersions(&args, 1, "T");
}

test "phase2 genksyms wrapper counts clustered short versions before missing short argument" {
    const args = [_][]const u8{
        "-VV",
        "-r",
    };

    try expectMissingShortArgumentAfterVersions(&args, 2, "r");
}
