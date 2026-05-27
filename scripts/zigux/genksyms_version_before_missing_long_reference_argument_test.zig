const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms bridge preserves version side effect before missing long reference argument" {
    const args = [_][]const u8{
        "--version",
        "--reference",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("--reference", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms bridge preserves abbreviated version side effect before abbreviated missing long reference argument" {
    const args = [_][]const u8{
        "--ver",
        "--ref",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("--reference", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
