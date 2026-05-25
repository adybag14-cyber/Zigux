const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectUnexpectedHelpFailure(args: []const []const u8, expected_version_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--help", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper preserves repeated version counts before exact unexpected help" {
    try expectUnexpectedHelpFailure(&.{ "--version", "--ver", "--help=extra" }, 2);
    try expectUnexpectedHelpFailure(&.{ "-VV", "--version", "--help=extra" }, 3);
}

test "phase2 genksyms wrapper preserves repeated version counts before abbreviated unexpected help" {
    try expectUnexpectedHelpFailure(&.{ "--version", "--ver", "--he=extra" }, 2);
    try expectUnexpectedHelpFailure(&.{ "-V", "--ver", "-VV", "--he=extra" }, 4);
}
