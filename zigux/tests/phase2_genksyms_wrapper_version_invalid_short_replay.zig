const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms_wrapper");

fn expectVersionBeforeInvalidShort(args: []const []const u8, expected_option: []const u8) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedInvalidOptionFailure,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}

test "version side effect survives invalid short option" {
    const exact_args = [_][]const u8{ "--version", "-Z" };
    try expectVersionBeforeInvalidShort(&exact_args, "Z");

    const short_args = [_][]const u8{ "-V", "-Z" };
    try expectVersionBeforeInvalidShort(&short_args, "Z");
}

test "abbreviated version side effect survives invalid short option" {
    const abbreviated_args = [_][]const u8{ "--ver", "-Z" };
    try expectVersionBeforeInvalidShort(&abbreviated_args, "Z");
}
