const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms bridge preserves repeated version side effects before missing short reference argument" {
    const args = [_][]const u8{
        "--version",
        "--ver",
        "-r",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("r", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms bridge preserves repeated version side effects before missing short dump-types argument" {
    const args = [_][]const u8{
        "-V",
        "--version",
        "-T",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("T", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
