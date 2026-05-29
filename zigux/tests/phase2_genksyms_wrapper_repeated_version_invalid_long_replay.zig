const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms");

fn expectInvalidLongFailureWithVersionCount(
    args: []const []const u8,
    expected_option: []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedInvalidLongOptionFailure,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}

test "repeated exact versions survive before invalid long option" {
    const args = [_][]const u8{
        "--version",
        "--version",
        "--unknown",
    };
    try expectInvalidLongFailureWithVersionCount(&args, "--unknown", 2);
}

test "mixed exact versions survive before invalid inline long option" {
    const args = [_][]const u8{
        "-V",
        "--version",
        "--not-a-real-option=extra",
    };
    try expectInvalidLongFailureWithVersionCount(&args, "--not-a-real-option=extra", 2);
}
