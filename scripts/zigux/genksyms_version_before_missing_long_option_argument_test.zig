const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectMissingLongOptionArgument(
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
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms bridge preserves version side effect before missing long reference argument" {
    const args = [_][]const u8{
        "--version",
        "--reference",
    };
    try expectMissingLongOptionArgument(&args, 1, "--reference");
}

test "genksyms bridge preserves abbreviated version side effect before missing long reference argument" {
    const args = [_][]const u8{
        "--ver",
        "--reference",
    };
    try expectMissingLongOptionArgument(&args, 1, "--reference");
}

test "genksyms bridge preserves version side effect before missing long dump-types argument" {
    const args = [_][]const u8{
        "--version",
        "--dump-types",
    };
    try expectMissingLongOptionArgument(&args, 1, "--dump-types");
}

test "genksyms bridge preserves abbreviated version side effect before abbreviated long dump-types argument" {
    const args = [_][]const u8{
        "--ver",
        "--dump-t",
    };
    try expectMissingLongOptionArgument(&args, 1, "--dump-types");
}
