const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms preserves repeated abbreviated version side effects before abbreviated reference argument failures" {
    const args = [_][]const u8{
        "--ver",
        "--ver",
        "--ref",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("--reference", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms preserves mixed repeated version side effects before abbreviated dump-types argument failures" {
    const args = [_][]const u8{
        "--ver",
        "-V",
        "--dump-t",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("--dump-types", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
