const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectUnexpectedLongOptionArgumentFailure(
    args: []const []const u8,
    expected_version_count: usize,
    expected_option: []const u8,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper version-prefixed exact unexpected long option arguments preserve version count" {
    try expectUnexpectedLongOptionArgumentFailure(&.{ "--version", "--quiet=extra" }, 1, "--quiet");
    try expectUnexpectedLongOptionArgumentFailure(&.{ "--ver", "--debug=extra" }, 1, "--debug");
    try expectUnexpectedLongOptionArgumentFailure(&.{ "-V", "--preserve=extra" }, 1, "--preserve");
}

test "phase2 genksyms wrapper version-prefixed abbreviated unexpected long option arguments stay canonical" {
    try expectUnexpectedLongOptionArgumentFailure(&.{ "--version", "--qui=extra" }, 1, "--quiet");
    try expectUnexpectedLongOptionArgumentFailure(&.{ "--ver", "--deb=extra" }, 1, "--debug");
    try expectUnexpectedLongOptionArgumentFailure(&.{ "-V", "--pres=extra" }, 1, "--preserve");
}
