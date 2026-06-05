const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectTooManyReferenceFiles(args: []const []const u8, expected_version_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .too_many_reference_files => {},
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedReferenceLimitFailure,
    }
}

test "genksyms bridge reports reference limit after positional request input" {
    const args = [_][]const u8{
        "leftover.c",
        "-r",
        "01.symref",
        "-r",
        "02.symref",
        "-r",
        "03.symref",
        "-r",
        "04.symref",
        "-r",
        "05.symref",
        "-r",
        "06.symref",
        "-r",
        "07.symref",
        "-r",
        "08.symref",
        "-r",
        "09.symref",
        "-r",
        "10.symref",
        "-r",
        "11.symref",
        "-r",
        "12.symref",
        "-r",
        "13.symref",
        "-r",
        "14.symref",
        "-r",
        "15.symref",
        "-r",
        "16.symref",
        "-r",
        "17.symref",
    };

    try expectTooManyReferenceFiles(&args, 0);
}

test "genksyms bridge preserves version side effect before reference limit after lone dash" {
    const args = [_][]const u8{
        "-V",
        "-",
        "-r",
        "01.symref",
        "-r",
        "02.symref",
        "-r",
        "03.symref",
        "-r",
        "04.symref",
        "-r",
        "05.symref",
        "-r",
        "06.symref",
        "-r",
        "07.symref",
        "-r",
        "08.symref",
        "-r",
        "09.symref",
        "-r",
        "10.symref",
        "-r",
        "11.symref",
        "-r",
        "12.symref",
        "-r",
        "13.symref",
        "-r",
        "14.symref",
        "-r",
        "15.symref",
        "-r",
        "16.symref",
        "-r",
        "17.symref",
    };

    try expectTooManyReferenceFiles(&args, 1);
}

test "genksyms bridge keeps required-option data out of reference limit counting" {
    const args = [_][]const u8{
        "--dump-types", "-rnot-a-reference",
        "-r",           "01.symref",
        "-r",           "02.symref",
        "-r",           "03.symref",
        "-r",           "04.symref",
        "-r",           "05.symref",
        "-r",           "06.symref",
        "-r",           "07.symref",
        "-r",           "08.symref",
        "-r",           "09.symref",
        "-r",           "10.symref",
        "-r",           "11.symref",
        "-r",           "12.symref",
        "-r",           "13.symref",
        "-r",           "14.symref",
        "-r",           "15.symref",
        "-r",           "16.symref",
        "-r",           "17.symref",
    };

    try expectTooManyReferenceFiles(&args, 0);
}
