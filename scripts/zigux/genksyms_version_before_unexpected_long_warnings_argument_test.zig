const std = @import("std");
const bridge = @import("genksyms.zig");

const testing = std.testing;

test "genksyms bridge keeps version side effect before unexpected long warnings option argument" {
    const args = [_][]const u8{
        "--version",
        "--warnings=extra",
    };
    const outcome = try bridge.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--warnings", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms bridge keeps abbreviated version side effect before abbreviated unexpected long warnings option argument" {
    const args = [_][]const u8{
        "--ver",
        "--warn=extra",
    };
    const outcome = try bridge.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--warnings", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
