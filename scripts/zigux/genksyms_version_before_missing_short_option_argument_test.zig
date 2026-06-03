const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectVersionedMissingShortArg(
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
        else => return error.ExpectedParseFailure,
    }
}

test "separated short reference missing argument preserves earlier short version side effect" {
    const args = [_][]const u8{
        "-V",
        "-r",
    };

    try expectVersionedMissingShortArg(&args, 1, "r");
}

test "separated short dump-types missing argument preserves repeated short version side effects" {
    const args = [_][]const u8{
        "-V",
        "-V",
        "-T",
    };

    try expectVersionedMissingShortArg(&args, 2, "T");
}

test "separated short missing argument after request option keeps accumulated version count" {
    const args = [_][]const u8{
        "-V",
        "--debug",
        "--version",
        "-r",
    };

    try expectVersionedMissingShortArg(&args, 2, "r");
}
