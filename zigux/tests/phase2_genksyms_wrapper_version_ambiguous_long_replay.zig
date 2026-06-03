const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms");

fn expectAmbiguousVersionCount(args: []const []const u8, expected_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_count, failure.version_count);
            switch (failure.reason) {
                .ambiguous_option => |option| try testing.expectEqualStrings("--d", option),
                else => return error.ExpectedAmbiguousLongOptionFailure,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}

test "long version before ambiguous long option preserves side effect" {
    const args = [_][]const u8{
        "--version",
        "--d",
    };

    try expectAmbiguousVersionCount(&args, 1);
}

test "abbreviated version before ambiguous long option preserves side effect" {
    const args = [_][]const u8{
        "--ver",
        "--d",
    };

    try expectAmbiguousVersionCount(&args, 1);
}

test "short version cluster before ambiguous long option preserves every side effect" {
    const args = [_][]const u8{
        "-VV",
        "--d",
    };

    try expectAmbiguousVersionCount(&args, 2);
}
