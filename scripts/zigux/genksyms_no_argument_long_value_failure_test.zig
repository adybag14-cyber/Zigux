const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

fn expectUnexpectedCanonical(args: []const []const u8, expected_option: []const u8, expected_versions: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_versions, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedUnexpectedOptionArgument,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}

test "no-argument long request options reject inline values canonically" {
    const cases = [_]struct {
        args: []const []const u8,
        expected_option: []const u8,
    }{
        .{ .args = &.{"--warnings=on"}, .expected_option = "--warnings" },
        .{ .args = &.{"--warn=on"}, .expected_option = "--warnings" },
        .{ .args = &.{"--quiet=off"}, .expected_option = "--quiet" },
        .{ .args = &.{"--qui=off"}, .expected_option = "--quiet" },
        .{ .args = &.{"--debug=2"}, .expected_option = "--debug" },
        .{ .args = &.{"--preserve=yes"}, .expected_option = "--preserve" },
        .{ .args = &.{"--pres=yes"}, .expected_option = "--preserve" },
    };

    for (cases) |case| {
        try expectUnexpectedCanonical(case.args, case.expected_option, 0);
    }
}

test "exact dump long option with value is not confused with dump-types" {
    try expectUnexpectedCanonical(&.{"--dump=types.symtypes"}, "--dump", 0);
}

test "version side effects survive before no-argument long value failures" {
    try expectUnexpectedCanonical(&.{ "--version", "--warnings=on" }, "--warnings", 1);
    try expectUnexpectedCanonical(&.{ "--ver", "--quiet=off" }, "--quiet", 1);
    try expectUnexpectedCanonical(&.{ "-VV", "--preserve=yes" }, "--preserve", 2);
}
