const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectReferenceLimitAfterVersions(args: []const []const u8, expected_version_count: usize) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(genksyms.ParseFailure.too_many_reference_files, failure.reason);
            try testing.expectEqual(expected_version_count, failure.version_count);
        },
        .command => return error.ExpectedReferenceLimitFailure,
    }
}

test "abbreviated long version is preserved before reference limit failure" {
    const args = [_][]const u8{
        "--ver",
        "--reference=ref-00.symvers",
        "--reference=ref-01.symvers",
        "--reference=ref-02.symvers",
        "--reference=ref-03.symvers",
        "--reference=ref-04.symvers",
        "--reference=ref-05.symvers",
        "--reference=ref-06.symvers",
        "--reference=ref-07.symvers",
        "--reference=ref-08.symvers",
        "--reference=ref-09.symvers",
        "--reference=ref-10.symvers",
        "--reference=ref-11.symvers",
        "--reference=ref-12.symvers",
        "--reference=ref-13.symvers",
        "--reference=ref-14.symvers",
        "--reference=ref-15.symvers",
        "--reference=ref-16.symvers",
    };

    try expectReferenceLimitAfterVersions(&args, 1);
}

test "mixed exact and abbreviated version counts survive separated reference limit" {
    const args = [_][]const u8{
        "--version",
        "--ver",
        "-V",
        "--reference",
        "ref-00.symvers",
        "--reference",
        "ref-01.symvers",
        "--reference",
        "ref-02.symvers",
        "--reference",
        "ref-03.symvers",
        "--reference",
        "ref-04.symvers",
        "--reference",
        "ref-05.symvers",
        "--reference",
        "ref-06.symvers",
        "--reference",
        "ref-07.symvers",
        "--reference",
        "ref-08.symvers",
        "--reference",
        "ref-09.symvers",
        "--reference",
        "ref-10.symvers",
        "--reference",
        "ref-11.symvers",
        "--reference",
        "ref-12.symvers",
        "--reference",
        "ref-13.symvers",
        "--reference",
        "ref-14.symvers",
        "--reference",
        "ref-15.symvers",
        "--reference",
        "ref-16.symvers",
    };

    try expectReferenceLimitAfterVersions(&args, 3);
}
