const std = @import("std");

const fixture = @embedFile("fixtures/phase2_cross_targets.json");
const alignment_checker_path = "scripts/zigux/check-phase2-cross-selftest-alignment.py";

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

fn requireCheckerMarker(checker: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker, marker) != null);
}

fn readAlignmentChecker(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        alignment_checker_path,
        allocator,
        .limited(192 * 1024),
    );
}

fn requireFixtureMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, fixture, marker) != null);
}

test "phase2 cross alignment checker keeps stable pass summary markers" {
    const checker = try readAlignmentChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try requireCheckerMarker(checker, "PHASE2_CROSS_ALIGNMENT=pass");
    try requireCheckerMarker(checker, "PHASE2_CROSS_ALIGNMENT_MARKER_COUNT=");
    try requireCheckerMarker(checker, "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=");
    try requireCheckerMarker(checker, "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=");

    try requireCheckerMarker(checker, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try requireCheckerMarker(checker, "EXPECTED_REQUIRED_MAKE_ROUTES = (");
    try requireCheckerMarker(checker, "\"phase2-cross\",");
}

test "phase2 cross alignment checker keeps grouped failure surface visible" {
    const checker = try readAlignmentChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try requireCheckerMarker(checker, "PHASE2_CROSS_ALIGNMENT=fail");
    try requireCheckerMarker(checker, "MISSING_DOCS_ROOT_README_MARKERS");
    try requireCheckerMarker(checker, "MISSING_PHASE2_NOTES_MARKERS");
    try requireCheckerMarker(checker, "MISSING_REVIEW_CHECKLIST_MARKERS");
    try requireCheckerMarker(checker, "MISSING_TESTS_README_MARKERS");
    try requireCheckerMarker(checker, "MISSING_SCRIPTS_README_MARKERS");
    try requireCheckerMarker(checker, "MISSING_MAKEFILE_LINES");
    try requireCheckerMarker(checker, "DUPLICATE_MAKEFILE_LINES");
    try requireCheckerMarker(checker, "MISSING_TOOLCHAIN_PINNING_MARKERS");
    try requireCheckerMarker(checker, "MISSING_TESTS_ALIGNMENT_MARKERS");
    try requireCheckerMarker(checker, "INVALID_CROSS_TARGET_FIXTURE_FIELD");
    try requireCheckerMarker(checker, "INVALID_CROSS_TARGET_MATRIX");
    try requireCheckerMarker(checker, "DUPLICATE_CROSS_TARGET_ENTRY");
    try requireCheckerMarker(checker, "{code}_START");
    try requireCheckerMarker(checker, "{code}_END");
}

test "phase2 cross alignment checker keeps self-test and fixture shape contract" {
    const checker = try readAlignmentChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try requireCheckerMarker(checker, "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass");
    try requireCheckerMarker(checker, "PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=");
    try requireCheckerMarker(checker, "checks_run == expected_case_count");
    try requireCheckerMarker(checker, "+ 19");
    try requireCheckerMarker(checker, "+ 10");

    try requireFixtureMarker("\"cross_targets\"");
    try requireFixtureMarker("\"archive_target_scope\"");
    try requireFixtureMarker("\"target\": \"x86_64-linux\"");
    try requireFixtureMarker("\"target\": \"aarch64-linux\"");
    try std.testing.expectEqual(@as(usize, 2), countNeedle(fixture, "\"target\": "));
}
