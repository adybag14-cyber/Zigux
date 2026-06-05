const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

fn expectUnexpectedLongValueAfterPositionals(
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

test "genksyms rejects quiet values after delayed positionals" {
    const args = [_][]const u8{
        "leftover.c",
        "--version",
        "--reference",
        "base.symref",
        "rightover.h",
        "--quiet=off",
    };

    try expectUnexpectedLongValueAfterPositionals(&args, "--quiet", 1);
}

test "genksyms rejects dump values after delayed positionals" {
    const args = [_][]const u8{
        "before.c",
        "-VV",
        "--dump-types",
        "types.symtypes",
        "after.h",
        "--dump=defs",
    };

    try expectUnexpectedLongValueAfterPositionals(&args, "--dump", 2);
}

test "genksyms canonicalizes empty abbreviated preserve values after positionals" {
    const args = [_][]const u8{
        "first-positional",
        "--ver",
        "-d",
        "second-positional",
        "--pres=",
    };

    try expectUnexpectedLongValueAfterPositionals(&args, "--preserve", 1);
}
