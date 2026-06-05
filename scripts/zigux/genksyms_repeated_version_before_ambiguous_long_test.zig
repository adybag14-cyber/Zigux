const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

test "repeated short versions are counted before ambiguous long option failure" {
    const args = [_][]const u8{
        "-VV",
        "--du",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .ambiguous_option => |option| try testing.expectEqualStrings("--du", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "mixed abbreviated and short versions are counted before ambiguous long option failure" {
    const args = [_][]const u8{
        "--ver",
        "-V",
        "--d",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .ambiguous_option => |option| try testing.expectEqualStrings("--d", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
