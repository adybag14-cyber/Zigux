const std = @import("std");
const testing = std.testing;

const max_file_size = 256 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

test "direct checker keeps grouped failure envelope explicit" {
    const checker_source = try readRepoFile(testing.allocator, "scripts/zigux/check-phase2-cross.py");
    defer testing.allocator.free(checker_source);

    try expectContains(checker_source, "def emit_issues(issues: list[tuple[str, str]]) -> int:");
    try expectContains(checker_source, "grouped: dict[str, list[str]] = {}");
    try expectContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE=fail");
    try expectContains(checker_source, "{code}_START");
    try expectContains(checker_source, "{code}_END");
    try expectOrdered(checker_source, "PHASE2_DIRECT_CROSS_ROUTE=fail", "{code}_START");
    try expectOrdered(checker_source, "{code}_START", "{code}_END");

    try expectContains(checker_source, "MISSING_MAKEFILE_LINE");
    try expectContains(checker_source, "DUPLICATE_MAKEFILE_LINE");
    try expectContains(checker_source, "INVALID_FIXTURE_FIELD");
    try expectContains(checker_source, "ARCHIVE_SCOPE_MISMATCH");
    try expectContains(checker_source, "DUPLICATE_CROSS_TARGET");
    try expectContains(checker_source, "INVALID_CROSS_TARGET_ROUTE");
    try expectContains(checker_source, "INVALID_CROSS_TARGET_ENTRY");
    try expectContains(checker_source, "INVALID_CROSS_TARGET_MODE");
    try expectContains(checker_source, "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH");
}

test "self-test still covers each grouped failure family" {
    const checker_source = try readRepoFile(testing.allocator, "scripts/zigux/check-phase2-cross.py");
    defer testing.allocator.free(checker_source);

    try expectContains(checker_source, "assert (\"MISSING_MAKEFILE_LINE\", marker) in collect_issues(root)");
    try expectContains(checker_source, "assert (\"DUPLICATE_MAKEFILE_LINE\", f\"{marker}:count=2\") in collect_issues(root)");
    try expectContains(checker_source, "assert (\"ARCHIVE_SCOPE_MISMATCH\", \"x86_64-linux\") in collect_issues(root)");
    try expectContains(checker_source, "assert (\"ARCHIVE_REQUIRED_TARGET_SET_MISMATCH\", \"\") in collect_issues(root)");
    try expectContains(checker_source, "assert (\"DUPLICATE_CROSS_TARGET\", \"x86_64-linux\") in collect_issues(root)");
    try expectContains(checker_source, "assert (\"INVALID_CROSS_TARGET_ROUTE\", \"aarch64-linux\") in collect_issues(root)");
    try expectContains(checker_source, "assert (\"INVALID_CROSS_TARGET_ENTRY\", \"aarch64-linux:review_status\") in collect_issues(root)");
    try expectContains(checker_source, "assert (\"INVALID_CROSS_TARGET_MODE\", \"aarch64-linux\") in collect_issues(root)");
    try expectContains(checker_source, "duplicate archive_target_scope entry");
    try expectContains(checker_source, "required file missing");
}

test "pass and self-test output surfaces keep count fields" {
    const checker_source = try readRepoFile(testing.allocator, "scripts/zigux/check-phase2-cross.py");
    defer testing.allocator.free(checker_source);

    try expectContains(checker_source, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass");
    try expectContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT={checks_run}");
    try expectContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try expectContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT={len(cross_targets)}");
    try expectContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT={len(load_archive_target_scope(args.root.resolve()))}");
    try expectOrdered(checker_source, "if issues:", "PHASE2_DIRECT_CROSS_ROUTE=pass");
}

test "fixture remains aligned with the grouped checker boundary" {
    const fixture_source = try readRepoFile(testing.allocator, "zigux/tests/fixtures/phase2_cross_targets.json");
    defer testing.allocator.free(fixture_source);

    try expectContains(fixture_source, "\"phase\": \"Phase 2\"");
    try expectContains(fixture_source, "\"status\": \"active\"");
    try expectContains(fixture_source, "\"archive_target_scope\"");
    try expectContains(fixture_source, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture_source, "\"review_status\": \"pinned bootstrap archive\"");
    try expectContains(fixture_source, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture_source, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture_source, "\"review_status\": \"route contract only\"");
    try expectContains(fixture_source, "\"validation_mode\": \"route_contract_only\"");
    try expectAbsent(fixture_source, "riscv64");

    try testing.expectEqual(@as(usize, 3), countOccurrences(fixture_source, "make -C zigux phase2-cross"));
    try testing.expectEqual(@as(usize, 2), countOccurrences(fixture_source, "\"target\""));
}
