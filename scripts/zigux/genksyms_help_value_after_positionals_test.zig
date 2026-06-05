const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

fn expectUnexpectedHelpArgumentAfterPositionals(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--help", option),
                else => return error.ExpectedUnexpectedHelpArgumentFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms rejects exact help values after delayed positionals" {
    const args = [_][]const u8{
        "leftover.c",
        "--version",
        "rightover.h",
        "--help=usage.txt",
    };

    try expectUnexpectedHelpArgumentAfterPositionals(&args, 1);
}

test "genksyms canonicalizes abbreviated help values after positionals" {
    const args = [_][]const u8{
        "source-before.c",
        "-VV",
        "--debug",
        "source-after.h",
        "--he=extra",
    };

    try expectUnexpectedHelpArgumentAfterPositionals(&args, 2);
}

test "genksyms canonicalizes empty abbreviated help values after required data" {
    const args = [_][]const u8{
        "prelude.c",
        "--reference",
        "--help=literal-reference.symref",
        "--dump-types=types.symtypes",
        "tail.h",
        "--hel=",
    };

    try expectUnexpectedHelpArgumentAfterPositionals(&args, 0);
}
