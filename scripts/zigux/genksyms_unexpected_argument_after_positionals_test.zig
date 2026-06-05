const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

fn expectUnexpectedArgumentAfterPositionals(
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
                else => return error.ExpectedUnexpectedArgumentFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms rejects unexpected long values after delayed positionals" {
    const args = [_][]const u8{
        "leftover.c",
        "-VV",
        "--debug",
        "rightover.h",
        "--quiet=extra",
    };

    try expectUnexpectedArgumentAfterPositionals(&args, "--quiet", 2);
}

test "genksyms canonicalizes abbreviated unexpected values after positionals" {
    const args = [_][]const u8{
        "source-before.c",
        "--version",
        "--reference",
        "base.symref",
        "source-after.h",
        "--pres=extra",
    };

    try expectUnexpectedArgumentAfterPositionals(&args, "--preserve", 1);
}

test "genksyms keeps exact dump separate from dump-types after positionals" {
    const args = [_][]const u8{
        "first-positional",
        "--ver",
        "--dump=types.symtypes",
        "late-positional",
    };

    try expectUnexpectedArgumentAfterPositionals(&args, "--dump", 1);
}
