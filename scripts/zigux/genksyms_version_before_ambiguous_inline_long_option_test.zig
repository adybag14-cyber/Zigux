const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectAmbiguousFailureWithVersions(
    args: []const []const u8,
    expected_versions: usize,
    expected_option: []const u8,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_versions, failure.version_count);
            switch (failure.reason) {
                .ambiguous_option => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms bridge preserves version before ambiguous inline long option" {
    const args = [_][]const u8{
        "--version",
        "--d=tail",
    };

    try expectAmbiguousFailureWithVersions(&args, 1, "--d");
}

test "genksyms bridge preserves repeated versions before ambiguous inline long option" {
    const args = [_][]const u8{
        "-VV",
        "--ver",
        "--du=types.symtypes",
    };

    try expectAmbiguousFailureWithVersions(&args, 3, "--du");
}
