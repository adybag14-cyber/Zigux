const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms abbreviated version rejects unexpected inline argument without version side effects" {
    const args = [_][]const u8{"--ver=extra"};
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 0), failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--version", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms long version rejects unexpected inline argument without version side effects" {
    const args = [_][]const u8{"--version=extra"};
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 0), failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--version", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
