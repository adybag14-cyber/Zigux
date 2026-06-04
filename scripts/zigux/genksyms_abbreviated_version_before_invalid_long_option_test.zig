const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "abbreviated version preserves side effect before invalid long options" {
    const separated_args = [_][]const u8{
        "--ver",
        "--not-a-genksyms-option",
    };
    const separated_outcome = try genksyms.parseArgs(testing.allocator, &separated_args);
    switch (separated_outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings("--not-a-genksyms-option", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }

    const inline_args = [_][]const u8{
        "--ver",
        "--not-a-genksyms-option=value",
    };
    const inline_outcome = try genksyms.parseArgs(testing.allocator, &inline_args);
    switch (inline_outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings("--not-a-genksyms-option=value", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
