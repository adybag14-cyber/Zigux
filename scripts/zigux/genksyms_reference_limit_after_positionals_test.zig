const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

fn expectReferenceLimitFailure(args: []const []const u8, expected_version_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .too_many_reference_files => {},
                else => return error.ExpectedReferenceLimitFailure,
            }
        },
        else => return error.ExpectedReferenceLimitFailure,
    }
}

test "genksyms reference limit still fires after delayed positionals" {
    const args = [_][]const u8{
        "--version",
        "prelude.c",
        "-r",
        "01.symref",
        "-r",
        "02.symref",
        "middle.c",
        "--reference=03.symref",
        "--reference",
        "04.symref",
        "-r05.symref",
        "-r",
        "06.symref",
        "--reference=07.symref",
        "-r08.symref",
        "--reference",
        "09.symref",
        "-r",
        "10.symref",
        "--reference=11.symref",
        "-r12.symref",
        "--reference",
        "13.symref",
        "-r",
        "14.symref",
        "--reference=15.symref",
        "-r16.symref",
        "tail.c",
        "--reference",
        "17.symref",
    };

    try expectReferenceLimitFailure(&args, 1);
}

test "genksyms reference limit preserves clustered version side effects" {
    const args = [_][]const u8{
        "-VV",
        "first.o",
        "--ref=01.symref",
        "--ref=02.symref",
        "--ref=03.symref",
        "--ref=04.symref",
        "--ref=05.symref",
        "--ref=06.symref",
        "--ref=07.symref",
        "--ref=08.symref",
        "second.o",
        "--ref=09.symref",
        "--ref=10.symref",
        "--ref=11.symref",
        "--ref=12.symref",
        "--ref=13.symref",
        "--ref=14.symref",
        "--ref=15.symref",
        "--ref=16.symref",
        "third.o",
        "--ref=17.symref",
    };

    try expectReferenceLimitFailure(&args, 2);
}
