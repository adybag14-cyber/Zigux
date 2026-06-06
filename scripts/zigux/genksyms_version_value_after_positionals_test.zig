const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

fn expectUnexpectedVersionArgumentAfterPositionals(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--version", option),
                else => return error.ExpectedUnexpectedVersionArgumentFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms rejects exact version values after delayed positionals" {
    const args = [_][]const u8{
        "leftover.c",
        "--version",
        "rightover.h",
        "--version=release.txt",
    };

    try expectUnexpectedVersionArgumentAfterPositionals(&args, 1);
}

test "genksyms canonicalizes abbreviated version values after positionals" {
    const args = [_][]const u8{
        "source-before.c",
        "-VV",
        "--debug",
        "source-after.h",
        "--ver=extra",
    };

    try expectUnexpectedVersionArgumentAfterPositionals(&args, 2);
}

test "genksyms rejects empty abbreviated version values after required data" {
    const args = [_][]const u8{
        "prelude.c",
        "--reference",
        "--version=literal-reference.symref",
        "--dump-types=types.symtypes",
        "tail.h",
        "--vers=",
    };

    try expectUnexpectedVersionArgumentAfterPositionals(&args, 0);
}
