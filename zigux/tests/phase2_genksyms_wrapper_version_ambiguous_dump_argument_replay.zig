const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms");

fn expectAmbiguousDumpFailureWithVersionCount(args: []const []const u8, expected_version_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .ambiguous_option => |option| try testing.expectEqualStrings("--du", option),
                else => return error.ExpectedAmbiguousDumpFailure,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}

test "version side effect survives before inline ambiguous dump-family argument" {
    const exact_args = [_][]const u8{
        "--version",
        "--du=extra",
    };
    try expectAmbiguousDumpFailureWithVersionCount(&exact_args, 1);

    const abbreviated_args = [_][]const u8{
        "--ver",
        "--du=extra",
    };
    try expectAmbiguousDumpFailureWithVersionCount(&abbreviated_args, 1);
}

test "repeated short versions survive before ambiguous dump-family prefix" {
    const args = [_][]const u8{
        "-VV",
        "--du",
    };
    try expectAmbiguousDumpFailureWithVersionCount(&args, 2);
}
