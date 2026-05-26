const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectUnexpectedHelpArgumentFailure(
    version_prefixes: []const []const u8,
    expected_version_count: usize,
) !void {
    var args = std.ArrayList([]const u8).empty;
    defer args.deinit(testing.allocator);

    try args.appendSlice(testing.allocator, version_prefixes);
    try args.append(testing.allocator, "--help=extra");

    const outcome = try genksyms.parseArgs(testing.allocator, args.items);
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

test "phase2 genksyms wrapper preserves repeated abbreviated version counts before unexpected help argument failures" {
    try expectUnexpectedHelpArgumentFailure(&.{ "--ver", "--ver" }, 2);
    try expectUnexpectedHelpArgumentFailure(&.{ "--ver", "-V", "--ver" }, 3);
    try expectUnexpectedHelpArgumentFailure(&.{ "--version", "--ver", "--ver" }, 3);
}
