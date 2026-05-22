const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms bridge keeps abbreviated version side effect before too many inline reference files" {
    var args: [18][]const u8 = undefined;
    args[0] = "--ver";
    for (args[1..]) |*arg| arg.* = "--reference=foo.symref";

    const outcome = try genksyms.parseArgs(testing.allocator, args[0..]);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .too_many_reference_files => {},
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms bridge keeps abbreviated version side effect before too many short reference files" {
    var args: [35][]const u8 = undefined;
    args[0] = "--ver";
    for (0..17) |index| {
        args[1 + (index * 2)] = "-r";
        args[2 + (index * 2)] = "foo.symref";
    }

    const outcome = try genksyms.parseArgs(testing.allocator, args[0..]);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .too_many_reference_files => {},
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
