const std = @import("std");
const testing = std.testing;

const genksyms = @import("../../scripts/zigux/genksyms.zig");

test "genksyms bridge keeps version side effect before missing short dump-types argument" {
    const args = [_][]const u8{"-VT"};
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

test "genksyms bridge keeps repeated version side effects before missing short reference argument" {
    const args = [_][]const u8{"-VVr"};
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
