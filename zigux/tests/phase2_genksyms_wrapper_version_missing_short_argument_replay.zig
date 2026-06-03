const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms");

fn expectMissingShortArgumentVersionCount(
    args: []const []const u8,
    expected_option: []const u8,
    expected_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_count, failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedMissingShortArgumentFailure,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}

test "long version before missing short reference argument preserves side effect" {
    const args = [_][]const u8{
        "--version",
        "-r",
    };

    try expectMissingShortArgumentVersionCount(&args, "r", 1);
}

test "abbreviated version before missing short dump-types argument preserves side effect" {
    const args = [_][]const u8{
        "--ver",
        "-T",
    };

    try expectMissingShortArgumentVersionCount(&args, "T", 1);
}

test "short version cluster before missing short argument preserves every side effect" {
    const args = [_][]const u8{
        "-VV",
        "-r",
    };

    try expectMissingShortArgumentVersionCount(&args, "r", 2);
}
