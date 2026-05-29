const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

fn expectVersionBeforeAmbiguousLong(args: []const []const u8, expected_option: []const u8) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .ambiguous_option => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedAmbiguousLongFailure,
    }
}

test "genksyms bridge keeps exact version side effect before broad ambiguous long option" {
    const args = [_][]const u8{
        "--version",
        "--d",
    };
    try expectVersionBeforeAmbiguousLong(&args, "--d");
}

test "genksyms bridge keeps abbreviated version side effect before inline ambiguous long option" {
    const args = [_][]const u8{
        "--ver",
        "--du=extra",
    };
    try expectVersionBeforeAmbiguousLong(&args, "--du=extra");
}
