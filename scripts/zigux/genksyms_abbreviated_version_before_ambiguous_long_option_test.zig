const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "genksyms bridge preserves abbreviated version before ambiguous long option" {
    const args = [_][]const u8{
        "--ver",
        "--du=types.symtypes",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .ambiguous_option => |option| try testing.expectEqualStrings("--du", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
