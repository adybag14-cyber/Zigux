const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

fn expectUnexpectedLongArgument(
    args: []const []const u8,
    expected_option: []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedUnexpectedOptionArgument,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}

test "version before unexpected exact long option argument preserves side effect" {
    const args = [_][]const u8{
        "--version",
        "--help=topic",
    };

    try expectUnexpectedLongArgument(&args, "--help", 1);
}

test "version before unexpected abbreviated long option argument canonicalizes failure" {
    const args = [_][]const u8{
        "--ver",
        "--deb=2",
    };

    try expectUnexpectedLongArgument(&args, "--debug", 1);
}

test "clustered short versions before unexpected long option argument preserve repeats" {
    const args = [_][]const u8{
        "-VV",
        "--quiet=no",
    };

    try expectUnexpectedLongArgument(&args, "--quiet", 2);
}
