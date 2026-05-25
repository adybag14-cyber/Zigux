const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms keeps repeated abbreviated version side effects before exact unexpected long option arguments" {
    const args = [_][]const u8{
        "--ver",
        "--ver",
        "--help=extra",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--help", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms keeps mixed repeated abbreviated version side effects before abbreviated unexpected long option arguments" {
    const args = [_][]const u8{
        "--ver",
        "-V",
        "--he=extra",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--help", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
