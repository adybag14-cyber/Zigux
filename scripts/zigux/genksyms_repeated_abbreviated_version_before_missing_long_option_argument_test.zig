const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectMissingLongOptionArgument(
    args: []const []const u8,
    expected_option: []const u8,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms bridge preserves repeated abbreviated version side effects before missing long reference argument" {
    const args = [_][]const u8{
        "--ver",
        "--ver",
        "--reference",
    };
    try expectMissingLongOptionArgument(&args, "--reference");
}

test "genksyms bridge preserves repeated abbreviated version side effects before abbreviated missing long dump-types argument" {
    const args = [_][]const u8{
        "--ver",
        "-V",
        "--dump-t",
    };
    try expectMissingLongOptionArgument(&args, "--dump-types");
}
