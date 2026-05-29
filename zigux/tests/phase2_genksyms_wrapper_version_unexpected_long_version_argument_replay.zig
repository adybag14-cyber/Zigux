const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms");

fn expectUnexpectedVersionArgument(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
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

test "exact version survives before unexpected exact long version argument" {
    const args = [_][]const u8{
        "--version",
        "--version=extra",
    };
    try expectUnexpectedVersionArgument(&args, 1);
}

test "abbreviated version survives before unexpected abbreviated long version argument" {
    const args = [_][]const u8{
        "--ver",
        "--ver=extra",
    };
    try expectUnexpectedVersionArgument(&args, 1);
}

test "mixed repeated versions survive before unexpected long version argument" {
    const args = [_][]const u8{
        "-V",
        "--version",
        "--ver=extra",
    };
    try expectUnexpectedVersionArgument(&args, 2);
}
