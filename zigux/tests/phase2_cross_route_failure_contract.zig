const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path_from_root: []const u8) ![]u8 {
    const candidate_paths = [_][]const u8{
        path_from_root,
        try std.fs.path.join(allocator, &.{ "../..", path_from_root }),
    };
    defer allocator.free(candidate_paths[1]);

    var last_error: anyerror = error.FileNotFound;
    for (candidate_paths) |candidate_path| {
        return std.Io.Dir.cwd().readFileAlloc(std.testing.io, candidate_path, allocator, .limited(1024 * 1024)) catch |err| {
            last_error = err;
            continue;
        };
    }
    return last_error;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOfPos(u8, haystack, first_index + first.len, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(second_index > first_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    return count;
}

test "direct cross route failures stay grouped for review" {
    const checker_source = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase2-cross.py");
    defer std.testing.allocator.free(checker_source);

    try expectContains(checker_source, "def emit_issues(issues: list[tuple[str, str]]) -> int:");
    try expectContains(checker_source, "print(\"PHASE2_DIRECT_CROSS_ROUTE=fail\")");
    try expectContains(checker_source, "print(f\"{code}_START\")");
    try expectContains(checker_source, "print(f\"{code}_END\")");
    try expectOrdered(checker_source, "print(\"PHASE2_DIRECT_CROSS_ROUTE=fail\")", "print(f\"{code}_START\")");
    try expectOrdered(checker_source, "print(f\"{code}_START\")", "print(f\"{code}_END\")");
}

test "primary route inputs fail closed in the checker self-test" {
    const checker_source = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase2-cross.py");
    defer std.testing.allocator.free(checker_source);

    try expectContains(checker_source, "for primary_path in (TOOLCHAIN_POLICY, MAKEFILE, FIXTURE):");
    try expectContains(checker_source, "resolve_path(root, primary_path).unlink()");
    try expectContains(checker_source, "assert \"required file missing\" in str(exc)");
    try expectContains(checker_source, "raise AssertionError(f\"missing primary file did not abort: {primary_path}\")");
    try expectOrdered(checker_source, "for primary_path in (TOOLCHAIN_POLICY, MAKEFILE, FIXTURE):", "assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT");
}

test "archive scope duplicate validation remains explicit" {
    const checker_source = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase2-cross.py");
    defer std.testing.allocator.free(checker_source);

    try expectContains(checker_source, "def load_archive_target_scope(root: Path) -> list[str]:");
    try expectContains(checker_source, "normalized: list[str] = []");
    try expectContains(checker_source, "seen_targets: set[str] = set()");
    try expectContains(checker_source, "duplicate archive_target_scope entry in required file");
    try expectOrdered(checker_source, "seen_targets: set[str] = set()", "duplicate archive_target_scope entry in required file");
}

test "failure self-test count covers the current direct route surface" {
    const checker_source = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase2-cross.py");
    defer std.testing.allocator.free(checker_source);

    try expectContains(checker_source, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(checker_source, "MISSING_MAKEFILE_LINE");
    try expectContains(checker_source, "DUPLICATE_MAKEFILE_LINE");
    try expectContains(checker_source, "ARCHIVE_SCOPE_MISMATCH");
    try expectContains(checker_source, "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH");
    try expectContains(checker_source, "DUPLICATE_CROSS_TARGET");
    try expectContains(checker_source, "INVALID_CROSS_TARGET_ROUTE");
    try expectContains(checker_source, "INVALID_CROSS_TARGET_ENTRY");
    try expectContains(checker_source, "INVALID_CROSS_TARGET_MODE");
}

test "fixture still splits archive-backed and route-contract targets" {
    const fixture_source = try readRepoFile(std.testing.allocator, "zigux/tests/fixtures/phase2_cross_targets.json");
    defer std.testing.allocator.free(fixture_source);

    try expectContains(fixture_source, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture_source, "\"review_status\": \"pinned bootstrap archive\"");
    try expectContains(fixture_source, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture_source, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture_source, "\"review_status\": \"route contract only\"");
    try expectContains(fixture_source, "\"validation_mode\": \"route_contract_only\"");
    try std.testing.expectEqual(@as(usize, 3), countOccurrences(fixture_source, "\"route\": \"make -C zigux phase2-cross\""));
}
