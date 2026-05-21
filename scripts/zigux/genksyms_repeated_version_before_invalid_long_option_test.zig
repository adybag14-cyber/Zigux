const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms bridge keeps repeated version side effects before invalid long option" {
    const args = [_][]const u8{
        "--version",
        "--ver",
        "--unknown",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings("--unknown", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms bridge keeps repeated version side effects before invalid long option with inline argument" {
    const args = [_][]const u8{
        "-V",
        "--version",
        "--not-a-real-option=extra",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings("--not-a-real-option=extra", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
