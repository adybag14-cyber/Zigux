const std = @import("std");

const expected_self_test_count = 17;
const checker_source_candidates = [_][]const u8{
    "scripts/zigux/check-phase2-cross.py",
    "../../scripts/zigux/check-phase2-cross.py",
};

fn readCheckerSource(allocator: std.mem.Allocator) ![]u8 {
    for (checker_source_candidates) |path| {
        if (std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024))) |source| {
            return source;
        } else |_| {}
    }
    return error.CheckerSourceNotFound;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |index| {
        count += 1;
        offset += index + needle.len;
    }
    return count;
}

test "direct cross checker keeps the self-test count pinned" {
    const checker_source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(checker_source);

    try expectContains(checker_source, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(checker_source, "assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT");
}

test "direct cross checker increments every advertised self-test case" {
    const checker_source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(checker_source);

    try std.testing.expectEqual(
        @as(usize, expected_self_test_count),
        countOccurrences(checker_source, "checks_run += 1"),
    );
}

test "direct cross checker self-test output remains script-readable" {
    const checker_source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(checker_source);

    try expectContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass");
    try expectContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT={checks_run}");
}

test "direct cross checker normal route output remains machine-readable" {
    const checker_source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(checker_source);

    try expectContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try expectContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE=fail");
    try expectContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT={len(cross_targets)}");
    try expectContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT={len(load_archive_target_scope(args.root.resolve()))}");
}
