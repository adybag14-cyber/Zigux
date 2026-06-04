const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectUnexpectedVersionArgument(args: []const []const u8, expected_version_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--version", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "abbreviated version with inline argument fails before recording version side effect" {
    const args = [_][]const u8{"--ver=extra"};
    try expectUnexpectedVersionArgument(&args, 0);
}

test "prior version side effects are preserved before abbreviated version argument failure" {
    const long_args = [_][]const u8{
        "--version",
        "--ver=extra",
    };
    try expectUnexpectedVersionArgument(&long_args, 1);

    const short_args = [_][]const u8{
        "-VV",
        "--ver=extra",
    };
    try expectUnexpectedVersionArgument(&short_args, 2);
}

test "abbreviated version argument failure does not consume later request arguments" {
    const args = [_][]const u8{
        "--ver=extra",
        "--debug",
        "--reference",
        "after.symref",
    };
    try expectUnexpectedVersionArgument(&args, 0);
}
