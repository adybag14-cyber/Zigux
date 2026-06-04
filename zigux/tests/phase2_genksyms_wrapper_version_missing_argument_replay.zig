const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms");

fn expectMissingArgument(args: []const []const u8, expected_version_count: usize, expected_option: []const u8) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedMissingOptionArgumentFailure,
            }
        },
        .command => return error.ExpectedFailure,
    }
}

test "version side effect is preserved before missing long reference argument" {
    const args = [_][]const u8{
        "--version",
        "--reference",
    };
    try expectMissingArgument(&args, 1, "--reference");
}

test "abbreviated version side effect is preserved before abbreviated missing dump-types argument" {
    const args = [_][]const u8{
        "--ver",
        "--dump-t",
    };
    try expectMissingArgument(&args, 1, "--dump-types");
}

test "clustered short versions are preserved before missing short dump-types argument" {
    const args = [_][]const u8{
        "-VV",
        "-T",
    };
    try expectMissingArgument(&args, 2, "T");
}
