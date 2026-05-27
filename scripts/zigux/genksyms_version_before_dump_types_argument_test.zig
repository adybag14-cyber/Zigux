const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms abbreviated version keeps version side effect before missing dump-types short argument" {
    const args = [_][]const u8{
        "--ver",
        "-T",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("T", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms long version keeps version side effect before missing dump-types short argument" {
    const args = [_][]const u8{
        "--version",
        "-T",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("T", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
