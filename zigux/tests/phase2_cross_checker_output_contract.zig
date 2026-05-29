const std = @import("std");

const fixture = @embedFile("fixtures/phase2_cross_targets.json");
const checker_path = "scripts/zigux/check-phase2-cross.py";

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

fn readChecker(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        checker_path,
        allocator,
        .limited(128 * 1024),
    );
}

fn requireFixtureMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, fixture, marker) != null);
}

test "phase2 direct cross checker keeps stable pass output markers" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try requireCheckerMarker(checker, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try requireCheckerMarker(checker, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=");
    try requireCheckerMarker(checker, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=");

    try requireFixtureMarker("\"cross_targets\"");
    try requireFixtureMarker("\"archive_target_scope\"");
    try requireFixtureMarker("\"target\": \"x86_64-linux\"");
    try requireFixtureMarker("\"target\": \"aarch64-linux\"");
    try std.testing.expectEqual(@as(usize, 2), countNeedle(fixture, "\"target\": "));
}

test "phase2 direct cross checker keeps stable grouped failure surface" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try requireCheckerMarker(checker, "PHASE2_DIRECT_CROSS_ROUTE=fail");
    try requireCheckerMarker(checker, "MISSING_MAKEFILE_LINE");
    try requireCheckerMarker(checker, "DUPLICATE_MAKEFILE_LINE");
    try requireCheckerMarker(checker, "INVALID_FIXTURE_FIELD");
    try requireCheckerMarker(checker, "ARCHIVE_SCOPE_MISMATCH");
    try requireCheckerMarker(checker, "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH");
    try requireCheckerMarker(checker, "DUPLICATE_CROSS_TARGET");
    try requireCheckerMarker(checker, "INVALID_CROSS_TARGET_ROUTE");
    try requireCheckerMarker(checker, "INVALID_CROSS_TARGET_MODE");
    try requireCheckerMarker(checker, "{code}_START");
    try requireCheckerMarker(checker, "{code}_END");
}

test "phase2 direct cross checker keeps self-test output contract visible" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try requireCheckerMarker(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try requireCheckerMarker(checker, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass");
    try requireCheckerMarker(checker, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT=");
    try requireCheckerMarker(checker, "checks_run == EXPECTED_SELF_TEST_CASE_COUNT");
}
