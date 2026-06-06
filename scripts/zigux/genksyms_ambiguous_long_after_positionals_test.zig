const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectAmbiguousLongFailure(
    args: []const []const u8,
    expected_option: []const u8,
    expected_versions: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_versions, failure.version_count);
            switch (failure.reason) {
                .ambiguous_option => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedAmbiguousOption,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}

test "genksyms ambiguous long prefixes still fail after delayed positionals" {
    const cases = [_]struct {
        args: []const []const u8,
        expected_option: []const u8,
        expected_versions: usize,
    }{
        .{
            .args = &.{ "--version", "prelude.c", "-w", "middle.o", "--d" },
            .expected_option = "--d",
            .expected_versions = 1,
        },
        .{
            .args = &.{ "early-positional", "--ver", "--du" },
            .expected_option = "--du",
            .expected_versions = 1,
        },
    };

    for (cases) |case| {
        try expectAmbiguousLongFailure(case.args, case.expected_option, case.expected_versions);
    }
}
