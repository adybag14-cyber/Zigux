const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

fn expectAmbiguousAfterPositionals(
    args: []const []const u8,
    expected_option: []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .ambiguous_option => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedAmbiguousOptionFailure,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}

test "genksyms bridge keeps scanning after positionals before ambiguous long option" {
    const args = [_][]const u8{
        "early-positional.c",
        "--version",
        "late-positional.h",
        "--du",
    };

    try expectAmbiguousAfterPositionals(&args, "--du", 1);
}

test "genksyms bridge strips inline value from delayed ambiguous long option" {
    const args = [_][]const u8{
        "seed-input.c",
        "--du=types.symtypes",
    };

    try expectAmbiguousAfterPositionals(&args, "--du", 0);
}

test "genksyms bridge counts clustered versions before delayed ambiguous long option" {
    const args = [_][]const u8{
        "-VV",
        "middle-positional.o",
        "--d",
    };

    try expectAmbiguousAfterPositionals(&args, "--d", 2);
}
