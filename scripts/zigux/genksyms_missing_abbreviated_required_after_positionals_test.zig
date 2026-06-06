const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "missing abbreviated long required args after positionals keep canonical names" {
    const cases = [_]struct {
        args: []const []const u8,
        expected_option: []const u8,
        expected_versions: usize,
    }{
        .{
            .args = &.{ "early-positional", "--version", "--ref" },
            .expected_option = "--reference",
            .expected_versions = 1,
        },
        .{
            .args = &.{ "early-positional", "--ver", "--dump-ty" },
            .expected_option = "--dump-types",
            .expected_versions = 1,
        },
    };

    for (cases) |case| {
        const outcome = try genksyms.parseArgs(testing.allocator, case.args);
        switch (outcome) {
            .failure => |failure| {
                try testing.expectEqual(case.expected_versions, failure.version_count);
                switch (failure.reason) {
                    .missing_option_argument => |option| try testing.expectEqualStrings(case.expected_option, option),
                    else => return error.ExpectedMissingOptionArgument,
                }
            },
            else => return error.ExpectedParseFailure,
        }
    }
}
