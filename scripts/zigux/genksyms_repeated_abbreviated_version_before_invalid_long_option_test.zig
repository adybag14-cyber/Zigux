const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectInvalidLongFailure(
    args: []const []const u8,
    expected_version_count: usize,
    expected_option: []const u8,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms keeps repeated abbreviated version side effects before invalid long option" {
    const repeated_abbreviated_args = [_][]const u8{
        "--ver",
        "--ver",
        "--unknown",
    };
    try expectInvalidLongFailure(&repeated_abbreviated_args, 2, "--unknown");

    const mixed_args = [_][]const u8{
        "--ver",
        "-V",
        "--not-a-real-option=extra",
    };
    try expectInvalidLongFailure(&mixed_args, 2, "--not-a-real-option=extra");
}
