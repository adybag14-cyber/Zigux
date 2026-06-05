const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

fn expectUnexpectedLongArgumentFailure(
    args: []const []const u8,
    expected_option: []const u8,
    expected_versions: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_versions, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms bridge keeps positional request input before unexpected help argument" {
    const args = [_][]const u8{
        "input.c",
        "--version",
        "--help=extra",
    };

    try expectUnexpectedLongArgumentFailure(&args, "--help", 1);
}

test "genksyms bridge keeps required option data before unexpected abbreviated version argument" {
    const args = [_][]const u8{
        "--reference",
        "--version",
        "--ver=extra",
    };

    try expectUnexpectedLongArgumentFailure(&args, "--version", 0);
}

test "genksyms bridge keeps short request cluster before unexpected preserve argument" {
    const args = [_][]const u8{
        "-Vd",
        "--preserve=1",
    };

    try expectUnexpectedLongArgumentFailure(&args, "--preserve", 1);
}
